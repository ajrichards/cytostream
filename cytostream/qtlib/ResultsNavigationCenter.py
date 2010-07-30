import sys,re
from PyQt4 import QtGui, QtCore

class ResultsNavigationCenter(QtGui.QWidget):
    def __init__(self, modelsRun, parent=None, infoBtnFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## variables
        modelsRun = [re.sub("\.pickle|\.csv","",mr) for mr in modelsRun]

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

        self.hbl1.addWidget(QtGui.QLabel('Select model to navigate'))
        
        self.modelSelector = QtGui.QComboBox(self)
        self.modelSelector.setMaximumWidth(200)
        self.modelSelector.setMinimumWidth(200)
        for model in modelsRun:
            self.modelSelector.addItem(model)
        self.hbl2.addWidget(self.modelSelector)

        self.navBtn = QtGui.QPushButton("Navigate selected model", self)
        self.navBtn.setMaximumWidth(200)
        self.navBtn.setMinimumWidth(200)
        self.hbl3.addWidget(self.navBtn)
        #self.connect(self.button,QtCore.SIGNAL('clicked()'), self.onStart)

        self.infoBtn = QtGui.QPushButton("Show selected model info", self)
        self.infoBtn.setMaximumWidth(200)
        self.infoBtn.setMinimumWidth(200)
        self.hbl4.addWidget(self.infoBtn)
        if infoBtnFn != None:
            self.connect(self.infoBtn, QtCore.SIGNAL('clicked()'),infoBtnFn)
        
        # finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addLayout(self.hbl2)
        self.vbl.addLayout(self.hbl3)
        self.vbl.addLayout(self.hbl4)
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.vbl)

    def generic_callback(self):
        print 'This button does nothing'

    #def set_message(self,msg):
    #    hbl = QtGui.QHBoxLayout()
    #    hbl.setAlignment(QtCore.Qt.AlignCenter)
    #    self.msg = QtGui.QLabel(msg)
    #    hbl.addWidget(self.msg)
    #    self.vbl.addLayout(hbl)

    def get_selected_model(self):
        smInd = self.modelSelector.currentIndex()
        sm = str(self.modelSelector.currentText())
        #sm = sm + ".pickle"

        return sm, smInd



### Run the tests                                                                                                                                                                
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    modelsRun = ['model1-dpmm-cpu','model2-dpmm-cpu','model3-dpmm-cpu']
    rnc = ResultsNavigationCenter(modelsRun)
    rnc.show()
    sys.exit(app.exec_())
    
