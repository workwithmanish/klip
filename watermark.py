"""Local-time capture watermark. No network or geolocation lookup."""
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics


def timestamp_label():
    now = datetime.now().astimezone()
    zone = os.environ.get('TZ', '').lstrip(':')
    if not zone:
        try:
            resolved = str(Path('/etc/localtime').resolve())
            if '/zoneinfo/' in resolved:
                zone = resolved.split('/zoneinfo/', 1)[1]
        except OSError:
            pass
    if not zone:
        try:
            zone = Path('/etc/timezone').read_text().strip()
        except OSError:
            pass
    if zone == 'Asia/Calcutta':
        zone = 'Asia/Kolkata'
    offset = now.strftime('%z')
    offset = offset[:3] + ':' + offset[3:]
    return f'[{now:%Y-%m-%d %H:%M:%S} | {now.tzname()} | UTC{offset} | {zone or "Local"}]'


def paint_watermark(painter, bounds, label, size, opacity):
    if bounds.width() < 8 or bounds.height() < 8:
        return
    painter.save()
    font = QFont(painter.font())
    font.setPixelSize(size)
    metrics = QFontMetrics(font)
    margin = min(12, bounds.width()//20, bounds.height()//10)
    available = max(1, bounds.width()-2*margin-12)
    if metrics.horizontalAdvance(label) > available:
        font.setPixelSize(max(1, int(size*available/metrics.horizontalAdvance(label))))
        metrics = QFontMetrics(font)
    painter.setFont(font)
    width = min(bounds.width()-2*margin, metrics.horizontalAdvance(label)+12)
    height = min(bounds.height()-2*margin, metrics.height()+8)
    rect = QRect(bounds.right()-margin-width+1, bounds.bottom()-margin-height+1, width, height)
    painter.setOpacity(opacity/100)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(12, 16, 24, 210))
    painter.drawRoundedRect(rect, 4, 4)
    painter.setPen(QColor('#ffffff'))
    painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)
    painter.restore()
