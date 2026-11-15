# Third-party dependencies

Klip's original code and artwork use the MIT license (LICENSE).
PySide6 / Qt for Python and Qt are separate projects with their own
LGPL/GPL/commercial licensing terms and third-party notices:

- https://doc.qt.io/qtforpython-6/licenses.html
- https://doc.qt.io/qtforpython-6/overviews/qtdoc-lgpl.html

The Debian package does not vendor Python, PySide6, Qt libraries or wheels.
It declares dependencies on distro-managed packages, whose notices and licenses
are installed by the distro under `/usr/share/doc/`. Source users obtain
dependencies separately via pip or the package manager; consult those installed
distributions' license files.

Icons in `icons.py` and `assets/` are original Klip artwork under MIT. No code,
branding or artwork from the reference Windows application is included.

Optional source-install OCR / required package OCR: Tesseract OCR is invoked
as a separate local executable and is licensed under Apache-2.0. It is not
vendored. Language data comes from separately installed distribution packages.
See https://github.com/tesseract-ocr/tesseract/blob/main/LICENSE and the distro's
installed copyright notices for the engine and trained language data.

## Flatpak preview

The Flatpak uses the Qt/PySide BaseApp and KDE runtime, and bundles dbus-next (MIT), Leptonica (BSD-style), Tesseract (Apache-2.0), and tessdata_fast English/Hindi data (Apache-2.0). Their upstream notices/licenses remain applicable. This differs from the Debian package, which uses distro-managed dependencies. Source URLs and hashes are pinned in the Flatpak manifest.
