"""Shared selection geometry for capture bounds and annotation objects."""
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QPen

def handles(rect):
    x, y = rect.center().x(), rect.center().y()
    return [rect.topLeft(), QPoint(x, rect.top()), rect.topRight(),
            QPoint(rect.right(), y), rect.bottomRight(), QPoint(x, rect.bottom()),
            rect.bottomLeft(), QPoint(rect.left(), y)]

def hit_handle(rect, point):
    for index, handle in enumerate(handles(rect)):
        if QRect(handle-QPoint(7, 7), handle+QPoint(7, 7)).contains(point):
            return index
    return -1

def paint_handles(painter, rect):
    painter.save()
    painter.setPen(QPen(QColor('#86b9ff'), 1, Qt.PenStyle.DashLine))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(rect)
    painter.setPen(QPen(QColor('#34405c'), 1))
    painter.setBrush(QColor('#ffffff'))
    for point in handles(rect):
        painter.drawRect(QRect(point-QPoint(3, 3), point+QPoint(3, 3)))
    painter.restore()

def transform_rect(original, anchor, point, handle, bounds):
    if handle == -1:
        result = original.translated(point-anchor)
        result.moveLeft(max(bounds.left(), min(result.left(), bounds.right()-result.width()+1)))
        result.moveTop(max(bounds.top(), min(result.top(), bounds.bottom()-result.height()+1)))
        return result
    result = QRect(original)
    point = QPoint(max(bounds.left(), min(point.x(), bounds.right())), max(bounds.top(), min(point.y(), bounds.bottom())))
    if handle in (0, 6, 7): result.setLeft(min(point.x(), result.right()-8))
    if handle in (2, 3, 4): result.setRight(max(point.x(), result.left()+8))
    if handle in (0, 1, 2): result.setTop(min(point.y(), result.bottom()-8))
    if handle in (4, 5, 6): result.setBottom(max(point.y(), result.top()+8))
    return result.intersected(bounds)

def cursor_for(handle):
    return [Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor,
            Qt.CursorShape.SizeBDiagCursor, Qt.CursorShape.SizeHorCursor,
            Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor,
            Qt.CursorShape.SizeBDiagCursor, Qt.CursorShape.SizeHorCursor][handle] if handle >= 0 else Qt.CursorShape.SizeAllCursor
