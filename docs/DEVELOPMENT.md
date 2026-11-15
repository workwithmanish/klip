# Developer and package instructions

The main README is the first-time user guide. This page covers development,
experimental Debian packages, and migration from the original shared-folder setup.

## Build and test

Python 3.10+, PySide6 6.8+ and dbus-next 0.2.3 are required.
OCR uses the separate Tesseract executable and language data.

```bash
python -m unittest discover -s tests
python3 packaging/build_deb.py
```

On Linux, run tests under `dbus-run-session -- python3 -m unittest discover -s tests -v`
to include the mock portal protocol test. Real Tesseract recognition is tested
when Tesseract/English data are installed. Install your distro's QtTest bindings
for system-Python tests. Windows checks skip the Linux bus/engine tests when unavailable.

The package builder needs only Python's standard library. It bundles original
Python source/PNG/SVG assets and declares distro Python/Qt/OCR/portal dependencies. It does not
vendor Qt or download/install dependencies during the build.

The `all` in `klip_0.3.0_all.deb` means the package source is architecture-independent;
native Qt packages must still be available for the target CPU and OS. Debian 13
CI checks installation, offscreen tests and removal. Real tray, X11 capture,
shortcuts and startup still require manual desktop checks (CONTRIBUTING.md).

## Install an experimental .deb

The current release is [v0.3.0-alpha](https://github.com/workwithmanish/klip/releases/tag/v0.3.0-alpha).
Its `.deb` can be downloaded directly; developers can build from a checkout, then:

```bash
sudo apt install ./dist/klip_0.3.0_all.deb
```

APT gets requirements from your configured repositories. Do not mix distro
repositories if dependencies are unavailable. Debian 13 is the package target;
other Debian/Ubuntu derivatives require testing and compatible PySide6 6.8+ packages.

The package installs `/usr/bin/klip`, `/usr/share/klip` and a system menu entry.
It needs no source checkout or venv at runtime. Remove with `sudo apt remove klip`.
User preferences/integrations are retained; disable startup and clear/apply the
capture shortcut before removing if those should be removed too.

## Migrate from the shared-folder development setup

Do not run `git clone` over an existing shared folder. Continue using its current
Python environment, or deliberately switch to the package.

For the original `~/klip` plus `~/.venvs/klip` setup:

```bash
~/.venvs/klip/bin/python ~/klip/klip.py --settings
```

Before switching to a package, disable the old version's login startup and clear/apply
its capture shortcut, then quit it. Remove the old per-user menu entry so it does
not override the packaged menu entry:

```bash
~/.venvs/klip/bin/python ~/klip/install_desktop.py --remove
```

Install the `.deb`, open it from the menu, then configure startup/shortcuts again.
Settings and screenshots are preserved. Existing Git checkouts with code changes
should be reviewed with `git status` before pulling; do not discard local changes.

## Command-line interface

Installed package: `klip --capture`, `klip --settings`, `klip --background`,
`klip --ocr`, `klip --open image.png`. Source setup: use the selected Python and `klip.py` path.
Flatpak: prefix arguments with `flatpak run io.github.workwithmanish.klip`.

Login startup and desktop shortcuts contain absolute paths. Recreate them after
moving the source/interpreter. They are per-user and need no administrator access.


## Flatpak preview builds

On a Linux host with Flatpak/flatpak-builder, add Flathub for the SDK/BaseApp:

```sh
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak-builder --user --assumeyes --install-deps-from=flathub --force-clean --repo=flatpak-repo flatpak-build packaging/io.github.workwithmanish.klip.json
flatpak build-bundle flatpak-repo klip_0.3.0_x86_64.flatpak io.github.workwithmanish.klip
```

Runtime/SDK/BaseApp and OCR dependencies require substantial download/build disk
space. Sources and language data are pinned with SHA-256 checksums. No RPM is
required to install the resulting bundle on Fedora. This is not a Flathub submission.

Test screenshot consent/cancel, region selection, OCR, native Save/Copy, global
shortcut permissions and manual fallback on actual GNOME/Wayland and KDE/Wayland.
Protocol tests use a mock D-Bus backend; they do not validate a real compositor.
Flatpak source code lives under `/app/share/klip`; the native package uses
`/usr/share/klip`. Both identify as `io.github.workwithmanish.klip` for portals.

## Release workflow

The GitHub workflow builds/tests Debian and Flatpak artifacts. A `v*` tag runs
those checks and publishes a pre-release with both assets/checksums only if both
jobs succeed. Update app/build version, workflow filenames, AppStream metadata,
release notes and user instructions together when preparing a new version.
Never replace an existing release tag to hide a fix; publish a new version.
See [TESTING.md](TESTING.md) for what automated success does and does not establish.
