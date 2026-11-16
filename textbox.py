"""Transparent inline text placement with move and resize handles."""
from PySide6.QtCore import Qt, QPoint, QRectF, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QTextDocument
from PySide6.QtWidgets import QWidget, QTextEdit


def text_document(text, pixels, color, width, family):
    """The same explicit pixel font and margins used by inline editing and export."""
    from PySide6.QtGui import QTextCursor, QTextCharFormat
    font = QFont(family)
    font.setPixelSize(pixels)
    doc = QTextDocument()
    doc.setDefaultFont(font)
    doc.setDocumentMargin(4)
    doc.setPlainText(text)
    cursor = QTextCursor(doc)
    cursor.select(QTextCursor.SelectionType.Document)
    fmt = QTextCharFormat()
    fmt.setFont(font)
    fmt.setForeground(QColor(color))
    cursor.mergeCharFormat(fmt)
    doc.setTextWidth(width)
    return doc


class TextInput(QTextEdit):
    accepted = Signal()
    cancelled = Signal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.accepted.emit()
        elif event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
        else:
            super().keyPressEvent(event)


class MoveHandle(QWidget):
    def __init__(self, box):
        super().__init__(box)
        self.box = box
        self.offset = None
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setToolTip('Drag to move text box')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.offset = event.globalPosition().toPoint() - self.box.pos()
            self.box.moving = True
            self.box.parentWidget().update()

    def mouseMoveEvent(self, event):
        if self.offset is not None:
            point = event.globalPosition().toPoint() - self.offset
            parent = self.box.parentWidget()
            self.box.move(max(0, min(point.x(), parent.rect().width()-self.box.width())),
                          max(0, min(point.y(), parent.rect().height()-self.box.height())))

    def mouseReleaseEvent(self, event):
        self.offset = None
        self.box.moving = False
        self.box.parentWidget().update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor('#55479c'))
        p.setPen(QColor('#f2efff'))
        font = p.font()
        font.setPixelSize(11)
        p.setFont(font)
        p.drawText(self.rect().adjusted(7, 0, -4, 0), Qt.AlignmentFlag.AlignVCenter, 'Move text')


class ResizeHandle(QWidget):
    def __init__(self, box):
        super().__init__(box)
        self.box = box
        self.anchor = None
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.anchor = event.globalPosition().toPoint()
            self.initial_size = self.box.size()

    def mouseMoveEvent(self, event):
        if self.anchor is not None:
            delta = event.globalPosition().toPoint() - self.anchor
            parent = self.box.parentWidget()
            self.box.resize(min(parent.rect().width()-self.box.x(), max(self.box.minimumWidth(), self.initial_size.width()+delta.x())),
                            min(parent.rect().height()-self.box.y(), max(self.box.minimumHeight(), self.initial_size.height()+delta.y())))

    def mouseReleaseEvent(self, event):
        self.anchor = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor('#7965dc'))
        p.setPen(QPen(QColor('white'), 1))
        p.drawLine(5, 12, 12, 5)
        p.drawLine(9, 12, 12, 9)


class TextBox(QWidget):
    accepted = Signal()
    cancelled = Signal()

    def __init__(self, parent, rect, color, pixels):
        super().__init__(parent)
        self.moving = False
        self.color = QColor(color)
        self.pixels = pixels
        self.setMinimumSize(min(120, parent.rect().width()), min(85, parent.rect().height()))
        self.setGeometry(rect)
        self.handle = MoveHandle(self)
        self.input = TextInput(self)
        self.input.setAcceptRichText(False)
        self.input.setFrameStyle(0)
        self.input.setPlaceholderText('Type here…')
        self.input.viewport().setAutoFillBackground(False)
        self.input.setAutoFillBackground(False)
        font = QFont(parent.font())
        font.setPixelSize(pixels)
        self.input.setFont(font)
        self.input.document().setDocumentMargin(4)
        self.set_text_style(color, pixels)
        self.input.textChanged.connect(parent.update)
        self.input.accepted.connect(self.accepted)
        self.input.cancelled.connect(self.cancelled)
        self.grip = ResizeHandle(self)
        self.grip.setToolTip('Drag to resize text box')
        self.grip.setStyleSheet('background: #7965dc; border-radius: 3px;')
        self.setToolTip('Enter: apply · Shift+Enter: new line · Esc: cancel')
        self.show()
        self.layout_children()
        self.input.setFocus()

    def set_text_style(self, color, pixels, family=None):
        self.color = QColor(color)
        self.pixels = pixels
        font = QFont(family or self.input.font().family())
        font.setPixelSize(pixels)
        # An explicit local rule prevents the application theme from forcing 13px.
        self.input.setStyleSheet('QTextEdit { background: transparent; color: '+self.color.name()+
            '; font-size: '+str(pixels)+'px; border: none; padding: 0; selection-background-color: #6254bd; }')
        self.input.setFont(font)
        self.input.document().setDefaultFont(font)
        from PySide6.QtGui import QTextCursor, QTextCharFormat
        selection = self.input.textCursor()
        cursor = QTextCursor(self.input.document())
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        fmt.setFont(font)
        fmt.setForeground(self.color)
        cursor.mergeCharFormat(fmt)
        self.input.setTextCursor(selection)
        self.input.setCurrentCharFormat(fmt)

    def layout_children(self):
        self.handle.setGeometry(1, 1, self.width()-2, 22)
        self.input.setGeometry(4, 25, max(1, self.width()-8), max(1, self.height()-32))
        self.grip.setGeometry(self.width()-17, self.height()-17, 16, 16)
        self.grip.raise_()
        self.parentWidget().update()

    def alignment_point(self):
        from PySide6.QtGui import QTextCursor
        cursor = QTextCursor(self.input.document())
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        caret = self.input.cursorRect(cursor)
        # Align to the first line's text origin and baseline, not the move bar.
        return self.input.viewport().mapTo(self.parentWidget(),
            QPoint(caret.left(), caret.top() + self.input.fontMetrics().ascent()))

    def resizeEvent(self, event):
        parent = self.parentWidget()
        self.setMaximumSize(max(1, parent.rect().width()-self.x()), max(1, parent.rect().height()-self.y()))
        if hasattr(self, 'input'):
            self.layout_children()
        super().resizeEvent(event)

    def moveEvent(self, event):
        parent = self.parentWidget()
        self.setMaximumSize(max(self.minimumWidth(), parent.rect().width()-self.x()),
                            max(self.minimumHeight(), parent.rect().height()-self.y()))
        super().moveEvent(event)
        parent.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(QColor('#b4a4ff'), 1, Qt.PenStyle.DashLine))
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def paint_text(self, painter):
        # Render a fresh document so scroll/caret/selection and handles never export.
        doc = text_document(self.input.toPlainText(), self.pixels, self.color,
                            self.input.viewport().width(), self.input.font().family())
        origin = self.input.viewport().mapTo(self.parentWidget(), QPoint(0, 0))
        painter.save()
        painter.translate(origin)
        doc.drawContents(painter, QRectF(0, 0, self.input.viewport().width(), self.input.viewport().height()))
        painter.restore()

