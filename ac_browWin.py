import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui

from PySide2.QtCore import *
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QRadioButton, QListWidget, QComboBox, QAbstractItemView, \
    QLineEdit, QPushButton, QMenu, QMenuBar, QWidgetAction

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
        #
        # Act = QWidgetAction()
        #
        # # Build Menu for other options
        # self.menuBar = QMenuBar()
        # self.menu = QMenu("File")
        # self.menu.addAction(Act)
        # self.menuBar.addMenu(self.menu)
        # self.mainLayout.addWidget(self.menu)

        # radio buttons load import
        self.radioLabel = QLabel("Action: ")
        self.importRadioBtn = QRadioButton("Import File")
        self.openRadioBtn = QRadioButton("Open File")
        self.saveRadioBtn = QRadioButton("Save File")

        # Find asset directories to load from and populate the drop down
        self.fileType = QComboBox()
        self.__populate_list(self.fileType)
        self.curr_cat = self.fileType.currentText()

        # list of assets in self.list
        self.fileList = QListWidget()
        self.fileList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__populate_list(
            self.fileList,
            directory=os.path.join(DIRECTORY, self.curr_cat)
        )

        self.fileName = QLineEdit()

        self.loadBtn = QPushButton("Load Asset")
        self.publishBtn = QPushButton("Publish")
        self.closeBtn = QPushButton("Close")

        # Add widgets to layouts
        self.radioLayout.addWidget(self.radioLabel)
        self.radioLayout.addWidget(self.importRadioBtn)
        self.radioLayout.addWidget(self.openRadioBtn)
        self.radioLayout.addWidget(self.saveRadioBtn)

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
        self.importRadioBtn.toggle()
        self.fileName.setPlaceholderText("file_name")
        self.fileName.setEnabled(False)
        self.publishBtn.setEnabled(False)

        # Signals
        self.fileType.currentIndexChanged.connect(self.selectionChanged)
        self.loadBtn.clicked.connect(self.loadBtnCmd)
        self.publishBtn.clicked.connect(self.publishBtnCmd)
        self.closeBtn.clicked.connect(self.closeBtnCmd)
        self.importRadioBtn.toggled.connect(self.onImportToggled)
        self.openRadioBtn.toggled.connect(self.onOpenToggled)
        self.saveRadioBtn.toggled.connect(self.onSaveToggled)

    def __populate_list(self, destination, directory=DIRECTORY):
        _dirs = os.listdir(directory)
        _items = [_dir for _dir in _dirs]

        return destination.addItems(_items)

    def selectionChanged(self):
        self.curr_cat = self.fileType.currentText()
        self.fileList.clear()
        self.__populate_list(
            self.fileList,
            directory=os.path.join(DIRECTORY, self.curr_cat)
        )

    def loadBtnCmd(self):
        if self.importRadioBtn.isChecked():
            selected_files = self.fileList.selectedItems()
            for _file in selected_files:
                asset_file = os.path.join(DIRECTORY, self.curr_cat, _file.text())
                cmds.file(asset_file, i=True)
        elif self.openRadioBtn.isChecked():
            selected_file = self.fileList.currentItem()
            asset_file = os.path.join(DIRECTORY, self.curr_cat, selected_file.text())
            cmds.file(asset_file, o=True, force=True)
        else:
            print("Did you mean to publish this asset?")

    def publishBtnCmd(self):
        if self.saveRadioBtn.isChecked() and self.fileName.text() is not None:
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
        items = self.fileList.selectedItems()
        for item in items:
            item.setSelected(False)
        return self.fileName.setEnabled(not self.fileName.isEnabled()), \
               self.publishBtn.setEnabled(not self.publishBtn.isEnabled())

    def onImportToggled(self):
        if self.importRadioBtn.isChecked():
            return self.fileList.setSelectionMode(QAbstractItemView.ExtendedSelection)


    def onOpenToggled(self):
        if self.openRadioBtn.isChecked():
            items = self.fileList.selectedItems()
            items.pop()
            for item in items:
                item.setSelected(False)
            return self.fileList.setSelectionMode(QAbstractItemView.SingleSelection)

win = BrowserWin()
win.show()



