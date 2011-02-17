#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
modeSelector

A bar of radio widgets to select from different subsample sizes

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget

class ModeSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsets. Upon selection variables corresponding to the
    selected subsets are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, modeList, color='white', parent=None, modeDefault=None, modeFn=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## error checking
        if modeDefault != None and modeList.__contains__(modeDefault) == False:
            print "ERROR: RadioBtnWidget - bad default specified",modeDefault
            return None

        ## variables
        self.modeList = modeList
        self.color = color
        self.modeList = modeList
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## mode selector
        hbox1.addWidget(QtGui.QLabel('visualization mode'))
        self.modeSelector = RadioBtnWidget(self.modeList,parent=self)
        hbox2.addWidget(self.modeSelector)

        #self.subsetSelector = QtGui.QComboBox(self)
        
        #for subsetName in subsetList:
        #    self.subsetSelector.addItem(subsetName)
        #
        #hbox2.addWidget(self.subsetSelector)

        #if subsetDefault != None:
        #    subsetDefault = str(int(float(subsetDefault)))
        #    if subsetList.__contains__(subsetDefault):
        #        self.subsetSelector.setCurrentIndex(subsetList.index(subsetDefault))
        #    else:
        #        print "ERROR: in subset selector - bad specified subsetDefault", subsetDefault

        #if selectionFn == None:
        #    selectionFn = self.generic_callback
        #self.connect(self.subsetSelector, QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)    


        #def __init__(self,modeList,parent=None,default=None,callBackFn=None,color='white'):

        #self.selectedItem = None

        #for bLabel in self.modeList:
        #    rad = QtGui.QRadioButton(bLabel)
        #    self.btns[bLabel] = rad
        #    self.connect(self.btns[bLabel], QtCore.SIGNAL('clicked()'),lambda item=bLabel:self.set_selected(item))
        #    vbox.addWidget(self.btns[bLabel])
        #
        #    if callBackFn != None:
        #        self.connect(self.btns[bLabel], QtCore.SIGNAL('clicked()'),lambda item=bLabel:callBackFn(item=item))
        #
        #    if default != None and bLabel == default:
        #        self.btns[bLabel].setChecked(True)
        #
        #hbox2.addWidget(

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
    
    subsetList = ['mode1', 'mode2']
    ms = ModeSelector(subsetList)
    ms.show()
    sys.exit(app.exec_())
