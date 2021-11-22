import os
import sys
from collections import namedtuple

UserFolders = namedtuple("UserFolders", ("home", "desktop", "startmenu"))

platform = sys.platform


if os.name == "nt":
    platform = "win"
if platform == "linux2":
    platform = "linux"

if platform.startswith('win'):
    pass

elif platform.startswith('darwin'):
    pass
else:
    pass


#!/usr/bin/env python
import os
import sys
from collections import namedtuple



Shortcut = namedtuple("Shortcut", ('name', 'description', 'icon', 'target',
                                   'script', 'full_script', 'arguments',
                                   'desktop_dir', 'startmenu_dir'))

def shortcut(script, userfolders, scut_ext, ico_ext, name=None, description=None, folder=None, icon=None):
    if not isinstance(script, str) or len(script) < 1:
        raise ValueError("`script` for shortcut must be a non-zero length string")

    words = script.split(' ', 1)
    if len(words) < 2:
        words.append('')

    return Shortcut(name, description, icon, target, script, full_script,
                    arguments, desktop_dir, startmenu_dir)


make_shortcut(script=r'C:\Users\indri\OpenVPN\log\client_.log',terminal=True, startmenu=True, desktop=True, executable=None)
