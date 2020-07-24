import os
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtWidgets import *

from shiboken2 import wrapInstance

DIRECTORY = "D:\demo_projects"

mainWindowPtr = omui.MQtUtil.mainWindow()
mainWindow = wrapInstance(long(mainWindowPtr), QWidget)

class BrowserWin(QWidget):
    def __init__(self, *args, **kwargs):

        super(BrowserWin, self).__init__(*args, **kwargs)

        # parent Maya window
        self.setParent(mainWindow)
        self.setWindowFlags(Qt.Window)
        # Window settings
        self.setWindowTitle('AC_AssetBrowser')


        # Build window
        self.mainLayout = QVBoxLayout()
        self.btnLayout = QHBoxLayout()
        self.radioLayout = QHBoxLayout()

        # radio buttons load import
        self.radioLabel = QLabel("Action: ")
        self.importBtn = QRadioButton("Import File")
        self.openBtn = QRadioButton("Open File")
        self.saveBtn = QRadioButton("Save File")

        # Find asset directories to load from and populate the drop down
        self.fileType = QComboBox()
        self.__populate_list(self.fileType)
        self.curr_cat = self.fileType.currentText()

        # list of assets in self.list
        self.fileList = QListWidget()
        self.__populate_list(self.fileList, directory=os.path.join(DIRECTORY, self.curr_cat))

        self.fileName = QLineEdit()

        self.loadBtn = QPushButton("Load Asset")
        self.publishBtn = QPushButton("Publish")
        self.closeBtn = QPushButton("Close")

        # Add widgets to layouts
        self.radioLayout.addWidget(self.radioLabel)
        self.radioLayout.addWidget(self.importBtn)
        self.radioLayout.addWidget(self.openBtn)
        self.radioLayout.addWidget(self.saveBtn)

        self.mainLayout.addLayout(self.radioLayout)

        self.mainLayout.addWidget(self.fileType)
        self.mainLayout.addWidget(self.fileList)
        self.mainLayout.addWidget(self.fileName)

        self.btnLayout.addWidget(self.loadBtn)
        self.btnLayout.addWidget(self.publishBtn)
        self.btnLayout.addWidget(self.closeBtn)

        self.mainLayout.addLayout(self.btnLayout)
        self.setLayout(self.mainLayout)

        # Set state of widgets
        self.importBtn.toggle()
        self.fileName.setPlaceholderText("file_name")
        self.fileName.setEnabled(False)

        # Signals
        self.fileType.currentIndexChanged.connect(self.selectionChanged)
        self.loadBtn.clicked.connect(self.loadBtnCmd)
        self.publishBtn.clicked.connect(self.publishBtnCmd)
        self.closeBtn.clicked.connect(self.closeBtnCmd)
        self.saveBtn.toggled.connect(self.onSaveToggled)

    def __populate_list(self, destination, directory=DIRECTORY):
        _dirs = os.listdir(directory)
        _items = [_dir for _dir in _dirs]

        return destination.addItems(_items)

    def selectionChanged(self):
        self.curr_cat = self.fileType.currentText()
        self.fileList.clear()
        self.__populate_list(self.fileList, directory=os.path.join(DIRECTORY, self.curr_cat))

    def loadBtnCmd(self):
        selected_file = self.fileList.currentItem()
        asset_file = os.path.join(DIRECTORY, self.curr_cat, selected_file.text())

        try:
            if self.importBtn.isChecked() and selected_file.text() is not None:
                cmds.file(asset_file, i=True)
            elif self.openBtn.isChecked() and selected_file.text() is not None:
                cmds.file(asset_file, o=True, force=True)
        except AttributeError:
            om.MGlobal.displayError("No file selected")
            raise

    def publishBtnCmd(self):
        if self.saveBtn.isChecked() and self.fileName.text is not None:
            path_to_save = os.path.join(DIRECTORY, self.curr_cat, self.fileName.text())
            cmds.file(rn="{}.ma".format(path_to_save))
            cmds.file(save=True)
            self.fileList.clear()
            self.__populate_list(
                self.fileList,
                directory=os.path.join(DIRECTORY, self.curr_cat)
            )

    def closeBtnCmd(self):
        self.close()

    def onSaveToggled(self):
        return self.fileName.setEnabled(not self.fileName.isEnabled())

win = BrowserWin()
win.show()



