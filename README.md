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

**Klip targets desktop Linux: native X11 capture plus experimental Wayland portal capture in 0.3.0.** Kali/XFCE/X11 is manually
tested; Debian 13 package/editor/OCR checks pass. Everything else below is
classified for clarity, not claimed as supported.

### How to read the categories

| Layer | What it tells you | Examples |
| --- | --- | --- |
| Kernel / OS family | The underlying system | Linux, Windows NT, Darwin, FreeBSD |
| Distribution lineage | Which project a Linux OS is derived from | Debian → Ubuntu → Mint; Arch → EndeavourOS |
| Package ecosystem | How software is built/installed | DEB/APT, RPM/DNF, Pacman, Nix, Portage |
| Desktop / session | The interface and screen-capture mechanism | XFCE/X11, GNOME/Wayland |
| CPU / system libraries | Whether dependencies can run | x86_64 vs ARM64; glibc vs musl |

**Debian is a distribution lineage; RPM is a package format.** They are not
identical kinds of category. Fedora and openSUSE both use RPM but have different
lineages, repositories and dependency versions. No single number describes all
Linux “types.” New distributions, spins and forks appear continually.

### 1. Kernel and operating-system families

| Kernel / OS ecosystem | Examples | Relationship to Linux | Klip status |
| --- | --- | --- | --- |
| **Desktop/server Linux** | Debian, Kali, Fedora, Ubuntu, Arch, etc. | Linux kernel, multiple userlands/package systems | The only current target; see distro and session tables below. |
| **Android** | Android / AOSP, LineageOS | Linux kernel with Android frameworks and Bionic libc | Unsupported; a Linux kernel does not make it a desktop-Linux target. |
| **ChromeOS** | ChromeOS, ChromiumOS | Linux-based OS with its own desktop/security model | Unsupported. A Linux development container is a separate environment, not native support. |
| **Windows NT** | Windows desktop/server | Separate kernel family | Unsupported release target. |
| **Darwin / XNU** | macOS, iOS, iPadOS | Separate kernel/userland family | Unsupported. |
| **FreeBSD** | FreeBSD, GhostBSD | BSD-derived, its own kernel/userland | Unsupported. |
| **OpenBSD** | OpenBSD | BSD-derived, its own kernel/userland | Unsupported. |
| **NetBSD** | NetBSD | BSD-derived, its own kernel/userland | Unsupported. |
| **DragonFly BSD** | DragonFly BSD | Separate BSD-derived kernel/userland | Unsupported. |
| **illumos / Solaris** | illumos distributions, OpenIndiana, Oracle Solaris | Separate Unix kernel ecosystems | Unsupported. |
| **GNU Hurd** | GNU/Hurd, Debian GNU/Hurd port | GNU Mach/Hurd, not the Linux kernel | Unsupported, even where Debian packaging tools are used. |
| **Haiku** | Haiku | Independent desktop OS/kernel | Unsupported. |
| **Zircon** | Fuchsia | Separate kernel/OS architecture | Unsupported. |
| **Other independent / research / embedded OSes** | Redox, SerenityOS, ReactOS, QNX, MINIX, FreeRTOS, Zephyr | Multiple unrelated kernels and runtime models | Unsupported; no general Python/Qt desktop assumption. |

This is an ecosystem map, **not a claim to list every OS ever created**. Legacy
systems, vendor forks, experimental kernels and embedded products are open-ended.

### 2. Linux distributions, lineage and package systems

| Lineage / ecosystem | Distributions / variants | Package or deployment tools | Klip status |
| --- | --- | --- | --- |
| **Debian** | Debian 13 | DEB · APT/dpkg | Automated package/editor/OCR checks pass; real desktop testing pending. X11 tested path; Wayland portal preview unverified. |
| Debian-derived / security | **Kali Linux Rolling** | DEB · APT/dpkg | **Main manually tested system: XFCE + X11**, including fresh package install. |
| Debian-derived / desktop | LMDE, MX Linux, antiX, SparkyLinux, Q4OS | Generally DEB · APT/dpkg | Untested; base version, dependencies and session must be checked. |
| Debian-derived / alternative init | Devuan | DEB · APT/dpkg | Untested; no systemd assumption is sufficient to establish support. |
| **Ubuntu** (Debian-derived) | Ubuntu, Kubuntu, Xubuntu, Lubuntu, Ubuntu MATE | DEB · APT/dpkg | Untested; desktop/session and available PySide6 version vary. |
| Ubuntu-derived | Linux Mint Ubuntu edition, Pop!_OS, Zorin OS, elementary OS, KDE neon | DEB · APT/dpkg | Untested. Debian ancestry does not guarantee package compatibility. |
| **Fedora** | Fedora Workstation, Server, desktop Spins | RPM · DNF | No RPM yet. **Use the 0.3.0 Flatpak preview for Fedora 44 GNOME/Wayland testing.** Real desktop verification pending. |
| Fedora image-based variants | Silverblue, Kinoite, other Fedora Atomic Desktops | Image deployments; rpm-ostree/variant-specific tooling | Untested; ordinary DNF installation instructions do not apply universally. |
| **RHEL ecosystem** | RHEL, CentOS Stream, Rocky Linux, AlmaLinux, Oracle Linux | RPM · DNF and platform-specific tooling | No Klip RPM; untested. Python/Qt availability varies by release. |
| **SUSE ecosystem** | openSUSE Leap, Tumbleweed; SUSE Linux Enterprise | RPM · Zypper | No Klip RPM; untested. Fedora RPMs are not automatically compatible. |
| SUSE transactional variants | openSUSE MicroOS, Aeon and related variants | Image/transactional workflows; variant-specific app delivery | Untested; do not assume conventional desktop package instructions apply. |
| Mandriva-related RPM ecosystems | Mageia, OpenMandriva | RPM · urpmi or DNF depending on distro | No Klip package; untested. |
| Independent RPM ecosystems | PCLinuxOS | RPM · APT-RPM / distro tooling | Untested. APT usage here does not imply DEB compatibility. |
| **Arch** | Arch Linux | Pacman · pkg.tar packages | No native Klip package; source/runtime untested. |
| Arch-derived | EndeavourOS, Manjaro, Garuda, CachyOS | Pacman and distro repositories | Untested; not automatically verified by Arch ancestry. |
| **Gentoo** | Gentoo, Calculate Linux | Portage · ebuild recipes/source builds | No Klip ebuild; untested. |
| **Slackware** | Slackware, Slackware-derived systems | pkgtools/slackpkg · tar-based packages | No Klip package; untested. |
| **Alpine** | Alpine Linux | APK · .apk packages | No Klip package; untested. musl-based libraries can affect binary dependencies. |
| Alpine-derived mobile | postmarketOS | APK plus mobile-specific integration | Unsupported mobile environment; not a tested desktop target. |
| **Void** | Void Linux (glibc or musl) | XBPS | No Klip package; both library variants untested. |
| **NixOS** | NixOS and derivatives | Nix · declarative configurations/store | No Klip Nix package; untested. Standard filesystem/install assumptions differ. |
| **GNU Guix System** | GNU Guix System | Guix · declarative/source-based tooling | No Klip Guix package; untested. |
| **Solus** | Solus | eopkg | No Klip package; untested. |
| **CRUX** | CRUX | Ports recipes · pkgutils | No Klip port; untested. |
| **Linux From Scratch** | LFS, Beyond Linux From Scratch | User-assembled; no single mandatory package manager | No general compatibility claim; environment-specific work required. |
| **Embedded / appliance Linux** | OpenWrt, Buildroot-based systems, Yocto-based products | Release/product-specific packages or generated images | Unsupported; many lack a compatible graphical desktop/Python/Qt stack. |
| **Purpose-built Linux systems** | Tails, Qubes OS, SteamOS, security/appliance derivatives | Base- and product-specific packaging/security/deployment rules | Untested as products. Base lineage alone does not establish screenshot access or support. |

Examples are grouped by ecosystem, not a complete census of forks. Distribution
versions and deployment tools evolve; check the project's own documentation.
Only the Kali and Debian rows above carry actual verification claims.

### 3. Desktop and display sessions — applies to EVERY Linux family

| Desktop / environment | Session | Capture / shortcut support |
| --- | --- | --- |
| **XFCE on Kali** | **X11** | **Manually tested capture.** Automatic Klip shortcut setup with conflict checking. |
| XFCE on another distro | X11 | Untested; XFCE integration exists, distro dependencies/integration need testing. |
| GNOME | X11, where available | Untested; manual desktop shortcut setup. |
| KDE Plasma | X11, where available | Untested; manual desktop shortcut setup. |
| Cinnamon / MATE / LXQt / LXDE | X11 | Untested; manual desktop shortcut setup. |
| Standalone window managers, e.g. i3/Openbox | X11 | Untested; tray availability and shortcut setup vary. |
| **GNOME / KDE / XFCE / any desktop** | **Wayland** | **Experimental screenshot/OCR via the desktop portal in 0.3.0.** Requires a working Screenshot backend and permission. Not manually verified on GNOME/KDE yet. |
| Wayland compositors, e.g. Sway/Hyprland | Wayland | Experimental portal path; depends on compositor backend support. Not tested. |
| Remote desktop / nested sessions | X11 or Wayland | Untested; screenshot and shortcut permissions are session-dependent. |
| Headless server / console / container without a desktop | No graphical session | No supported interactive capture workflow. |

Opening an existing image for editing/OCR may work on otherwise untested systems
if Python/Qt/Tesseract run, but that does not mean their screen capture works.

### 4. CPU, libraries and installer formats are separate questions

| Category | Examples | Klip meaning |
| --- | --- | --- |
| CPU architecture | x86_64/amd64, ARM64/aarch64, ARM32, RISC-V | Only x86_64 has current manual/CI evidence. Others untested; dependencies must exist for that CPU. |
| C library | glibc, musl | PySide6 wheel/native package availability differs; both are not automatically interchangeable. |
| Native packages | DEB, RPM, Arch packages, APK, XBPS, Nix/Guix definitions | Klip currently provides a DEB build setup only. |
| Cross-distro app delivery | Flatpak, Snap, AppImage | Delivery formats, **not kernel/distro families**. No Klip builds provided yet; sandbox/portal integration would need testing. |
| Source installation | Python + PySide6 + Tesseract | Avoids a specific installer format, but does not bypass Wayland or dependency limitations. |

Reference documentation: [Debian](https://www.debian.org/intro/about),
[Fedora packages](https://docs.fedoraproject.org/en-US/quick-docs/dnf/),
[Void/XBPS](https://docs.voidlinux.org/), [Alpine/musl](https://alpinelinux.org/about/),
[NixOS](https://nixos.org/manual/nixos/stable/),
[FreeBSD vs Linux](https://docs.freebsd.org/en/books/faq/).

Check your display session in a terminal:

```bash
echo "$XDG_SESSION_TYPE"
```

**`x11`** → native capture. **`wayland`** → use version 0.3.0 portal preview; your desktop will ask permission and handle selection. Earlier releases do not support Wayland capture.

## Cross-distro preview: Flatpak (Fedora / GNOME / KDE)

Version **0.3.0** adds a downloadable Flatpak preview for **x86_64** Linux.
It bundles Python/Qt, Tesseract and English/Hindi OCR data, avoiding distro-specific
Python dependency installation. It is not an RPM and is not listed on Flathub.

Download `klip_0.3.0_x86_64.flatpak` from the new pre-release when available.
With Flatpak installed on your distro:

```bash
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --user ./klip_0.3.0_x86_64.flatpak
flatpak run io.github.workwithmanish.klip
```

Fedora Workstation users without Flatpak can install it with `sudo dnf install flatpak`.
Run the app as your normal desktop user, without sudo. Do not run the Flatpak and
native version simultaneously while testing.

**Wayland:** the desktop's Screenshot portal owns consent and selection. Its UI
and region options may differ from Klip's X11 overlay. If the portal backend is
missing or refuses a request, Klip reports the error; it does not bypass permissions.
Flatpak uses this capture path on X11 too.

**Shortcuts:** Settings → Shortcuts → Configure desktop portal shortcuts. Your
desktop chooses keys and requests permission. Backend availability varies; if it
fails, add a desktop keyboard shortcut for:

```text
flatpak run io.github.workwithmanish.klip --capture
```

Portal shortcuts require Klip to remain running. GNOME may not display the tray
icon; the application menu opens the control panel when no tray is available.
Flatpak preview login startup is set manually through your desktop's Startup
Applications with `flatpak run io.github.workwithmanish.klip --background`.
Save access is provided to Pictures/Downloads and native file-picker portals.

**Testing status:** automated protocol/build tests are separate from real
Fedora/GNOME and KDE desktop testing. Please test and report those results before
assuming broad compatibility. Flatpak updates for these standalone bundles are
manual: download and install a newer bundle. No automatic update repository yet.

## Install Klip: choose ONE method

These instructions target **Kali/XFCE/X11 and Debian 13/X11**. Internet access
is needed to install dependencies. Use your normal desktop account; do not
launch Klip with `sudo`.

| Method | Best for | Available now? |
| --- | --- | --- |
| **A. Source installation** | Trying Klip today and getting updates | Yes |
| **B. Local `.deb` package** | Installing an independent system application | Yes, build it first |
| **C. Download a ready-made `.deb`** | Trying the older alpha | v0.1.0-alpha available; latest development version is 0.3.0 |

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

For the latest development version (0.3.0), build the package locally:

```bash
sudo apt update
sudo apt install -y git python3
git clone https://github.com/workwithmanish/klip.git "$HOME/klip-build"
cd "$HOME/klip-build"
python3 packaging/build_deb.py
sudo apt install ./dist/klip_0.3.0_all.deb
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
sudo apt install ./dist/klip_0.3.0_all.deb
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
existing 0.3.0 installation to the older alpha.

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
secure redaction. No true blur yet. Wayland capture is an experimental portal integration.

[Developer/package details](docs/DEVELOPMENT.md) · [Contributing](CONTRIBUTING.md) ·
[MIT license](LICENSE) · [Qt/PySide6 notices](THIRD_PARTY.md)
