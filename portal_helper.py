"""Async desktop portal protocol; isolated from Qt's event loop."""
import asyncio
import json
import sys
import uuid
from pathlib import Path

APP_ID = 'io.github.workwithmanish.klip'
SERVICE = 'org.freedesktop.portal.Desktop'
PATH = '/org/freedesktop/portal/desktop'


def emit(**data):
    print(json.dumps(data), flush=True)


async def portal_properties(bus, interface):
    """Inspect advertised support without requesting screenshot permission."""
    from dbus_next import Message, MessageType
    try:
        reply = await asyncio.wait_for(bus.call(Message(destination=SERVICE, path=PATH,
            interface='org.freedesktop.DBus.Properties', member='GetAll',
            signature='s', body=[interface])), 3)
        if reply.message_type == MessageType.ERROR:
            return {'available': False, 'error': reply.error_name}
        values = {key: value.value for key, value in reply.body[0].items()}
        return {'available': bool(values), **values}
    except asyncio.TimeoutError:
        return {'available': False, 'error': 'Portal capability check timed out'}


def screenshot_options(capabilities, variant):
    options = {'modal': variant('b', False)}
    version = capabilities.get('version')
    if version is None or version >= 2:
        options['interactive'] = variant('b', True)
    if version is not None and version >= 3 and capabilities.get('AvailableTargets', 0) & 4:
        options['target'] = variant('u', 4)
    return options


async def run(mode, parent=''):
    from dbus_next.aio import MessageBus
    from dbus_next import Message, MessageType, Variant
    bus = await MessageBus().connect()
    if mode == 'capabilities':
        try:
            screenshot = await portal_properties(bus, 'org.freedesktop.portal.Screenshot')
            shortcuts = await portal_properties(bus, 'org.freedesktop.portal.GlobalShortcuts')
            emit(event='capabilities', screenshot=screenshot, shortcuts=shortcuts)
        finally:
            bus.disconnect()
        return
    if not Path('/.flatpak-info').exists():
        registration = await bus.call(Message(destination=SERVICE,path=PATH,
            interface='org.freedesktop.host.portal.Registry',member='Register',
            signature='sa{sv}',body=[APP_ID,{}]))
        if registration.message_type == MessageType.ERROR and registration.error_name not in (
            'org.freedesktop.DBus.Error.UnknownInterface','org.freedesktop.DBus.Error.UnknownMethod'):
            raise RuntimeError('Desktop app registration failed: '+str(registration.body))
    pending = {}
    activated = asyncio.Queue()

    def receive(message):
        if message.message_type != MessageType.SIGNAL:
            return
        if message.interface == 'org.freedesktop.portal.Request' and message.member == 'Response':
            future = pending.get(message.path)
            if future is not None and not future.done():
                future.set_result(message.body)
        if message.interface == 'org.freedesktop.portal.GlobalShortcuts' and message.member == 'Activated':
            activated.put_nowait(message.body)
    bus.add_message_handler(receive)
    rule = "type='signal',sender='org.freedesktop.portal.Desktop'"
    reply = await bus.call(Message(destination='org.freedesktop.DBus',path='/org/freedesktop/DBus',
        interface='org.freedesktop.DBus',member='AddMatch',signature='s',body=[rule]))
    if reply.message_type == MessageType.ERROR:
        raise RuntimeError(reply.body[0])

    async def call_request(interface, member, signature, body, options):
        token = 'klip_'+uuid.uuid4().hex
        options['handle_token'] = Variant('s',token)
        sender = bus.unique_name.lstrip(':').replace('.','_')
        path = '/org/freedesktop/portal/desktop/request/'+sender+'/'+token
        future = asyncio.get_running_loop().create_future()
        pending[path] = future
        try:
            reply = await bus.call(Message(destination=SERVICE,path=PATH,interface=interface,
                member=member,signature=signature,body=body))
            if reply.message_type == MessageType.ERROR:
                raise RuntimeError(str(reply.body[0]) if reply.body else reply.error_name)
            actual = reply.body[0]
            if actual != path:
                pending[actual] = future
            try:
                code, results = await asyncio.wait_for(future,180)
            except asyncio.TimeoutError:
                await bus.call(Message(destination=SERVICE,path=actual,
                    interface='org.freedesktop.portal.Request',member='Close'))
                raise RuntimeError('Desktop permission request timed out.')
            if code == 1:
                raise PermissionError('Desktop request cancelled.')
            if code != 0:
                raise RuntimeError('Desktop portal denied the request or the backend failed.')
            return {key:value.value for key,value in results.items()}
        finally:
            for key in list(pending):
                if pending[key] is future:
                    pending.pop(key)

    try:
        if mode == 'screenshot':
            capabilities = await portal_properties(bus, 'org.freedesktop.portal.Screenshot')
            options = screenshot_options(capabilities, Variant)
            results = await call_request('org.freedesktop.portal.Screenshot','Screenshot','sa{sv}',[parent,options],options)
            emit(event='screenshot',uri=results.get('uri',''))
        else:
            interface = 'org.freedesktop.portal.GlobalShortcuts'
            options = {'session_handle_token':Variant('s','klip_'+uuid.uuid4().hex)}
            result = await call_request(interface,'CreateSession','a{sv}',[options],options)
            session = result['session_handle']
            options = {}
            shortcuts = [['capture',{'description':Variant('s','Capture area with Klip')}],
                         ['ocr',{'description':Variant('s','Capture text with Klip')}]]
            result = await call_request(interface,'BindShortcuts','oa(sa{sv})sa{sv}',
                [session,shortcuts,parent,options],options)
            # An empty returned list means no shortcut was granted.
            if not result.get('shortcuts'):
                raise RuntimeError('No shortcuts were enabled. Use desktop keyboard settings as a fallback.')
            emit(event='shortcuts-ready')
            while True:
                body = await activated.get()
                if body[0] == session and body[1] in ('capture','ocr'):
                    emit(event='activated',action=body[1])
    finally:
        bus.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(run(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else ''))
    except PermissionError as error:
        emit(event='cancelled',message=str(error))
    except Exception as error:
        emit(event='error',message=str(error))
        sys.exit(1)
