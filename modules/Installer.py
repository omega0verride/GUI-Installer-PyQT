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
    def __init__(self, app_name, source_app_files_folder, exe_folder, exe_path, icon_path, install_destination_folder, add_desktop_shortcut, add_start_menu_entry, start_on_boot, launch_after_install):
        super(Installer, self).__init__()
        self.signals = WorkerSignals()
        self.running = 1
        self.install_destination_folder = os.path.join(install_destination_folder, app_name)
        self.source_app_files_folder = source_app_files_folder
        self.app_name = app_name
        self.add_desktop_shortcut = add_desktop_shortcut
        self.add_start_menu_entry = add_start_menu_entry
        self.start_on_boot = start_on_boot
        self.launch_after_install = launch_after_install

        self.exe_path = os.path.join(self.install_destination_folder, exe_path)
        self.exe_folder = os.path.join(self.install_destination_folder, exe_folder)
        self.icon_path = os.path.join(self.install_destination_folder, icon_path)

    @pyqtSlot()
    def run(self):
        try:
            self.updateLogBox("Starting Installation Process...")
            log.info("Starting Installation Process...")
            self.signals.start.emit()
            self.create_folder_in_install_directory(self.install_destination_folder)
            if self.running:
                self.copy_files_to_install_dir(self.source_app_files_folder, self.install_destination_folder, )
            if self.running:
                self.addShortcuts()  # these are not crucial for the installation so we can continue even if they fail.
                if self.start_on_boot:  # ..
                    self.addToBoot()  # ..
                self.updateLogBox("\nDone!")
                log.info("\nDone!")
                if self.launch_after_install:
                    try:
                        Popen(self.exe_path, cwd=self.exe_folder)
                    except:
                        self.updateLogBox("Could not start the app Automatically. Try starting it manually or check if there is any issue with the app itself.")
                        logging.error(traceback.format_exc())
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

    def create_folder_in_install_directory(self, path):
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

        if platform.system().lower() == 'windows':
            try:
                self.updateLogBox("\nChanging folder permissions for Windows.")
                log.info("Changing folder permissions for Windows.")
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
        self.updateLogBox(src + " -> " + dest + "\n")
        log.info(src + " -> " + dest + "\n")
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
        if self.add_desktop_shortcut:
            Desktop = {"type": "Desktop", "shortcut": shell_.CreateShortCut(os.path.join(winshell.desktop(), "%s.lnk" % self.app_name))}
            shortcuts.append(Desktop)
        if self.add_start_menu_entry:
            StartMenu = {"type": "Start Menu", "shortcut": shell_.CreateShortCut(os.path.join(shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0), "%s.lnk" % self.app_name))}
            shortcuts.append(StartMenu)
        for s in shortcuts:
            try:
                self.updateLogBox('\nCreating ' + s['type'] + ' Shortcut ')
                log.info('\nCreating ' + s['type'] + ' Shortcut ')
                shortcut = s['shortcut']
                shortcut.WindowStyle = 0
                shortcut.Description = self.app_name
                shortcut.Targetpath = self.exe_path
                shortcut.WorkingDirectory = self.exe_folder
                shortcut.IconLocation = self.icon_path
                shortcut.save()
                self.updateLogBox(s['type'] + ' Shortcut Created Successfully')
                log.info(s['type'] + ' Shortcut Created Successfully')
                s.clear()
            except:
                self.updateLogBox('Could not create ' + s['type'] + ' Shortcut. Ignoring.')
                log.info(traceback.format_exc())

    def add_linux_shortcuts(self):
        pass

    def add_mac_shortcuts(self):
        pass

    def addToBoot(self):
        system = platform.system().lower()
        if system == 'windows':
            self.win_add_to_Startup()
        elif system == 'linux':
            self.linux_add_to_Startup()
        elif system == 'darwin':
            self.mac_add_to_Startup()

    def win_add_to_Startup(self):
        try:
            import winshell
            from win32com.client import Dispatch
            from win32com.shell import shell, shellcon
            shell_ = Dispatch('WScript.Shell')
            path=os.path.join(self.exe_folder, "%s.lnk" % self.app_name)
            shortcut = shell_.CreateShortCut(path)
            self.updateLogBox('\nCreating Startup Shortcut ')
            log.info('\nCreating Startup Shortcut ')
            shortcut.WindowStyle = 0
            shortcut.Description = self.app_name
            shortcut.Targetpath = self.exe_path
            shortcut.WorkingDirectory = self.exe_folder
            shortcut.IconLocation = self.icon_path
            shortcut.save()
            # to remove the shortcut from the app itself you would have to delete this key
            Popen(r'reg.exe add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "{}" /t REG_SZ /f /d "\"{}\""'.format(self.app_name, path))
            self.updateLogBox('Startup Shortcut Created Successfully')
            log.info('Startup Shortcut Created Successfully')
        except:
            self.updateLogBox('Could not create Startup Shortcut. Ignoring.')
            log.info(traceback.format_exc())

    def linux_add_to_Startup(self):
        pass

    def mac_add_to_Startup(self):
        pass
