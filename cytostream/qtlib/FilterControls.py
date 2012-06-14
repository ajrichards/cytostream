import sys,os,time,re
from PyQt4 import QtGui, QtCore
from random import randint

class FilterControls(QtGui.QWidget):
    def __init__(self, mainWindow=None,parent=None):
        QtGui.QWidget.__init__(self,parent)


        ## variables
        self.parent = parent
        self.mainWindow = mainWindow
        maxWidth = 100

        ##  init the ui
        self.filteringLabel = QtGui.QLabel("Filter controls")
        self.gateSelector = QtGui.QComboBox(self)
        for gt in ["None","Draw","Polygon", "Rectangle", "Square"]:
            self.gateSelector.addItem(gt)

        self.gateSelector.setCurrentIndex(0)
        if self.parent != None:
            self.connect(self.gateSelector, QtCore.SIGNAL('activated(int)'),self.parent.gate_select_callback)
        
        self.gate_set = QtGui.QPushButton("Set")
        if self.parent != None:
            self.connect(self.gate_set, QtCore.SIGNAL('clicked()'), self.parent.gate_set_callback)
        self.gate_set.setEnabled(False)
        self.gate_set.setMaximumWidth(maxWidth*0.6)
        self.gate_set.setMinimumWidth(maxWidth*0.6)

        self.gate_clear = QtGui.QPushButton("Clear")
        if self.parent != None:
            self.connect(self.gate_clear, QtCore.SIGNAL('clicked()'), self.parent.gate_clear_callback)
        self.gate_clear.setEnabled(False)
        self.gate_clear.setMaximumWidth(maxWidth*0.6)
        self.gate_clear.setMinimumWidth(maxWidth*0.6)

        self.gate_save = QtGui.QPushButton("Save Gate")
        if self.parent != None:
            self.connect(self.gate_save, QtCore.SIGNAL('clicked()'), self.parent.gate_save_callback)
        self.gate_save.setEnabled(False)

        self.defaultVert = 6
        self.vertSliderLabel = QtGui.QLabel(str(self.defaultVert))
        self.vertSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.vertSlider.setRange(3,8)
        self.vertSlider.setValue(self.defaultVert)
        self.vertSlider.setTracking(True)
        self.vertSlider.setTickPosition(QtGui.QSlider.TicksBothSides)
        if self.parent != None:
            self.connect(self.vertSlider, QtCore.SIGNAL('valueChanged(int)'), self.parent.gate_vert_selector_callback)
        self.vertSlider.setEnabled(False)
        self.vertSlider.setMaximumWidth(maxWidth)
        self.vertSlider.setMinimumWidth(maxWidth)

        ## layout
        masterBox = QtGui.QVBoxLayout()
        hboxGate0 = QtGui.QHBoxLayout()
        hboxGate0.setAlignment(QtCore.Qt.AlignCenter)
        hboxGate0.addWidget(self.filteringLabel)
        hboxGate1 = QtGui.QHBoxLayout()
        hboxGate1.setAlignment(QtCore.Qt.AlignCenter)
        hboxGate1.addWidget(self.gateSelector)
        hboxGate1.addWidget(self.gate_set)
        hboxGate2 = QtGui.QHBoxLayout()
        hboxGate2.setAlignment(QtCore.Qt.AlignCenter)
        hboxGate2.addWidget(QtGui.QLabel(" "))
        hboxGate3 = QtGui.QHBoxLayout()
        hboxGate3.setAlignment(QtCore.Qt.AlignCenter)
        hboxGate3.addWidget(self.vertSliderLabel)
        hboxGate4 = QtGui.QHBoxLayout()
        hboxGate4.setAlignment(QtCore.Qt.AlignCenter)
        hboxGate4.addWidget(self.vertSlider)
        hboxGate5 = QtGui.QHBoxLayout()
        hboxGate5.setAlignment(QtCore.Qt.AlignCenter)
        hboxGate5.addWidget(self.gate_save)
        hboxGate6 = QtGui.QHBoxLayout()
        hboxGate6.setAlignment(QtCore.Qt.AlignCenter)
        hboxGate6.addWidget(self.gate_clear)

        masterBox.addLayout(hboxGate0)
        masterBox.addLayout(hboxGate1)
        masterBox.addLayout(hboxGate2)
        masterBox.addLayout(hboxGate3)
        masterBox.addLayout(hboxGate4)
        masterBox.addLayout(hboxGate5)
        masterBox.addLayout(hboxGate6)

        self.setLayout(masterBox)

    def change_label(self,newLabel):
        self.label.setText(newLabel)

    def generic_callback(self):
        print 'this callback does nothing'

### Run the tests 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    bp = FilterControls()
    bp.show()
    sys.exit(app.exec_())
    
