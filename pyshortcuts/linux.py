#!/usr/bin/env python
"""
Create desktop shortcuts for Linux
"""
import os
import sys
from shortcut import shortcut
from collections import namedtuple
UserFolders = namedtuple("UserFolders", ("home", "desktop", "startmenu"))

scut_ext = 'desktop'
ico_ext = ('ico', 'svg', 'png')

DESKTOP_FORM = """[Desktop Entry]
Name={name:s}
Type=Application
Comment={desc:s}
Terminal={term:s}
Icon={icon:s}
Exec={exe:s} {script:s} {args:s}
"""

_HOME = None
def get_homedir():
    global _HOME
    if _HOME is not None:
        return _HOME

    home = None
    try:
        from pathlib import Path  #  Py3.5+
        home = str(Path.home())
    except:
        pass

    if home is None:
        home = os.path.expanduser("~")
    if home is None:
        home = os.environ.get("HOME", os.path.abspath("."))
    _HOME = home
    return home

def get_desktop():
    homedir = get_homedir()
    desktop = os.path.join(homedir, 'Desktop')

    # search for .config/user-dirs.dirs in HOMEDIR
    ud_file = os.path.join(homedir, '.config', 'user-dirs.dirs')
    if os.path.exists(ud_file):
        val = desktop
        with open(ud_file, 'r') as fh:
            text = fh.readlines()
        for line in text:
            if 'DESKTOP' in line:
                line = line.replace('$HOME', homedir)[:-1]
                key, val = line.split('=')
                val = val.replace('"', '').replace("'", "")
        desktop = val
    return desktop

def get_startmenu():
    homedir = get_homedir()
    return os.path.join(homedir, '.local', 'share', 'applications')

def get_folders():
    return UserFolders(get_homedir(), get_desktop(), get_startmenu())


def make_shortcut(script, name=None, description=None, icon=None,
                  folder=None, terminal=True, desktop=True,
                  startmenu=True, executable=None):

    userfolders = get_folders()
    scut = shortcut(script, userfolders, scut_ext=scut_ext, ico_ext=ico_ext, name=name, description=description,
                    folder=folder, icon=icon)


    text = DESKTOP_FORM.format(name=scut.name, desc=scut.description,
                               exe=executable, icon=scut.icon,
                               script=scut.full_script, args=scut.arguments,
                               term='true' if terminal else 'false')

    for (create, folder) in ((desktop, scut.desktop_dir),
                             (startmenu, scut.startmenu_dir)):
        if create:
            if not os.path.exists(folder):
                os.makedirs(folder)
            dest = os.path.join(folder, scut.target)
            with open(dest, 'w') as fout:
                fout.write(text)
            os.chmod(dest, 493) ## = octal 755 / rwxr-xr-x
    return scut
