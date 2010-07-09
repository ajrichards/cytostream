import sys,os,time
from PyQt4 import QtGui, QtCore
from BasicWidgets import *

class ModelDock(QtGui.QWidget):
    def __init__(self,modelList, parent=None, subsetDefault=None, contBtnFn=None, componentsFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.modelList = modelList
        self.setWindowTitle('Model')
        defaultComponents = 16

        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        hbox3 = QtGui.QHBoxLayout()
        hbox4 = QtGui.QHBoxLayout()
        hbox5 = QtGui.QHBoxLayout()

        ## subset selector 
        hbox1.addWidget(QtGui.QLabel('Model Selector'))
        hbox1.setAlignment(QtCore.Qt.AlignCenter)

        self.modelSelector = QtGui.QComboBox(self)
        self.modelSelector.setMaximumWidth(150)
        for modelType in modelList:
            self.modelSelector.addItem(modelType)
        
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        hbox2.addWidget(self.modelSelector)

        ## components slider viewer
        #self.componentViewer = QtGui.QLCDNumber(self)
        #self.componentViewer.display(defaultComponents)
        self.componentViewer = QtGui.QLabel('%s'%defaultComponents)
        hbox5.setAlignment(QtCore.Qt.AlignCenter)
        hbox5.addWidget(self.componentViewer)

        ## component viewer
        hbox3.addWidget(QtGui.QLabel('Num. of Componnets (<i>K</i>)'))
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        self.componentSlider = Slider(self)
        self.componentSlider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.componentSlider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.componentSlider.setGeometry(30, 40, 100, 30)
        self.componentSlider.setValue(defaultComponents)
        self.componentSlider.setRange(8,256)
        self.componentSlider.setSingleStep(8)
        self.componentSlider.setPageStep(8)
        self.componentSlider.setTickInterval(8)

        if componentsFn == None:
            componentsFn = self.generic_callback
        self.connect(self.componentSlider, QtCore.SIGNAL('valueChanged(int)'), componentsFn)
        #self.connect(self.componentSlider, QtCore.SIGNAL('valueChanged(int)'), self.componentViewer, QtCore.SLOT("display(int)"))
        self.connect(self.componentSlider, QtCore.SIGNAL('valueChanged(int)'), self.set_components)
        hbox4.setAlignment(QtCore.Qt.AlignCenter)
        hbox4.addWidget(self.componentSlider)

        ## finalize layout
        vbox.setAlignment(QtCore.Qt.AlignCenter)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('white'))
        self.setPalette(palette)

        ## finalize layout
        vbox.setAlignment(QtCore.Qt.AlignBottom)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3) 
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        self.setLayout(vbox)

    def set_components(self,value):
        self.componentViewer.setText(str(value))

    def get_selected_model(self):
        msInd = self.modelSelector.currentIndex()
        ms = self.modelSelector.currentText()
        return ms, msInd

    def generic_callback(self,value):
        print 'thing does not do anything',value

### Run the tests                                                                           
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    modelList = ['model1', 'model2']
    md = ModelDock(modelList)
    md.show()
    sys.exit(app.exec_())
    
