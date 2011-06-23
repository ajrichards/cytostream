#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
SubsetSelector 

A combobox widget to select from different files

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore

class FileSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of files.  Upon selection variables corresponding to the
    selected files are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, fileList, color='white', parent=None, modelsRun=None, fileDefault=None, selectionFn=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.color = color
        self.fileList = fileList
        self.parent = parent

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)     
   
        ## file selector
        hbox1.addWidget(QtGui.QLabel('file'))
        self.fileSelector = QtGui.QComboBox(self)
        
        self.fileList = [re.sub("\.fcs","",f) for f in self.fileList]
        for fileName in self.fileList:
            self.fileSelector.addItem(fileName)

        hbox2.addWidget(self.fileSelector)
     
        if fileDefault != None:
            fileDefault = re.sub("\.fcs","",fileDefault)
            if self.fileList.__contains__(fileDefault):
                self.fileSelector.setCurrentIndex(self.fileList.index(fileDefault))
            else:
                print "ERROR: in file selector - bad specified fileDefault", fileDefault

        if selectionFn == None:
            selectionFn = self.generic_callback
        self.connect(self.fileSelector, QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)    

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)    
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def set_refresh_thumbs_fn(self,refreshFn):
        self.connect(self.fileSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn)
        if self.modelSelector != None:
            self.connect(self.modelSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn) 
        

    def get_selected_file(self):
        sfInd = self.fileSelector.currentIndex()
        sf = str(self.fileSelector.currentText())

        return sf+".fcs", sfInd

    def get_selected_model(self):
        smInd = self.modelSelector.currentIndex()
        sm = str(self.modelSelector.currentText())
        
        return sm, smInd

    def generic_callback(self):
        print 'callback does not do anything yet'


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    fileList = ['file1', 'file2']
    modelsRun = ['fileName_sampleID_modelID1', 'fileName_sampleID_modelID2']
    fs = FileSelector(fileList)
    fs.show()
    sys.exit(app.exec_())
