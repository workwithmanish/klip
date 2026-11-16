# Contributing

Want to use the app rather than develop it? Follow the [easy installation guide](docs/INSTALL.md).

Current release: **v0.3.1-alpha**. Read [README](README.md),
[developer instructions](docs/DEVELOPMENT.md) and [testing status](docs/TESTING.md).

Report your distro/version, CPU architecture, desktop, X11/Wayland,
installation method (`.deb`, Flatpak or source), reproduction steps and errors.
For native/source reports, include Python/PySide6/Tesseract versions when relevant.
For portal errors, include the desktop portal/backend versions if known.
Remove secrets from screenshots and logs. Do not call an environment supported
based only on sharing a package family with a tested distro.

Run `python -m unittest discover -s tests` and `python packaging/build_deb.py`.
On Linux, use `dbus-run-session -- python3 -m unittest discover -s tests -v`
to exercise success, cancellation and denial against the mock portal service.
Build Flatpak using the manifest/instructions in the developer guide.

Before release, test on a clean supported Linux VM:

1. Test native `.deb` on Kali/XFCE/X11, and Flatpak on Fedora/GNOME/Wayland and KDE/Wayland when testers are available.
2. Test application-menu launch, tray/control-panel fallback, capture/settings/quit.
   X11: move/resize/confirm/cancel. Portal: consent, selection, cancellation, denial and missing backend.
3. Exercise annotations, inline text, undo/redo, PNG/JPEG save and clipboard paste.
4. Verify timestamps/timezones and a second monitor if available.
5. Test XFCE registration/conflict refusal, portal shortcut permission/activation/disable, and manual keyboard fallback.
6. Test native login startup and manual Flatpak startup, disabling/removing integrations, updates, and package uninstall.
7. Verify English/Hindi OCR, missing-language messages, loading state, timeout/cancel and text export.

Record exact environments/results in release notes. Do not claim untested desktop
or distribution compatibility. CI artifacts are development builds; publish a
release with clear testing limits. A compatibility preview may include unverified
desktop paths, but they must be labeled experimental. Current runtime verification
is recorded in [TESTING.md](docs/TESTING.md); automated tests do not replace it.
