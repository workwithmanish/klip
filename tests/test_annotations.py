"""User-facing annotation regressions: retained edits, picking and history."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import sys
from pathlib import Path
import unittest
sys.path.insert(0, os.environ.get('KLIP_SOURCE', str(Path(__file__).resolve().parents[1])))
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from klip import Canvas, diagnostics


class AnnotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.source = QImage(640, 420, QImage.Format.Format_ARGB32)
        self.source.fill(QColor('white'))
        self.c = Canvas(self.source)
        self.c.guides_enabled = False
        self.c.show()
        self.app.processEvents()

    def tearDown(self):
        self.c.close()
        self.c.deleteLater()
        self.app.processEvents()

    def draw(self, tool, start, end):
        self.c.tool = tool
        self.c.selected = None
        QTest.mousePress(self.c, Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(self.c, end)
        QTest.mouseRelease(self.c, Qt.MouseButton.LeftButton, pos=end)

    def text(self):
        self.draw('Text', QPoint(40, 60), QPoint(280, 180))
        QTest.keyClicks(self.c.text_box.input, 'Hello Klip')
        QTest.keyClick(self.c.text_box.input, Qt.Key.Key_Return)

    def test_pen_retains_points_and_can_move_undo_recolor(self):
        self.draw('Pen', QPoint(40, 40), QPoint(160, 110))
        self.assertEqual(self.c.image, self.source)
        self.assertEqual(self.c.objects[0]['tool'], 'Pen')
        self.assertEqual(self.c.hit_object(QPoint(100, 75)), 0)
        before = self.c.export_image()
        self.c.tool = 'Select'
        QTest.mousePress(self.c, Qt.MouseButton.LeftButton, pos=QPoint(100,75))
        QTest.mouseMove(self.c, QPoint(140,115))
        QTest.mouseRelease(self.c, Qt.MouseButton.LeftButton, pos=QPoint(140,115))
        self.assertNotEqual(self.c.export_image(), before)
        self.c.undo()
        self.assertEqual(self.c.export_image(), before)
        self.c.redo()
        self.c.selected = 0
        self.c.set_property('color', QColor('blue'))
        self.assertEqual(self.c.objects[0]['color'], QColor('blue'))

    def test_text_reedit_cancel_commit_delete_and_history(self):
        self.text()
        self.assertEqual(self.c.image, self.source)
        self.assertEqual(self.c.objects[0]['text'], 'Hello Klip')
        original = self.c.export_image()
        self.c.tool = 'Select'
        QTest.mouseDClick(self.c, Qt.MouseButton.LeftButton, pos=QPoint(80,100))
        self.assertIsNotNone(self.c.text_box)
        self.c.text_box.input.setPlainText('Changed')
        QTest.keyClick(self.c.text_box.input, Qt.Key.Key_Escape)
        self.assertEqual(self.c.export_image(), original)
        QTest.mouseDClick(self.c, Qt.MouseButton.LeftButton, pos=QPoint(80,100))
        self.c.text_box.input.setPlainText('Changed')
        QTest.keyClick(self.c.text_box.input, Qt.Key.Key_Return)
        self.assertEqual(len(self.c.objects), 1)
        self.assertEqual(self.c.objects[0]['text'], 'Changed')
        self.c.undo()
        self.assertEqual(self.c.export_image(), original)
        self.c.redo()
        self.assertEqual(self.c.objects[0]['text'], 'Changed')
        self.c.selected = 0
        self.c.delete_selected()
        self.assertEqual(self.c.export_image(), self.source)

    def test_hit_testing_ignores_empty_shape_interiors(self):
        self.draw('Ellipse', QPoint(50,50), QPoint(200,200))
        self.assertIsNone(self.c.hit_object(QPoint(125,125)))
        self.assertEqual(self.c.hit_object(QPoint(125,50)), 0)
        self.draw('Line', QPoint(250,50), QPoint(400,200))
        self.assertIsNone(self.c.hit_object(QPoint(260,180)))
        self.assertEqual(self.c.hit_object(QPoint(325,125)), 1)

    def test_chronological_layering_and_pixelate_undo(self):
        self.draw('Rectangle', QPoint(30,30), QPoint(220,180))
        self.c.color = QColor('blue')
        self.c.width = 12
        self.draw('Pen', QPoint(10,80), QPoint(250,80))
        self.assertEqual(self.c.export_image().pixelColor(30,80), QColor('blue'))
        before = self.c.export_image()
        self.draw('Pixelate', QPoint(20,60), QPoint(90,110))
        self.assertEqual(self.c.image, self.source)
        self.assertNotEqual(self.c.export_image(), before)
        self.c.undo()
        self.assertEqual(self.c.export_image(), before)

    def test_cursor_moves_reuse_composite_and_edit_invalidates_it(self):
        self.draw('Rectangle', QPoint(30,30), QPoint(100,100))
        cached = self.c.composed_image()
        QTest.mouseMove(self.c, QPoint(400,200))
        self.assertIs(self.c.composed_image(), cached)
        self.c.set_property('color', QColor('blue'))
        self.assertIsNot(self.c.composed_image(), cached)
        self.c.undo()
        self.assertEqual(self.c.export_image().pixelColor(30,60), QColor('#ff526b'))

    def test_select_without_drag_does_not_consume_undo(self):
        self.draw('Line', QPoint(40,40), QPoint(180,120))
        self.c.tool = 'Select'
        QTest.mouseClick(self.c, Qt.MouseButton.LeftButton, pos=QPoint(110,80))
        self.c.undo()
        self.assertEqual(self.c.objects, [])

    def test_diagnostics_omits_personal_paths_and_capture_data(self):
        report = diagnostics()
        self.assertEqual(report['application'], 'Klip')
        self.assertIsInstance(report['session_bus_present'], bool)
        self.assertNotIn('HOME', report)
        self.assertNotIn('screenshot', report)


if __name__ == '__main__':
    unittest.main()
