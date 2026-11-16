# Klip v0.3.1-alpha

[Published release](https://github.com/workwithmanish/klip/releases/tag/v0.3.1-alpha).
Installer/app version: 0.3.1. Linux compatibility preview: X11 capture plus experimental desktop-portal capture
on Wayland, with a cross-distribution Flatpak build.

## Download and install

**Fedora / GNOME / KDE and other Flatpak-capable desktops (x86_64):**

1. Install Flatpak using your distribution's instructions.
2. Add Flathub for the KDE runtime if it is not already configured:

```sh
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --user ./klip_0.3.1_x86_64.flatpak
flatpak run io.github.workwithmanish.klip
```

**Kali / Debian 13:**

```sh
sudo apt install ./klip_0.3.1_all.deb
```

Quit any old running instance before updating. Choose one installation method.

## What is fixed

- Text font size and color match during editing and after applying. Text has an independent pixel-size control.
- All annotation edits can be undone back to the original capture; timestamp changes participate in Undo/Redo.
- Pen/text remain editable; hover selection, layering and render caching are improved.
- Desktop capability checks distinguish unknown query failures from confirmed missing services. InvalidArgs is not an unsupported-system result.
- Run `klip --check-desktop` to inspect advertised portal support without taking a screenshot.

## What is included

- Permission-based screenshot portal capture on Wayland; native X11 capture retained.
- Desktop portal global shortcuts with manual desktop-keyboard fallback.
- Flatpak with Python/Qt, Tesseract, and English/Hindi data included.
- Current light UI, original Klip logo, inline text, editable shapes and timestamps.
- Offline OCR with a visible loading state, editable results and Copy/Save.

## Important preview limitations

Actual Fedora/GNOME and KDE Wayland desktop testing is still needed. Protocol,
package and editor tests do not prove every desktop backend works. Your desktop
owns the screenshot permission/selection dialog; it may offer different region
options from Klip's X11 overlay. Global shortcut portals are backend-dependent.
GNOME may not show a tray icon without desktop support; open Klip's control panel
from the application menu instead. Flatpak startup is configured manually in your
desktop's Startup Applications using `flatpak run io.github.workwithmanish.klip --background`.
The Flatpak is a downloadable preview bundle, not a Flathub listing or RPM.

Report your distro/version, desktop, session type and package method with bugs.

The Flatpak is cross-distro and may also be tested on Kali; it is not Fedora-only.
Quit any other installed Klip instance first. Download/install newer bundles manually;
there is no automatic Klip update repository yet. Both assets include SHA-256 files;
run `sha256sum -c <downloaded-filename>.sha256` in their download folder to verify.
For the current evidence and pending checks, see [Testing status](https://github.com/workwithmanish/klip/blob/main/docs/TESTING.md).

## Fedora GNOME / KDE tester checklist

Use the Flatpak asset above. This is a preview, not a verified compatibility claim.

1. Quit any old Klip instance, install the new bundle, and open Klip.
2. Run `flatpak run io.github.workwithmanish.klip --check-desktop` and keep its output.
3. Capture an area; also try cancelling/denying desktop permission and then retrying.
4. Add text at 26 px, apply/re-edit it, then draw and move/resize annotations.
5. Undo back to the original screenshot and redo the edits.
6. Copy and paste into a browser and another application; save through the file chooser.
7. Extract text with OCR, then test shortcut permission/activation and quit/relaunch.

Report desktop/session versions and which steps passed/failed through GitHub Issues.
`unknown` in diagnostics means the query did not establish support; a successful
property query alone also does not prove the real capture workflow works.
