#!/usr/bin/env python
"""
Create desktop shortcuts for Darwin / MacOS
"""
import os
import sys
import shutil

from shortcut import shortcut
from linux import get_homedir, get_desktop
from collections import namedtuple
UserFolders = namedtuple("UserFolders", ("home", "desktop", "startmenu"))

scut_ext = 'app'
ico_ext = ('icns',)

def get_startmenu():
    return ''

def get_folders():
    return UserFolders(get_homedir(), get_desktop(), get_startmenu())

def make_shortcut(script, name=None, description=None, icon=None,
                  folder=None, terminal=True, desktop=True,
                  startmenu=True, executable=None):

    if not desktop:
        return

    userfolders = get_folders()

    scut = shortcut(script, userfolders, scut_ext=scut_ext, ico_ext=ico_ext, name=name, description=description,
                    folder=folder, icon=icon)

    osascript = '%s %s' % (scut.full_script, scut.arguments)
    osascript = osascript.replace(' ', '\\ ')

    if not os.path.exists(scut.desktop_dir):
        os.makedirs(scut.desktop_dir)

    dest = os.path.join(scut.desktop_dir, scut.target)
    if os.path.exists(dest):
        shutil.rmtree(dest)

    os.mkdir(dest)
    os.mkdir(os.path.join(dest, 'Contents'))
    os.mkdir(os.path.join(dest, 'Contents', 'MacOS'))
    os.mkdir(os.path.join(dest, 'Contents', 'Resources'))

    opts = dict(name=scut.name,
                desc=scut.description,
                script=scut.full_script,
                args=scut.arguments,
                prefix=sys.prefix,
                exe=executable,
                osascript=osascript)

    info = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
  <key>CFBundleGetInfoString</key> <string>{desc:s}</string>
  <key>CFBundleName</key> <string>{name:s}</string>
  <key>CFBundleExecutable</key> <string>{name:s}</string>
  <key>CFBundleIconFile</key> <string>{name:s}</string>
  <key>CFBundlePackageType</key> <string>APPL</string>
  </dict>
</plist>
"""

    header = """#!/bin/bash
## Make sure to set PYTHONEXECUTABLE to Python that created this script
export PYTHONEXECUTABLE={prefix:s}/bin/python
export EXE={exe:s}
export SCRIPT={script:s}
export ARGS='{args:s}'
"""
    text = "$EXE $SCRIPT $ARGS"
    if terminal:
        text = """
osascript -e 'tell application "Terminal"
   do script "'${{EXE}}\ {osascript:s}'"
end tell
'
"""

    with open(os.path.join(dest, 'Contents', 'Info.plist'), 'w') as fout:
        fout.write(info.format(**opts))

    ascript_name = os.path.join(dest, 'Contents', 'MacOS', scut.name)
    with open(ascript_name, 'w') as fout:
        fout.write(header.format(**opts))
        fout.write(text.format(**opts))
        fout.write("\n")

    os.chmod(ascript_name, 493) ## = octal 755 / rwxr-xr-x
    icon_dest = os.path.join(dest, 'Contents', 'Resources', scut.name + '.icns')
    shutil.copy(scut.icon, icon_dest)
    return scut
