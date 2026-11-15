"""User preferences and explicit desktop integration for Klip."""
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from ui_spacing import polish_inputs

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
        self.setStyleSheet('''
            ControlPanel { background: #171b27; color: #eef0ff; }
            QLabel, QCheckBox { color: #eef0ff; }
            QListWidget { background: #202638; color: #bfc9e0; border: 0; border-radius: 8px; padding: 6px; }
            QListWidget::item { padding: 0px 12px; border: 0; }
            QListWidget::item:selected { background: #6254bd; color: white; border-radius: 6px; }
            QListWidget::item:focus { outline: none; }
            QLineEdit, QSpinBox, QComboBox, QKeySequenceEdit { background: #262d40; color: #eef0ff; border: 1px solid #46516d; border-radius: 4px; padding: 5px; }
            QPushButton { background: #34405c; color: #eef0ff; border: 1px solid #526385; padding: 8px 12px; border-radius: 5px; }
            QPushButton:hover { background: #514797; }
            QPushButton:disabled, QCheckBox:disabled { color: #778298; }
            QScrollArea { border: 1px solid #46516d; background: #171b27; }
            QCheckBox { spacing: 10px; padding: 4px 0; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #7181a1; border-radius: 4px; background: #262d40; }
            QCheckBox::indicator:checked { background: #8e7aff; border: 2px solid #c3b9ff; }
        ''')
        assets = Path(__file__).absolute().parent / 'assets'
        down = (assets / 'chevron-down.svg').as_posix()
        up = (assets / 'chevron-up.svg').as_posix()
        check = (assets / 'check.svg').as_posix()
        self.setStyleSheet(self.styleSheet() + '''
            QLineEdit, QSpinBox, QComboBox { min-height: 24px; padding: 6px 10px; selection-background-color: #6254bd; }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid #a394ff; }
            QPushButton { min-height: 22px; }
            QPushButton:focus { border: 1px solid #b6aaff; }
            QComboBox { padding-right: 38px; }
            QComboBox::drop-down { subcontrol-origin: border; subcontrol-position: top right; width: 32px; border-left: 1px solid #46516d; border-top-right-radius: 4px; border-bottom-right-radius: 4px; background: #34405c; }
            QComboBox::down-arrow { image: url("DOWN"); width: 16px; height: 16px; }
            QComboBox QAbstractItemView { background: #262d40; color: #eef0ff; selection-background-color: #6254bd; padding: 4px; border: 1px solid #526385; }
            QSpinBox { padding-right: 36px; }
            QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 30px; height: 19px; border-left: 1px solid #46516d; border-bottom: 1px solid #46516d; background: #34405c; }
            QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 30px; height: 19px; border-left: 1px solid #46516d; background: #34405c; }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover, QComboBox::drop-down:hover { background: #514797; }
            QSpinBox::up-arrow { image: url("UP"); width: 14px; height: 14px; }
            QSpinBox::down-arrow { image: url("DOWN"); width: 14px; height: 14px; }
            QCheckBox::indicator:checked { image: url("CHECK"); background: #7965dc; border: 1px solid #b4a6ff; }
        '''.replace('DOWN', down).replace('UP', up).replace('CHECK', check))
        self.resize(980, 740)
        self.setMinimumSize(880, 680)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 18, 24, 18)
        root.setSpacing(18)
        title = QLabel('Klip  /  Control panel')
        title.setStyleSheet('font-size: 24px; font-weight: 600; padding: 12px;')
        root.addWidget(title)
        body = QHBoxLayout()
        body.setSpacing(24)
        root.addLayout(body, 1)
        nav = QListWidget()
        nav.addItems(['General', 'Shortcuts', 'About'])
        nav.setFixedWidth(172)
        nav.setSpacing(6)
        nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for index in range(nav.count()):
            nav.item(index).setSizeHint(QSize(148, max(46, nav.fontMetrics().height()+24)))
        body.addWidget(nav)
        stack = QStackedWidget()
        stack.setMaximumWidth(980)
        body.addWidget(stack, 1)
        nav.currentRowChanged.connect(stack.setCurrentIndex)
        self.general = QWidget()
        form = QFormLayout(self.general)
        form.setContentsMargins(12, 12, 12, 12)
        form.setHorizontalSpacing(24)
        form.setVerticalSpacing(18)
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
        save.clicked.connect(self.save_general)
        form.addRow('', save)
        note = QLabel('Changes apply to new captures. Closing this panel keeps Klip in the tray.')
        note.setWordWrap(True)
        note.setStyleSheet('color: #a9b6d0; padding-top: 8px;')
        form.addRow(note)
        stack.addWidget(self.general)
        shortcuts = QWidget()
        layout = QVBoxLayout(shortcuts)
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
        command.setCursorPosition(0)
        layout.addWidget(QLabel('Capture command for other desktops:'))
        layout.addWidget(command)
        layout.addWidget(QLabel('Editor shortcuts · active inside the editor'))
        scroller = QScrollArea()
        scroller.setWidgetResizable(True)
        fields = QWidget()
        fields.setStyleSheet('background: #171b27;')
        key_form = QFormLayout(fields)
        self.keys = {}
        for name in KEYS:
            field = QKeySequenceEdit(QKeySequence(prefs.shortcut(name)))
            field.setMaximumSequenceLength(1)
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
        save_keys.clicked.connect(self.save_keys)
        buttons.addWidget(save_keys)
        layout.addLayout(buttons)
        stack.addWidget(shortcuts)
        about = QWidget()
        about_layout = QVBoxLayout(about)
        about_layout.setContentsMargins(16, 16, 16, 16)
        about_layout.setSpacing(16)
        heading = QLabel('Klip')
        heading.setStyleSheet('font-size: 32px; font-weight: 700; color: #c4b6ff;')
        about_layout.addWidget(heading)
        tagline = QLabel('Capture. Mark. Share.  ·  Version 0.2.0 / Early development')
        tagline.setWordWrap(True)
        tagline.setStyleSheet('color: #b4c0da; padding-bottom: 8px;')
        about_layout.addWidget(tagline)
        description = QLabel('An independent Linux screenshot and annotation app. Capture an area, add drawings or text, and save or copy your image.')
        description.setWordWrap(True)
        about_layout.addWidget(description)
        details = QLabel('Created by <b>Manish</b> · <b>@workwithmanish</b><br><br>'
            'Tested desktop: Kali Linux · XFCE · X11<br>'
            'Debian 13: automated package checks passed; desktop testing pending.<br>'
            'Wayland capture is not supported yet.')
        details.setWordWrap(True)
        details.setStyleSheet('background: #222a3c; padding: 16px; border-radius: 8px;')
        about_layout.addWidget(details)
        links = QLabel(
            '<a href="https://github.com/workwithmanish">Developer profile</a> &nbsp;·&nbsp; '
            '<a href="https://github.com/workwithmanish/klip">Source code &amp; installation</a><br><br>'
            '<a href="https://github.com/workwithmanish/klip/issues">Report a bug / suggest a feature</a> &nbsp;·&nbsp; '
            '<a href="https://github.com/workwithmanish/klip/releases">Releases</a><br><br>'
            '<a href="https://github.com/workwithmanish/klip/blob/main/LICENSE">MIT license</a> &nbsp;·&nbsp; '
            '<a href="https://github.com/workwithmanish/klip/blob/main/THIRD_PARTY.md">Qt / PySide6 notices</a>')
        links.setOpenExternalLinks(True)
        links.setWordWrap(True)
        links.setStyleSheet('padding: 8px 0;')
        # Explicit link colors remain readable with both light and dark system palettes.
        links.setText(links.text().replace('<a href=', '<a style="color: #baaaff;" href='))
        about_layout.addWidget(links)
        privacy = QLabel('Your captures stay local. Klip makes no network requests while capturing or editing. Clicking a link above opens your browser.\n\n© 2026 Manish and Klip contributors · Original code and artwork under MIT.')
        privacy.setWordWrap(True)
        privacy.setStyleSheet('color: #a9b6d0; padding-top: 8px;')
        about_layout.addWidget(privacy)
        about_layout.addStretch(1)
        about_scroll = QScrollArea()
        about_scroll.setWidgetResizable(True)
        about_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        about.setStyleSheet('background: #171b27;')
        about_scroll.setWidget(about)
        stack.addWidget(about_scroll)
        nav.setCurrentRow(0)
        footer = QHBoxLayout()
        self.status = QLabel('Ready')
        self.status.setWordWrap(True)
        footer.addWidget(self.status, 1)
        capture_button = QPushButton('Capture area')
        capture_button.clicked.connect(lambda: (self.hide(), delayed_capture(capture)))
        footer.addWidget(capture_button)
        close = QPushButton('Close')
        close.clicked.connect(self.close)
        footer.addWidget(close)
        root.addLayout(footer)
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
