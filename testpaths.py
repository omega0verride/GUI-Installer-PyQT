import os
import sys

def app_path():
    if getattr(sys, 'frozen', False):
        # running in executable mode
        app_dir = sys._MEIPASS
    else:
        # running in a normal Python environment
        app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir)


working_directory = app_path()
os.chdir(working_directory)

print(working_directory)

source_app_files_folder = "AppFiles"

appName = "test"
exe_folder = ""
exe_path = "AutoShoot Bot.exe"
icon_path = "style/icon.ico"

if not os.path.exists(source_app_files_folder):
    raise Exception("Invalid app source folder. Make sure the AppFiles folder exists in the same directory as this script.")
    exit()

if not os.path.exists(os.path.join(source_app_files_folder, exe_folder)):
    raise Exception(
        "Invalid exe_folder path. This folder represents the directory the exe should run on.  Make sure that you have placed it inside the AppFiles folder and that you have supplied the relative path i.e: myApp.exe or myFolder/folder2/myApp.exe (subdirectories of AppFiles)")
    exit()

if not os.path.isfile(os.path.join(source_app_files_folder, exe_path)):
    raise Exception(
        "Invalid exe path. Make sure that you have placed it inside the AppFiles folder and that you have supplied the relative path i.e: myApp.exe or myFolder/folder2/myApp.exe (subdirectories of AppFiles)")
    exit()

if not os.path.isfile(os.path.join(source_app_files_folder, icon_path)):
    raise Exception(
        "Invalid icon path. Make sure that you have placed it inside the AppFiles folder and that you have supplied the relative path i.e: myIcon.ico or myFolder/folder2/myIco.ico (subdirectories of AppFiles)")
    exit()

if icon_path.rsplit(".", 1)[1] != 'ico':
    raise Warning("It is recommended to use .ico files to make sure the image is displayed on all systems. You can convert the file online.")
