#!/usr/bin/env python

__version__ = '1.8.0'
__data__ = '2020-Dec-09'

import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from collections import namedtuple

UserFolders = namedtuple("UserFolders", ("home", "desktop", "startmenu"))

platform = sys.platform


if os.name == "nt":
    platform = "win"
if platform == "linux2":
    platform = "linux"

from linux import (scut_ext, ico_ext, make_shortcut,
                    get_folders, get_homedir, get_desktop)

if platform.startswith('win'):
    from windows import (scut_ext, ico_ext, make_shortcut,
                          get_folders, get_homedir, get_desktop)

elif platform.startswith('darwin'):
    from darwin import (scut_ext, ico_ext, make_shortcut,
                         get_folders, get_homedir, get_desktop)

from shortcut import shortcut, Shortcut, fix_filename

make_shortcut(script=r'C:\Users\indri\OpenVPN\log\client_.log',terminal=True, startmenu=True, desktop=True, executable=None)

# make_shortcut(scriptname, name=args.name, description=desc,
#               terminal=args.terminal, folder=args.folder,
#               icon=args.icon, desktop=args.desktop,
#               startmenu=args.startmenu, executable=args.exe)
