import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,os.environ.get('KLIP_SOURCE',str(Path(__file__).resolve().parents[1])))
from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage,QColor
from portals import image_from_uri,use_capture_portal


class PortalImageTests(unittest.TestCase):
    def test_query_errors_are_unknown_instead_of_unsupported(self):
        from portal_helper import capability_error
        for error in ('org.freedesktop.DBus.Error.InvalidArgs',
                      'org.freedesktop.DBus.Error.AccessDenied',
                      'org.freedesktop.DBus.Error.UnknownInterface',
                      'Portal capability check timed out'):
            result = capability_error(error)
            self.assertIsNone(result['available'])
            self.assertEqual(result['status'], 'unknown')
            self.assertEqual(result['error'], error)
        result = capability_error('org.freedesktop.DBus.Error.ServiceUnknown')
        self.assertFalse(result['available'])
        self.assertEqual(result['status'], 'unavailable')

    def test_local_uri_and_reject_remote(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'screen with spaces.png'
            image=QImage(80,40,QImage.Format.Format_RGB32);image.fill(QColor('red'));image.save(str(path))
            self.assertEqual(image_from_uri(QUrl.fromLocalFile(str(path)).toString()).size(),image.size())
        for uri in ('https://example.com/screen.png','file://remotehost/screen.png','not-a-uri'):
            with self.assertRaises(ValueError):image_from_uri(uri)

    def test_wayland_uses_portal(self):
        with patch.dict(os.environ,{'XDG_SESSION_TYPE':'wayland'}):
            self.assertTrue(use_capture_portal())

    def test_wayland_display_fallback_without_session_variable(self):
        with patch.dict(os.environ, {'XDG_SESSION_TYPE':'', 'WAYLAND_DISPLAY':'wayland-0'}):
            self.assertTrue(use_capture_portal())

    def test_screenshot_options_negotiate_advertised_version(self):
        from portal_helper import screenshot_options
        variant = lambda kind, value: value
        self.assertNotIn('interactive', screenshot_options({'version':1}, variant))
        self.assertNotIn('target', screenshot_options({'version':2}, variant))
        self.assertEqual(screenshot_options({'version':3, 'AvailableTargets':5}, variant)['target'], 4)
        self.assertNotIn('target', screenshot_options({'version':3, 'AvailableTargets':1}, variant))


class CapabilityQueryTests(unittest.IsolatedAsyncioTestCase):
    async def test_probe_error_empty_success_and_timeout(self):
        import asyncio
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        from dbus_next import MessageType, Variant
        from portal_helper import portal_properties
        bus = SimpleNamespace(call=AsyncMock(return_value=SimpleNamespace(
            message_type=MessageType.ERROR, error_name='org.freedesktop.DBus.Error.InvalidArgs')))
        result = await portal_properties(bus, 'org.freedesktop.portal.Screenshot')
        self.assertIsNone(result['available'])
        self.assertEqual(result['status'], 'unknown')
        bus.call.return_value = SimpleNamespace(message_type=MessageType.METHOD_RETURN, body=[{}])
        self.assertIsNone((await portal_properties(bus, 'test'))['available'])
        bus.call.return_value.body = [{'version': Variant('u', 3), 'AvailableTargets': Variant('u', 5)}]
        result = await portal_properties(bus, 'test')
        self.assertTrue(result['available'])
        self.assertEqual(result['status'], 'available')
        self.assertEqual(result['AvailableTargets'], 5)
        bus.call.side_effect = asyncio.TimeoutError
        self.assertIsNone((await portal_properties(bus, 'test'))['available'])


@unittest.skipUnless(os.environ.get('DBUS_SESSION_BUS_ADDRESS'),'Requires a temporary session bus')
class PortalProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_dbus_request_response(self):
        import asyncio
        from dbus_next.aio import MessageBus
        from dbus_next.service import ServiceInterface,method,signal,dbus_property
        from dbus_next.constants import PropertyAccess
        from dbus_next import Variant
        import portal_helper
        class Request(ServiceInterface):
            def __init__(self):super().__init__('org.freedesktop.portal.Request')
            @signal()
            def Response(self,code:'u',data:'a{sv}')->'ua{sv}':return [code,data]
        request=Request()
        response_code=[0]
        request_path='/org/freedesktop/portal/desktop/request/test/klip_mock'
        class Registry(ServiceInterface):
            def __init__(self):super().__init__('org.freedesktop.host.portal.Registry')
            @method()
            def Register(self,app_id:'s',options:'a{sv}'):
                if app_id!='io.github.workwithmanish.klip':raise ValueError('Incorrect app identity')
        class Screenshot(ServiceInterface):
            def __init__(self):super().__init__('org.freedesktop.portal.Screenshot')
            @dbus_property(access=PropertyAccess.READ)
            def version(self)->'u': return 3
            @dbus_property(access=PropertyAccess.READ)
            def AvailableTargets(self)->'u': return 5
            @method()
            def Screenshot(self,parent:'s',options:'a{sv}')->'o':
                if not options['interactive'].value:raise ValueError('Must request interactive capture')
                if options['target'].value != 4:raise ValueError('Must request advertised area target')
                asyncio.get_running_loop().call_later(.05,lambda:request.Response(response_code[0],{'uri':Variant('s','file:///tmp/test.png')}))
                return request_path
        bus=await MessageBus().connect()
        await bus.request_name(portal_helper.SERVICE)
        bus.export(portal_helper.PATH,Registry());bus.export(portal_helper.PATH,Screenshot())
        bus.export(request_path,request)
        emitted=[]
        try:
            with patch.object(portal_helper,'emit',side_effect=lambda **data:emitted.append(data)):
                await asyncio.wait_for(portal_helper.run('capabilities'),5)
            self.assertEqual(emitted[0]['screenshot']['version'],3)
            self.assertEqual(emitted[0]['screenshot']['AvailableTargets'],5)
            emitted.clear()
            with patch.object(portal_helper,'emit',side_effect=lambda **data:emitted.append(data)):
                await asyncio.wait_for(portal_helper.run('screenshot'),5)
            self.assertEqual(emitted,[{'event':'screenshot','uri':'file:///tmp/test.png'}])
            response_code[0]=1
            with self.assertRaises(PermissionError):
                await asyncio.wait_for(portal_helper.run('screenshot'),5)
            response_code[0]=2
            with self.assertRaises(RuntimeError):
                await asyncio.wait_for(portal_helper.run('screenshot'),5)
        finally:bus.disconnect()
