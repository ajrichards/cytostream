import sys,os,time,re
from PyQt4 import QtGui, QtCore

class ModelSelector(QtGui.QWidget):
    def __init__(self, modelsRun, color='white', parent=None, modelDefault=None, selectionFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables 
        modelsRun = [re.sub("\.pickle|\.csv","",mr) for mr in modelsRun]

        self.color = color
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignTop)
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        
        ## model selector label
        hbox1.addWidget(QtGui.QLabel('Model Selector'))
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        
        ## model selector combobox
        self.modelSelector = QtGui.QComboBox(self)
        self.modelSelector.setMaximumWidth(180)
        self.modelSelector.setMinimumWidth(180)
        for model in modelsRun:
            self.modelSelector.addItem(model)
        hbox2.addWidget(self.modelSelector)

        if modelDefault != None:
            if modelsRun.__contains__(modelDefault):
                self.modelSelector.setCurrentIndex(modelsRun.index(modelDefault))
            else:
                print "ERROR: in dpd - bad specified modelDefault"
        
        if selectionFn != None:
            self.connect(self.modelSelector,QtCore.SIGNAL('activated(QString)'), selectionFn)
        
        ## finalize layout                                                                                                                                                 

        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)


    def get_selected_model(self):
        smInd = self.modelSelector.currentIndex()
        sm = str(self.modelSelector.currentText())
    
        return sm, smInd


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    modelsRun = ['model1-dpmm-cpu','model2-dpmm-cpu','model3-dpmm-cpu']
    ms = ModelSelector(modelsRun)
    ms.show()
    sys.exit(app.exec_())
