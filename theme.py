"""Precision Crimson: shared native-widget light theme."""
from pathlib import Path


def stylesheet():
    assets = (Path(__file__).absolute().parent/'assets').as_posix()
    return '''
    QWidget { color: #0b1c30; font-size: 13px; }
    QMainWindow, QWidget#controlPanel, QWidget#ocrWindow { background: #ffffff; }
    QLabel { background: transparent; }
    QToolBar { background: #eff4ff; border: none; border-bottom: 1px solid #e2e8f0; padding: 6px 10px; spacing: 6px; }
    QToolButton { background: transparent; border: 1px solid transparent; padding: 8px; border-radius: 5px; }
    QToolButton:hover { background: #dce9ff; }
    QToolButton:checked { background: #ffe4eb; border-color: #f3a4b7; }
    QPushButton { background: #e5eeff; color: #0b1c30; border: 1px solid transparent; border-radius: 5px; padding: 9px 16px; min-height: 20px; }
    QPushButton:hover { background: #d3e4fe; }
    QPushButton:pressed { background: #c3d7f5; }
    QPushButton:focus { border-color: #e11d48; }
    QPushButton#primary { background: #e11d48; color: white; }
    QPushButton#primary:hover { background: #be123c; }
    QPushButton:disabled { color: #94a3b8; background: #f1f5f9; }
    QLineEdit, QSpinBox, QComboBox, QKeySequenceEdit, QPlainTextEdit { background: #eff4ff; color: #0b1c30; border: 1px solid transparent; border-radius: 5px; padding: 6px 10px; selection-background-color: #ffd2de; selection-color: #881337; }
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QKeySequenceEdit:focus, QPlainTextEdit:focus { border-color: #e11d48; }
    QKeySequenceEdit QLineEdit { border: none; background: transparent; padding: 0; }
    QSpinBox { padding-right: 28px; min-height: 24px; }
    QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 26px; height: 19px; background: transparent; border: none; }
    QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 26px; height: 19px; background: transparent; border: none; }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover { background: #dce9ff; }
    QSpinBox::up-arrow { image: url("ASSETS/light-up.svg"); width: 12px; height: 12px; }
    QSpinBox::down-arrow, QComboBox::down-arrow { image: url("ASSETS/light-down.svg"); width: 12px; height: 12px; }
    QComboBox { padding-right: 30px; min-height: 24px; }
    QComboBox::drop-down { subcontrol-origin: border; subcontrol-position: top right; width: 28px; border: none; background: transparent; }
    QComboBox QAbstractItemView { background: white; color: #0b1c30; selection-background-color: #ffe4eb; border: 1px solid #e2e8f0; padding: 4px; }
    QCheckBox { spacing: 10px; padding: 4px 0; background: transparent; }
    QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #bfcee6; background: #eff4ff; border-radius: 2px; }
    QCheckBox::indicator:checked { image: url("ASSETS/check.svg"); background: #e11d48; border-color: #be123c; }
    QCheckBox:disabled { color: #94a3b8; }
    QListWidget { background: #eff4ff; border: none; padding: 8px; outline: none; }
    QListWidget::item { padding: 0 14px; border-radius: 5px; }
    QListWidget::item:selected { background: #e11d48; color: white; }
    QListWidget::item:hover:!selected { background: #dce9ff; }
    QScrollArea { background: white; border: none; }
    QWidget#card { background: white; border: 1px solid #edf0f6; border-radius: 10px; }
    QWidget#pageFooter { background: #eff4ff; }
    QMenu { background: white; color: #0b1c30; border: 1px solid #dce4f0; padding: 6px; }
    QMenu::item { padding: 8px 20px; border-radius: 4px; }
    QMenu::item:selected { background: #ffe4eb; color: #be123c; }
    QStatusBar { background: #eff4ff; color: #526078; padding: 4px 10px; }
    QToolTip { background: #0b1c30; color: white; padding: 6px; border: none; }
    QScrollBar:vertical { background: #f8f9ff; width: 10px; }
    QScrollBar::handle:vertical { background: #c7d5ea; border-radius: 5px; min-height: 24px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    '''.replace('ASSETS',assets)
