#!/usr/bin/env python

# -*- coding: utf-8 -*-

import sys,os,re
from PyQt4 import QtGui, QtCore

class FileUploader(QtGui.QWidget):
    def __init__(self,parent=None,mainLabel='Foo'):
        QtGui.QWidget.__init__(self,parent)

        self.setWindowTitle('File Uploader')

        ## declare variables
        self.loadedFileNames = []
        self.loadedFilePaths = []
        self.maxNumRows = 1
        #self.resize(600, int(50*self.maxNumRows))

        ## setup layout 
        mainBox = QtGui.QVBoxLayout()
        mainBox.setAlignment(QtCore.Qt.AlignCenter)
        hbox1 = QtGui.QHBoxLayout()
        hbox1a = QtGui.QHBoxLayout()
        hbox1a.setAlignment(QtCore.Qt.AlignLeft)
        hbox1b = QtGui.QHBoxLayout()
        hbox1b.setAlignment(QtCore.Qt.AlignRight)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)

        ## initialize widgets
        self.mainLabel = QtGui.QLabel(mainLabel)
        self.selectBtn = QtGui.QPushButton("Browse")
        self.clearBtn = QtGui.QPushButton("Clear")
        self.model = QtGui.QStandardItemModel(self.maxNumRows,1)
        self.clear_list()
        self.fileList = QtGui.QListView()
        self.fileList.setModel(self.model)

        self.fileList.setMaximumHeight(50)

        ## connect widgets
        self.connect(self.selectBtn, QtCore.SIGNAL('clicked()'),self.load_file)
        self.connect(self.clearBtn, QtCore.SIGNAL('clicked()'),self.clear_list)

        ## add widgets to layout
        hbox1a.addWidget(self.mainLabel)
        hbox1b.addWidget(self.selectBtn)
        hbox1b.addWidget(self.clearBtn)
        hbox2.addWidget(self.fileList)

        # finalize layout
        hbox1.addLayout(hbox1a)
        hbox1.addLayout(hbox1b)
        mainBox.addLayout(hbox1)
        mainBox.addLayout(hbox2)
        
        self.setLayout(mainBox)
     
    def clear_list(self):
        for i in range(self.maxNumRows):
            index = self.model.index(i,0,QtCore.QModelIndex())
            self.model.setData(index,'')
            item = self.model.itemFromIndex(index)
            item.setEditable(False)
        
        self.loadedFileNames = []
        self.loadedFilePaths = []

    def generic_callback(self):
        print 'generic callback'
   
    def load_file(self):
        inputFilePath = QtGui.QFileDialog.getOpenFileName(self,'Open file(s)')

        ## return if user aborts
        if inputFilePath == '':
            return

        inputFilePath = str(inputFilePath)
        inputFileName = os.path.split(inputFilePath)[-1]
        if re.search(">|<|\*|\||^\$|;|#|\@|\&|\s",inputFileName):
            msg1 = "There were invalid characters in the uploaded file name\n"
            msg2 = "To proceed remove all spaces and characters like\n, '$', ';', '@', '|', '<', and '*'\n\n"
            msg3 = "Spaces may be replaced with a '_'"
            msg = msg1 + msg2 + msg3
            QtGui.QMessageBox.information(self,'Information',msg)
            return

        self.update_list(inputFilePath)

    def update_list(self,filePath):
        
        if len(self.loadedFileNames) == self.maxNumRows:
            msg = "The maximum number of items have been uploaded\nclear the list to begin again"
            QtGui.QMessageBox.information(self,'Information',msg)
            return 

        filePath = os.path.abspath(filePath)
        fileName = os.path.split(filePath)[-1]
        self.loadedFileNames.append(fileName)
        self.loadedFilePaths.append(filePath)

        for i in range(len(self.loadedFileNames)):
            index = self.model.index(i,0,QtCore.QModelIndex())
            self.model.setData(index,fileName)

### Run the tests 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    fu = FileUploader(parent=None)
    fu.show()
    sys.exit(app.exec_())
