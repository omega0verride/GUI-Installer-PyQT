import os
import sys
import traceback
from PyQt5.QtCore import *
from modules.AlertWindow import AppAlreadyRunning
from modules.InstallerMainWindow import *
from modules.Installer import Installer
import platform
import logging
from elevate import elevate


# noinspection PyBroadException
def startInstallation():
    try:
        window.thread = QThread()
        window.installer = Installer(appName=config.appName, source_app_files_folder=source_app_files_folder, exe_folder=config.exe_folder, exe_path=config.exe_path, icon_path=config.icon_path,
                                     install_destination_folder=window.defaultInstallDirectory, addDesktopShortcut=window.addDesktopShortcut, addStartMenuEntry=window.addStartMenuEntry,
                                     startOnBoot=window.startOnBoot, launchAfterInstall=window.launchAfterInstall)  # Any other args, kwargs are passed to the run function
        window.installer.moveToThread(window.thread)
        window.thread.started.connect(window.installer.run)

        window.installer.signals.progress.connect(updateFromInstaller)
        window.installer.signals.start.connect(started_successfully)
        window.installer.signals.manualExit.connect(installation_cancelled)
        window.installer.signals.finished.connect(finished_successfully)
        window.installer.signals.abort.connect(installation_cancelled)

        window.cancelButton.clicked.connect(lambda x: window.installer.stop())
        window.thread.start()
    except:
        logging.error(traceback.format_exc())
        installation_cancelled()


def updateFromInstaller(data):
    logging.info(data)
    window.updateLogBox(data)


def installation_cancelled():
    window.installerRunning = False
    window.thread.exit()
    window.installButton.setEnabled(1)
    window.cancelButton.hide()


def started_successfully():
    window.installerRunning = True
    window.installButton.setDisabled(True)  # disable the button to avoid starting new threads
    window.cancelButton.show()


def finished_successfully():
    installation_cancelled()
    window.installButton.hide()
    window.exitButton.show()


# installation process

BAD_FILECHARS = ';~,`!%$@$&^?*#:"/|\'\\\t\r\n(){}[]<>'
GOOD_FILECHARS = '_' * len(BAD_FILECHARS)


def fix_filename(s):
    t = str(s).translate(str.maketrans(BAD_FILECHARS, GOOD_FILECHARS))
    if t.count('.') > 1:
        for i in range(t.count('.') - 1):
            idot = t.find('.')
            t = "%s_%s" % (t[:idot], t[idot + 1:])
    return t


def set_app_path():
    if getattr(sys, 'frozen', False):
        # running in executable mode
        app_dir = sys._MEIPASS
    else:
        # running in a normal Python environment
        app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    return app_dir


def check_paths():
    if not os.path.exists(source_app_files_folder):
        raise Exception("Invalid app source folder. Make sure the AppFiles folder exists in the same directory as this script.")
        exit()

    if not os.path.exists(os.path.join(source_app_files_folder, config.exe_folder)):
        raise Exception(
            "Invalid exe_folder path. This folder represents the directory the exe should run on.  Make sure that you have placed it inside the AppFiles folder and that you have supplied the relative path i.e: myApp.exe or myFolder/folder2/myApp.exe (subdirectories of AppFiles)")
        exit()

    if not os.path.isfile(os.path.join(source_app_files_folder, config.exe_path)):
        raise Exception(
            "Invalid exe path. Make sure that you have placed it inside the AppFiles folder and that you have supplied the relative path i.e: myApp.exe or myFolder/folder2/myApp.exe (subdirectories of AppFiles)")
        exit()

    if not os.path.isfile(os.path.join(source_app_files_folder, config.icon_path)):
        raise Exception(
            "Invalid icon path. Make sure that you have placed it inside the AppFiles folder and that you have supplied the relative path i.e: myIcon.ico or myFolder/folder2/myIco.ico (subdirectories of AppFiles)")
        exit()

    if config.icon_path.rsplit(".", 1)[1] != 'ico':
        raise Warning("It is recommended to use .ico files to make sure the image is displayed on all systems. You can convert the file online.")


def set_default_installation_path():
    system = platform.system().lower()
    if system == 'windows':
        if config.x64:
            default_install_dir = config.x62win_default_install_dir
        else:
            default_install_dir = config.x32win_default_install_dir
    elif system == 'linux':
        default_install_dir = config.linux_default_install_dir
    elif system == 'darwin':
        default_install_dir = config.macOs_default_install_dir
    else:
        return "/"
    return default_install_dir


def setLogging():
    logging.basicConfig(filename=config.logfile, filemode='a+', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')



class Config:
    def __init__(self):
        self.appName = "installer"
        self.exe_folder = ""
        self.exe_path = "AutoShoot Bot.exe"
        self.icon_path = "style/icon.ico"
        self.addDesktopShortcut = True
        self.addStartMenuEntry = True
        self.startOnBoot = True

        self.launchAfterInstall = True
        self.x64 = True

        self.linux_default_install_dir = "/usr/local/bin"
        self.x32win_default_install_dir = "C:/Program Files (x86)/"
        self.x62win_default_install_dir = "C:/Program Files/"
        self.macOs_default_install_dir = "/usr/local/bin"

    logfile = "log.log"

    def __str__(self):
        s = "\n"
        for var in vars(self):
            s += var + ":" + str(getattr(self, var)) + "\n"
        return s


if __name__ == '__main__':

    # elevate()
    config = Config()
    try:
        setLogging()
        set_app_path()
        logging.info(config)
        source_app_files_folder = "AppFiles"
        check_paths()
        config.appName = fix_filename(config.appName)
        defaultInstallDirectory = set_default_installation_path()

        app = QtWidgets.QApplication(sys.argv)
        if 0:
            print('............App Already Running............')
            window = AppAlreadyRunning(installer_appName=config.appName, alertMessage="App Already Running!", working_directory=os.getcwd())
        else:
            window = InstallerMainWindow(defaultInstallDirectory=defaultInstallDirectory, installer_appName=config.appName, addStartMenuEntry=config.addStartMenuEntry,
                                         addDesktopShortcut=config.addDesktopShortcut, startOnBoot=config.startOnBoot, launchAfterInstall=config.launchAfterInstall,
                                         working_directory=os.getcwd())
            window.installButton.clicked.connect(startInstallation)
        app.exec_()
    except:
        logging.error(traceback.format_exc())
