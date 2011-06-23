#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
kSelectorSelector

A bar of radio widgets to select from different models to run

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget,Slider

class KSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsets. Upon selection variables corresponding to the
    selected subsets are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, color='white', parent=None, kDefault=None, kCallback=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## defaults
        if kDefault == None:
            defaultComponents = 16
        else:
            defaultComponents = kDefault

        ## variables
        self.color = color
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        
        ## kSelector selector
        self.componentViewer = QtGui.QLabel('%s'%defaultComponents)
        self.componentViewer.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        hbox1.addWidget(self.componentViewer)

        ## component viewer 
        hbox2.addWidget(QtGui.QLabel('Components (<i>k</i>)'))
        #self.componentSlider = QtGui.QSlider(parent=self)
        self.componentSlider = QtGui.QSlider(QtCore.Qt.Horizontal, parent=self)
        self.componentSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.componentSlider.setGeometry(30, 40, 100, 30)
        self.componentSlider.setValue(defaultComponents)
        self.componentSlider.setRange(16,256)
        self.componentSlider.setSingleStep(16)
        self.componentSlider.setPageStep(16)
        self.componentSlider.setTickInterval(16)

        if kCallback != None:
            self.connect(self.componentSlider, QtCore.SIGNAL('valueChanged(int)'), kCallback)
        self.connect(self.componentSlider, QtCore.SIGNAL('valueChanged(int)'), self.set_components)
        hbox3.addWidget(self.componentSlider)

        ## finalize layout
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def get_text(self):
        return str(self.componentSlider.value())

    def set_components(self,value):
        self.componentViewer.setText(str(value))

    def set_checked(self,kSelectorLabel):
        if self.kSelectorList.__contains__(kSelectorLabel) == False:
            print "ERROR: ModelToRunSelector - bad kSelector label in set_checked"
            return None

        self.kSelectorSelector.btns[kSelectorLabel].setChecked(True)

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ms = KSelector()
    ms.show()
    sys.exit(app.exec_())
