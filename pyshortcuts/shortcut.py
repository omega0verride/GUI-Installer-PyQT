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
