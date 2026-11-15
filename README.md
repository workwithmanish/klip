# Klip

Take a screenshot, draw on it, add text, and save or copy it—all from your Linux desktop.

Klip stays in your system tray, near the clock. After setup, you can open it from
your application menu without keeping a terminal open.

> **Early development:** Kali Linux with XFCE has been tested manually. Debian 13
> package installation passes automated checks. Other Linux desktops still need testing.

## 1. Check whether Klip can run on your computer

Klip currently needs a **Linux desktop using X11**. It does not capture screens
on Wayland yet. Windows and macOS are not supported.

Not sure what you use? Open a terminal and paste:

```bash
echo "$XDG_SESSION_TYPE"
```

- **`x11`** → continue below.
- **`wayland`** → use an X11 session if your login screen offers one. Otherwise,
  this version of Klip cannot capture your screen yet.
- **Nothing printed** → run the command in a terminal inside your graphical desktop.

The instructions below are for **Kali Linux and Debian 13**. They have not been
verified on Ubuntu, Mint, or other distributions.

## 2. Install Klip

**There is no public release download yet.** For now, use the setup below.
You only need to do this once. It downloads Klip and installs its requirements
in a separate environment so they do not replace your system Python packages.

Open a terminal as your usual desktop user. Paste these commands **one line at
a time**. If a command reports an error, stop and check [Need help?](#need-help).

```bash
sudo apt update
sudo apt install -y git python3-venv libxcb-cursor0 libxkbcommon-x11-0
git clone https://github.com/workwithmanish/klip.git "$HOME/klip"
cd "$HOME/klip"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python install_desktop.py
```

Your password may be requested by `sudo`. No characters appear while you type it;
that is normal. An internet connection is needed for this setup.

**Already have a `klip` folder?** These first-time instructions will not overwrite
it. See [Updating an existing installation](#updating-an-existing-installation).

## 3. Open Klip

1. Open your Linux application menu.
2. Search for **Klip** and click it.
3. Look near the clock for the purple Klip icon. Klip starts there rather than
   opening a large window.
4. Click/right-click the icon and choose **Capture area** or **Settings**.

You can close the setup terminal now. **Keep the `klip` folder and its `.venv`
folder**—this development installation uses them to run the app.

## 4. Take your first screenshot

1. Choose **Capture area** from the tray icon.
2. Drag across the part of the screen you want.
3. Adjust the selection by dragging inside it or using its edge/corner handles.
4. Click **Capture**. To cancel, click **Cancel** or press **Esc**.
5. In the editor, choose a drawing or text tool. Hover an icon to see its name.
6. Click **Save** to create an image file, or **Copy** to paste it into another app.

Closing the editor keeps Klip running in the tray. Choose **Quit Klip** from the
tray menu when you want to exit completely.

## Useful tools

| What you want to do | What to use |
| --- | --- |
| Draw freely | Pen |
| Point something out | Arrow, Rectangle, or Ellipse |
| Mark a passage | Highlight |
| Add a note | Text: drag a box and type directly inside it |
| Move or resize a shape | Select: click the shape, then drag it or its handles |
| Undo a mistake | Undo / Ctrl+Z |
| Save or copy | Save / Ctrl+S or Copy / Ctrl+C |
| Add date, time, and timezone | Enable Timestamp at the bottom of the editor |

For text, drag its top bar to move the box and its corner to resize it.
**Enter** applies the text, **Shift+Enter** adds a new line, and **Esc** cancels.
After applying, text and pen marks cannot be reselected; Undo can remove them.
Saved images do not retain editable shapes.

## Set a capture keyboard shortcut

On **XFCE**:

1. Open **Settings** from Klip's tray menu.
2. Choose **Shortcuts**.
3. Click the global capture shortcut field and press your preferred keys.
4. Click **Apply capture shortcut**.

Klip warns you if the keys are already assigned. Choose another combination.
Press the shortcut while your Linux desktop has keyboard focus.

On other desktops, use that desktop's keyboard settings to assign a shortcut
to this command (replace `YOUR_USER` with your Linux username):

```text
/home/YOUR_USER/klip/.venv/bin/python /home/YOUR_USER/klip/klip.py --capture
```

## Start Klip automatically

Open **Settings → General**, enable **Start Klip when I log in**, then click
**Save general settings**. Klip will start in the tray at your next login.

## Updating an existing installation

These commands are for an installation made by cloning this repository using
the instructions above. Quit Klip from its tray menu first:

```bash
cd "$HOME/klip"
git pull --ff-only
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python install_desktop.py
```

Then open Klip from your application menu again. If you use a shared Windows
folder, a different Python environment, or a `.deb`, follow
[the installation notes](docs/DEVELOPMENT.md) instead of mixing setups.

## Need help?

| Problem | What to check |
| --- | --- |
| Klip does not appear in the menu | Run the last installer command again, then reopen the menu. |
| Clicking Klip opens no window | Check the tray near the clock—this is expected. |
| Capture says X11 is required | Your session uses Wayland; see step 1. |
| Selection stays on screen | Click Capture or press Enter; Esc cancels. |
| Shortcut does nothing | Click Apply capture shortcut and check for a conflict warning. |
| Install command fails | Stop and copy the exact error. Do not change your system repositories. |

To see startup errors, run from a terminal:

```bash
"$HOME/klip/.venv/bin/python" "$HOME/klip/klip.py" --settings
```

[Report a problem](https://github.com/workwithmanish/klip/issues) with your Linux
version, desktop, and error message. Remove private information from screenshots.

## Remove Klip

First disable login startup and clear/apply Klip's capture shortcut in Settings,
then choose **Quit Klip**. Remove the menu launcher:

```bash
"$HOME/klip/.venv/bin/python" "$HOME/klip/install_desktop.py" --remove
```

You can then delete the `klip` project folder using your file manager. Your saved
screenshots are not deleted. Per-user preferences are retained.

## Privacy and project details

Klip makes no network requests while capturing/editing. Screenshots remain local
unless you save, copy, or share them. Pixelation is a visual effect; do not rely
on it to securely remove sensitive information.

Want to build a `.deb` or contribute? See [Developer and package instructions](docs/DEVELOPMENT.md)
and [CONTRIBUTING.md](CONTRIBUTING.md).

Original Klip code/artwork: [MIT license](LICENSE).
Qt/PySide6: [third-party notices](THIRD_PARTY.md).
