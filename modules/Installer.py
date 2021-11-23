from PyQt5.QtCore import *
import traceback
import time
import os
import shutil
from subprocess import Popen, PIPE, STDOUT
from distutils.dir_util import copy_tree
import platform
import logging
log = logging.getLogger(__name__)

class WorkerSignals(QObject):
    start = pyqtSignal()
    finished = pyqtSignal()
    manualExit = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(str)
    abort = pyqtSignal()


class Installer(QObject):
    def __init__(self, appName, source_app_files_folder,  exe_folder, exe_path, icon_path, install_destination_folder, addDesktopShortcut, addStartMenuEntry, startOnBoot, launchAfterInstall, *args, **kwargs):
        super(Installer, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
        self.running = 1
        self.install_destination_folder = install_destination_folder
        self.source_app_files_folder = source_app_files_folder
        self.appName = appName
        self.addDesktopShortcut = addDesktopShortcut
        self.addStartMenuEntry = addStartMenuEntry
        self.startOnBoot = startOnBoot
        self.launchAfterInstall = launchAfterInstall

        self.exe_path = exe_path
        self.exe_folder = exe_folder
        self.icon_path = icon_path

    @pyqtSlot()
    def run(self):
        try:
            self.updateLogBox("Starting Installation Process...")
            log.info("Starting Installation Process...")
            self.signals.start.emit()
            self.create_folder_in_install_driectory(self.install_destination_folder)
            if self.running:
                self.copy_files_to_install_dir(self.source_app_files_folder, self.install_destination_folder,)
            if self.running:
                self.addShortcuts()   # these are not crucial for the installation so we can continue even if they fail.
                if self.startOnBoot:  # ..
                    self.addToBoot()  # ..
                self.updateLogBox("\nDone!")
                log.info("\nDone!")
                if self.launchAfterInstall:
                    Popen(self.exe_path,  cwd=self.exe_folder)
                self.signals.finished.emit()
            else:
                self.signals.abort.emit()
        except:
            log.error(traceback.format_exc())
            self.updateLogBox(traceback.format_exc())
            self.stop()

    def stop(self):
        self.running = False
        self.signals.manualExit.emit()

    def updateLogBox(self, data):
        self.signals.progress.emit(str(data))

    def create_folder_in_install_driectory(self, path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                time.sleep(2)  # wait for folder to be removed
        except:
            self.updateLogBox("Could not delete old destination folder -> " + str(path) + "\n Try running as admin or manually deleting the directory.")
            log.info(traceback.format_exc())
            self.stop()
            return

        try:
            os.makedirs(path, mode=0o777, exist_ok=False)
        except:
            self.updateLogBox("Could not create destination folder -> " + str(path) + "\n Try running as admin or manually creating the directory.")
            log.info(traceback.format_exc())
            self.stop()
            return

        try:
            os.chmod(path, 0o777)
        except:
            self.updateLogBox("Could not modify folder permission. chmod 777 " + str(path) + "\n Try running as admin or manually creating the directory.")
            log.error(traceback.format_exc())
            self.stop()
            return

        if platform.system().lower()== 'windows':
            try:
                self.change_folder_permissions_windows(path)
            except:
                self.updateLogBox("Could not update folder permissions for Windows.")
                log.error(traceback.format_exc())
                self.stop()
                return

        self.updateLogBox("Created Install Folder -> " + str(path))
        log.info("Created Install Folder -> " + str(path))

    def change_folder_permissions_windows(self, path):
        command = "ICACLS \"%s\" /GRANT Everyone:(OI)(CI)F" % (str(path))
        p = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)


    def copy_files_to_install_dir(self, src, dest):
        self.updateLogBox("\nCopying files to install directory...")
        log.info("\nCopying files to install directory...")
        self.updateLogBox(src+" -> "+dest+"\n")
        log.info(src+" -> "+dest+"\n")
        try:
            copy_tree(src, dest)
        except:
            self.updateLogBox("Could not copy files! Try running as admin.")
            log.error(traceback.format_exc())
            self.stop()

    def addShortcuts(self):
        system = platform.system().lower()
        if system == 'windows':
            self.add_win_shortcuts()
        elif system == 'linux':
            self.add_linux_shortcuts()
        elif system == 'darwin':
            self.add_mac_shortcuts()

    def add_win_shortcuts(self):
        import winshell
        from win32com.client import Dispatch
        from win32com.shell import shell, shellcon
        shell_ = Dispatch('WScript.Shell')
        shortcuts = []
        if self.addDesktopShortcut:
            Desktop = {"type": "Desktop", "shortcut": shell_.CreateShortCut(os.path.join(winshell.desktop(), "%s.lnk" % self.appName))}
            shortcuts.append(Desktop)
        if self.addStartMenuEntry:
            StartMenu = {"type": "Start Menu", "shortcut": shell_.CreateShortCut(os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0), "%s.lnk" % self.appName))}
            shortcuts.append(StartMenu)
        for s in shortcuts:
            try:
                self.updateLogBox('\nCreating '+s['type']+' Shortcut ')
                log.info('\nCreating '+s['type']+' Shortcut ')
                shortcut = s['shortcut']
                shortcut.WindowStyle = 0
                shortcut.Description = self.appName
                shortcut.Targetpath = self.exe_path
                shortcut.WorkingDirectory = self.exe_folder
                shortcut.IconLocation = self.icon_path
                shortcut.save()
                self.updateLogBox(s['type']+' Shortcut Created Successfully')
                log.info(s['type']+' Shortcut Created Successfully')
                s.clear()
            except:
                self.updateLogBox('Could not create '+s['type']+' Shortcut. Ignoring.')
                log.info(traceback.format_exc())

    def add_linux_shortcuts(self):
        pass
    def add_mac_shortcuts(self):
        pass

    def addToBoot(self):
        pass