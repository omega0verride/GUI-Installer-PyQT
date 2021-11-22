import os
import sys
import traceback

platform = sys.platform

if os.name == "nt":
    platform = "win"
if platform == "linux2":
    platform = "linux"

if platform.startswith('win'):
    import winshell
    from win32com.client import Dispatch
    from win32com.shell import shell, shellcon
elif platform.startswith('darwin'):
    pass
else:
    pass


def add_win_shortcuts(addDesktopShortcut, addStartMenuEntry, appname, exe_path, exe_folder, icon_path):
    shell_ = Dispatch('WScript.Shell')
    shortcuts = []
    if addDesktopShortcut:
        Desktop = {"type": "Desktop", "shortcut": shell_.CreateShortCut(os.path.join(winshell.desktop(), "%s.lnk" % appname))}
        shortcuts.append(Desktop)
    if addStartMenuEntry:
        StartMenu = {"type": "Start Menu", "shortcut": shell_.CreateShortCut(os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0), "%s.lnk" % appname))}
        shortcuts.append(StartMenu)

    for s in shortcuts:
        try:
            print('Creating ' + s['type'] + ' Shortcut ')
            # updateLogBox('Creating '+s['type']+' Shortcut ')
            # sterelize appname first
            shortcut = s['shortcut']
            shortcut.WindowStyle = 0
            shortcut.Description = appname
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = exe_folder
            shortcut.IconLocation = icon_path
            shortcut.save()
            print(s['type'] + ' Shortcut Created Successfully')
            s.clear()
            shortcuts.remove(s)
            # updateLogBox(s['type']+' Shortcut Created Successfully')
        except Exception as ex:
            print(str(traceback.format_exc()))
            # updateLogBox(str(traceback.format_exc()))


add_win_shortcuts(1, 1, "test", r"C:\Program Files\atest1\AutoShoot Bot.exe", r"C:\Program Files\atest1", r"C:\Program Files\atest1\icon.ico")
