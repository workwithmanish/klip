"""Render the supplied logo to the standard desktop icon size at build time."""
import sys
from PySide6.QtGui import QImage
from PySide6.QtCore import Qt
image = QImage(sys.argv[1])
if image.isNull() or not image.scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation).save(sys.argv[2]):
    raise SystemExit('Could not export launcher icon')
