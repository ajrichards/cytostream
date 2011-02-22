#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
SubsampleSelector

A combobox widget to select from different subsample sizes

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore

class SubsampleSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsamples. Upon selection variables corresponding to the
    selected subsamples are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, subsampleList, color='white', parent=None, subsampleDefault=None, selectionFn=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        subsampleList = [str(int(float(ss))) for ss in subsampleList[:-1]] + [subsampleList[-1]]
        
        ## setup layouts
        self.color = color
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## subsample selector
        hbox1.addWidget(QtGui.QLabel('subsample'))
        self.subsampleSelector = QtGui.QComboBox(self)
        
        for subsampleName in subsampleList:
            self.subsampleSelector.addItem(subsampleName)

        hbox2.addWidget(self.subsampleSelector)

        if subsampleDefault != None and subsampleDefault == 'original':
            subsampleDefault = "All Data"

        if subsampleDefault != None:
            subsampleDefault = str(int(float(subsampleDefault)))
            if subsampleList.__contains__(subsampleDefault):
                self.subsampleSelector.setCurrentIndex(subsampleList.index(subsampleDefault))
            else:
                print "ERROR: in subsample selector - bad specified subsampleDefault", subsampleDefault

        if selectionFn == None:
            selectionFn = self.generic_callback
        self.connect(self.subsampleSelector, QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)    

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
        self.connect(self.subsampleSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn)

    def get_selected_subsample(self):
        sfInd = self.subsampleSelector.currentIndex()
        sf = str(self.subsampleSelector.currentText())

        return sf, sfInd

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    subsampleList = ['subsample1', 'subsample2']
    fs = SubsampleSelector(subsampleList)
    fs.show()
    sys.exit(app.exec_())
