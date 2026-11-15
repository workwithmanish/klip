Linux compatibility preview: X11 capture plus experimental desktop-portal capture
on Wayland, with a cross-distribution Flatpak build.

## Download and install

**Fedora / GNOME / KDE and other Flatpak-capable desktops (x86_64):**

1. Install Flatpak using your distribution's instructions.
2. Add Flathub for the KDE runtime if it is not already configured:

```sh
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --user ./klip_0.3.0_x86_64.flatpak
flatpak run io.github.workwithmanish.klip
```

**Kali / Debian 13:**

```sh
sudo apt install ./klip_0.3.0_all.deb
```

Quit any old running instance before updating. Choose one installation method.

## What's included

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
