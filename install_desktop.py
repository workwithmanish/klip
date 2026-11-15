"""Install a per-user Linux application launcher using this Python environment."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


def desktop_quote(value):
    value = str(value).replace('%', '%%')
    for char in ('\\', '"', '`', '$'):
        value = value.replace(char, '\\'+char)
    return ('"'+value+'"').replace('\\', '\\\\')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--remove', action='store_true', help='Remove the menu launcher only')
    args = parser.parse_args()
    if sys.platform != 'linux':
        parser.error('Run this installer inside your Linux desktop session.')
    data = Path(os.environ.get('XDG_DATA_HOME', str(Path.home()/'.local/share')))
    applications = data/'applications'
    target = applications/'klip.desktop'
    if args.remove:
        target.unlink(missing_ok=True)
        print('Klip menu launcher removed. Project and settings were preserved.')
        return
    source = Path(__file__).absolute().parent
    script = source/'klip.py'
    if not script.is_file():
        parser.error('klip.py is missing from the installer directory.')
    try:
        from PySide6 import QtCore, QtWidgets, QtNetwork
    except ImportError:
        parser.error('Run using the Klip virtual environment Python after installing requirements.txt.')
    icon_dir = data/'icons/hicolor/scalable/apps'
    icon_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source/'assets/klip.svg', icon_dir/'klip.svg')
    command = desktop_quote(sys.executable)+' '+desktop_quote(script)
    applications.mkdir(parents=True, exist_ok=True)
    target.write_text('[Desktop Entry]\nVersion=1.0\nType=Application\nName=Klip\nGenericName=Screenshot Tool\nComment=Capture and annotate your screen\nExec='+command+' --background\nIcon=klip\nTerminal=false\nCategories=Graphics;Utility;\nKeywords=screenshot;capture;annotation;clip;\nStartupNotify=false\nActions=Capture;Settings;\n\n[Desktop Action Capture]\nName=Capture area\nExec='+command+' --capture\n\n[Desktop Action Settings]\nName=Klip settings\nExec='+command+' --settings\n', encoding='utf-8')
    if shutil.which('update-desktop-database'):
        subprocess.run(['update-desktop-database', str(applications)], check=False)
    print('Installed: '+str(target))
    print('Search for Klip in your application menu. It starts in the tray without a terminal.')
    print('Keep the project folder and Python environment at their current paths.')


if __name__ == '__main__':
    main()
