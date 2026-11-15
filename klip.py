"""Klip — original local screenshot capture and annotation tool."""
import argparse
import math
import os
import sys
import copy
from datetime import datetime
from preferences import Preferences, ControlPanel
from icons import tool_icon
from textbox import TextBox
from watermark import timestamp_label, paint_watermark
from ui_spacing import polish_inputs
from ocr import show_ocr
from geometry_tools import handles, hit_handle, paint_handles, transform_rect, cursor_for

from PySide6.QtCore import Qt, QRect, QPoint, QTimer, Signal, QLockFile, QDir, QSize
from PySide6.QtGui import (QAction, QColor, QIcon, QImage, QKeySequence,
                          QPainter, QPen, QPixmap, QShortcut)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QToolBar,
    QFileDialog, QColorDialog, QInputDialog, QScrollArea, QSystemTrayIcon,
    QMenu, QMessageBox, QLabel, QSpinBox, QCheckBox, QPushButton, QHBoxLayout)


class Canvas(QWidget):
    text_editing = Signal(bool)
    object_selected = Signal()
    def __init__(self, image):
        super().__init__()
        self.image = image.convertToFormat(QImage.Format.Format_ARGB32)
        self.history = []
        self.future = []
        self.objects = []
        self.selected = None
        self.hovered = None
        self.drag = None
        self.opacity = 100
        self.watermark_enabled = False
        self.watermark_size = 14
        self.watermark_opacity = 65
        self.watermark_label = image.text('klip-timestamp') or timestamp_label()
        self.filled = False
        self.tool = 'Pen'
        self.text_box = None
        self.color = QColor('#ff526b')
        self.width = 4
        self.start = self.end = None
        self.guide_position = None
        self.guides_enabled = True
        self.setMouseTracking(True)

        self.setFixedSize(self.image.size())
        self.setCursor(Qt.CursorShape.CrossCursor)

    def checkpoint(self):
        self.history.append((self.image.copy(), copy.deepcopy(self.objects)))
        self.history = self.history[-30:]
        self.future.clear()

    def undo(self):
        if self.history:
            self.future.append((self.image.copy(), copy.deepcopy(self.objects)))
            self.image, self.objects = self.history.pop()
            self.selected = None
            self.object_selected.emit()
            self.update()

    def redo(self):
        if self.future:
            self.history.append((self.image.copy(), copy.deepcopy(self.objects)))
            self.image, self.objects = self.future.pop()
            self.selected = None
            self.object_selected.emit()
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawImage(0, 0, self.image)
        for obj in self.objects:
            self.paint_object(p, obj)
        self.paint_watermark(p)
        if self.tool == 'Select' and self.drag is None and self.hovered is not None and self.hovered < len(self.objects) and self.hovered != self.selected:
            glow = copy.deepcopy(self.objects[self.hovered])
            glow['color'] = QColor('#ac9cff')
            glow['filled'] = False
            for extra, opacity in ((10, 10), (5, 18), (2, 45)):
                glow['width'] = self.objects[self.hovered]['width'] + extra
                glow['opacity'] = opacity
                self.paint_object(p, glow)
        if self.start is not None:
            self.draw(p)
        if self.guides_enabled and self.tool != 'Select':
            point = (self.text_box.alignment_point() if self.text_box.moving else None) if self.text_box is not None else self.guide_position
            if point is not None:
                draw_guides(p, self.rect(), point)
        if self.selected is not None:
            paint_handles(p, self.object_rect(self.objects[self.selected]))
        if self.guides_enabled and self.text_box is None and self.tool != 'Select':
            point = self.guide_position
            if point is not None:
                draw_inspector(p, self.rect(), point, self.export_image())

    def object_rect(self, obj):
        return QRect(obj['start'], obj['end']).normalized()

    def paint_object(self, painter, obj):
        names = ('start', 'end', 'tool', 'color', 'width', 'opacity', 'filled')
        saved = {name: getattr(self, name) for name in names}
        for name in names:
            setattr(self, name, obj[name])
        painter.save()
        self.draw(painter)
        painter.restore()
        for name, value in saved.items():
            setattr(self, name, value)

    def export_image(self):
        result = self.image.copy()
        painter = QPainter(result)
        for obj in self.objects:
            self.paint_object(painter, obj)
        self.paint_watermark(painter)
        painter.end()
        return result

    def paint_watermark(self, painter):
        if self.watermark_enabled:
            paint_watermark(painter, self.image.rect(), self.watermark_label, self.watermark_size, self.watermark_opacity)

    def set_property(self, name, value):
        setattr(self, name, value)
        if self.selected is not None:
            self.checkpoint()
            self.objects[self.selected][name] = value
            self.update()

    def delete_selected(self):
        if self.selected is not None:
            self.checkpoint()
            self.objects.pop(self.selected)
            self.selected = None
            self.object_selected.emit()
            self.update()

    def leaveEvent(self, event):
        self.guide_position = None
        self.hovered = None
        self.update()
        super().leaveEvent(event)

    def draw(self, p):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(self.opacity/100)
        p.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine,
                      Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        rect = QRect(self.start, self.end).normalized()
        if self.filled and self.tool in ('Rectangle', 'Ellipse'):
            p.setBrush(self.color)
        if self.tool == 'Rectangle':
            p.drawRect(rect)
        elif self.tool == 'Ellipse':
            p.drawEllipse(rect)
        elif self.tool in ('Line', 'Arrow'):
            p.drawLine(self.start, self.end)
            if self.tool == 'Arrow':
                angle = math.atan2(self.end.y()-self.start.y(), self.end.x()-self.start.x())
                for offset in (-0.5, 0.5):
                    p.drawLine(self.end, self.end - QPoint(int(18*math.cos(angle+offset)), int(18*math.sin(angle+offset))))
        elif self.tool == 'Highlight':
            color = QColor(self.color)
            color.setAlpha(85)
            p.fillRect(rect, color)
        elif self.tool == 'Pixelate':
            p.setPen(QPen(QColor('#7c9aff'), 2, Qt.PenStyle.DashLine))
            p.drawRect(rect)
        elif self.tool == 'Text':
            p.setPen(QPen(QColor('#b4a4ff'), 1, Qt.PenStyle.DashLine))
            p.drawRect(rect)

    def finish_text(self, apply=True):
        box = self.text_box
        if box is None:
            return
        if apply and box.input.toPlainText().strip():
            self.checkpoint()
            painter = QPainter(self.image)
            box.paint_text(painter)
            painter.end()
        self.text_box = None
        box.hide()
        box.deleteLater()
        self.text_editing.emit(False)
        self.setFocus()
        self.update()

    def mousePressEvent(self, event):
        self.guide_position = event.position().toPoint()
        if event.button() != Qt.MouseButton.LeftButton:
            return
        self.finish_text()
        point = event.position().toPoint()
        if self.selected is not None:
            obj = self.objects[self.selected]
            rect = self.object_rect(obj)
            handle = hit_handle(rect, point)
            if handle >= 0 or rect.contains(point):
                self.checkpoint()
                self.drag = (point, rect, handle, copy.deepcopy(obj))
                return
        if self.tool == 'Select':
            self.selected = None
            for index in range(len(self.objects)-1, -1, -1):
                if self.object_rect(self.objects[index]).adjusted(-5,-5,5,5).contains(point):
                    self.selected = index
                    self.object_selected.emit()
                    obj = self.objects[index]
                    self.checkpoint()
                    self.drag = (point, self.object_rect(obj), -1, copy.deepcopy(obj))
                    break
            self.object_selected.emit()
            self.update()
            return
        self.selected = None
        self.start = self.end = event.position().toPoint()
        if self.tool == 'Pen':
            self.checkpoint()
        self.update()

    def mouseMoveEvent(self, event):
        self.guide_position = event.position().toPoint()
        if self.tool == 'Select' and self.drag is None:
            self.hovered = next((i for i in range(len(self.objects)-1, -1, -1)
                if self.object_rect(self.objects[i]).adjusted(-5,-5,5,5).contains(self.guide_position)), None)
            self.setCursor(Qt.CursorShape.PointingHandCursor if self.hovered is not None else Qt.CursorShape.ArrowCursor)
        self.update()
        if self.drag is not None:
            anchor, original, handle, obj = self.drag
            rect = transform_rect(original, anchor, self.guide_position, handle, self.rect())
            current = self.objects[self.selected]
            for name in ('start', 'end'):
                point = obj[name]
                x = rect.left() + round((point.x()-original.left()) * max(1,rect.width()-1)/max(1,original.width()-1))
                y = rect.top() + round((point.y()-original.top()) * max(1,rect.height()-1)/max(1,original.height()-1))
                current[name] = QPoint(x,y)
            return
        if self.selected is not None:
            rect = self.object_rect(self.objects[self.selected])
            handle = hit_handle(rect, self.guide_position)
            self.setCursor(cursor_for(handle) if handle >= 0 or rect.contains(self.guide_position) else Qt.CursorShape.CrossCursor)
        if self.start is None:
            return
        previous = self.end
        self.end = event.position().toPoint()
        if self.tool == 'Pen':
            p = QPainter(self.image)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(QPen(self.color, self.width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(previous, self.end)
            p.end()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.drag is not None:
            self.drag = None
            self.update()
            return
        if self.start is None or event.button() != Qt.MouseButton.LeftButton:
            return
        self.end = event.position().toPoint()
        if self.tool in ('Rectangle', 'Ellipse', 'Highlight', 'Line', 'Arrow'):
            self.checkpoint()
            self.objects.append({name: copy.deepcopy(getattr(self, name)) for name in ('start', 'end', 'tool', 'color', 'width', 'opacity', 'filled')})
            self.selected = len(self.objects)-1
            self.start = self.end = None
            self.object_selected.emit()
            self.update()
            return
        if self.tool == 'Text':
            rect = QRect(self.start, self.end).normalized().intersected(self.rect())
            if rect.width() < 30 or rect.height() < 30:
                rect = QRect(rect.topLeft(), QSize(min(300, self.rect().width()), min(140, self.height())))
            rect.setWidth(min(max(min(120, self.rect().width()), rect.width()), self.rect().width()))
            rect.setHeight(min(max(min(85, self.height()), rect.height()), self.height()))
            rect.moveLeft(max(0, min(rect.left(), self.rect().width()-rect.width())))
            rect.moveTop(max(0, min(rect.top(), self.height()-rect.height())))
            self.start = self.end = None
            self.guide_position = None
            self.text_editing.emit(True)
            self.text_box = TextBox(self, rect, self.color, max(18, self.width * 5))
            self.text_box.accepted.connect(lambda: self.finish_text(True))
            self.text_box.cancelled.connect(lambda: self.finish_text(False))
            self.update()
            return
        if self.tool != 'Pen':
            self.checkpoint()
            if self.tool == 'Pixelate':
                rect = QRect(self.start, self.end).normalized().intersected(self.image.rect())
                if rect.width() > 0 and rect.height() > 0:
                    tile = self.image.copy(rect).scaled(max(1, rect.width()//14), max(1, rect.height()//14))
                    tile = tile.scaled(rect.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                    p = QPainter(self.image)
                    p.drawImage(rect.topLeft(), tile)
                    p.end()
            else:
                p = QPainter(self.image)
                self.draw(p)
                p.end()
        self.start = self.end = None
        self.update()


class Editor(QMainWindow):
    def __init__(self, image, prefs=None):
        super().__init__()
        self.prefs = prefs or Preferences()
        self.setWindowTitle('Klip · Edit capture')
        self.canvas = Canvas(image)
        self.canvas.color = QColor(self.prefs.get('color'))
        self.canvas.width = self.prefs.get('width')
        self.canvas.guides_enabled = self.prefs.get('guides')
        self.shortcut_actions = {}
        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(scroll)
        bar = QToolBar('Annotation tools')
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.setIconSize(QSize(24, 24))
        bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(bar)
        self.tools = []
        for name in ('Select', 'Pen', 'Line', 'Arrow', 'Rectangle', 'Ellipse', 'Highlight', 'Text', 'Pixelate'):
            action = bar.addAction(tool_icon(name), name)
            action.setToolTip(name)
            action.setCheckable(True)
            action.setChecked(name == 'Pen')
            action.triggered.connect(lambda checked=False, n=name: self.select_tool(n))
            self.tools.append(action)
            self.shortcut_actions[name] = action
        bar.addSeparator()
        color_action = bar.addAction(tool_icon('Color'), 'Color', self.choose_color)
        color_action.setToolTip('Annotation color')
        width = QSpinBox()
        width.setRange(1, 30)
        width.setValue(self.canvas.width)
        width.setPrefix('Size ')
        width.setMinimumWidth(100)
        width.setMinimumHeight(34)
        self.width_control = width
        width.valueChanged.connect(lambda value: self.canvas.set_property('width', value))
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(12, 4, 12, 4)
        controls_layout.setSpacing(16)
        controls.setStyleSheet('QSpinBox { background: #292f40; color: #eef0ff; border: 1px solid #4b5671; border-radius: 5px; padding: 5px 8px; padding-right: 24px; } QSpinBox:focus { border-color: #a394ff; } QCheckBox { color: #eef0ff; spacing: 9px; padding: 4px 6px; }')
        asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets').replace('\\', '/')
        controls.setStyleSheet(controls.styleSheet() + '''
            QSpinBox { background: #242835; border: 1px solid #42495d; border-radius: 6px; padding: 6px 10px; padding-right: 27px; selection-background-color: #6254bd; }
            QSpinBox:hover { border-color: #64708d; }
            QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 24px; height: 20px; border: none; background: transparent; border-top-right-radius: 6px; }
            QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 24px; height: 20px; border: none; background: transparent; border-bottom-right-radius: 6px; }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #3b4156; }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed { background: #514797; }
            QSpinBox::up-arrow { image: url("ASSETS/chevron-up.svg"); width: 10px; height: 10px; }
            QSpinBox::down-arrow { image: url("ASSETS/chevron-down.svg"); width: 10px; height: 10px; }
        '''.replace('ASSETS', asset_dir))
        controls_layout.addWidget(width)
        self.opacity_control = QSpinBox()
        self.opacity_control.setRange(5,100)
        self.opacity_control.setValue(100)
        self.opacity_control.setPrefix('Opacity ')
        self.opacity_control.setSuffix('%')
        self.opacity_control.setMinimumWidth(155)
        self.opacity_control.setMinimumHeight(34)
        self.opacity_control.valueChanged.connect(lambda value: self.canvas.set_property('opacity', value))
        controls_layout.addWidget(self.opacity_control)
        self.fill_control = QCheckBox('Fill')
        self.fill_control.setMinimumHeight(34)
        self.fill_control.toggled.connect(lambda value: self.canvas.set_property('filled', value))
        controls_layout.addWidget(self.fill_control)
        self.controls_separator = bar.addSeparator()
        self.controls_action = bar.addWidget(controls)
        self.canvas.object_selected.connect(self.sync_object_controls)
        self.update_tool_controls()
        bar2 = QToolBar('Capture actions')
        bar2.setMovable(False)
        bar2.setFloatable(False)
        bar2.setIconSize(QSize(22, 22))
        bar2.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, bar2)
        for name, callback, shortcut in [('Undo', self.canvas.undo, 'Ctrl+Z'), ('Redo', self.canvas.redo, 'Ctrl+Shift+Z'), ('Copy', self.copy, 'Ctrl+C'), ('Save', self.save, 'Ctrl+S')]:
            action = bar2.addAction(tool_icon(name), name, callback)
            action.setShortcut(QKeySequence(shortcut))
            self.shortcut_actions[name] = action
        bar2.addSeparator()
        ocr_action = bar2.addAction('Extract text (OCR)', self.extract_text)
        ocr_action.setToolTip('Read text from this image locally using Tesseract (excludes the timestamp watermark)')
        self.watermark_toggle = QCheckBox('Timestamp')
        self.watermark_toggle.setStyleSheet('color: #eef0ff; padding: 8px;')
        self.watermark_toggle.setToolTip('Show the capture timestamp at bottom-right using your system timezone')
        bar2.addWidget(self.watermark_toggle)
        self.watermark_font = QSpinBox()
        self.watermark_font.setRange(8, 48)
        self.watermark_font.setValue(14)
        self.watermark_font.setPrefix('Size ')
        self.watermark_font.setSuffix(' px')
        self.watermark_font.setMinimumWidth(110)
        self.watermark_alpha = QSpinBox()
        self.watermark_alpha.setRange(0,100)
        self.watermark_alpha.setValue(65)
        self.watermark_alpha.setPrefix('Opacity ')
        self.watermark_alpha.setSuffix('%')
        self.watermark_alpha.setMinimumWidth(140)
        watermark_controls = QWidget()
        watermark_layout = QHBoxLayout(watermark_controls)
        watermark_layout.setContentsMargins(12, 4, 12, 4)
        watermark_layout.setSpacing(16)
        watermark_layout.addWidget(self.watermark_font)
        watermark_layout.addWidget(self.watermark_alpha)
        watermark_controls.setStyleSheet(controls.styleSheet())
        font_action = bar2.addWidget(watermark_controls)
        alpha_action = font_action
        font_action.setVisible(False)
        alpha_action.setVisible(False)
        def watermark_changed():
            enabled = self.watermark_toggle.isChecked()
            self.canvas.watermark_enabled = enabled
            self.canvas.watermark_size = self.watermark_font.value()
            self.canvas.watermark_opacity = self.watermark_alpha.value()
            font_action.setVisible(enabled)
            alpha_action.setVisible(enabled)
            self.canvas.update()
        self.watermark_toggle.toggled.connect(watermark_changed)
        self.watermark_font.valueChanged.connect(watermark_changed)
        self.watermark_alpha.valueChanged.connect(watermark_changed)
        close_action = QAction('Close', self)
        close_action.triggered.connect(self.close)
        self.addAction(close_action)
        self.shortcut_actions['Close'] = close_action
        self.apply_shortcuts()
        delete = QShortcut(QKeySequence('Delete'), self)
        delete.activated.connect(self.canvas.delete_selected)
        self.delete_shortcut = delete
        self.canvas.text_editing.connect(self.text_mode)
        self.statusBar().showMessage('Edit locally · Ctrl+S save · Ctrl+C copy')
        self.resize(min(1200, image.width()+60), min(850, image.height()+150))
        self.setStyleSheet('QToolBar { spacing: 6px; padding: 5px 8px; } QStatusBar { padding: 4px 8px; }')
        polish_inputs(self)

    def apply_shortcuts(self):
        for name, action in self.shortcut_actions.items():
            action.setShortcut(QKeySequence(self.prefs.shortcut(name)))
            shortcut = self.prefs.shortcut(name)
            action.setToolTip(name + (' (' + shortcut + ')' if shortcut else ''))
        self.canvas.guides_enabled = self.prefs.get('guides')
        self.canvas.update()
        self.statusBar().showMessage('Ready · Shortcuts can be changed in Klip Settings')

    def text_mode(self, active):
        # Let normal typing and text-editor shortcuts reach the inline editor.
        for action in self.shortcut_actions.values():
            action.setShortcut(QKeySequence() if active else QKeySequence(self.prefs.shortcut(action.text())))
        self.delete_shortcut.setEnabled(not active)
        self.statusBar().showMessage('Drag header to move · Drag corner to resize · Enter apply · Shift+Enter new line · Esc cancel' if active else 'Text applied or cancelled · Ready')

    def select_tool(self, name):
        self.canvas.finish_text()
        self.canvas.selected = None
        self.canvas.update()
        self.canvas.tool = name
        self.canvas.hovered = None
        self.canvas.setCursor(Qt.CursorShape.ArrowCursor if name == 'Select' else Qt.CursorShape.CrossCursor)
        self.update_tool_controls()
        for action in self.tools:
            action.setChecked(action.text() == name)

    def choose_color(self):
        color = QColorDialog.getColor(self.canvas.color, self)
        if color.isValid():
            self.canvas.set_property('color', color)

    def sync_object_controls(self):
        self.update_tool_controls()
        if self.canvas.selected is None:
            return
        obj = self.canvas.objects[self.canvas.selected]
        self.canvas.color = QColor(obj['color'])
        for name in ('width', 'opacity', 'filled'):
            setattr(self.canvas, name, obj[name])
        for widget, name in ((self.width_control, 'width'), (self.opacity_control, 'opacity'), (self.fill_control, 'filled')):
            widget.blockSignals(True)
            if name == 'filled': widget.setChecked(obj[name])
            else: widget.setValue(obj[name])
            widget.blockSignals(False)

    def update_tool_controls(self):
        tool = self.canvas.tool
        if self.canvas.selected is not None:
            tool = self.canvas.objects[self.canvas.selected]['tool']
        self.width_control.setVisible(tool in ('Pen', 'Line', 'Arrow', 'Rectangle', 'Ellipse', 'Text'))
        self.opacity_control.setVisible(tool in ('Line', 'Arrow', 'Rectangle', 'Ellipse', 'Highlight'))
        self.fill_control.setVisible(tool in ('Rectangle', 'Ellipse'))
        relevant = tool in ('Pen', 'Line', 'Arrow', 'Rectangle', 'Ellipse', 'Text', 'Highlight')
        self.controls_action.setVisible(relevant)
        self.controls_separator.setVisible(relevant)

    def copy(self):
        self.canvas.finish_text()
        QApplication.clipboard().setImage(self.canvas.export_image())
        self.statusBar().showMessage('Capture copied to clipboard', 4000)

    def extract_text(self):
        self.canvas.finish_text()
        enabled = self.canvas.watermark_enabled
        self.canvas.watermark_enabled = False
        try:
            image = self.canvas.export_image()
        finally:
            self.canvas.watermark_enabled = enabled
        show_ocr(image)

    def save(self):
        self.canvas.finish_text()
        fmt = self.prefs.get('format')
        name = 'Klip-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.' + fmt
        path, _ = QFileDialog.getSaveFileName(self, 'Save capture', os.path.join(self.prefs.get('folder'), name), 'PNG image (*.png)' if fmt == 'png' else 'JPEG image (*.jpg)')
        if path:
            if not path.lower().endswith('.' + fmt):
                path += '.' + fmt
            if not self.canvas.export_image().save(path, fmt.upper()):
                QMessageBox.warning(self, 'Save failed', 'Could not write the image to that location.')
            else:
                self.statusBar().showMessage('Saved to ' + path, 5000)


def draw_guides(painter, rect, position):
    """Draw transient alignment guides; never modify the image buffer."""
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    for color, width in ((QColor(0, 0, 0, 180), 3), (QColor('#79deed'), 1)):
        painter.setPen(QPen(color, width, Qt.PenStyle.DashLine))
        painter.drawLine(rect.left(), position.y(), rect.right(), position.y())
        painter.drawLine(position.x(), rect.top(), position.x(), rect.bottom())
    painter.restore()


def draw_inspector(painter, bounds, point, source):
    """Transient pixel loupe; coordinates are image pixels, origin top-left."""
    if source.isNull():
        return
    sx = source.width()/max(1, bounds.width())
    sy = source.height()/max(1, bounds.height())
    x = max(0, min(source.width()-1, int((point.x()-bounds.left())*sx)))
    y = max(0, min(source.height()-1, int((point.y()-bounds.top())*sy)))
    color = source.pixelColor(x, y).name().upper()
    painter.save()
    painter.setOpacity(1)
    font = painter.font()
    font.setPixelSize(10)
    painter.setFont(font)
    painter.setPen(QColor('#b0d7ee'))
    for value in range(0, source.width(), 100):
        px = bounds.left()+round(value/sx)
        painter.drawLine(px, bounds.top(), px, bounds.top()+5)
        painter.drawText(px+3, bounds.top()+14, str(value))
    for value in range(0, source.height(), 100):
        py = bounds.top()+round(value/sy)
        painter.drawLine(bounds.left(), py, bounds.left()+5, py)
        painter.drawText(bounds.left()+7, py+12, str(value))
    painter.restore()
    width, height = 190, 116
    if bounds.width() < width+8 or bounds.height() < height+8:
        return
    left = point.x()+22
    top = point.y()+22
    if left+width > bounds.right()-4:
        left = point.x()-width-22
    if top+height > bounds.bottom()-4:
        top = point.y()-height-22
    left = max(bounds.left()+4, min(left, bounds.right()-width-4))
    top = max(bounds.top()+4, min(top, bounds.bottom()-height-4))
    painter.save()
    painter.setOpacity(1)
    painter.setPen(QPen(QColor('#8aa6da'), 1))
    painter.setBrush(QColor('#171b27'))
    painter.drawRoundedRect(left, top, width, height, 6, 6)
    # Pad the source sample so the inspected pixel stays centered at edges.
    sample = QImage(15, 9, QImage.Format.Format_ARGB32)
    sample.fill(QColor('#34405c'))
    sp = QPainter(sample)
    sp.drawImage(7-x, 4-y, source)
    sp.end()
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
    painter.drawImage(QRect(left+5, top+5, 180, 72), sample)
    painter.setPen(QPen(QColor('#64e4d4'), 1))
    painter.drawLine(left+95, top+5, left+95, top+77)
    painter.drawLine(left+5, top+41, left+185, top+41)
    painter.drawRect(left+89, top+37, 12, 8)
    font = painter.font()
    font.setPixelSize(12)
    painter.setFont(font)
    painter.setPen(QColor('#eef0ff'))
    painter.drawText(left+9, top+94, f'X {x}   Y {y}')
    painter.fillRect(left+9, top+101, 12, 10, QColor(color))
    painter.drawText(left+28, top+111, color)
    painter.restore()


class Selection(QWidget):
    selected = Signal(QImage)
    cancelled = Signal()

    def __init__(self, screen, guides=True):
        super().__init__()
        self.shot = screen.grabWindow(0)
        self.timestamp = timestamp_label()
        self.start = self.end = None
        self.selection_rect = None
        self.selection_drag = None
        self.guide_position = None
        self.guides_enabled = guides
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setGeometry(screen.geometry())
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        self.confirm_bar = QWidget(self)
        self.confirm_bar.setCursor(Qt.CursorShape.ArrowCursor)
        self.confirm_bar.setStyleSheet('QWidget { background: #222838; color: white; } QPushButton { padding: 8px 16px; border: 1px solid #8794c4; border-radius: 4px; background: #6254bd; color: white; }')
        layout = QHBoxLayout(self.confirm_bar)
        layout.setContentsMargins(6,6,6,6)
        capture = QPushButton('Capture')
        capture.setCursor(Qt.CursorShape.ArrowCursor)
        capture.clicked.connect(self.confirm)
        cancel = QPushButton('Cancel · Esc')
        cancel.setCursor(Qt.CursorShape.ArrowCursor)
        cancel.clicked.connect(self.cancel)
        layout.addWidget(capture)
        layout.addWidget(cancel)
        self.confirm_bar.hide()

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawPixmap(self.rect(), self.shot)
        p.fillRect(self.rect(), QColor(0, 0, 0, 115))
        rect = QRect(self.start, self.end).normalized() if self.start is not None else self.selection_rect
        if rect is not None:
            p.save()
            p.setClipRect(rect)
            p.drawPixmap(self.rect(), self.shot)
            p.restore()
            p.setPen(QPen(QColor('#75a7ff'), 2))
            p.drawRect(rect)
            paint_handles(p, rect)
        p.setPen(Qt.GlobalColor.white)
        p.drawText(24, 32, 'KLIP  /  Drag area · Move/resize selection · Enter or double-click to capture · Esc cancel')
        if self.guides_enabled and self.guide_position is not None and self.selection_rect is None:
            draw_guides(p, self.rect(), self.guide_position)
            draw_inspector(p, self.rect(), self.guide_position, self.shot.toImage())

    def leaveEvent(self, event):
        self.guide_position = None
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.position().toPoint()
            if self.selection_rect is not None:
                handle = hit_handle(self.selection_rect, point)
                if handle >= 0 or self.selection_rect.contains(point):
                    self.selection_drag = (point, QRect(self.selection_rect), handle)
                    return
            self.selection_rect = None
            self.confirm_bar.hide()
            self.start = self.end = point

    def mouseMoveEvent(self, event):
        self.guide_position = event.position().toPoint()
        self.update()
        if self.selection_drag is not None:
            anchor, rect, handle = self.selection_drag
            self.selection_rect = transform_rect(rect, anchor, self.guide_position, handle, self.rect())
            self.position_confirm_bar()
            return
        if self.selection_rect is not None:
            handle = hit_handle(self.selection_rect, self.guide_position)
            self.setCursor(cursor_for(handle) if handle >= 0 or self.selection_rect.contains(self.guide_position) else Qt.CursorShape.CrossCursor)
        if self.start is not None:
            self.end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.selection_drag is not None:
            self.selection_drag = None
            return
        if self.start is None:
            return
        self.end = event.position().toPoint()
        rect = QRect(self.start, self.end).normalized().intersected(self.rect())
        if rect.width() < 3 or rect.height() < 3:
            return
        self.selection_rect = rect
        self.start = self.end = None
        self.position_confirm_bar()
        self.confirm_bar.show()
        self.confirm_bar.raise_()
        self.update()

    def position_confirm_bar(self):
        if self.selection_rect is None:
            return
        self.confirm_bar.adjustSize()
        rect = self.selection_rect
        gap = 8
        width, height = self.confirm_bar.width(), self.confirm_bar.height()
        left = rect.left()
        top = rect.bottom()+gap
        if top+height > self.height()-4:
            top = rect.top()-height-gap
        if top < 4:
            top = rect.bottom()-height-gap
        self.confirm_bar.move(max(4, min(left, self.rect().width()-width-4)),
                              max(4, min(top, self.height()-height-4)))
        self.confirm_bar.raise_()

    def confirm(self):
        if self.selection_rect is None:
            return
        rect = self.selection_rect
        ratio = self.shot.devicePixelRatio()
        physical = QRect(round(rect.x()*ratio), round(rect.y()*ratio), round(rect.width()*ratio), round(rect.height()*ratio))
        result = self.shot.toImage().copy(physical)
        result.setText('klip-timestamp', self.timestamp)
        result.setDevicePixelRatio(1)
        self.hide()
        self.selected.emit(result)

    def cancel(self):
        self.hide()
        self.cancelled.emit()

    def mouseDoubleClickEvent(self, event):
        if self.selection_rect is not None and self.selection_rect.contains(event.position().toPoint()):
            self.confirm()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.confirm()
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.cancelled.emit()


class Controller:
    def __init__(self, app):
        self.app = app
        self.prefs = Preferences()
        self.panel = None
        self.overlays = []
        self.editors = []
        icon_image = QPixmap(64, 64)
        icon_image.fill(QColor('#7160e8'))
        p = QPainter(icon_image)
        p.setPen(QPen(Qt.GlobalColor.white, 5))
        p.drawRect(15, 18, 34, 28)
        p.drawLine(26, 12, 26, 25)
        p.end()
        self.icon = QIcon(icon_image)
        app.setWindowIcon(self.icon)
        self.tray = QSystemTrayIcon(self.icon)
        self.tray.setToolTip('Klip · Capture and annotate')
        menu = QMenu()
        menu.addAction('Capture area', self.capture)
        menu.addAction('Capture text (OCR)', lambda: self.capture('ocr'))
        menu.addAction('Settings…', self.show_settings)
        menu.addSeparator()
        menu.addAction('Quit Klip', app.quit)
        self.tray.setContextMenu(menu)
        self.menu = menu
        self.tray.activated.connect(lambda reason: self.capture() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    def show_settings(self):
        if self.panel is None:
            self.panel = ControlPanel(self.prefs, self.settings_changed, self.capture)
        self.panel.show()
        self.panel.raise_()
        self.panel.activateWindow()

    def settings_changed(self):
        for editor in self.editors:
            editor.apply_shortcuts()

    def cleanup(self):
        for overlay in self.overlays:
            overlay.close()
            overlay.deleteLater()
        self.overlays.clear()

    def capture(self, mode='edit'):
        if self.overlays:
            return
        self.capture_mode = 'ocr' if mode == 'ocr' else 'edit'
        if os.environ.get('XDG_SESSION_TYPE') == 'wayland':
            QMessageBox.information(None, 'Klip · X11 required', 'This first version supports X11 capture. Log into an X11 desktop session to capture. Wayland portal support is planned.')
            return
        for screen in self.app.screens():
            overlay = Selection(screen, self.prefs.get('guides'))
            if overlay.shot.isNull():
                self.cleanup()
                QMessageBox.warning(None, 'Capture failed', 'The desktop did not provide a screenshot.')
                return
            overlay.selected.connect(self.capture_finished)
            overlay.cancelled.connect(self.cleanup)
            self.overlays.append(overlay)
        for overlay in self.overlays:
            overlay.show()
            overlay.raise_()
            overlay.activateWindow()

    def capture_finished(self, image):
        if self.capture_mode == 'ocr':
            self.cleanup()
            show_ocr(image)
        else:
            self.edit(image)

    def edit(self, image):
        self.cleanup()
        if self.prefs.get('sound'):
            QApplication.beep()
        editor = Editor(image, self.prefs)
        editor.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.editors.append(editor)
        editor.destroyed.connect(lambda: self.editors.remove(editor) if editor in self.editors else None)
        editor.show()
        editor.raise_()
        editor.activateWindow()


def main():
    parser = argparse.ArgumentParser(description='Klip screenshot tool')
    parser.add_argument('--capture', action='store_true', help='Capture immediately; signals an existing instance')
    parser.add_argument('--ocr', action='store_true', help='Select a screen area and extract text locally')
    parser.add_argument('--settings', action='store_true', help='Open the Klip control panel')
    parser.add_argument('--background', action='store_true', help='Start quietly in the tray')
    parser.add_argument('--open', metavar='IMAGE', help='Open an image in the editor')
    args = parser.parse_args()
    app = QApplication(sys.argv)
    app.setApplicationName('Klip')
    app.setQuitOnLastWindowClosed(False)
    app.setStyle('Fusion')
    app.setStyleSheet('QMainWindow, QToolBar, QMenu { background: #222532; color: #eef0ff; } QToolButton { padding: 8px; color: #eef0ff; } QToolButton:checked { background: #6254bd; border-radius: 5px; } QScrollArea { background: #151722; }')
    server = None
    lock = None
    if not args.open:
        name = 'klip-' + os.environ.get('USER', os.environ.get('USERNAME', 'desktop'))
        lock = QLockFile(QDir.tempPath() + '/' + name + '.lock')
        if not lock.tryLock(100):
            socket = QLocalSocket()
            socket.connectToServer(name)
            if not socket.waitForConnected(1500):
                print('Klip is starting or unavailable; try again.', file=sys.stderr)
                return 1
            socket.write(b'ocr' if args.ocr else b'capture' if args.capture else b'settings' if not args.background else b'background')
            socket.waitForBytesWritten(1500)
            socket.disconnectFromServer()
            return 0
        QLocalServer.removeServer(name)
        server = QLocalServer()
        server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption)
        if not server.listen(name):
            print(server.errorString(), file=sys.stderr)
            return 1
    controller = Controller(app)
    connections = []
    if server:
        def receive():
            while server.hasPendingConnections():
                connection = server.nextPendingConnection()
                connections.append(connection)
                buffer = bytearray()
                handled = [False]
                timeout = QTimer(connection)
                timeout.setSingleShot(True)
                def expire(c=connection, done=handled):
                    if done[0] != 'closed':
                        c.abort()
                timeout.timeout.connect(expire)
                timeout.start(5000)
                def dispatch(c=connection, data=buffer, done=handled):
                    if done[0]:
                        return
                    data.extend(bytes(c.readAll()))
                    message = bytes(data)
                    if done[0] or message not in (b'capture', b'ocr', b'settings', b'background'):
                        return
                    done[0] = True
                    if message == b'capture':
                        QTimer.singleShot(150, controller.capture)
                    elif message == b'ocr':
                        QTimer.singleShot(150, lambda: controller.capture('ocr'))
                    elif message == b'settings':
                        controller.show_settings()
                    c.disconnectFromServer()
                def release(c=connection, timer=timeout, done=handled):
                    if done[0] == 'closed':
                        return
                    done[0] = 'closed'
                    timer.stop()
                    if c in connections:
                        connections.remove(c)
                    c.deleteLater()
                connection.readyRead.connect(dispatch)
                connection.disconnected.connect(release)
                # Read any bytes already buffered now, while the socket is alive.
                # The timeout is owned by the socket, so deletion cancels it.
                dispatch()
        server.newConnection.connect(receive)
    if args.open:
        image = QImage(args.open)
        if image.isNull():
            print('Cannot open image: ' + args.open, file=sys.stderr)
            return 1
        controller.edit(image)
        app.setQuitOnLastWindowClosed(True)
    elif args.ocr:
        QTimer.singleShot(200, lambda: controller.capture('ocr'))
    elif args.capture:
        QTimer.singleShot(200, controller.capture)
    elif args.settings or not args.background or not QSystemTrayIcon.isSystemTrayAvailable():
        QTimer.singleShot(0, controller.show_settings)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())

