#!/usr/bin/python
'''
Cytostream
OpenExistingProject

A menu to allow the user to select from then open an existing project

 '''

__author__ = "A Richards"


import sys
from PyQt4 import QtGui, QtCore

class OpenExistingProject(QtGui.QWidget):
    def __init__(self, projectList, parent=None, openBtnFn=None,closeBtnFn=None,rmBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        self.projectList = projectList
        self.selectedProject = None
        self.openBtnFn = openBtnFn
        self.parent = parent

        ## setup layouts
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl2 = QtGui.QHBoxLayout()
        self.hbl2.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl3 = QtGui.QHBoxLayout()
        self.hbl3.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl4 = QtGui.QHBoxLayout()
        self.hbl4.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl5 = QtGui.QHBoxLayout()
        self.hbl5.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl6 = QtGui.QHBoxLayout()
        self.hbl6.setAlignment(QtCore.Qt.AlignCenter)

        ## set up main widget label
        self.hbl1.addWidget(QtGui.QLabel('Choose an existing project'))

        ## show files to be loaded
        self.hbl2.addWidget(QtGui.QLabel('\t\t\t'))
        self.modelLoad = QtGui.QStandardItemModel()

        for p in range(len(projectList)):
            project = projectList[p]
            item0 = QtGui.QStandardItem(str(p+1))
            item1 = QtGui.QStandardItem('%s'%project)

            ## populate model
            item0.setEditable(False)
            item1.setEditable(False)
            self.modelLoad.appendRow([item0,item1])
            self.modelLoad.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant('#'))
            self.modelLoad.setHeaderData(0, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignLeft),QtCore.Qt.TextAlignmentRole)
            self.modelLoad.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant('saved projects'))
            self.modelLoad.setHeaderData(1, QtCore.Qt.Horizontal, QtCore.QVariant(QtCore.Qt.AlignLeft),QtCore.Qt.TextAlignmentRole)

        self.viewLoad = QtGui.QTreeView()
        self.viewLoad.setModel(self.modelLoad)
        self.connect(self.viewLoad,QtCore.SIGNAL('currentChanged()'),self.generic_callback)
        self.hbl2.addWidget(self.viewLoad)
        
        self.hbl2.addWidget(QtGui.QLabel('\t\t\t'))

        ## create the buttons
        self.openBtn = QtGui.QPushButton("Open project", self)
        self.openBtn.setMaximumWidth(200)
        self.openBtn.setMinimumWidth(200)
        self.hbl3.addWidget(self.openBtn)
        if openBtnFn == None:
            openBtnFn = self.generic_callback

        self.connect(self.openBtn,QtCore.SIGNAL('clicked()'), self.open_project_callback)

        self.closeBtn = QtGui.QPushButton("Close screen", self)
        self.closeBtn.setMaximumWidth(200)
        self.closeBtn.setMinimumWidth(200)
        self.hbl4.addWidget(self.closeBtn)
        if closeBtnFn == None:
            closeBtnFn = self.generic_callback

        self.connect(self.closeBtn, QtCore.SIGNAL('clicked()'),closeBtnFn)
        
        self.rmBtn = QtGui.QPushButton("Delete selected project", self)
        self.rmBtn.setMaximumWidth(200)
        self.rmBtn.setMinimumWidth(200)
        self.hbl5.addWidget(self.rmBtn)
        if rmBtnFn == None:
            rmBtnFn = self.generic_callback

        self.connect(self.rmBtn, QtCore.SIGNAL('clicked()'),rmBtnFn)
        
        # finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addWidget(QtGui.QLabel('\n'))
        self.vbl.addLayout(self.hbl2)
        self.vbl.addWidget(QtGui.QLabel('\n'))
        self.vbl.addLayout(self.hbl3)
        self.vbl.addLayout(self.hbl4)
        self.vbl.addLayout(self.hbl5)
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.vbl)

    def generic_callback(self):
        print 'This button does nothing'

    def open_project_callback(self):
        '''
        saves alternate file names 
        
        '''

        n = len(self.projectList)
        #altFiles = [str(self.modelFiles.data(self.modelFiles.index(i,2)).toString()) for i in range(n)]
        selectedProject = None
        projects = [str(self.modelLoad.data(self.modelLoad.index(i,1)).toString()) for i in range(n)]
        selectedRow = self.viewLoad.selectionModel().selectedRows()
        if len(selectedRow) > 0: 
            selectedRowInd = int(str(selectedRow[0].row()))
            selectedProject = self.projectList[selectedRowInd]
        else:
            reply = QtGui.QMessageBox.warning(self, "Warning", "A project must first be selected in order to load it")
            return None

        self.selectedProject = selectedProject

        if self.selectedProject != None and self.parent != None:
            self.openBtnFn()

        if self.selectedProject != None and self.parent == None:
            print "this opens project:", self.selectedProject



### Run the tests
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    projectList = ['project1','project2','project3']
    oep = OpenExistingProject(projectList)
    oep.show()
    sys.exit(app.exec_())
    
