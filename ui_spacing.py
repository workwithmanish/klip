"""Consistent inner spacing across native Qt input controls."""
from PySide6.QtWidgets import QAbstractSpinBox, QLineEdit


def polish_inputs(widget):
    for field in widget.findChildren(QLineEdit):
        field.setTextMargins(8, 2, 8, 2)
    for field in widget.findChildren(QAbstractSpinBox):
        field.setMinimumHeight(38)
        field.lineEdit().setTextMargins(9, 2, 6, 2)
