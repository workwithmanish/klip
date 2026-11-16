# Testing status — v0.3.1-alpha

Release date: 2026-11-16. Installer/app version: 0.3.1.

## Release checks — 2026-11-16

This release includes the annotation and diagnostics improvements.
Local Windows offscreen checks: 27 tests, 25 passed and 2
skipped because Tesseract and a Linux session bus are unavailable. These checks
cover editable pen/text, text re-edit cancel/apply, shape hit testing, stacking,
pixelation undo, render-cache invalidation and selection without a spurious undo.
An offscreen editor preview was also visually checked. These are editor checks,
not a Windows support claim or a Wayland compositor test.

Additional manual regression for a new build:

1. Draw a pen stroke; Select, hover, move, resize, recolor, delete, undo and redo.
2. Add multiline text; move/resize it, double-click to edit, then try Apply and Cancel.
3. Draw through an earlier shape; verify the newer stroke renders on top.
4. Hover an empty ellipse centre and away from a diagonal line; neither should select.
5. Move a pixelation region; verify it samples the content at its new position.
6. Copy diagnostics from the tray and run `klip --diagnostics` on the installed build.
7. Make at least 75 edits, then undo to the original capture and redo them all.
   Include timestamp changes and confirm the timestamp controls follow Undo/Redo.
8. With the app theme active, use Text 26 px, type text and change size/color while
   editing. Confirm the applied result has the same font, wrapping and placement.
9. Run `klip --check-desktop`; it should report properties without taking a screenshot.
10. On Wayland, cancel a pending portal request and immediately try another capture.

Real GNOME parent-window association, portal permissions, GTK/Qt/browser clipboard
paste after closing the editor, and mixed-DPI multi-monitor capture remain pending.
Do not describe those behaviours as fixed solely because offscreen checks pass.

| Environment / check | Evidence | What is still unverified |
| --- | --- | --- |
| Kali Rolling, XFCE/X11, x86_64 | User reports current source works; 0.3.1 DEB upgrade, dpkg version and installed diagnostics verified on 2026-11-16 | Complete manual text/undo/capture regression on installed 0.3.1 still pending |
| Debian 13 CI | 0.3.1 release workflow passed package build, install/uninstall and the full 27-test suite | Actual compositor, tray, multi-monitor and login session |
| Screenshot portal protocol | Real temporary D-Bus connection with a mock service; success/cancel/denial tested | Real GNOME/KDE/compositor implementation and permission UI |
| x86_64 Flatpak CI | Bundle built; editor creation, bundled Tesseract recognition and language-data checks passed | Interactive capture, permissions, file picker, clipboard and shortcuts on real desktops |
| Fedora 44 GNOME/Wayland | Downloadable Flatpak preview provided | Friend/community desktop results pending |
| KDE Plasma/Wayland | Portal code and Flatpak build provided | Real desktop testing pending |
| Other distros/desktops/CPU architectures | No additional manual verification recorded | Must not be called generally supported |

## Quick tester checklist

Quit any native/source/Flatpak Klip instance before changing installation method.
Install the matching asset from [v0.3.1-alpha](https://github.com/workwithmanish/klip/releases/tag/v0.3.1-alpha).

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

For diagnostics, an InvalidArgs query must report `available: null` and
`status: "unknown"`; it must not label a functioning native X11 setup unsupported.
