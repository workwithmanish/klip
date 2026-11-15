# Contributing

Report your distro/version, desktop, X11/Wayland, Python/PySide6 versions,
reproduction steps and traceback. Remove secrets from screenshots and logs.

Run `python -m unittest discover -s tests` and `python packaging/build_deb.py`.

Before release, test on a clean supported Linux VM:

1. Install with APT and launch via the application menu without a terminal.
2. Test tray capture/settings/quit, capture move/resize/confirm/cancel.
3. Exercise annotations, inline text, undo/redo, PNG/JPEG save and clipboard paste.
4. Verify timestamps/timezones and a second monitor if available.
5. Test unused XFCE shortcut registration and refusal of conflicts.
6. Test login startup, disabling it, removing shortcuts, and package uninstall.

Record exact environments/results in release notes. Do not claim untested desktop
or distribution compatibility. CI artifacts are development builds; publish a
release only after manual checks.
