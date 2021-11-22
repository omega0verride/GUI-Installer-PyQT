import os
import sys
import traceback

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from modules.AlertWindow import AppAlreadyRunning
from modules.InstallerMainWindow import *
from modules.Installer import Installer
from threading import Thread
from elevate import elevate
import time


def progress_fn(data):
    print(data)
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


# noinspection PyBroadException
def startInstallation():
    print("Start Installer Thread")
    try:
        window.thread = QThread()
        window.installer = Installer("C:\Program Files\\atest", r"C:\Program Files\AutoShoot Bot", "test")  # Any other args, kwargs are passed to the run function
        window.installer.moveToThread(window.thread)
        window.thread.started.connect(window.installer.run)

        window.installer.signals.progress.connect(progress_fn)
        window.installer.signals.start.connect(started_successfully)
        window.installer.signals.manualExit.connect(installation_cancelled)
        window.installer.signals.finished.connect(finished_successfully)
        window.installer.signals.abort.connect(installation_cancelled)

        window.cancelButton.clicked.connect(lambda x: window.installer.stop())
        window.thread.start()
    except:
        print(traceback.format_exc())
        installation_cancelled()


BAD_FILECHARS = ';~,`!%$@$&^?*#:"/|\'\\\t\r\n(){}[]<>'
GOOD_FILECHARS = '_'*len(BAD_FILECHARS)

def fix_filename(s):
    t = str(s).translate(str.maketrans(BAD_FILECHARS, GOOD_FILECHARS))
    if t.count('.') > 1:
        for i in range(t.count('.') - 1):
            idot = t.find('.')
            t = "%s_%s" % (t[:idot], t[idot+1:])
    return t


if __name__ == '__main__':
    elevate()
    working_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(working_directory)
    print(working_directory)

    app = QtWidgets.QApplication(sys.argv)
    if 0:
        print('............App Already Running............')
        window = AppAlreadyRunning(working_directory=working_directory, installer_appName="Installer", alertMessage="App Already Running!")
    else:
        window = InstallerMainWindow(working_directory=working_directory, defaultInstallDirectory='C:/Program Files (x86)/', installer_appName="test", addStartMenuEntry=1,
                                     addDesktopShortcut=1)
        window.installButton.clicked.connect(startInstallation)
    app.exec_()
