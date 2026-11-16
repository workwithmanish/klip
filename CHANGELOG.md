# Changelog

## Unreleased — development changes, 2026-11-16

- Fix themed inline text rendering: dedicated font size in pixels, live font/color
  changes and matching export; remove the drawing-width-to-font multiplier.
- Replace the 30-entry snapshot cutoff with per-edit annotation changes. Undo can
  reach the unedited capture and redo every retained edit, including timestamp changes.
- Inspect screenshot/shortcut portal capabilities via tray diagnostics and
  `--check-desktop`; negotiate interactive/area options by advertised interface
  version and targets. Detect Wayland even without XDG_SESSION_TYPE; pass real
  X11 parent identifiers when available, without inventing Wayland handles.

- Keep pen strokes and committed text as selectable annotations, with text re-editing
  on double-click, move/resize, color changes, deletion and undo/redo.
- Match hover/click selection to stroke geometry; preserve chronological layering.
- Keep pixelation in the annotation stack and recompute it when moved/resized.
- Cache composed images during pointer movement and retain the immutable capture.
  Simple selection no longer adds an undo step.
- Add tray Copy diagnostics, CLI `--diagnostics`, and Cancel pending capture.
- Add regression checks for retained annotations, geometry, history and caching.

The published 0.3.0-alpha installers are unchanged. GNOME/KDE Wayland and mixed-DPI
desktop validation remain pending; these changes do not claim new platform support.

## 0.3.0-alpha — released 2026-11-15

[Download release](https://github.com/workwithmanish/klip/releases/tag/v0.3.0-alpha).
Installer/app version: `0.3.0`. Wayland remains experimental; see [testing status](docs/TESTING.md).

- Experimental permission-based Screenshot portal capture on Wayland and in Flatpak.
- Desktop portal capture/OCR shortcuts with manual keyboard-settings fallback.
- Cross-distro x86_64 Flatpak bundling Qt/PySide6, Tesseract and English/Hindi data.
- Native Debian package and existing X11 region overlay retained.
- Automated D-Bus success/cancel/denial checks; Fedora/GNOME and KDE desktop validation still pending.
- GitHub pre-release build/asset automation.


## 0.2.1 — development

- OCR loading view with animated activity indicator, elapsed time and cancellation.
- Simplified OCR results: automatic English/Hindi language-pack selection and image preparation.
- Precision Crimson light theme across settings, editor and OCR.
- Minimal About page with developer credits and project/support links.
- User-supplied purple/mint logo in app windows, tray, About, launcher and README.
- Version bump ensures APT upgrades existing 0.2.0 installations.

## 0.2.0 — development

- Offline Tesseract OCR from tray capture or editor image.
- Editable results, clipboard copy, UTF-8 text saving and retry.
- Missing-engine/language messages, timeout and temporary-image cleanup.

## 0.1.0 — initial alpha

- X11 area capture, move/resize selection and attached confirmation buttons.
- Annotation tools, editable shapes, inline text, undo/redo and image export.
- Alignment guides, coordinates, HEX inspector and timestamp watermark.
- Settings, XFCE shortcut registration, login startup and Debian packaging.

GitHub Releases are published separately from development commits. Consult the
release page for actual downloadable versions.
