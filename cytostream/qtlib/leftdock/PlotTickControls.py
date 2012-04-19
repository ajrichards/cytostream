#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
PlotSelector 

A combobox widget to select from different files

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore

class PlotTickControls(QtGui.QWidget):
    '''
    Class that handles misc. controls for plotting that can be toggled via a tick mechanism. 
    '''

    def __init__(self,color='white',parent=None,mainWindow=None,gridDefault=False,scaleDefault=False,
                 titleDefault=True,axesDefault=True):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.color = color
        self.parent = parent
        self.mainWindow = mainWindow
   
        ## initialize widgets
        self.gridCB = QtGui.QCheckBox("Grid")
        self.gridCB.setChecked(gridDefault)
        self.connect(self.gridCB,QtCore.SIGNAL('stateChanged(int)'), self.grid_callback)
        self.scaleCB = QtGui.QCheckBox("Scale")
        self.scaleCB.setChecked(scaleDefault)
        self.connect(self.scaleCB,QtCore.SIGNAL('stateChanged(int)'), self.scale_callback)
        self.axesCB = QtGui.QCheckBox("Axes")
        self.axesCB.setChecked(axesDefault)
        self.connect(self.axesCB,QtCore.SIGNAL('stateChanged(int)'), self.axes_callback)
        self.titleCB = QtGui.QCheckBox("Title")
        self.titleCB.setChecked(titleDefault)
        self.connect(self.titleCB,QtCore.SIGNAL('stateChanged(int)'), self.title_callback)

        ## layouts
        masterBox = QtGui.QHBoxLayout()
        col1Box = QtGui.QVBoxLayout()
        col1Box.setAlignment(QtCore.Qt.AlignLeft)
        col2Box = QtGui.QVBoxLayout()
        col2Box.setAlignment(QtCore.Qt.AlignLeft)
        
        col1Box.addWidget(self.titleCB)
        col1Box.addWidget(self.scaleCB)
        col2Box.addWidget(self.gridCB)
        col2Box.addWidget(self.axesCB)
        
        ### finalize layout
        masterBox.addLayout(col1Box)
        masterBox.addLayout(col2Box)
        self.setLayout(masterBox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def generic_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            print 'main window does something'

    def grid_callback(self):        
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            print 'main window does something'

    def title_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            print 'main window does something'

    def scale_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            print 'main window does something'

    def axes_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            print 'main window does something'


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    ptc = PlotTickControls()
    ptc.show()
    sys.exit(app.exec_())
