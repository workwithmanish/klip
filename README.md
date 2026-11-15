# Klip

**Take a screenshot, draw on it, add text, and save or copy it.**
Klip runs in the tray near your desktop clock. This project is in early development.

## Linux, Debian, Ubuntu, Kali… what is the difference?

Windows and macOS are operating systems. **Linux** is a kernel—the core of an
operating system. Complete operating systems built around it are called
**Linux distributions**, or **distros**. There are hundreds; you do not need to
learn them all to use Klip.

| Name | Simple explanation |
| --- | --- |
| Debian | A Linux distribution; the base for many others. |
| Ubuntu | A Linux distribution based on Debian. |
| Linux Mint | Usually based on Ubuntu; a Debian-based edition also exists. |
| Kali Linux | Based on Debian, with a focus on security tools. |
| Fedora, Arch, openSUSE | Other Linux distribution families. |
| XFCE, GNOME, KDE Plasma | Desktop interfaces, not separate operating systems. |
| X11 / Wayland | Systems used by the desktop to display windows and handle input. |

Being based on Debian **does not automatically mean every Debian app works**
on Ubuntu, Mint, or Kali. Versions and available dependencies also matter.

## Who is Klip for right now?

| Your system | Current Klip status |
| --- | --- |
| **Kali Linux + XFCE + X11** | Main tested desktop environment. |
| **Debian 13 + X11** | Package install and automated editor checks pass; real desktop testing is pending. |
| Ubuntu, Mint, other Linux distributions | Not verified yet. No general support claim. |
| Linux desktop using Wayland | Screen capture is not supported yet. |
| Windows / macOS | Not supported. |

Check your display session in a terminal:

```bash
echo "$XDG_SESSION_TYPE"
```

**`x11`** → continue. **`wayland`** → this version cannot capture your screen.
If your login screen offers an X11 session, you can choose it before logging in.

## Install Klip: choose ONE method

These instructions target **Kali/XFCE/X11 and Debian 13/X11**. Internet access
is needed to install dependencies. Use your normal desktop account; do not
launch Klip with `sudo`.

| Method | Best for | Available now? |
| --- | --- | --- |
| **A. Source installation** | Trying Klip today and getting updates | Yes |
| **B. Local `.deb` package** | Installing an independent system application | Yes, build it first |
| Download a ready-made `.deb` | Easiest future installation | **Not yet—Releases is empty** |

Do not combine A and B. If you already installed a development/shared-folder
version, read [migration instructions](docs/DEVELOPMENT.md#migrate-from-the-shared-folder-development-setup)
before switching to B.

### A. Install from source

Open a terminal and run each line in order. If a command fails, stop and copy
the error. This first-time setup expects that `~/klip` does not already exist.

```bash
sudo apt update
sudo apt install -y git python3-venv libxcb-cursor0 libxkbcommon-x11-0
git clone https://github.com/workwithmanish/klip.git "$HOME/klip"
cd "$HOME/klip"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python install_desktop.py
```

Now open your application menu, search **Klip**, and click it. Look for its
purple icon near the clock. You can close the terminal.

**Keep `~/klip` and its `.venv` folder:** this method uses them to run.

Update later: quit Klip from its tray menu, then run:

```bash
cd "$HOME/klip"
git pull --ff-only
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python install_desktop.py
```

Open Klip from the menu again. If you changed the source yourself, review
`git status` before updating rather than discarding your changes.

### B. Build and install a `.deb`

A **`.deb` is an installation package** used by Debian and related systems.
This method installs Klip as a system application; it does not need a source
folder or a Python virtual environment afterward.

There is no download in Releases yet. Build the development package locally:

```bash
sudo apt update
sudo apt install -y git python3
git clone https://github.com/workwithmanish/klip.git "$HOME/klip-build"
cd "$HOME/klip-build"
python3 packaging/build_deb.py
sudo apt install ./dist/klip_0.2.0_all.deb
```

Use a different unused folder name if `~/klip-build` already exists. APT installs
the required Qt/Python packages. If dependencies are unavailable, stop—do not
add another distribution's repositories to force installation.

Search **Klip** in your application menu and open it. After installation, the
`klip-build` folder is not needed to run the app. This package is experimental;
real desktop testing outside Kali is still pending.

For a later update, quit Klip and repeat the build/install from your build checkout:

```bash
cd "$HOME/klip-build"
git pull --ff-only
python3 packaging/build_deb.py
sudo apt install ./dist/klip_0.2.0_all.deb
```

The version/filename will change for future releases; use the name printed by
the build command.

## Use Klip: menu, shortcut, or terminal

| How | What to do |
| --- | --- |
| **Application menu** | Search Klip, open it, then use its tray icon → Capture area. |
| **Keyboard shortcut** | In Klip Settings → Shortcuts, record keys and click Apply capture shortcut. Automatic setup supports XFCE. |
| **Terminal** | Use the command below for your installation method. Useful for seeing errors. |

**Source installation (A):**

```bash
"$HOME/klip/.venv/bin/python" "$HOME/klip/klip.py" --capture
```

**Installed `.deb` (B):**

```bash
klip --capture
```

Replace `--capture` with `--settings` to open the control panel. Once started
from the menu, Klip does not need an open terminal. Enable **Settings → General →
Start Klip when I log in → Save general settings** for automatic startup.

On desktops other than XFCE, global shortcuts must be configured manually in
the desktop's keyboard settings using the appropriate capture command above.

## Your first screenshot

### Extract text from a screenshot (OCR)

In version 0.2.0 development builds, choose **tray → Capture text (OCR)** and
select an area. Or click **Extract text (OCR)** in the image editor. Recognition
runs locally; the editor timestamp watermark is excluded.

Choose English, Hindi, or English + Hindi, then **Extract text / Retry**.
Edit the recognized text, **Copy text**, or **Save .txt**. Retry replaces a
successful result. Try Text block/Scattered text/Automatic layout or toggle
image improvement if recognition is poor. OCR can make mistakes, especially
in punctuation or code—review text before using it.

The `.deb` installs English OCR dependencies. Source users install them once:

```bash
sudo apt install tesseract-ocr tesseract-ocr-eng
```

For Hindi, optionally install:

```bash
sudo apt install tesseract-ocr-hin
```

You can also run `klip --ocr` (package) or
`~/klip/.venv/bin/python ~/klip/klip.py --ocr` (source). No Python OCR packages
or cloud account are needed. A temporary local PNG is removed after processing.

### Capture and annotate

1. Tray icon → **Capture area**.
2. Drag to select an area. Move it or resize it using the edge/corner handles.
3. Click **Capture** (or press Enter). **Esc** cancels.
4. Choose a toolbar tool; hover an icon to see its name.
5. Click **Save** or **Copy** to paste into another app.

| Tool/action | Use |
| --- | --- |
| Pen / Arrow / Rectangle / Ellipse | Draw or point things out. |
| Highlight | Mark an area with transparent color. |
| Text | Drag a box and type; move by its header, resize by its corner. |
| Select | Click an editable shape to move/resize it. |
| Timestamp | Add date, time, and timezone; adjust size and opacity. |
| Ctrl+Z / Ctrl+Shift+Z | Undo / redo. |
| Ctrl+S / Ctrl+C | Save / copy. |

Text: **Enter** applies, **Shift+Enter** adds a line, **Esc** cancels.
Applied text and pen strokes cannot be reselected; Undo can remove them.
Exported images do not keep editable objects. Closing an editor leaves Klip
in the tray; choose **Quit Klip** to exit completely.

## Common questions

- **Nothing opens after clicking Klip?** Check the tray near the clock; this is expected.
- **Menu entry missing?** For A, rerun `install_desktop.py`; for B, check that APT finished successfully.
- **Selection seems stuck?** Click Capture or press Enter. Esc cancels.
- **Shortcut does nothing?** Click Apply, check for conflicts, and give your Linux desktop keyboard focus.
- **Password is invisible while typing?** This is normal for `sudo`.
- **Install failed?** Stop and [report the exact error](https://github.com/workwithmanish/klip/issues), with your distro, desktop, and X11/Wayland result.

## Uninstall

First disable login startup, clear/apply Klip's capture shortcut in Settings,
and quit Klip from the tray.

**A. Source:** remove the menu launcher, then delete the `klip` folder in your file manager:

```bash
"$HOME/klip/.venv/bin/python" "$HOME/klip/install_desktop.py" --remove
```

**B. Package:**

```bash
sudo apt remove klip
```

Your saved screenshots are not deleted. User preferences are retained.

## More information

Klip makes no network requests while capturing/editing. Captures stay local
unless saved, copied, or shared. Pixelation is a visual effect, not guaranteed
secure redaction. No true blur or Wayland capture yet.

[Developer/package details](docs/DEVELOPMENT.md) · [Contributing](CONTRIBUTING.md) ·
[MIT license](LICENSE) · [Qt/PySide6 notices](THIRD_PARTY.md)
