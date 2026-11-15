import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, os.environ.get('KLIP_SOURCE', str(Path(__file__).resolve().parents[1])))
from PySide6.QtCore import QPoint, Qt, QSettings
from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from klip import Editor
from preferences import Preferences, normalize_binding, xfce_key


class EditorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        prefs = Preferences()
        prefs.store = QSettings(str(Path(self.temp.name)/'test.ini'), QSettings.Format.IniFormat)
        self.image = QImage(800, 450, QImage.Format.Format_ARGB32)
        self.image.fill(QColor('#222532'))
        self.editor = Editor(self.image, prefs)
        self.editor.show()
        self.app.processEvents()

    def tearDown(self):
        self.editor.close()
        self.app.processEvents()
        self.temp.cleanup()

    def test_context_controls(self):
        for tool, expected in {'Pen':(1,0,0), 'Text':(1,0,0), 'Line':(1,1,0),
            'Arrow':(1,1,0), 'Rectangle':(1,1,1), 'Ellipse':(1,1,1),
            'Highlight':(0,1,0), 'Pixelate':(0,0,0), 'Select':(0,0,0)}.items():
            self.editor.select_tool(tool)
            self.app.processEvents()
            self.assertEqual(tuple(int(w.isVisible()) for w in
                (self.editor.width_control, self.editor.opacity_control, self.editor.fill_control)), expected)

    def test_shape_export_and_undo(self):
        c = self.editor.canvas
        self.editor.select_tool('Rectangle')
        QTest.mousePress(c, Qt.MouseButton.LeftButton, pos=QPoint(40,40))
        QTest.mouseMove(c, QPoint(180,130))
        QTest.mouseRelease(c, Qt.MouseButton.LeftButton, pos=QPoint(180,130))
        self.assertEqual(len(c.objects), 1)
        self.assertEqual(c.image, self.image)
        self.assertNotEqual(c.export_image(), self.image)
        c.undo()
        self.assertEqual(c.export_image(), self.image)
        c.redo()
        self.assertEqual(len(c.objects), 1)

    def test_watermark_is_optional(self):
        c = self.editor.canvas
        self.assertEqual(c.export_image(), c.image)
        self.editor.watermark_toggle.setChecked(True)
        self.assertNotEqual(c.export_image(), c.image)
        self.editor.watermark_alpha.setValue(0)
        self.assertEqual(c.export_image(), c.image)

    def test_inline_text_cancel(self):
        c = self.editor.canvas
        self.editor.select_tool('Text')
        QTest.mouseClick(c, Qt.MouseButton.LeftButton, pos=QPoint(60,60))
        self.assertIsNotNone(c.text_box)
        QTest.keyClicks(c.text_box.input, 'test text')
        QTest.keyClick(c.text_box.input, Qt.Key.Key_Escape)
        self.assertIsNone(c.text_box)
        self.assertEqual(c.image, self.image)

    def test_xfce_key_normalization(self):
        self.assertEqual(normalize_binding(xfce_key('Ctrl+Alt+K')), normalize_binding('<Alt><Primary>k'))


if __name__ == '__main__':
    unittest.main()
