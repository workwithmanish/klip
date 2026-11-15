"""Original scalable tool icons, drawn locally with Qt."""
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QPen, QColor, QPolygonF


def tool_icon(name):
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(2, 2)
    p.setPen(QPen(QColor('#334155'), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    if name == 'General':
        for y, x in ((8,11),(16,22),(24,15)):
            p.drawLine(5,y,27,y)
            p.setBrush(QColor('#eff4ff'))
            p.drawEllipse(x-3,y-3,6,6)
    elif name == 'Shortcuts':
        p.drawRoundedRect(3,7,26,19,2,2)
        for y in (12,17):
            for x in (8,13,18,23):
                p.drawPoint(x,y)
        p.drawLine(10,22,22,22)
    elif name == 'About':
        p.drawEllipse(4,4,24,24)
        p.drawPoint(16,10)
        p.drawLine(16,15,16,23)
    elif name == 'Select':
        p.drawPolygon(QPolygonF([QPointF(7,4), QPointF(25,17), QPointF(17,18), QPointF(13,27)]))
    elif name in ('Pen', 'Highlight'):
        p.drawPolygon(QPolygonF([QPointF(8, 20), QPointF(21, 7), QPointF(26, 12), QPointF(13, 25), QPointF(6, 27)]))
        p.drawLine(18, 10, 23, 15)
        if name == 'Highlight':
            p.setPen(QPen(QColor('#f5d95e'), 4))
            p.drawLine(7, 29, 26, 29)
    elif name in ('Line', 'Arrow'):
        p.drawLine(6, 26, 26, 6)
        if name == 'Arrow':
            p.drawLine(14, 6, 26, 6)
            p.drawLine(26, 6, 26, 18)
    elif name == 'Rectangle':
        p.drawRoundedRect(5, 8, 22, 17, 1, 1)
    elif name == 'Ellipse':
        p.drawEllipse(5, 7, 22, 19)
    elif name == 'Text':
        p.drawLine(6, 7, 26, 7)
        p.drawLine(16, 7, 16, 26)
        p.drawLine(11, 26, 21, 26)
    elif name == 'Pixelate':
        for y in range(3):
            for x in range(3):
                p.fillRect(5+x*8, 5+y*8, 6, 6, QColor(['#334155', '#8e9bbd', '#5b6888'][(x+y)%3]))
    elif name == 'Color':
        for x, color in enumerate(('#ff526b', '#f5d95e', '#6de0ad', '#82aaff')):
            p.fillRect(5+x*6, 6, 6, 20, QColor(color))
    elif name in ('Undo', 'Redo'):
        if name == 'Redo':
            p.translate(32, 0)
            p.scale(-1, 1)
        # A broad return arrow with a distinct left-pointing chevron.
        path = QPainterPath(QPointF(6, 12))
        path.lineTo(18, 12)
        path.cubicTo(24, 12, 27, 16, 27, 21)
        path.cubicTo(27, 25, 23, 27, 19, 27)
        p.drawPath(path)
        p.drawLine(6, 12, 12, 6)
        p.drawLine(6, 12, 12, 18)
    elif name == 'Copy':
        p.drawRoundedRect(11, 10, 16, 18, 2, 2)
        p.drawLine(21, 5, 5, 5)
        p.drawLine(5, 5, 5, 22)
    elif name == 'Save':
        p.drawRoundedRect(5, 5, 22, 23, 2, 2)
        p.drawRect(10, 5, 11, 8)
        p.drawRect(10, 19, 12, 9)
    p.end()
    return QIcon(pix)
