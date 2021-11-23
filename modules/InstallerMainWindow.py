from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
import traceback
import platform
import logging
import os

log = logging.getLogger(__name__)


# noinspection PyBroadException
class InstallerMainWindow(QtWidgets.QWidget):

    def __init__(self, default_install_dir="", installer_app_name="Installer",
                 add_desktop_shortcut=True, show_add_desktop_shortcut_checkbox=True,
                 add_start_menu_entry=True, show_add_start_menu_entry_checkbox=True,
                 start_on_boot=True, show_start_on_boot_checkbox=True,
                 launch_after_install=True,
                 working_directory=os.getcwd(), *args, **kwargs):
        super(InstallerMainWindow, self).__init__(*args, **kwargs)
        self.working_directory = working_directory
        if self.working_directory is None:
            self.working_directory = os.getcwd()
            log.info("Working directory was not passed as a parameter, this may cause issues accessing stylesheets. Using:", self.working_directory)
        self.default_install_dir = default_install_dir
        self.installer_app_name = installer_app_name
        self.add_desktop_shortcut = add_desktop_shortcut
        self.show_add_desktop_shortcut_checkbox = show_add_desktop_shortcut_checkbox
        self.add_start_menu_entry = add_start_menu_entry
        self.show_add_start_menu_entry_checkbox = show_add_start_menu_entry_checkbox
        self.start_on_boot = start_on_boot
        self.show_start_on_boot_checkbox = show_start_on_boot_checkbox
        self.launch_after_install = launch_after_install
        self.installerRunning = False

        # style
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle(self.installer_app_name)
        try:
            self.setStyleSheet((open(os.path.join(self.working_directory, 'style', 'guiStylesheet.css')).read()))
        except:
            log.error(traceback.format_exc())
        try:
            self.appIcon = QtGui.QIcon(os.path.join(self.working_directory, 'style', 'installer_icon.ico'))
            self.setWindowIcon(self.appIcon)
        except:
            log.error(traceback.format_exc())
        self.setFixedSize(550, 390)
        self.center()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        #  window tittle and buttons
        self.titleLayout = QHBoxLayout()
        self.titleLayout.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel(self.installer_app_name)
        self.title.setFixedSize(200, 22)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("windowTitle")

        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setFixedSize(30, 22)
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFocusPolicy(QtCore.Qt.NoFocus)

        self.btn_minimise = QPushButton("_")
        self.btn_minimise.clicked.connect(self.showMinimized)
        self.btn_minimise.setFixedSize(30, 22)
        self.btn_minimise.setObjectName("minimiseBtn")
        self.btn_minimise.setFocusPolicy(QtCore.Qt.NoFocus)

        self.titleLayout.addStretch(1)
        self.titleLayout.addSpacing(self.btn_close.width() + self.btn_minimise.width())
        self.titleLayout.addWidget(self.title)
        self.titleLayout.addStretch(1)
        self.titleLayout.addWidget(self.btn_minimise)
        self.titleLayout.addSpacing(-5)
        self.titleLayout.addWidget(self.btn_close)

        # --------------------------------------------------------------------------------------------------------------

        self.directoryLabel = QLabel("Install Directory")
        self.directoryLabel.setObjectName('label')

        self.directoryInput = QLineEdit()
        self.directoryInput.setFixedWidth(350)
        self.directoryInput.setText(self.default_install_dir)
        self.directoryInput.textChanged.connect(self.getDirectoryFromQlineEdit)

        self.directoryInputButton = QPushButton()
        self.directoryInputButton.clicked.connect(self.getDirectoryFromUser)
        self.directoryInputButton.setObjectName('chooseDirectoryBtn')
        self.directoryInputButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.directoryLay = QHBoxLayout()
        self.directoryLay.addSpacing(20)
        self.directoryLay.addWidget(self.directoryLabel)
        self.directoryLay.addSpacing(6)
        self.directoryLay.addWidget(self.directoryInput)
        self.directoryLay.addWidget(self.directoryInputButton)
        self.directoryLay.addStretch(1)

        self.errorLabel = QLabel()
        self.errorLabel.setObjectName('errorLabel')
        self.errorLay = QHBoxLayout()
        self.errorLay.addSpacing(20)
        self.errorLay.addWidget(self.errorLabel)

        self.addStartMenuEntryCheckbox = QCheckBox("Add Start Menu Entry")
        self.addStartMenuEntryCheckbox.clicked.connect(self.setAddStartMenuEntry)
        self.addStartMenuEntryCheckbox.setObjectName("checkboxes")
        self.addStartMenuEntryCheckbox.setChecked(self.add_start_menu_entry)
        self.addStartMenuEntryCheckbox.setFocusPolicy(QtCore.Qt.NoFocus)

        self.addDesktopShortcutCheckbox = QCheckBox("Add Desktop Shortcut")
        self.addDesktopShortcutCheckbox.clicked.connect(self.setAddDesktopShortcutCheckbox)
        self.addDesktopShortcutCheckbox.setObjectName("checkboxes")
        self.addDesktopShortcutCheckbox.setChecked(self.add_desktop_shortcut)
        self.addDesktopShortcutCheckbox.setFocusPolicy(QtCore.Qt.NoFocus)

        self.startOnBootCheckbox = QCheckBox("Add to StartUp")
        self.startOnBootCheckbox.clicked.connect(self.setStartOnBootCheckbox)
        self.startOnBootCheckbox.setObjectName("checkboxes")
        self.startOnBootCheckbox.setChecked(self.start_on_boot)
        self.startOnBootCheckbox.setFocusPolicy(QtCore.Qt.NoFocus)

        self.checkboxesLay = QHBoxLayout()
        self.checkboxesLay.addSpacing(20)
        if self.show_add_desktop_shortcut_checkbox:
            self.checkboxesLay.addWidget(self.addDesktopShortcutCheckbox)
            self.checkboxesLay.addSpacing(10)
        if self.show_start_on_boot_checkbox:
            self.checkboxesLay.addWidget(self.startOnBootCheckbox)

        self.checkboxesLay.addStretch(1)

        self.autoScroll = QCheckBox("AutoScroll")
        self.autoScroll.clicked.connect(self.setAutoScroll)
        self.autoScroll.setObjectName("autoScroll")
        self.autoScroll.setChecked(True)
        self.autoScroll.setFocusPolicy(QtCore.Qt.NoFocus)

        self.autoScrollLay = QHBoxLayout()
        self.autoScroll.setMaximumHeight(13)
        self.autoScrollLay.addSpacing(20)
        if self.show_add_start_menu_entry_checkbox:
            if platform.system().lower() != 'darwin':
                self.autoScrollLay.addWidget(self.addStartMenuEntryCheckbox)
            else:
                self.add_start_menu_entry = False
        # self.autoScrollLay.addWidget(self.startOnBootCheckbox)
        self.autoScrollLay.addStretch(1)
        self.autoScrollLay.addWidget(self.autoScroll)
        self.autoScrollLay.addSpacing(22)

        self.logBox = QTextEdit()
        self.logBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.logBox.setObjectName('logBox')
        self.logBox.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignTop)
        self.logBox.setReadOnly(True)

        self.logBoxLay = QHBoxLayout()
        self.logBoxLay.addSpacing(20)
        self.logBoxLay.addWidget(self.logBox)
        self.logBoxLay.addSpacing(20)

        self.installButton = QPushButton('Install')
        self.installButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.installButton.setObjectName('installBtn')

        self.cancelButton = QPushButton('Cancel')
        self.cancelButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancelButton.setObjectName('cancelBtn')

        self.exitButton = QPushButton('Exit')
        self.exitButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.exitButton.clicked.connect(self.close)
        self.exitButton.setObjectName('exitBtn')

        self.controlButtonsLay = QHBoxLayout()
        self.controlButtonsLay.addSpacing(18)
        self.controlButtonsLay.addWidget(self.cancelButton)
        self.controlButtonsLay.addStretch(1)
        self.controlButtonsLay.addWidget(self.installButton)
        self.controlButtonsLay.addWidget(self.exitButton)
        self.exitButton.hide()
        self.cancelButton.hide()
        self.controlButtonsLay.addSpacing(20)

        self.mainLay = QVBoxLayout()
        self.mainLay.addSpacing(18)
        self.mainLay.addLayout(self.directoryLay)
        self.mainLay.addLayout(self.errorLay)
        self.mainLay.addSpacing(8)
        self.mainLay.addLayout(self.checkboxesLay)
        self.mainLay.addLayout(self.autoScrollLay)
        self.mainLay.addLayout(self.logBoxLay)
        self.mainLay.addLayout(self.controlButtonsLay)

        self.layout.addLayout(self.titleLayout)
        self.layout.addLayout(self.mainLay)
        self.layout.addStretch(1)

        self.setLayout(self.layout)
        self.oldPos = self.pos()

        self.getDirectoryFromQlineEdit()

        # show the window
        self.show()

    # install controls
    def setAutoScroll(self):
        if self.autoScroll.isChecked():
            sb = self.logBox.verticalScrollBar()
            sb.setValue(sb.maximum())

    def setAddStartMenuEntry(self):
        self.add_start_menu_entry = self.addStartMenuEntryCheckbox.isChecked()

    def setAddDesktopShortcutCheckbox(self):
        self.add_desktop_shortcut = self.addDesktopShortcutCheckbox.isChecked()

    def setStartOnBootCheckbox(self):
        self.start_on_boot = self.startOnBootCheckbox.isChecked()

    def getDirectoryFromUser(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.default_install_dir))
        if directory:
            self.default_install_dir = directory
            self.directoryInput.setText(self.default_install_dir)

    def getDirectoryFromQlineEdit(self):
        self.default_install_dir = self.directoryInput.text()
        if os.path.exists(self.default_install_dir):
            self.errorLabel.setText("")
            if not self.installerRunning:
                self.installButton.setEnabled(True)
        else:
            self.errorLabel.setText("This directory does not Exists. Please choose a valid directory.")
            self.installButton.setDisabled(True)

    # -------------------------------------------------------------------------------------------------

    # logBox controls
    def updateLogBox(self, text):
        logBoxText = str(text) + '\n'
        self.logBox.insertPlainText(logBoxText)
        if self.autoScroll.isChecked():
            sb = self.logBox.verticalScrollBar()
            sb.setValue(sb.maximum())

    # window controls
    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
    # -------------------------------------------------------------------------------------------------
