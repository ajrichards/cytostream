import sys,os,time
from PyQt4 import QtGui, QtCore
from BasicWidgets import *
import numpy as np

class PipelineDock(QtGui.QWidget):

    def __init__(self, parent=None, eSize=35, btnCallBacks=None):
        QtGui.QWidget.__init__(self, parent)

        ## set variables
        self.eSize = eSize
        self.buff = 2.0
        self.btnColor = QtGui.QColor(255, 204, 153)
        self.btnCallBacks = btnCallBacks

        ## actions
        self.create_buttons()

        ## color
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor('black'))
        self.setPalette(palette)
        self.setAutoFillBackground(True)


    def create_buttons(self):
        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox = QtGui.QVBoxLayout()

        ## create buttons (7 to 1.5)
        self.dataProcessingBtn = QtGui.QPushButton("Data")
        self.dataProcessingBtn.setMaximumWidth(self.eSize*1.5)
        self.dataProcessingBtn.setMinimumWidth(self.eSize*1.5)
        self.dataProcessingBtn.setAutoFillBackground(True)
        hbox.addWidget(self.dataProcessingBtn)
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.connect(self.dataProcessingBtn, QtCore.SIGNAL('clicked()'),lambda x='data processing': self.btn_callback(x))

        self.qualityAssuranceBtn = QtGui.QPushButton("QA")
        self.qualityAssuranceBtn.setMaximumWidth(self.eSize*1.5)
        self.qualityAssuranceBtn.setMinimumWidth(self.eSize*1.5)
        self.qualityAssuranceBtn.setAutoFillBackground(True)
        hbox.addWidget(self.qualityAssuranceBtn)
        self.connect(self.qualityAssuranceBtn, QtCore.SIGNAL('clicked()'),lambda x='quality assurance': self.btn_callback(x))

        self.modelBtn = QtGui.QPushButton("Model")
        self.modelBtn.setMaximumWidth(self.eSize*1.5)
        self.modelBtn.setMinimumWidth(self.eSize*1.5)
        self.modelBtn.setAutoFillBackground(True)
        hbox.addWidget(self.modelBtn)
        self.connect(self.modelBtn, QtCore.SIGNAL('clicked()'),lambda x='model': self.btn_callback(x))

        self.resultsNavigationBtn = QtGui.QPushButton("Results")
        self.resultsNavigationBtn.setMaximumWidth(self.eSize*1.5)
        self.resultsNavigationBtn.setMinimumWidth(self.eSize*1.5)
        self.resultsNavigationBtn.setAutoFillBackground(True)
        hbox.addWidget(self.resultsNavigationBtn)
        self.connect(self.resultsNavigationBtn, QtCore.SIGNAL('clicked()'),lambda x='results navigation': self.btn_callback(x))

        ## finalize layout
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox)
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(vbox)

    #def btn_callback(self,value):
    #    self.set_btn_highlight(value)

    def unset_all_highlights(self):
        #self.dataProcessingBtn.setEnabled(True)
        #self.qualityAssuranceBtn.setEnabled(True)
        #self.modelBtn.setEnabled(True)
        #self.resultsNavigationBtn.setEnabled(True)
        self.dataProcessingBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.qualityAssuranceBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.modelBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.resultsNavigationBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        QtCore.QCoreApplication.processEvents()

    def set_btn_highlight(self,btnName):
        if btnName == 'data processing':
            self.unset_all_highlights()
            self.dataProcessingBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            #self.dataProcessingBtn.setEnabled(False)
           
        elif btnName == 'quality assurance':
            self.unset_all_highlights()
            self.qualityAssuranceBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            #self.qualityAssuranceBtn.setEnabled(False)

        elif btnName == 'model':
            self.unset_all_highlights()
            self.modelBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            #self.modelBtn.setEnabled(False)

        elif btnName == 'results navigation':
            self.unset_all_highlights()
            self.resultsNavigationBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            #self.resultsNavigationBtn.setEnabled(False)
        else:
            print 'ERROR: Invalid value in button callback - pipelinedock - %s'%value

        QtCore.QCoreApplication.processEvents()

    def btn_callback(self,btnName):
        goFlag = False
        if btnName == 'data processing':
            if self.btnCallBacks != None:
                goFlag = self.btnCallBacks[0]()
           
        elif btnName == 'quality assurance':
            if self.btnCallBacks != None:
                goFlag = self.btnCallBacks[1]()

        elif btnName == 'model':
            if self.btnCallBacks != None:
                goFlag = self.btnCallBacks[2]()

        elif btnName == 'results navigation':
            if self.btnCallBacks != None:
                goFlag = self.btnCallBacks[3]()
        else:
            print 'ERROR: Invalid value in button callback - pipelinedock - %s'%value

        if goFlag == True:
            self.set_btn_highlight(btnName)

        QtCore.QCoreApplication.processEvents()    

### Run the tests                                                                           
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pipelineDoc = PipelineDock()
    pipelineDoc.show()
    sys.exit(app.exec_())
