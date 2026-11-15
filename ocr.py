"""Offline, asynchronous Tesseract OCR and editable results."""
import shutil
import tempfile
from pathlib import Path
from PySide6.QtCore import QProcess, QTimer, Qt
from PySide6.QtGui import QImage, QPainter, QColor
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QCheckBox, QPushButton, QPlainTextEdit, QApplication, QFileDialog)
from ui_spacing import polish_inputs


def prepare_image(image, improve):
    result = QImage(image.size(), QImage.Format.Format_RGB32)
    result.fill(Qt.GlobalColor.white)
    painter = QPainter(result)
    painter.drawImage(0, 0, image)
    painter.end()
    if improve:
        result = result.convertToFormat(QImage.Format.Format_Grayscale8)
        samples = [result.pixelColor(x,y).red() for y in range(0,result.height(),max(1,result.height()//20))
                   for x in range(0,result.width(),max(1,result.width()//20))]
        if samples and sum(samples)/len(samples) < 127:
            result.invertPixels()
        # Bound enlargement on large screenshots to avoid excessive memory use.
        factor = min(2.0, 3200/max(result.width(),result.height()))
        if factor > 1:
            result = result.scaled(round(result.width()*factor), round(result.height()*factor),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    bordered = QImage(result.width()+24, result.height()+24, QImage.Format.Format_RGB32)
    bordered.fill(Qt.GlobalColor.white)
    painter = QPainter(bordered)
    painter.drawImage(12,12,result)
    painter.end()
    return bordered


class OCRWindow(QWidget):
    windows = set()
    def __init__(self, image, engine=None):
        super().__init__()
        self.image = image.copy()
        self.engine = engine
        self.process = None
        self.temp = None
        self.stage = ''
        self.closing = False
        self.cancelled = False
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        OCRWindow.windows.add(self)
        self.destroyed.connect(lambda: OCRWindow.windows.discard(self))
        self.setWindowTitle('Klip · Extract text (OCR)')
        self.resize(820,600)
        self.setMinimumSize(620,440)
        self.setStyleSheet('QWidget { background: #171b27; color: #eef0ff; } QPlainTextEdit, QComboBox { background: #262d40; border: 1px solid #526385; border-radius: 5px; padding: 8px; } QPushButton { background: #34405c; border: 1px solid #526385; border-radius: 5px; padding: 9px 14px; } QPushButton:hover { background: #514797; } QPushButton:disabled { color: #778298; } QCheckBox { spacing: 8px; }')
        root = QVBoxLayout(self)
        root.setContentsMargins(20,20,20,20)
        root.setSpacing(14)
        title = QLabel('Extract text')
        title.setStyleSheet('font-size: 24px; font-weight: 600;')
        root.addWidget(title)
        note = QLabel('Offline OCR · Review and edit the result before copying, especially commands or code.')
        note.setWordWrap(True)
        root.addWidget(note)
        options = QHBoxLayout()
        options.setSpacing(12)
        options.addWidget(QLabel('Language'))
        self.language = QComboBox()
        for name, code in [('English','eng'),('Hindi','hin'),('English + Hindi','eng+hin')]:
            self.language.addItem(name,code)
        options.addWidget(self.language)
        self.layout_mode = QComboBox()
        self.layout_mode.addItem('Text block', '6')
        self.layout_mode.addItem('Scattered text', '11')
        self.layout_mode.addItem('Automatic layout', '3')
        options.addWidget(self.layout_mode)
        self.improve = QCheckBox('Improve small / dark text')
        self.improve.setChecked(True)
        options.addWidget(self.improve)
        root.addLayout(options)
        self.result = QPlainTextEdit()
        self.result.setPlaceholderText('Recognized text appears here. You can edit it before copying or saving.')
        root.addWidget(self.result,1)
        self.status = QLabel('Ready. Click Extract text.')
        self.status.setWordWrap(True)
        root.addWidget(self.status)
        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        self.extract = QPushButton('Extract text / Retry')
        self.extract.clicked.connect(self.start)
        self.cancel = QPushButton('Cancel OCR')
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(self.cancel_run)
        copy = QPushButton('Copy text')
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.result.toPlainText()))
        save = QPushButton('Save .txt')
        save.clicked.connect(self.save_text)
        close = QPushButton('Close')
        close.clicked.connect(self.close)
        for widget in (self.extract,self.cancel,copy,save,close):
            buttons.addWidget(widget)
        root.addLayout(buttons)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)
        polish_inputs(self)

    def busy(self, value):
        for control in (self.extract,self.language,self.layout_mode,self.improve):
            control.setEnabled(not value)
        self.cancel.setEnabled(value)

    def start(self):
        if self.process is not None:
            return
        command = self.engine or ([shutil.which('tesseract')] if shutil.which('tesseract') else None)
        if not command:
            self.status.setText('Tesseract is not installed. On Kali/Debian run: sudo apt install tesseract-ocr tesseract-ocr-eng (Hindi: tesseract-ocr-hin). Then Retry.')
            return
        self.command = command
        self.cancelled = False
        self.timed_out = False
        self.busy(True)
        self.status.setText('Checking installed OCR languages…')
        self.launch(['--list-langs'], 'languages')

    def launch(self, arguments, stage):
        self.stage = stage
        self.process = QProcess(self)
        self.process.finished.connect(self.finished)
        self.process.errorOccurred.connect(self.process_error)
        self.timer.start(60000)
        self.process.start(self.command[0],self.command[1:]+arguments)

    def process_error(self, error):
        if error == QProcess.ProcessError.FailedToStart:
            self.finish('Could not start Tesseract. Check its installation and executable permissions.')

    def finished(self, code, exit_status):
        if self.process is None:
            return
        process = self.process
        text = bytes(process.readAllStandardOutput()).decode('utf-8','replace')
        diagnostic = bytes(process.readAllStandardError()).decode('utf-8','replace')
        process.deleteLater()
        self.process = None
        self.timer.stop()
        if self.cancelled:
            self.finish('OCR cancelled.' if not getattr(self,'timed_out',False) else 'OCR timed out. Try a smaller area.')
            return
        if code or exit_status != QProcess.ExitStatus.NormalExit:
            self.finish('OCR failed: '+(diagnostic.strip()[-900:] or 'The engine exited unexpectedly.'))
            return
        if self.stage == 'languages':
            available = set(text.splitlines()) | set(diagnostic.splitlines())
            missing = [lang for lang in self.language.currentData().split('+') if lang not in available]
            if missing:
                self.finish('Missing language data. Install: sudo apt install '+' '.join('tesseract-ocr-'+lang for lang in missing)+'. Then Retry.')
                return
            try:
                self.temp = tempfile.TemporaryDirectory(prefix='klip-ocr-')
                path = str(Path(self.temp.name)/'capture.png')
                if not prepare_image(self.image,self.improve.isChecked()).save(path,'PNG'):
                    raise OSError('Could not write the temporary OCR image.')
            except OSError as error:
                self.finish(str(error))
                return
            self.status.setText('Recognizing text locally…')
            self.launch([path,'stdout','-l',self.language.currentData(),'--psm',self.layout_mode.currentData(),'-c','preserve_interword_spaces=1'], 'ocr')
            return
        if text.strip():
            self.result.setPlainText(text.strip())
            self.finish('Done. Review/edit the text, then Copy or Save. Retry replaces the current result.')
        else:
            self.finish('No text found. Previous edits were kept. Try a tighter crop, another layout, or toggle image improvement.')

    def finish(self, message):
        self.timer.stop()
        if self.process is not None:
            self.process.deleteLater()
            self.process = None
        if self.temp is not None:
            self.temp.cleanup()
            self.temp = None
        self.status.setText(message)
        self.busy(False)
        if self.closing:
            self.close()

    def cancel_run(self):
        if self.process is not None:
            self.cancelled = True
            self.process.kill()

    def timeout(self):
        self.timed_out = True
        self.cancel_run()

    def save_text(self):
        path,_ = QFileDialog.getSaveFileName(self,'Save recognized text',str(Path.home()/'Klip-text.txt'),'Text (*.txt)')
        if path:
            try:
                Path(path).write_text(self.result.toPlainText(),encoding='utf-8')
                self.status.setText('Text saved.')
            except OSError as error:
                self.status.setText('Save failed: '+str(error))

    def closeEvent(self, event):
        if self.process is not None:
            self.closing = True
            self.cancel_run()
            event.ignore()
        else:
            event.accept()


def show_ocr(image):
    window = OCRWindow(image)
    window.show()
    window.raise_()
    window.activateWindow()
    QTimer.singleShot(0,window.start)
    return window
