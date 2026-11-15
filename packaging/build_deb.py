"""Build a dependency-based, architecture-independent Debian package with Python.

No bundled Python/Qt, root access, pip downloads, or post-install scripts.
Linux install and runtime checks are still required before a public release.
"""
import argparse
import gzip
import hashlib
import io
from pathlib import Path
import re
import tarfile

ROOT = Path(__file__).resolve().parents[1]
MODULES = ('klip.py', 'preferences.py', 'geometry_tools.py', 'icons.py',
           'textbox.py', 'ui_spacing.py', 'watermark.py', 'ocr.py', 'theme.py')


def archive(files):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w', format=tarfile.USTAR_FORMAT) as tar:
        directories = set()
        for name in files:
            parent = Path(name).parent
            while str(parent) != '.':
                directories.add(parent.as_posix())
                parent = parent.parent
        for name in sorted(directories, key=lambda value: (value.count('/'), value)):
            item = tarfile.TarInfo('./'+name+'/')
            item.type, item.mode = tarfile.DIRTYPE, 0o755
            item.uid = item.gid = item.mtime = 0
            item.uname = item.gname = 'root'
            tar.addfile(item)
        for name, (data, mode) in sorted(files.items()):
            item = tarfile.TarInfo('./'+name)
            item.size, item.mode = len(data), mode
            item.uid = item.gid = item.mtime = 0
            item.uname = item.gname = 'root'
            tar.addfile(item, io.BytesIO(data))
    return gzip.compress(buffer.getvalue(), mtime=0)


def ar_member(name, data):
    header = f'{name+"/":<16}{0:<12}{0:<6}{0:<6}{"100644":<8}{len(data):<10}`\n'.encode('ascii')
    assert len(header) == 60
    return header + data + (b'\n' if len(data) % 2 else b'')


def build(version, output):
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:[+~.-][A-Za-z0-9.+~-]+)?', version):
        raise ValueError('Use a Debian-compatible version, e.g. 0.1.0')
    files = {}
    for name in MODULES:
        files['usr/share/klip/'+name] = ((ROOT/name).read_bytes(), 0o644)
    for asset in sorted((ROOT/'assets').iterdir()):
        if asset.suffix not in ('.svg', '.png'):
            continue
        files['usr/share/klip/assets/'+asset.name] = (asset.read_bytes(), 0o644)
    files['usr/bin/klip'] = (b'#!/bin/sh\nexec /usr/bin/python3 /usr/share/klip/klip.py "$@"\n', 0o755)
    files['usr/share/applications/klip.desktop'] = ((ROOT/'packaging/klip.desktop').read_bytes(), 0o644)
    for name in ('README.md', 'LICENSE', 'THIRD_PARTY.md'):
        files['usr/share/doc/klip/'+name] = ((ROOT/name).read_bytes(), 0o644)
    files['usr/share/doc/klip/copyright'] = ((ROOT/'LICENSE').read_bytes() + b'\nSee THIRD_PARTY.md for separately installed Qt/PySide6 dependencies.\n', 0o644)
    dependencies = ', '.join(['python3 (>= 3.10)', 'python3-pyside6.qtcore (>= 6.8)',
        'python3-pyside6.qtgui (>= 6.8)', 'python3-pyside6.qtwidgets (>= 6.8)',
        'python3-pyside6.qtnetwork (>= 6.8)', 'python3-pyside6.qtsvg (>= 6.8)', 'tzdata', 'tesseract-ocr', 'tesseract-ocr-eng'])
    control = f'''Package: klip
Version: {version}
Section: graphics
Priority: optional
Architecture: all
Maintainer: Manish <workwithmanish@users.noreply.github.com>
Depends: {dependencies}
Recommends: xfconf
Suggests: tesseract-ocr-hin
Installed-Size: {sum(len(data) for data, _ in files.values())//1024+1}
Homepage: https://github.com/workwithmanish/klip
Description: Screenshot capture and annotation tool for X11 desktops
 Select and resize capture regions, annotate images, and export captures.
 Includes configurable XFCE shortcuts and local-time timestamp watermarks.
 Wayland capture is not currently supported.
'''.encode()
    sums = ''.join(hashlib.md5(data).hexdigest()+'  '+name+'\n' for name, (data, _) in sorted(files.items())).encode()
    package = b'!<arch>\n'
    for name, data in [('debian-binary', b'2.0\n'), ('control.tar.gz', archive({'control': (control, 0o644), 'md5sums': (sums, 0o644)})), ('data.tar.gz', archive(files))]:
        package += ar_member(name, data)
    output.mkdir(parents=True, exist_ok=True)
    destination = output/f'klip_{version}_all.deb'
    destination.write_bytes(package)
    destination.with_suffix('.deb.sha256').write_text(hashlib.sha256(package).hexdigest()+'  '+destination.name+'\n')
    print(destination)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', default='0.2.1')
    parser.add_argument('--output', type=Path, default=ROOT/'dist')
    args = parser.parse_args()
    build(args.version, args.output)
