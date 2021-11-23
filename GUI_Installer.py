from modules.InstallerMainWindow import InstallerMainWindow
from modules.AlertWindow import AppAlreadyRunning
from modules.Installer import Installer
from elevate import elevate
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
import traceback
import platform
import logging
import sys
import os


# noinspection PyBroadException
# exceptions are handled by traceback in order to get the whole error stack
def start_installation():
    try:
        window.thread = QThread()
        window.installer = Installer(app_name=config.app_name, source_app_files_folder=source_app_files_folder, exe_folder=config.exe_folder, exe_path=config.exe_path,
                                     icon_path=config.icon_path,
                                     install_destination_folder=window.default_install_dir, add_desktop_shortcut=window.add_desktop_shortcut,
                                     add_start_menu_entry=window.add_start_menu_entry,
                                     start_on_boot=window.start_on_boot, launch_after_install=window.launch_after_install)  # Any other args, kwargs are passed to the run function
        window.installer.moveToThread(window.thread)
        window.thread.started.connect(window.installer.run)

        window.installer.signals.progress.connect(update_from_installer)
        window.installer.signals.start.connect(started_successfully)
        window.installer.signals.manualExit.connect(installation_cancelled)
        window.installer.signals.finished.connect(finished_successfully)
        window.installer.signals.abort.connect(installation_cancelled)

        window.cancelButton.clicked.connect(lambda x: window.installer.stop())
        window.thread.start()
    except:
        logging.error(traceback.format_exc())
        installation_cancelled()


def update_from_installer(data):
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


BAD_FILECHARS = ';~,`!%$@$&^?*#:"/|\'\\\t\r\n(){}[]<>'
GOOD_FILECHARS = '_' * len(BAD_FILECHARS)


def fix_filename(s):
    t = str(s).translate(str.maketrans(BAD_FILECHARS, GOOD_FILECHARS))
    if t.count('.') > 1:
        for i in range(t.count('.') - 1):
            idot = t.find('.')
            t = "%s_%s" % (t[:idot], t[idot + 1:])
    return t


def check_paths():
    config.exe_path = os.path.normpath(config.exe_path)
    config.exe_folder = os.path.normpath(config.exe_folder)
    config.icon_path = os.path.normpath(config.icon_path)
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
    return os.path.normpath(default_install_dir)


def check_config():
    check_paths()
    config.app_name = fix_filename(config.app_name)
    config.default_install_dir = set_default_installation_path()
    if config.installer_app_name is None:
        config.installer_app_name = config.app_name + " Installer"


def set_logging():
    logging.basicConfig(filename=config.logfile, filemode='a+', format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


def set_app_path():
    if getattr(sys, 'frozen', False):
        # running in executable mode
        app_dir = sys._MEIPASS
    else:
        # running in a normal Python environment
        app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    return app_dir


class Config:
    def __init__(self):
        self.app_name = "MyApp"  # name of app
        # copy all the files of your app into the AppFiles folder of this project, the following are relative paths to that folder
        self.exe_folder = ""  # folder where the executable is located (working directory) leave empty if the same. Please do not pass a full(absolute) path
        self.exe_path = "AutoShoot Bot.exe"  # relative path to the executable
        self.icon_path = "style/icon.ico"  # relative path to the icon (recommended to be an .ico file)

        self.x64 = True  # set this to true if your app is 64 bit (this will affect only windows installation dir)
        self.installer_app_name = None  # set this to the name of this installer, if none it will automatically be app_name+"Installer"

        # default installation directories
        self.linux_default_install_dir = "/usr/local/bin"
        self.x32win_default_install_dir = "C:/Program Files (x86)/"
        self.x62win_default_install_dir = "C:/Program Files/"
        self.macOs_default_install_dir = "/usr/local/bin"

        # use these to set which checkboxes are shown and their default value
        self.add_desktop_shortcut_default_value = True
        self.show_add_desktop_shortcut_checkbox = True

        self.add_start_menu_entry_default_value = True
        self.show_add_start_menu_entry_checkbox = True

        self.start_on_boot_default_value = True
        self.show_start_on_boot_checkbox = True

        # set if you want to launch the app after installing it
        self.launch_after_install = True

    logfile = "log.log"

    def __str__(self):
        s = "\n"
        for var in vars(self):
            s += var + ":" + str(getattr(self, var)) + "\n"
        return s


if __name__ == '__main__':
    elevate()
    config = Config()
    # noinspection PyBroadException
    try:
        set_logging()
        set_app_path()
        source_app_files_folder = "AppFiles"
        check_config()
        logging.info(config)
        logging.info("default_install_dir:" + config.default_install_dir)

        app = QtWidgets.QApplication(sys.argv)
        if 0:  # not implemented will probably be removed since it is not necessary
            print('............App Already Running............')
            window = AppAlreadyRunning(installer_app_name=config.app_name, alertMessage="App Already Running!", working_directory=os.getcwd())
        else:
            window = InstallerMainWindow(default_install_dir=config.default_install_dir, installer_app_name=config.installer_app_name,
                                         add_desktop_shortcut=config.add_desktop_shortcut_default_value, show_add_desktop_shortcut_checkbox=config.show_add_desktop_shortcut_checkbox,
                                         add_start_menu_entry=config.add_start_menu_entry_default_value, show_add_start_menu_entry_checkbox=config.show_add_start_menu_entry_checkbox,
                                         start_on_boot=config.start_on_boot_default_value, show_start_on_boot_checkbox=config.show_start_on_boot_checkbox,
                                         launch_after_install=config.launch_after_install,
                                         working_directory=os.getcwd())

            window.installButton.clicked.connect(start_installation)
        app.exec_()
    except:
        logging.error(traceback.format_exc())
