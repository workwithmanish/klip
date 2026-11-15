# Testing status — v0.3.0-alpha

Released 2026-11-15. Installer/app version: 0.3.0.

| Environment / check | Evidence | What is still unverified |
| --- | --- | --- |
| Kali Rolling, XFCE/X11, x86_64 | User manually tested capture/editor and fresh native installation during earlier 0.1/0.2 development | Full manual regression on 0.3.0 is not yet reported |
| Debian 13 CI | Package build, install/uninstall and 13 tests passed | Actual compositor, tray, multi-monitor and login session |
| Screenshot portal protocol | Real temporary D-Bus connection with a mock service; success/cancel/denial tested | Real GNOME/KDE/compositor implementation and permission UI |
| x86_64 Flatpak CI | Bundle built; editor creation, bundled Tesseract recognition and language-data checks passed | Interactive capture, permissions, file picker, clipboard and shortcuts on real desktops |
| Fedora 44 GNOME/Wayland | Downloadable Flatpak preview provided | Friend/community desktop results pending |
| KDE Plasma/Wayland | Portal code and Flatpak build provided | Real desktop testing pending |
| Other distros/desktops/CPU architectures | No additional manual verification recorded | Must not be called generally supported |

## Quick tester checklist

Quit any native/source/Flatpak Klip instance before changing installation method.
Install the matching asset from [v0.3.0-alpha](https://github.com/workwithmanish/klip/releases/tag/v0.3.0-alpha).

1. Open the control panel and start capture.
2. On Wayland/Flatpak, accept the desktop permission request and capture an area
   if the backend offers that option. Also test Cancel/deny.
3. Draw, add text, select/resize shapes, undo/redo, save and paste a copied image.
4. Extract text, check the loading view, cancel/retry, edit and copy/save results.
5. Configure portal shortcuts, test activation, then disable. If unsupported,
   test a manual desktop shortcut to the matching capture command.
6. Quit/reopen and test your startup method. Check update/uninstall behavior.

Report distro version, desktop version, `echo "$XDG_SESSION_TYPE"`, CPU (`uname -m`),
installation method and exact errors through [Issues](https://github.com/workwithmanish/klip/issues).
State which steps passed/failed instead of reporting only “works.”
