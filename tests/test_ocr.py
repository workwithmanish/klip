import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
from pathlib import Path
import shutil
import tempfile
import unittest
sys.path.insert(0,os.environ.get('KLIP_SOURCE',str(Path(__file__).resolve().parents[1])))
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage,QColor,QPainter,QFont
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from ocr import OCRWindow,prepare_image


class OCRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.image=QImage(700,140,QImage.Format.Format_RGB32)
        self.image.fill(QColor('white'))
        self.script=Path(self.temp.name)/'fake.py'
        self.script.write_text('import sys,time\nif "--list-langs" in sys.argv: print("List of available languages:\\neng")\nelse: print("Recognized sample text")\n')
        self.window=OCRWindow(self.image,[sys.executable,str(self.script)])

    def tearDown(self):
        self.window.close()
        for _ in range(20):
            self.app.processEvents()
            QTest.qWait(5)
        self.temp.cleanup()

    def wait_done(self):
        for _ in range(1000):
            self.app.processEvents()
            if self.window.process is None: return
            QTest.qWait(10)
        self.fail('OCR did not finish')

    def test_async_result_and_editing(self):
        self.window.start()
        self.assertFalse(self.window.extract.isEnabled())
        self.assertIs(self.window.content.currentWidget(),self.window.loading)
        self.assertFalse(self.window.copy_button.isEnabled())
        self.wait_done()
        self.assertEqual(self.window.result.toPlainText(),'Recognized sample text')
        self.assertIs(self.window.content.currentWidget(),self.window.result)
        self.assertTrue(self.window.copy_button.isEnabled())
        self.assertFalse(self.window.loading_timer.isActive())
        self.window.result.setPlainText('Edited result')
        self.assertEqual(self.window.result.toPlainText(),'Edited result')
        self.assertIsNone(self.window.temp)

    def test_missing_language_preserves_text(self):
        self.window.result.setPlainText('Keep my edits')
        self.window.language.setCurrentIndex(1)
        self.window.start(); self.wait_done()
        self.assertIn('tesseract-ocr-hin',self.window.status.text())
        self.assertEqual(self.window.result.toPlainText(),'Keep my edits')

    def test_cancel_and_empty_output(self):
        self.script.write_text('import time\ntime.sleep(10)\n')
        self.window.start(); self.window.cancel_run(); self.wait_done()
        self.assertIn('cancelled',self.window.status.text())
        self.script.write_text('import sys\nif "--list-langs" in sys.argv: print("eng")\n')
        self.window.start(); self.wait_done()
        self.assertIn('No text',self.window.status.text())

    def test_preprocessing_preserves_source(self):
        original=self.image.copy()
        prepared=prepare_image(self.image,True)
        self.assertEqual(self.image,original)
        self.assertGreater(prepared.width(),self.image.width())

    @unittest.skipUnless(shutil.which('tesseract'),'Tesseract not installed')
    def test_real_english_engine(self):
        self.window.engine=None
        painter=QPainter(self.window.image)
        font=QFont('DejaVu Sans'); font.setPixelSize(36)
        painter.setFont(font); painter.setPen(QColor('black'))
        painter.drawText(25,80,'Klip screenshot text 12345')
        painter.end()
        self.window.start(); self.wait_done()
        self.assertIn('12345',self.window.result.toPlainText(),self.window.status.text())


if __name__=='__main__': unittest.main()
