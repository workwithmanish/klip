# Klip

**Capture. Mark. Share.** An independent screenshot and annotation app for Linux
X11 desktops, built with Python and PySide6. **Early development: 0.1.0.**

## Features

- System tray and terminal-free application menu launcher
- Resizable capture selection with attached Capture/Cancel buttons
- Alignment guides, coordinates, pixel magnifier and HEX color inspector
- Pen, line, arrow, rectangle, ellipse, highlight, inline text and pixelation
- Select/move/resize shapes; configurable color, thickness, opacity and fill
- Transparent movable/resizable text box; Enter applies, Shift+Enter adds a line
- Undo/redo, PNG/JPEG export and clipboard copy
- Optional timestamp watermark with system timezone, adjustable size and opacity
- Settings, login startup, editor shortcuts and XFCE global shortcut registration

## Compatibility

| Environment | Status |
| --- | --- |
| Kali Rolling, XFCE/X11, x86_64, VirtualBox | Manually tested during development |
| Debian 13+, X11 | Package dependency target; desktop testing pending |
| Other Debian/Ubuntu-derived systems | Need PySide6 6.8+ distro packages; unverified |
| Wayland | Capture unsupported |
| Multiple monitors | Selection within one monitor; cannot span monitors |

## Debian package

Build a development package from the project directory:

```sh
python3 packaging/build_deb.py
sudo apt install ./dist/klip_0.1.0_all.deb
```

Search **Klip** in the application menu. It starts in the tray without a
terminal. Files install to `/usr/share/klip` and `/usr/bin/klip`; no shared folder
or virtual environment is needed at runtime. APT obtains Python/Qt dependencies
from your distro repositories. If dependencies cannot be resolved, the package
is not supported on that system yet. Do not mix distribution repositories.

The package uses `Architecture: all` because it contains Python source and SVGs;
native Qt dependencies must be available for your machine. It is not a bundled
standalone executable. Builds are experimental until Linux install testing passes.

If migrating from the development launcher, quit Klip and remove the old menu
entry (it overrides the packaged entry):

```sh
~/.venvs/klip/bin/python ~/klip/install_desktop.py --remove
```

Disable old login startup and remove Klip's old global shortcut in its settings
before switching, then re-enable them from the installed version to update paths.
Uninstall with `sudo apt remove klip`. Per-user settings/integrations are retained;
disable startup and clear/apply the shortcut before uninstalling to remove those.

## Run from source

```sh
git clone https://github.com/workwithmanish/klip.git
cd klip
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python klip.py --settings
```

On Kali/X11, system packages `python3-venv`, `libxcb-cursor0` and
`libxkbcommon-x11-0` may be needed. Run as the graphical desktop user, without sudo.
Optional development menu launcher: `.venv/bin/python install_desktop.py`.
Keep its interpreter and project paths in place, or reinstall the launcher.

## Usage

- Drag a capture area; move inside or resize using handles. Capture/Enter/double-click
  confirms; Esc cancels. Guides/inspector hide after selecting the area.
- Hover toolbar icons for tool names. Controls appear only when relevant.
- Select (**V**) reselects editable shapes. Drag to move/resize; Delete removes.
- Text (**T**): drag a box, type, move via header, resize via corner. Enter applies,
  Shift+Enter adds a line, Esc cancels. Movement guides follow the text baseline.
- **Ctrl+S** save, **Ctrl+C** copy, **Ctrl+Z** undo, **Ctrl+Shift+Z** redo.
- **Timestamp** enables a bottom-right watermark with size/opacity controls. It uses
  system timezone and capture time, without GPS or location services.
- Closing windows leaves Klip in the tray; tray → Quit exits.

CLI: `klip --capture`, `klip --settings`, `klip --background`, `klip --open image.png`.
For source use, replace `klip` with your Python interpreter and `klip.py` path.
XFCE global capture shortcuts can be applied in Settings → Shortcuts; conflicts
are refused. Other desktops require manual binding of `klip --capture`.

## Limits and privacy

Applied text, pen strokes and pixelation are raster edits and cannot be reselected.
Editable shapes render above raster edits. Exports flatten all content; reopening
them does not restore objects. Pixelation is not guaranteed sensitive-data redaction.
Captures remain in memory until saved/copied. No application network requests are
made; clipboard managers may retain copied captures. No OCR or true blur yet.
The timestamp shrinks automatically on narrow images.

## Development

Python 3.10+ and PySide6 6.8+. Run `python -m unittest discover -s tests`.
The package builder uses Python's standard library and needs no root or downloads.
CI installs the `.deb` in Debian 13 and runs offscreen tests. These checks do not
replace real X11/tray/shortcut/startup testing. CI artifacts are development builds,
not automatic public releases. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License and support

Original code/artwork: [MIT](LICENSE). Qt/PySide6 have separate licenses; see
[THIRD_PARTY.md](THIRD_PARTY.md). Report bugs at
[GitHub Issues](https://github.com/workwithmanish/klip/issues).
