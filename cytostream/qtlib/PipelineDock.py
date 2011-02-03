import sys
from PyQt4 import QtGui, QtCore
import numpy as np

from BasicWidgets import Tooltip

class PipelineDock(QtGui.QWidget):

    def __init__(self, parent=None, appColor='black', eSize=35, btnCallBacks=None):
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
        palette.setColor(role, QtGui.QColor(appColor))
        self.setPalette(palette)
        self.setAutoFillBackground(True)


    def create_buttons(self):
        ## setup layout
        hbl = QtGui.QVBoxLayout()
        hboxTop = QtGui.QVBoxLayout()
        hboxTop.setAlignment(QtCore.Qt.AlignCenter)
        vboxTop = QtGui.QHBoxLayout()
        vboxTop.addLayout(hboxTop)
        vboxTop.setAlignment(QtCore.Qt.AlignTop)

        hboxCenter = QtGui.QHBoxLayout()
        hboxCenter.setAlignment(QtCore.Qt.AlignCenter)
        vboxCenter = QtGui.QVBoxLayout()
        vboxCenter.addLayout(hboxCenter)
        vboxCenter.setAlignment(QtCore.Qt.AlignCenter)

        hboxBottom = QtGui.QHBoxLayout()
        hboxBottom.setAlignment(QtCore.Qt.AlignCenter)
        vboxBottom = QtGui.QVBoxLayout()
        vboxBottom.addLayout(hboxBottom)
        vboxBottom.setAlignment(QtCore.Qt.AlignBottom)

        ## data processing
        self.dataProcessingBtn = QtGui.QPushButton("Data")
        self.dataProcessingBtn.setMaximumWidth(self.eSize)
        self.dataProcessingBtn.setMinimumWidth(self.eSize)
        self.dataProcessingBtn.setAutoFillBackground(True)
        self.dataProcessingBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.dataProcessingTip = Tooltip(msg="Carry out channel selection, labeling, transformation and more",parent=self.dataProcessingBtn)
        hboxTop.addWidget(self.dataProcessingBtn)
        self.connect(self.dataProcessingBtn, QtCore.SIGNAL('clicked()'),lambda x='data processing': self.btn_callback(x))

        ## quality assurance
        self.qualityAssuranceBtn = QtGui.QPushButton("QA")
        self.qualityAssuranceBtn.setMaximumWidth(self.eSize)
        self.qualityAssuranceBtn.setMinimumWidth(self.eSize)
        self.qualityAssuranceBtn.setAutoFillBackground(True)
        self.qualityAssuranceBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.qualityAssuranceTip = Tooltip(msg="Assess the quality of each file",parent=self.qualityAssuranceBtn)
        hboxTop.addWidget(self.qualityAssuranceBtn)
        self.connect(self.qualityAssuranceBtn, QtCore.SIGNAL('clicked()'),lambda x='quality assurance': self.btn_callback(x))

        ## model
        self.modelBtn = QtGui.QPushButton("Model")
        self.modelBtn.setMaximumWidth(self.eSize)
        self.modelBtn.setMinimumWidth(self.eSize)
        self.modelBtn.setAutoFillBackground(True)
        self.modelBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.modelTip = Tooltip(msg="Run a model on the fcs files",parent=self.modelBtn)
        hboxTop.addWidget(self.modelBtn)
        self.connect(self.modelBtn, QtCore.SIGNAL('clicked()'),lambda x='model': self.btn_callback(x))

        ## results navigation
        self.resultsNavigationBtn = QtGui.QPushButton("Results")
        self.resultsNavigationBtn.setMaximumWidth(self.eSize)
        self.resultsNavigationBtn.setMinimumWidth(self.eSize)
        self.resultsNavigationBtn.setAutoFillBackground(True)
        self.resultsNavigationTip = Tooltip(msg="Navigate the results of models run",parent=self.resultsNavigationBtn)
        self.resultsNavigationBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        hboxTop.addWidget(self.resultsNavigationBtn)
        self.connect(self.resultsNavigationBtn, QtCore.SIGNAL('clicked()'),lambda x='results navigation': self.btn_callback(x))

        ## summary and reports
        self.resultsSummaryBtn = QtGui.QPushButton("Summary")
        self.resultsSummaryBtn.setMaximumWidth(self.eSize)
        self.resultsSummaryBtn.setMinimumWidth(self.eSize)
        self.resultsSummaryBtn.setAutoFillBackground(True)
        self.resultsSummaryBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.resultsSummaryTip = Tooltip(msg="View summaries of the models and produce reports",parent=self.resultsSummaryBtn)
        hboxTop.addWidget(self.resultsSummaryBtn)
        self.connect(self.resultsSummaryBtn, QtCore.SIGNAL('clicked()'),lambda x='results summary': self.btn_callback(x))


         ## continue btn      
        self.contBtn = QtGui.QPushButton("Continue")
        self.contBtn.setMaximumWidth(100)
        hboxBottom.addWidget(self.contBtn)
        #contBtnFn = mainWindow.generic_callback
        #mainWindow.connect(mainWindow.contBtn, QtCore.SIGNAL('clicked()'),contBtnFn)

        ## finalize layout
        hbl.addLayout(vboxTop)
        hbl.addLayout(vboxCenter)
        hbl.addLayout(vboxBottom)

        #vbox.addLayout(hbox)
        #vbox.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(hbl)

    #def btn_callback(self,value):
    #    self.set_btn_highlight(value)

    def unset_all_highlights(self):
        self.dataProcessingBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.qualityAssuranceBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.modelBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.resultsNavigationBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.resultsSummaryBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        QtCore.QCoreApplication.processEvents()

    def set_btn_highlight(self,btnName):
        if btnName == 'data processing':
            self.unset_all_highlights()
            self.dataProcessingBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
        elif btnName == 'quality assurance':
            self.unset_all_highlights()
            self.qualityAssuranceBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
        elif btnName == 'model':
            self.unset_all_highlights()
            self.modelBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
        elif btnName == 'results navigation':
            self.unset_all_highlights()
            self.resultsNavigationBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
        elif btnName == 'results summary':
            self.unset_all_highlights()
            self.resultsSummaryBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
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
        elif btnName == 'results summary':
            if self.btnCallBacks != None:
                goFlag = self.btnCallBacks[4]()
        else:
            print 'ERROR: Invalid value in button callback - pipelinedock - %s'%value

        if goFlag == True:
            self.set_btn_highlight(btnName)

        #QtCore.QCoreApplication.processEvents()

    def inactivate_all(self):
        self.dataProcessingBtn.setEnabled(False)
        self.qualityAssuranceBtn.setEnabled(False)
        self.modelBtn.setEnabled(False)
        self.resultsNavigationBtn.setEnabled(False)
        self.resultsSummaryBtn.setEnabled(False)

    def activate_all(self):
        self.dataProcessingBtn.setEnabled(True)
        self.qualityAssuranceBtn.setEnabled(True)
        self.modelBtn.setEnabled(True)
        self.resultsNavigationBtn.setEnabled(True)
        self.resultsSummaryBtn.setEnabled(True)


### Run the tests                                                                           
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pipelineDoc = PipelineDock()
    pipelineDoc.show()
    sys.exit(app.exec_())
