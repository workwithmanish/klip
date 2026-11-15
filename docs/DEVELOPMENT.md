# Developer and package instructions

The main README is the first-time user guide. This page covers development,
experimental Debian packages, and migration from the original shared-folder setup.

## Build and test

Python 3.10+ and PySide6 6.8+ are required.

```bash
python -m unittest discover -s tests
python3 packaging/build_deb.py
```

The package builder needs only Python's standard library. It bundles original
Python source/SVG assets and declares distro Python/Qt dependencies. It does not
vendor Qt or download/install dependencies during the build.

The `all` in `klip_0.2.1_all.deb` means the package source is architecture-independent;
native Qt packages must still be available for the target CPU and OS. Debian 13
CI checks installation, offscreen tests and removal. Real tray, X11 capture,
shortcuts and startup still require manual desktop checks (CONTRIBUTING.md).

## Install an experimental .deb

The published v0.1.0-alpha is older than development version 0.2.1.
For the latest code, build from a checkout, then:

```bash
sudo apt install ./dist/klip_0.2.1_all.deb
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
`klip --open image.png`. Source setup: use the selected Python and `klip.py` path.

Login startup and desktop shortcuts contain absolute paths. Recreate them after
moving the source/interpreter. They are per-user and need no administrator access.
