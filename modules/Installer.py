from PyQt5.QtCore import *
import traceback
import sys
import time
import os
import shutil
from subprocess import Popen, PIPE, STDOUT
import getpass
from distutils.dir_util import copy_tree


class WorkerSignals(QObject):
    start = pyqtSignal()
    finished = pyqtSignal()
    manualExit = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(str)
    abort = pyqtSignal()


class Installer(QObject):
    """
    REF: https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, install_destination_folder, source_app_files_folder, appName, *args, **kwargs):
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

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        try:
            self.updateLogBox("Starting Installation Process...")
            self.signals.start.emit()
            self.create_folder_in_install_driectory(self.install_destination_folder)
            if self.running:
                self.copy_files_to_install_dir(self.source_app_files_folder, self.install_destination_folder,)
            # self.addShortcuts()
            # self.change_folder_permissions(install_folder)
            if self.running:
                self.updateLogBox("Done!")
                self.signals.finished.emit()
            else:
                self.signals.abort.emit()
        except:
            self.updateLogBox(str(traceback.format_exc()))
            self.stop()

    def stop(self):
        self.running = False
        self.signals.manualExit.emit()

    def updateLogBox(self, data):
        print(str(data))
        self.signals.progress.emit(data)

    def create_folder_in_install_driectory(self, path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
                time.sleep(2)  # wait for folder to be removed
        except:
            self.updateLogBox("Could not delete old destination folder -> " + str(path) + "\n Try running as admin or manually deleting the directory.")
            self.updateLogBox(str(traceback.format_exc()))
            self.stop()
            return

        try:
            os.makedirs(path, mode=0o777, exist_ok=False)
        except:
            self.updateLogBox("Could not create destination folder -> " + str(path) + "\n Try running as admin or manually creating the directory.")
            self.updateLogBox(str(traceback.format_exc()))
            self.stop()
            return

        try:
            os.chmod(path, 0o777)
        except:
            self.updateLogBox(str(traceback.format_exc()))
            self.stop()
            return

        try:
            self.change_folder_permissions_windows(path)
        except:
            self.updateLogBox("Could not update folder permissions for Windows.")
            self.updateLogBox(str(traceback.format_exc()))
            self.stop()
            return

        self.updateLogBox("Created Install Folder -> " + str(path))

    def change_folder_permissions_windows(self, path):
        command = "ICACLS \"%s\" /GRANT Everyone:(OI)(CI)F" % (str(path))
        p = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)


    def copy_files_to_install_dir(self, src, dest):
        self.updateLogBox("\nCopying files to install directory...")
        self.updateLogBox(src+" -> "+dest+"\n")
        try:
            copy_tree(src, dest)
        except:
            self.updateLogBox("Could not copy files!")
            self.updateLogBox(str(traceback.format_exc()))
            self.stop()

    # def addShortcuts():
    #     print("Adding Shortcuts")
    #     if addDesktopShortcut:
    #         try:
    #             print('Creating Desktop Shortcut...')
    #             updateLogBox('Creating Desktop Shortcut...')
    #
    #             desktop = winshell.desktop()
    #             path = os.path.join(desktop, "%s.lnk" % appname)
    #             target = os.path.join(defaultInstallDirectory, appname, exe)
    #             wDir = os.path.join(defaultInstallDirectory, appname)
    #             icon = os.path.join(defaultInstallDirectory, appname, icon_directory)
    #
    #             shell = Dispatch('WScript.Shell')
    #             shortcut = shell.CreateShortCut(path)
    #             shortcut.Targetpath = target
    #             shortcut.WorkingDirectory = wDir
    #             shortcut.IconLocation = icon
    #             shortcut.save()
    #             print("Desktop Shortcut Created Successfully")
    #             updateLogBox("Desktop Shortcut Created Successfully")
    #         except Exception as ex:
    #             print(str(traceback.format_exc()))
    #             updateLogBox(str(traceback.format_exc()))
    #     if addStartMenuEntry:
    #         print('Creating Start Menu Shortcut...')
    #         try:
    #             print('Creating StartMenu Entry...')
    #             updateLogBox('Creating StartMenu Entry...')
    #             start_menu = winshell.start_menu()
    #             print(start_menu)
    #             path = os.path.join(start_menu, "%s.lnk" % appname)
    #             target = os.path.join(defaultInstallDirectory, appname, exe)
    #             wDir = os.path.join(defaultInstallDirectory, appname)
    #             icon = os.path.join(defaultInstallDirectory, appname, icon_directory)
    #             print('-------------', start_menu, path, target, wDir, icon)
    #             shell = Dispatch('WScript.Shell')
    #             shortcut = shell.CreateShortCut(path)
    #             shortcut.Targetpath = target
    #             shortcut.WorkingDirectory = wDir
    #             shortcut.IconLocation = icon
    #             shortcut.save()
    #             print("StartMenu Entry Created Successfully")
    #             updateLogBox("StartMenu Entry Created Successfully")
    #         except Exception as ex:
    #             print(str(traceback.format_exc()))
    #             updateLogBox(str(traceback.format_exc()))
