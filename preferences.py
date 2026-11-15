"""User preferences and explicit desktop integration for Klip."""
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from ui_spacing import polish_inputs
from theme import stylesheet
from icons import tool_icon

from PySide6.QtCore import QSettings, QStandardPaths, QSize, Qt
from PySide6.QtGui import QColor, QKeySequence, QIcon, QPixmap, QPainter, QPen
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QStackedWidget, QLabel, QFormLayout, QLineEdit, QPushButton, QComboBox,
    QCheckBox, QSpinBox, QKeySequenceEdit, QScrollArea, QMessageBox,
    QFileDialog, QColorDialog)

TOOLS = ('Pen', 'Line', 'Arrow', 'Rectangle', 'Ellipse', 'Highlight', 'Text', 'Pixelate')
KEYS = dict(zip(TOOLS, ('P', 'L', 'A', 'R', 'E', 'H', 'T', 'M')))
KEYS.update(Undo='Ctrl+Z', Redo='Ctrl+Shift+Z', Copy='Ctrl+C', Save='Ctrl+S', Close='Esc')
KEYS['Select'] = 'V'


class Preferences:
    def __init__(self):
        self.store = QSettings('Klip', 'Klip')

    def get(self, key, default=None):
        defaults = {'folder': QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation) or str(Path.home()),
                    'format': 'png', 'sound': False, 'guides': True, 'color': '#ff526b', 'width': 4}
        value = self.store.value(key, defaults.get(key, default))
        if key in ('sound', 'guides'):
            return str(value).lower() in ('true', '1')
        if key == 'width':
            return max(1, min(30, int(value)))
        return value

    def shortcut(self, name):
        return self.get('keys/' + name, KEYS[name])

    def set(self, key, value):
        self.store.setValue(key, value)


def launch_command():
    return shlex.join([sys.executable, str(Path(__file__).absolute().with_name('klip.py')), '--capture'])


def autostart_path():
    return Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home()/'.config'))) / 'autostart' / 'klip.desktop'


def set_autostart(enabled):
    path = autostart_path()
    if enabled:
        def quote(value):
            value = value.replace('%', '%%')
            for char in ('\\', '"', '`', '$'):
                value = value.replace(char, '\\' + char)
            return '"' + value + '"'
        command = ' '.join(quote(v) for v in (sys.executable, str(Path(__file__).absolute().with_name('klip.py')), '--background'))
        # Desktop-entry strings require another escaping pass for backslashes.
        command = command.replace('\\', '\\\\')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('[Desktop Entry]\nType=Application\nName=Klip\nComment=Screenshot and annotation tool\nExec=' + command + '\nTerminal=false\n', encoding='utf-8')
    elif path.exists():
        path.unlink()


def xfce_key(sequence):
    if ',' in sequence:
        raise ValueError('Use a single key combination for capture.')
    parts = sequence.split('+')
    key = parts[-1]
    modifiers = {'Ctrl': '<Primary>', 'Alt': '<Alt>', 'Shift': '<Shift>', 'Meta': '<Super>'}
    if any(part not in modifiers for part in parts[:-1]):
        raise ValueError('Unsupported modifier combination.')
    if not re.fullmatch(r'[A-Za-z0-9]|F(?:[1-9]|[12][0-9]|3[0-5])|Print', key):
        raise ValueError('Use a letter, number, F-key, or Print Screen with modifiers.')
    if len(key) == 1 and len(parts) == 1:
        raise ValueError('Add Ctrl, Alt, or Super to a letter or number.')
    return ''.join(modifiers[p] for p in ('Ctrl', 'Alt', 'Shift', 'Meta') if p in parts[:-1]) + (key.lower() if len(key) == 1 else key)


def normalize_binding(value):
    tokens = re.findall(r'<([^>]+)>', value)
    aliases = {'Control': 'Primary', 'Ctrl': 'Primary', 'Mod1': 'Alt', 'Mod4': 'Super'}
    return (tuple(sorted(aliases.get(t, t) for t in tokens)), re.sub(r'<[^>]+>', '', value).lower())


def register_capture(prefs, sequence):
    if sys.platform != 'linux' or 'XFCE' not in os.environ.get('XDG_CURRENT_DESKTOP', '').upper() or not shutil.which('xfconf-query'):
        raise ValueError('Automatic registration currently supports XFCE only. Use the command below in your desktop keyboard settings.')
    def run(*args):
        result = subprocess.run(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', *args], capture_output=True, text=True, timeout=5)
        if result.returncode:
            raise ValueError(result.stderr.strip() or 'XFCE shortcut update failed.')
        return result.stdout.strip()
    old = prefs.get('capture_property', '')
    owned_command = prefs.get('capture_command', '')
    entries = {}
    for line in run('-l', '-v').splitlines():
        pieces = line.split(None, 1)
        if len(pieces) == 2:
            entries[pieces[0]] = pieces[1].strip()
    target = '/commands/custom/' + xfce_key(sequence) if sequence else ''
    if target:
        wanted = normalize_binding(target.rsplit('/', 1)[-1])
        for prop, command in entries.items():
            if normalize_binding(prop.rsplit('/', 1)[-1]) == wanted:
                if prop == old and command == owned_command:
                    continue
                # A custom mapping overrides its default counterpart.
                if '/default/' in prop and prop.replace('/default/', '/custom/') in entries:
                    continue
                raise ValueError('That shortcut is already assigned in XFCE. Choose another combination.')
        command = launch_command()
        if target in entries:
            run('-p', target, '-s', command)
        else:
            run('-p', target, '-n', '-t', 'string', '-s', command)
    if old and old != target and entries.get(old) == owned_command:
        try:
            run('-p', old, '-r')
        except ValueError:
            if target and target not in entries:
                run('-p', target, '-r')
            raise
    prefs.set('capture_property', target)
    prefs.set('capture_command', launch_command() if target else '')
    prefs.set('capture_key', sequence)
    prefs.store.sync()


class ControlPanel(QWidget):
    def __init__(self, prefs, changed, capture):
        super().__init__()
        self.prefs = prefs
        self.changed = changed
        self.setWindowTitle('Klip · Control panel')
        self.setObjectName('controlPanel')
        self.setStyleSheet(stylesheet())
        self.resize(1100, 760)
        self.setMinimumSize(880, 680)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        title = QLabel('<span style="color: #be0037; font-weight: 600;">Klip</span> / Control panel')
        title.setStyleSheet('font-size: 19px; padding: 20px 24px; border-bottom: 1px solid #edf0f6;')
        root.addWidget(title)
        body = QHBoxLayout()
        body.setSpacing(24)
        root.addLayout(body, 1)
        nav = QListWidget()
        nav.addItems(['General', 'Shortcuts', 'About'])
        for index, name in enumerate(('General', 'Shortcuts', 'About')):
            nav.item(index).setIcon(tool_icon(name))
        nav.setIconSize(QSize(18,18))
        nav.setFixedWidth(200)
        nav.setSpacing(6)
        nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for index in range(nav.count()):
            nav.item(index).setSizeHint(QSize(148, max(46, nav.fontMetrics().height()+24)))
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet('background: #eff4ff;')
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0,12,0,0)
        sidebar_layout.setSpacing(4)
        nav_title = QLabel('CONFIGURATION')
        nav_title.setStyleSheet('font-size: 10px; color: #64748b; padding: 6px 16px;')
        sidebar_layout.addWidget(nav_title)
        sidebar_layout.addWidget(nav,1)
        body.addWidget(sidebar)
        stack = QStackedWidget()
        stack.setMaximumWidth(1060)
        stack.setContentsMargins(0, 20, 24, 20)
        body.addWidget(stack, 1)
        nav.currentRowChanged.connect(stack.setCurrentIndex)
        self.general = QWidget()
        self.general.setObjectName('card')
        form = QFormLayout(self.general)
        form.setContentsMargins(24, 24, 24, 24)
        form.setHorizontalSpacing(30)
        form.setVerticalSpacing(20)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        self.folder = QLineEdit(prefs.get('folder'))
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(self.folder)
        browse = QPushButton('Browse…')
        browse.setMinimumWidth(100)
        browse.clicked.connect(self.browse)
        row.addWidget(browse)
        form.addRow('Save folder', row)
        self.format = QComboBox()
        self.format.addItems(['png', 'jpg'])
        self.format.setFixedWidth(150)
        self.format.setCurrentText(prefs.get('format'))
        form.addRow('Image format', self.format)
        self.width = QSpinBox()
        self.width.setRange(1, 30)
        self.width.setFixedWidth(150)
        self.width.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.width.setValue(prefs.get('width'))
        form.addRow('Default drawing size', self.width)
        self.color_value = prefs.get('color')
        self.color = QPushButton(self.color_value)
        self.color.setFixedWidth(150)
        self.update_color_swatch()
        self.color.clicked.connect(self.pick_color)
        form.addRow('Default annotation color', self.color)
        self.sound = QCheckBox('Play a notification beep after capture')
        self.sound.setChecked(prefs.get('sound'))
        form.addRow(self.sound)
        self.guides = QCheckBox('Show alignment guides in capture and editor')
        self.guides.setChecked(prefs.get('guides'))
        form.addRow(self.guides)
        self.startup = QCheckBox('Start Klip when I log in')
        self.startup.setChecked(autostart_path().exists() if sys.platform == 'linux' else False)
        self.startup.setEnabled(sys.platform == 'linux')
        form.addRow(self.startup)
        save = QPushButton('Save general settings')
        save.setFixedWidth(200)
        save.setObjectName('primary')
        save.clicked.connect(self.save_general)
        form.addRow('', save)
        note = QLabel('Changes apply to new captures. Closing this panel keeps Klip in the tray.')
        note.setWordWrap(True)
        note.setStyleSheet('color: #64748b; padding-top: 8px;')
        form.addRow(note)
        stack.addWidget(self.general)
        shortcuts = QWidget()
        shortcuts.setObjectName('card')
        layout = QVBoxLayout(shortcuts)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(12)
        layout.addWidget(QLabel('Global capture shortcut · XFCE integration'))
        self.capture_key = QKeySequenceEdit(QKeySequence(prefs.get('capture_key', '')))
        self.capture_key.setMaximumSequenceLength(1)
        self.capture_key.setClearButtonEnabled(True)
        layout.addWidget(self.capture_key)
        apply_global = QPushButton('Apply capture shortcut')
        apply_global.clicked.connect(self.save_capture)
        layout.addWidget(apply_global)
        hint = QLabel('Click the field and press your keys. Existing XFCE assignments are preserved. Clear the field and apply to remove a shortcut created by Klip.')
        hint.setWordWrap(True)
        layout.addWidget(hint)
        command = QLineEdit(launch_command())
        command.setReadOnly(True)
        from PySide6.QtGui import QFontDatabase
        data_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        command.setFont(data_font)
        self.folder.setFont(data_font)
        self.capture_key.setFont(data_font)
        command.setCursorPosition(0)
        layout.addWidget(QLabel('Capture command for other desktops:'))
        layout.addWidget(command)
        layout.addWidget(QLabel('Editor shortcuts · active inside the editor'))
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        fields = QWidget()
        fields.setObjectName('shortcutFields')
        fields.setStyleSheet('QWidget#shortcutFields { background: white; }')
        key_form = QFormLayout(fields)
        self.keys = {}
        for name in KEYS:
            field = QKeySequenceEdit(QKeySequence(prefs.shortcut(name)))
            field.setMaximumSequenceLength(1)
            field.setFont(data_font)
            field.setClearButtonEnabled(True)
            self.keys[name] = field
            key_form.addRow(name, field)
        scroller.setWidget(fields)
        layout.addWidget(scroller, 1)
        buttons = QHBoxLayout()
        defaults = QPushButton('Restore editor defaults')
        defaults.clicked.connect(self.restore_keys)
        buttons.addWidget(defaults)
        save_keys = QPushButton('Save editor shortcuts')
        save_keys.setObjectName('primary')
        save_keys.clicked.connect(self.save_keys)
        buttons.addWidget(save_keys)
        layout.addLayout(buttons)
        stack.addWidget(shortcuts)
        about = QWidget()
        about.setStyleSheet('background: white;')
        about_layout = QVBoxLayout(about)
        about_layout.setContentsMargins(28, 24, 28, 20)
        about_layout.setSpacing(0)
        about_layout.addStretch(1)

        def label(text, style='', gap=12):
            item = QLabel(text)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setWordWrap(True)
            item.setStyleSheet(style)
            about_layout.addWidget(item)
            about_layout.addSpacing(gap)
            return item

        logo = label('', gap=16)
        logo.setPixmap(QIcon(str(Path(__file__).parent / 'assets' / 'klip.png')).pixmap(80, 80))
        label('Klip', 'font-size: 36px; font-weight: 600; color: #0b1c30;', 8)
        label('Capture. Mark. Share.', 'font-size: 15px; color: #64748b;', 12)
        label('v0.2.1 · Alpha', 'font-size: 11px; color: #be0037;', 24)
        label('Screenshot capture and annotation for Linux.', 'color: #64748b;', 28)
        label('Made by Manish', 'color: #0b1c30;', 6)

        def linked(text, gap=12, muted=False):
            color = '#64748b' if muted else '#be0037'
            item = label(text.replace('<a href=', '<a style="color: '+color+'; text-decoration: none;" href='), '', gap)
            item.setOpenExternalLinks(True)
            return item

        linked('<a href="https://github.com/workwithmanish">@workwithmanish</a>', 28)
        linked('<a href="https://github.com/workwithmanish/klip">GitHub</a> &nbsp;&nbsp; · &nbsp;&nbsp; '
               '<a href="https://github.com/workwithmanish/klip/issues">Report an issue</a> &nbsp;&nbsp; · &nbsp;&nbsp; '
               '<a href="https://github.com/workwithmanish/klip/releases">Releases</a>', 28)
        label('Local capture. Offline OCR.', 'font-size: 12px; color: #64748b;', 0)
        about_layout.addStretch(2)
        linked('© 2026 Manish &nbsp; · &nbsp; '
               '<a href="https://github.com/workwithmanish/klip/blob/main/LICENSE">MIT License</a> &nbsp; · &nbsp; '
               '<a href="https://github.com/workwithmanish/klip/blob/main/THIRD_PARTY.md">Third-party notices</a>', 0, True)
        about_scroll = QScrollArea()
        about_scroll.setWidgetResizable(True)
        about_scroll.setStyleSheet('QScrollArea { border: none; background: white; }')
        about_scroll.setWidget(about)
        stack.addWidget(about_scroll)
        nav.setCurrentRow(0)
        footer_widget = QWidget()
        footer_widget.setObjectName('pageFooter')
        footer = QHBoxLayout(footer_widget)
        footer.setContentsMargins(20,12,20,12)
        footer.setSpacing(12)
        self.status = QLabel('Ready')
        self.status.setWordWrap(True)
        footer.addWidget(self.status, 1)
        capture_button = QPushButton('Capture area')
        capture_button.setObjectName('primary')
        capture_button.clicked.connect(lambda: (self.hide(), delayed_capture(capture)))
        
        close = QPushButton('Close')
        close.clicked.connect(self.close)
        footer.addWidget(close)
        footer.addWidget(capture_button)
        root.addWidget(footer_widget)
        polish_inputs(self)

    def browse(self):
        folder = QFileDialog.getExistingDirectory(self, 'Save folder', self.folder.text())
        if folder:
            self.folder.setText(folder)

    def pick_color(self):
        color = QColorDialog.getColor(QColor(self.color_value), self)
        if color.isValid():
            self.color_value = color.name()
            self.color.setText(color.name())
            self.update_color_swatch()

    def update_color_swatch(self):
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor('#e5eaff'), 1))
        painter.setBrush(QColor(self.color_value))
        painter.drawRoundedRect(1, 1, 18, 18, 4, 4)
        painter.end()
        self.color.setIcon(QIcon(pixmap))
        self.color.setIconSize(QSize(20, 20))

    def save_general(self):
        try:
            folder = Path(self.folder.text()).expanduser()
            if not folder.is_absolute() or not folder.is_dir() or not os.access(folder, os.W_OK):
                raise ValueError('Choose an existing writable absolute save folder.')
            if sys.platform == 'linux':
                set_autostart(self.startup.isChecked())
            for key, value in {'folder': str(folder), 'format': self.format.currentText(), 'width': self.width.value(), 'color': self.color_value, 'sound': self.sound.isChecked(), 'guides': self.guides.isChecked()}.items():
                self.prefs.set(key, value)
            self.prefs.store.sync()
            if self.prefs.store.status() != QSettings.Status.NoError:
                raise ValueError('Could not save preferences to disk.')
            self.status.setText('General settings saved. New captures use these defaults.')
            self.changed()
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, 'Settings not saved', str(error))

    def save_capture(self):
        try:
            sequence = self.capture_key.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
            register_capture(self.prefs, sequence)
            self.status.setText('Capture shortcut applied.' if sequence else 'Klip capture shortcut removed.')
            self.changed()
        except (ValueError, OSError, subprocess.TimeoutExpired) as error:
            QMessageBox.warning(self, 'Shortcut not applied', str(error))

    def restore_keys(self):
        for name, field in self.keys.items():
            field.setKeySequence(QKeySequence(KEYS[name]))
        self.status.setText('Defaults loaded. Click Save editor shortcuts to apply.')

    def save_keys(self):
        values = {name: field.keySequence().toString(QKeySequence.SequenceFormat.PortableText) for name, field in self.keys.items()}
        nonempty = [v for v in values.values() if v]
        if len(set(nonempty)) != len(nonempty):
            QMessageBox.warning(self, 'Duplicate shortcut', 'Each editor action needs a different shortcut.')
            return
        for name, value in values.items():
            self.prefs.set('keys/' + name, value)
        self.prefs.store.sync()
        self.changed()
        self.status.setText('Editor shortcuts saved and applied to open editors.')


def delayed_capture(callback):
    from PySide6.QtCore import QTimer
    QTimer.singleShot(250, callback)
