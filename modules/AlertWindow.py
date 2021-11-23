from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
import traceback
import os
import logging
log = logging.getLogger(__name__)

# noinspection PyBroadException
class AppAlreadyRunning(QtWidgets.QWidget):
    def __init__(self, installer_appName="Installer", alertMessage="App Already Running!", working_directory=None, *args, **kwargs):
        super(AppAlreadyRunning, self).__init__(*args, **kwargs)
        self.working_directory = working_directory
        if self.working_directory is None:
            self.working_directory = os.getcwd()
            log.info("Working directory was not passed as a parameter, this may cause issues accessing stylesheets. Using:", self.working_directory)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(250, 100)
        self.setWindowTitle(installer_appName)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        try:
            self.setStyleSheet(open(os.path.join(self.working_directory, 'style', 'alertWindowStylesheet.css')).read())
        except:
            log.error(traceback.format_exc())
        try:
            self.appIcon = QtGui.QIcon(os.path.join(self.working_directory, 'style', 'installer_icon.ico'))
            self.setWindowIcon(self.appIcon)
        except:
            log.error(traceback.format_exc())

        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setFixedSize(25, 20)
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setFocusPolicy(QtCore.Qt.NoFocus)

        self.closeBtnLayout = QHBoxLayout()
        self.closeBtnLayout.addStretch(1)
        self.closeBtnLayout.addWidget(self.btn_close)

        self.alertMessage = QLabel(alertMessage)
        self.alertMessage.setAlignment(QtCore.Qt.AlignCenter)
        self.alertMessage.setObjectName("alert")

        self.okBtn = QPushButton("OK")
        self.okBtn.clicked.connect(self.close)
        self.okBtn.setFixedWidth(50)
        self.okBtnLay = QHBoxLayout()
        self.okBtnLay.addStretch(1)
        self.okBtnLay.addWidget(self.okBtn)
        self.okBtnLay.addStretch(1)

        self.layout.addLayout(self.closeBtnLayout)
        self.layout.addWidget(self.alertMessage)
        self.layout.addSpacing(8)
        self.layout.addLayout(self.okBtnLay)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        self.show()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
