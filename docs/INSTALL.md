# Install Klip — start here

Current preview: **0.3.1-alpha**. Pick **one** method below.
You do not need Python, Git or a source checkout when installing a ready-made package.

## 1. Choose your system

| Your desktop Linux system | Choose | What has been verified? |
| --- | --- | --- |
| Kali Linux, XFCE + X11 | DEB: section 2 | User reports Klip works; 0.3.1 installation and diagnostics verified |
| Debian 13 | DEB: section 2 | Automated install/editor/OCR checks; real desktop testing still needed |
| Fedora, including GNOME/Wayland | Flatpak: section 3 | Bundle built/tested automatically; actual Fedora desktop testing pending |
| Ubuntu, Mint, Pop!_OS, Zorin, elementary OS | Flatpak preview: section 3 | Klip desktop behaviour not yet verified |
| Arch, EndeavourOS, Manjaro, openSUSE | Flatpak preview: section 3 | Klip desktop behaviour not yet verified |
| Another Linux desktop with Flatpak | Flatpak preview: section 3 | Requires working desktop portals; not a compatibility guarantee |
| Windows, macOS, BSD, Android, iOS | No supported installer | Not supported by this release |
| A server without a graphical desktop | No supported capture workflow | Klip needs a graphical desktop session |

The provided Flatpak is for **x86_64** computers. Check with `uname -m`.
If it prints `aarch64`/`arm64`, this Flatpak is not the right architecture.
The DEB is named `all` because its Python source is architecture-independent,
but compatible native dependencies are still required; ARM desktop use is unverified.

**X11 and Wayland are desktop display systems**, not separate distributions.
Klip uses native capture on X11; Wayland uses the desktop's permission-based
screenshot portal. A Flatpak install also uses the portal on X11. Changing package
format does not remove permission requirements or guarantee desktop compatibility.

## 2. Kali / Debian 13: install the DEB

Quit any old Klip instance through **tray → Quit Klip** first.
Open a terminal and run these lines in order. If a line fails, stop there.

```bash
sudo apt update
sudo apt install -y wget
mkdir -p "$HOME/klip-install"
cd "$HOME/klip-install"
wget -O klip_0.3.1_all.deb https://github.com/workwithmanish/klip/releases/download/v0.3.1-alpha/klip_0.3.1_all.deb
ls -lh klip_0.3.1_all.deb
sudo apt install ./klip_0.3.1_all.deb
dpkg-query -W klip
```

The last command should show **`klip 0.3.1`**. APT installs the required
Python/Qt, OCR and portal dependencies automatically.
Now search **Klip** in the application menu and open it. No terminal needs to stay open.

If APT cannot find a dependency, do not add another distribution's repositories.
Your OS may need a different package set; consider the experimental Flatpak route.

## 3. Fedora and other Linux desktops: install the Flatpak preview

**First install Flatpak for your own distribution.** Use the
[official setup selector](https://flathub.org/en/setup):
[Fedora](https://flathub.org/en/setup/Fedora),
[Ubuntu](https://flathub.org/en/setup/Ubuntu),
[Debian](https://flathub.org/en/setup/Debian),
[Mint](https://flathub.org/en/setup/Linux%20Mint),
[Arch](https://flathub.org/en/setup/Arch),
[openSUSE](https://flathub.org/en/setup/openSUSE),
or choose your distribution on that page. Follow any logout/restart instructions.
Fedora Workstation, Silverblue and Kinoite normally already include Flatpak.

Then:

1. [Download Klip 0.3.1 x86_64 Flatpak](https://github.com/workwithmanish/klip/releases/download/v0.3.1-alpha/klip_0.3.1_x86_64.flatpak).
2. Open the folder containing that downloaded file in your file manager.
3. Right-click empty space and choose **Open in Terminal** (wording varies).
4. Run the following commands **without sudo**:

```bash
ls -lh klip_0.3.1_x86_64.flatpak
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install --user ./klip_0.3.1_x86_64.flatpak
flatpak run io.github.workwithmanish.klip
```

Answer the installation prompts. The first install can download a large shared Qt
runtime. Flathub supplies that runtime; **Klip itself is a downloaded preview bundle,
not a Flathub-listed application**. Python, Qt and OCR are included in the bundle.

Later, search **Klip** in your application menu. On desktops without a visible tray
icon, use its control panel. On Wayland, complete the desktop screenshot permission
dialog; its selection options may differ from Klip's native X11 selection.
Please report actual Fedora/GNOME/KDE test results before calling those setups verified.

## 4. First capture and keyboard shortcut

Open Klip, choose **Capture area**, select an area, then draw/add text and Copy or Save.

- **Native XFCE:** Settings → Shortcuts → record and apply the capture shortcut.
- **Portal/Flatpak:** configure desktop portal shortcuts in Klip Settings. If the
  desktop does not support them, create a shortcut in its keyboard settings using
  `flatpak run io.github.workwithmanish.klip --capture`.
- Klip must remain running for its active tray/portal shortcut session.
  Configure login startup if you want it to start automatically.

## 5. Updates, diagnostics and removal

Updates are currently manual. Quit Klip, download the newer release's matching
DEB or Flatpak, and install that file using the same method. Use the new filename.
GitHub pushes alone do not update an installed copy. Avoid running source, DEB and
Flatpak copies simultaneously. [All release downloads](https://github.com/workwithmanish/klip/releases).

| Task | DEB install | Flatpak install |
| --- | --- | --- |
| Open settings | `klip --settings` | `flatpak run io.github.workwithmanish.klip --settings` |
| Check desktop support | `klip --check-desktop` | `flatpak run io.github.workwithmanish.klip --check-desktop` |
| Remove app | `sudo apt remove klip` | `flatpak uninstall --user io.github.workwithmanish.klip` |

`status: "unknown"` / `available: null` means a capability query did not establish
support. On native X11, such a portal query error does not itself mean capture is broken.
Diagnostic availability is not a substitute for actually testing capture and shortcuts.

**Common errors:**

- `Unsupported file ./klip_...deb`: confirm the file exists in your current folder
  with `ls -lh`; download it before running APT. Section 2 uses a fixed folder to avoid this.
- `unrecognized arguments: --check-desktop`: you are likely running an older copy.
  Quit it, verify `dpkg-query -W klip`, and try `/usr/bin/klip --check-desktop` for DEB.
- Missing `dbus_next` when running source with system Python: on Kali/Debian use
  `sudo apt install python3-dbus-next`; for a venv install the project's requirements
  using that venv's Python. Ready-made packages already declare/bundle this dependency.

## Want to build or edit the source instead?

Use the [source and local-build instructions](../README.md#install-klip-choose-one-method)
and [developer guide](DEVELOPMENT.md). Those native dependency commands target
Kali/Debian; they are not universal commands for Fedora/Arch/openSUSE.
