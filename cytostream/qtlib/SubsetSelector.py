#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
SubsetSelector

A combobox widget to select from different subsample sizes

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore

class SubsetSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsets. Upon selection variables corresponding to the
    selected subsets are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, subsetList, color='white', parent=None, subsetDefault=None, selectionFn=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        subsetList = [str(int(float(ss))) for ss in subsetList[:-1]] + [subsetList[-1]]
        
        ## setup layouts
        self.color = color
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## subset selector
        hbox1.addWidget(QtGui.QLabel('subsample'))
        self.subsetSelector = QtGui.QComboBox(self)
        
        for subsetName in subsetList:
            self.subsetSelector.addItem(subsetName)

        hbox2.addWidget(self.subsetSelector)

        if subsetDefault != None:
            subsetDefault = str(int(float(subsetDefault)))
            if subsetList.__contains__(subsetDefault):
                self.subsetSelector.setCurrentIndex(subsetList.index(subsetDefault))
            else:
                print "ERROR: in subset selector - bad specified subsetDefault", subsetDefault

        if selectionFn == None:
            selectionFn = self.generic_callback
        self.connect(self.subsetSelector, QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)    

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
        self.connect(self.subsetSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn)

    def get_selected_subset(self):
        sfInd = self.subsetSelector.currentIndex()
        sf = str(self.subsetSelector.currentText())

        return sf, sfInd

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    subsetList = ['subset1', 'subset2']
    fs = SubsetSelector(subsetList)
    fs.show()
    sys.exit(app.exec_())
