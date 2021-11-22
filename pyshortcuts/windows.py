#!/usr/bin/env python
"""
Create desktop shortcuts for Windows
"""
import os
import sys
import time
from shortcut import shortcut
from collections import namedtuple
import win32com.client
from win32com.shell import shell, shellcon
UserFolders = namedtuple("UserFolders", ("home", "desktop", "startmenu"))



scut_ext = 'lnk'
ico_ext = ('ico',)

_WSHELL = win32com.client.Dispatch("Wscript.Shell")

# Windows Special Folders
# see: https://docs.microsoft.com/en-us/windows/win32/shell/csidl
def get_homedir():
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None, 0)


def get_desktop():
    return shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)


def get_startmenu():
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0)


def get_folders():
    return UserFolders(get_homedir(), get_desktop(), get_startmenu())

def make_shortcut(script, name=None, description=None, icon=None,
                  folder=None, terminal=True, desktop=True,
                  startmenu=True, executable=None):
    ''''
    script      (str) path to script, may include command-line arguments
    name        (str, None) name to display for shortcut [name of script]
    description (str, None) longer description of script [`name`]
    icon        (str, None) path to icon file [python icon]
    folder      (str, None) subfolder of Desktop for shortcut [None] (See Note 1)
    terminal    (bool) whether to run in a Terminal [True]
    desktop     (bool) whether to add shortcut to Desktop [True]
    startmenu   (bool) whether to add shortcut to Start Menu [True] (See Note 2)
    executable  (str, None) name of executable to use [this Python] (see Note 3)

     `folder` will place shortcut in a subfolder of Desktop and/or Start Menu
     Start Menu does not exist for Darwin / MacOSX
    '''

    userfolders = get_folders()

    shortcut_ = shortcut(script, userfolders, scut_ext=scut_ext, ico_ext=ico_ext, name=name, description=description, folder=folder, icon=icon)

    for (create, folder) in ((desktop, shortcut_.desktop_dir),
                             (startmenu, shortcut_.startmenu_dir)):
        if create:
            if not os.path.exists(folder):
                os.makedirs(folder)
            dest = os.path.join(folder, shortcut_.target)

            wscript = _WSHELL.CreateShortCut(dest)
            wscript.Targetpath = '"%s"' % script
            # wscript.Arguments = ar
            wscript.WorkingDirectory = userfolders.home
            wscript.WindowStyle = 0
            wscript.Description = shortcut_.description
            wscript.IconLocation = shortcut_.icon
            wscript.save()

    return shortcut_
