# Klip

<img src="assets/klip.png" alt="Klip logo" width="96" />

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

**Read the distro row AND the display-session row.** For example, Fedora 44
with GNOME/Wayland has both an untested distro/package setup and an unsupported
capture session. A different installer format cannot remove the Wayland limitation.

### Linux distributions and installer families

| Package family | Distribution | Usual package / manager | Klip status right now |
| --- | --- | --- | --- |
| Debian / DEB | **Kali Linux Rolling** | `.deb` / APT | **Main tested environment: XFCE + X11.** Fresh package install and capture manually tested. |
| Debian / DEB | **Debian 13** | `.deb` / APT | Package installation and automated editor/OCR tests pass. Real desktop capture testing pending; requires X11. |
| Debian / DEB | **Ubuntu** | `.deb` / APT | Not tested. Dependency availability depends on Ubuntu version; X11 required for capture. |
| Debian / DEB | **Linux Mint — Ubuntu edition** | `.deb` / APT | Not tested. Being Ubuntu-based does not establish compatibility; X11 required. |
| Debian / DEB | **LMDE — Linux Mint Debian Edition** | `.deb` / APT | Not tested. Dependency availability depends on its Debian base; X11 required. |
| Debian / DEB | **Pop!_OS** | `.deb` / APT | Not tested. Check the actual session; Wayland capture is unsupported. |
| Debian / DEB | **Zorin OS** | `.deb` / APT | Not tested. Check dependency versions and X11/Wayland session. |
| RPM | **Fedora — including Fedora 44** | `.rpm` / DNF | No Klip RPM yet; source installation untested. **The reported Fedora 44 GNOME/Wayland setup cannot capture yet.** |
| RPM | **RHEL / Rocky Linux / AlmaLinux** | `.rpm` / DNF | No Klip RPM; no testing. Python/Qt versions and desktop session must be checked. |
| RPM | **openSUSE Leap / Tumbleweed** | `.rpm` / Zypper | No Klip RPM; no testing. RPM files are not automatically interchangeable with Fedora packages. |
| Arch | **Arch Linux** | Arch packages / Pacman | No native Klip package; source installation and capture untested. |
| Arch | **EndeavourOS / Manjaro** | Arch-derived packages / Pacman | No native Klip package; source installation and capture untested. |
| Alpine | **Alpine Linux** | `.apk` / APK | No native package; untested. Different system libraries may require additional work. |
| Nix | **NixOS** | Nix packages / Nix | No Klip Nix package; untested. The standard source-install commands are not NixOS instructions. |
| Independent | **Gentoo** | Ebuilds / Portage | No Klip ebuild; source installation and capture untested. |

These are common distribution families, not a list of every Linux distribution.
**Only Kali/XFCE/X11 is manually verified.** A distro appearing here does not
mean it is supported, and a package family does not guarantee dependencies.
The installation commands below target Kali and Debian 13 only.

### Desktop and screen-capture support

| Desktop / display session | Capture status | Global shortcut setup |
| --- | --- | --- |
| **XFCE + X11 on Kali** | **Manually tested.** | Automatic registration in Klip, with conflict checking. |
| **XFCE + X11 on another distro** | Untested; depends on working Python/Qt and desktop integration. | Integration targets XFCE; distro-specific testing pending. |
| **GNOME + X11, where available** | Untested. | Configure manually in GNOME keyboard settings. |
| **KDE Plasma + X11, where available** | Untested. | Configure manually in KDE keyboard settings. |
| **Cinnamon / MATE + X11** | Untested. | Configure manually in desktop keyboard settings. |
| **GNOME / KDE / any desktop using Wayland** | **Screen capture and capture-to-OCR unsupported.** Existing-image editing/OCR may work if dependencies run; untested. | No Wayland shortcut-portal integration yet. |

### Operating systems outside Linux

| Operating system | Klip support |
| --- | --- |
| **Windows** | Not a supported release target; no installer or desktop-capture support claim. |
| **macOS** | Not supported; no installer or desktop-capture testing. |
| **FreeBSD / OpenBSD** | Not Linux; no package or runtime testing. |

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
| **C. Download a ready-made `.deb`** | Trying the older alpha | v0.1.0-alpha available; latest development version is 0.2.1 |

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

For the latest development version (0.2.1), build the package locally:

```bash
sudo apt update
sudo apt install -y git python3
git clone https://github.com/workwithmanish/klip.git "$HOME/klip-build"
cd "$HOME/klip-build"
python3 packaging/build_deb.py
sudo apt install ./dist/klip_0.2.1_all.deb
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
sudo apt install ./dist/klip_0.2.1_all.deb
```

The version/filename will change for future releases; use the name printed by
the build command.

### C. Download the published alpha

Visit [Releases](https://github.com/workwithmanish/klip/releases/tag/v0.1.0-alpha)
and download `klip_0.1.0_all.deb`. In a terminal opened in the download folder:

```bash
sudo apt install ./klip_0.1.0_all.deb
```

This older release does **not** contain the newer OCR, logo, loading screen or
light-theme changes. Use A or B for the latest version. Do not downgrade an
existing 0.2.1 installation to the older alpha.

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

In the current development version, choose **tray → Capture text (OCR)** and
select an area. Or click **Extract text (OCR)** in the image editor. Recognition
runs locally; the editor timestamp watermark is excluded.

English/Hindi selection and image preparation happen automatically using the
installed language packs. A loading screen shows progress while OCR runs;
you can cancel. Edit the result, **Copy text**, or **Save .txt**. Retry replaces
a successful result. OCR can make mistakes, especially
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
