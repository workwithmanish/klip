"""Qt-facing, non-blocking desktop portal client."""
import json
import os
import sys
from pathlib import Path
from PySide6.QtCore import QObject,QProcess,Signal,QUrl
from PySide6.QtGui import QImage


def use_capture_portal():
    return os.environ.get('XDG_SESSION_TYPE','').lower() == 'wayland' or Path('/.flatpak-info').exists()


def image_from_uri(uri):
    url = QUrl(uri)
    if not url.isLocalFile() or url.host() not in ('','localhost'):
        raise ValueError('The portal returned a non-local screenshot URI.')
    image = QImage(url.toLocalFile())
    if image.isNull():
        raise ValueError('The screenshot returned by the desktop could not be opened.')
    return image


class PortalClient(QObject):
    image_ready = Signal(QImage)
    error = Signal(str)
    cancelled = Signal()
    shortcut_ready = Signal()
    activated = Signal(str)
    stopped = Signal()

    def __init__(self,parent=None):
        super().__init__(parent)
        self.process = None
        self.buffer = b''
        self.received = False

    def start(self, mode, window=''):
        if self.process is not None:
            return False
        self.buffer = b''
        self.received = False
        process = self.process = QProcess(self)
        process.readyReadStandardOutput.connect(self.read)
        process.finished.connect(self.finished)
        process.errorOccurred.connect(self.failed)
        process.start(sys.executable,[str(Path(__file__).with_name('portal_helper.py')),mode,window])
        return True

    def read(self):
        if self.process is None:
            return
        self.buffer += bytes(self.process.readAllStandardOutput())
        while b'\n' in self.buffer:
            line,self.buffer = self.buffer.split(b'\n',1)
            try:
                data = json.loads(line)
                self.received = True
                event = data.get('event')
                if event == 'screenshot':
                    self.image_ready.emit(image_from_uri(data['uri']))
                elif event == 'error':
                    self.error.emit(data.get('message','Desktop portal failed.'))
                elif event == 'cancelled':
                    self.cancelled.emit()
                elif event == 'shortcuts-ready':
                    self.shortcut_ready.emit()
                elif event == 'activated':
                    self.activated.emit(data['action'])
            except (ValueError,KeyError) as error:
                self.error.emit(str(error))

    def failed(self,error):
        if error == QProcess.ProcessError.FailedToStart:
            self.error.emit('Could not start the portal helper.')
            self.finished()

    def finished(self,*args):
        if self.process is None:
            return
        self.read()
        process,self.process = self.process,None
        if not self.received:
            diagnostic = bytes(process.readAllStandardError()).decode('utf-8','replace')
            self.error.emit(diagnostic[-600:] or 'Desktop portal helper exited without a response.')
        process.deleteLater()
        self.stopped.emit()

    def stop(self):
        if self.process is not None:
            self.received = True
            self.process.kill()
