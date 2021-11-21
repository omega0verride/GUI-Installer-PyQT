import os
import sys
import time
import shutil
import psutil
import winshell
import subprocess
import getpass
from win32com.client import Dispatch
import pythoncom
from threading import Thread
from easysettings import EasySettings
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets, QtGui
from elevate import elevate
import traceback
from subprocess import Popen, PIPE, STDOUT
from modules.appAlreadyRunning import alertWindow



def installation_process():
    pythoncom.CoInitialize()

    def create_folder_in_install_driectory(install_folder):
        try:
            files_in_install_dir = os.listdir(defaultInstallDirectory)
            if len(files_in_install_dir) > 0:
                if appname in files_in_install_dir:
                    shutil.rmtree(install_folder)
            time.sleep(2)  # wait for folder to be removed
            os.mkdir(install_folder)
            print("Created Install Folder -> " + str(install_folder))
            updateLogBox("Created Install Folder -> " + str(install_folder))
        except Exception as e:
            print("---------------------------\nError: %s\n---------------------------\n" % str(e))
            updateLogBox("---------------------------\nError: %s\n---------------------------\n" % str(e))

    def change_folder_permissions(install_folder):
        try:
            command = "ICACLS \"%s\" /INHERITANCE:e /GRANT:r %s:(F) /T /C" % (
                str(install_folder), str(getpass.getuser()))
            p = Popen(command, stdout=PIPE,
                      stderr=STDOUT, shell=True)
        except Exception as e:
            print(e)
            updateLogBox(str(e))

    def copy_files_to_install_dir(app_files_folder, install_folder):
        updateLogBox("\nCopying files to install directory")
        print("\nCopying files to install directory")
        updateLogBox('----> ' + app_files_folder)
        updateLogBox('----> ' + install_folder)
        command = "xcopy \"%s\" \"%s\" /E/H/C/I" % (
            app_files_folder, install_folder)

        updateLogBox('\n')
        updateLogBox(command)
        print(command)
        p = Popen(command, stdout=PIPE,
                  stderr=STDOUT, shell=True)
        output = ''

        for line in p.stdout:
            output = output + str(line.decode()) + '\n'
            updateLogBox(str(line.decode()))

    def addShortcuts():
        print("Adding Shortcuts")
        if addDesktopShortcut:
            try:
                print('Creating Desktop Shortcut...')
                updateLogBox('Creating Desktop Shortcut...')

                desktop = winshell.desktop()
                path = os.path.join(desktop, "%s.lnk" % appname)
                target = os.path.join(defaultInstallDirectory, appname, exe)
                wDir = os.path.join(defaultInstallDirectory, appname)
                icon = os.path.join(defaultInstallDirectory, appname, icon_directory)

                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = wDir
                shortcut.IconLocation = icon
                shortcut.save()
                print("Desktop Shortcut Created Successfully")
                updateLogBox("Desktop Shortcut Created Successfully")
            except Exception as ex:
                print(str(traceback.format_exc()))
                updateLogBox(str(traceback.format_exc()))
        if addStartMenuEntry:
            print('Creating Start Menu Shortcut...')
            try:
                print('Creating StartMenu Entry...')
                updateLogBox('Creating StartMenu Entry...')
                start_menu = winshell.start_menu()
                print(start_menu)
                path = os.path.join(start_menu, "%s.lnk" % appname)
                target = os.path.join(defaultInstallDirectory, appname, exe)
                wDir = os.path.join(defaultInstallDirectory, appname)
                icon = os.path.join(defaultInstallDirectory, appname, icon_directory)
                print('-------------', start_menu, path, target, wDir, icon)
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(path)
                shortcut.Targetpath = target
                shortcut.WorkingDirectory = wDir
                shortcut.IconLocation = icon
                shortcut.save()
                print("StartMenu Entry Created Successfully")
                updateLogBox("StartMenu Entry Created Successfully")
            except Exception as ex:
                print(str(traceback.format_exc()))
                updateLogBox(str(traceback.format_exc()))

    while 1:
        try:
            time.sleep(0.1)
            global startInstallationProcess
            if startInstallationProcess:
                updateLogBox("Starting Installation Process...")
                print("Starting Installation Process...")
                install_folder = os.path.join(defaultInstallDirectory, appname)
                app_files_folder = os.path.join(working_directory, 'files', app_files_folder)  # temp

                create_folder_in_install_driectory(install_folder)

                copy_files_to_install_dir(app_files_folder, install_folder)

                addShortcuts()
                change_folder_permissions(install_folder)
                updateLogBox("Done!")
                startInstallationProcess = 0
        except Exception as ex:
            print(str(traceback.format_exc()))
            updateLogBox(str(traceback.format_exc()))
            startInstallationProcess = 0


def updateLogBox(text):
    global logBoxText
    logBoxText = str(text) + '\n'
    global logBox
    logBox.insertPlainText(logBoxText)
    sb = logBox.verticalScrollBar()
    sb.setValue(sb.maximum())


def create_GUI():
    app = QtWidgets.QApplication(sys.argv)
    try:
        app.setStyleSheet((open(os.path.join(working_directory, 'style', 'guiStylesheet.css')).read()))
        appIcon = QtGui.QIcon(os.path.join(working_directory, 'style', 'installer_icon.ico'))
        app.setWindowIcon(appIcon)
    except Exception as e:
        print(e)
    window = MainWindow()
    window.show()
    app.exec_()


def alert_already_running():
    app = QtWidgets.QApplication(sys.argv)
    try:
        app.setStyleSheet(open(os.path.join(working_directory, 'style', 'alertWindowStylesheet.css')).read())
        appIcon = QtGui.QIcon(os.path.join(working_directory, 'style', 'installer_icon.ico'))
        app.setWindowIcon(appIcon)
    except Exception as e:
        print(e)
    window = alertWindow(installer_appname=installer_appname, appIcon=appIcon)
    window.show()
    app.exec_()


if __name__ == '__main__':
    logging = 1
    icon_directory = 'icon.ico'
    appname = "AutoShoot Bot"
    app_files_folder = '/AutoShoot Bot'
    exe = '/AutoShoot Bot/AutoShoot Bot.exe'
    installer_appname = appname + " Installer"

    x64 = True

    elevate()
    if logging:
        sys.stdout = open('log.txt', 'w+')

    global defaultInstallDirectory
    if x64:
        defaultInstallDirectory = 'C:/Program Files/'
    else:
        defaultInstallDirectory = 'C:/Program Files (x86)/'


    def app_path():
        if getattr(sys, 'frozen', False):
            # running in executable mode
            app_dir = sys._MEIPASS
            processes = list(p.name() for p in psutil.process_iter())
            print('\n----------------------Running Processes----------------------\n' + str(
                processes) + '\n----------------------Running Processes----------------------')
            print('Number of %s App Running: ' % installer_appname + str(processes.count(installer_appname + '.exe')))
        else:
            # running in a normal Python environment
            app_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_dir)


    working_directory = app_path()
    os.chdir(working_directory)

    print(working_directory)
    global startInstallationProcess
    startInstallationProcess = 0
    global logBoxText
    logBoxText = ''
    addStartMenuEntry = 1
    addDesktopShortcut = 1

    processes = [0]
    # if processes.count(installer_appname + '.exe') < 2:
    if 1:
        gui_process = Thread(target=create_GUI, args=())
        installation_process = Thread(target=installation_process, args=())
        gui_process.start()
        installation_process.setDaemon(gui_process)
        installation_process.start()
        gui_process.join()
    else:
        print('............App Already Running............')
        alert_already_running()
