import sys
from PyQt4 import QtGui, QtCore
import numpy as np

from BasicWidgets import Tooltip

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

        ## data processing
        self.dataProcessingBtn = QtGui.QPushButton("Data")
        self.dataProcessingBtn.setMaximumWidth(self.eSize*1.5)
        self.dataProcessingBtn.setMinimumWidth(self.eSize*1.5)
        self.dataProcessingBtn.setAutoFillBackground(True)
        self.dataProcessingBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.dataProcessingTip = Tooltip(msg="Carry out channel selection, labeling, transformation and more",parent=self.dataProcessingBtn)
        hbox.addWidget(self.dataProcessingBtn)
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        self.connect(self.dataProcessingBtn, QtCore.SIGNAL('clicked()'),lambda x='data processing': self.btn_callback(x))

        ## quality assurance
        self.qualityAssuranceBtn = QtGui.QPushButton("QA")
        self.qualityAssuranceBtn.setMaximumWidth(self.eSize*1.5)
        self.qualityAssuranceBtn.setMinimumWidth(self.eSize*1.5)
        self.qualityAssuranceBtn.setAutoFillBackground(True)
        self.qualityAssuranceBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.qualityAssuranceTip = Tooltip(msg="Assess the quality of each file",parent=self.qualityAssuranceBtn)
        hbox.addWidget(self.qualityAssuranceBtn)
        self.connect(self.qualityAssuranceBtn, QtCore.SIGNAL('clicked()'),lambda x='quality assurance': self.btn_callback(x))

        ## model
        self.modelBtn = QtGui.QPushButton("Model")
        self.modelBtn.setMaximumWidth(self.eSize*1.5)
        self.modelBtn.setMinimumWidth(self.eSize*1.5)
        self.modelBtn.setAutoFillBackground(True)
        self.modelBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.modelTip = Tooltip(msg="Run a model on the fcs files",parent=self.modelBtn)
        hbox.addWidget(self.modelBtn)
        self.connect(self.modelBtn, QtCore.SIGNAL('clicked()'),lambda x='model': self.btn_callback(x))

        ## results navigation
        self.resultsNavigationBtn = QtGui.QPushButton("Results")
        self.resultsNavigationBtn.setMaximumWidth(self.eSize*1.5)
        self.resultsNavigationBtn.setMinimumWidth(self.eSize*1.5)
        self.resultsNavigationBtn.setAutoFillBackground(True)
        self.resultsNavigationTip = Tooltip(msg="Navigate the results of models run",parent=self.resultsNavigationBtn)
        self.resultsNavigationBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        hbox.addWidget(self.resultsNavigationBtn)
        self.connect(self.resultsNavigationBtn, QtCore.SIGNAL('clicked()'),lambda x='results navigation': self.btn_callback(x))

        ## summary and reports
        self.resultsSummaryBtn = QtGui.QPushButton("Summary")
        self.resultsSummaryBtn.setMaximumWidth(self.eSize*1.5)
        self.resultsSummaryBtn.setMinimumWidth(self.eSize*1.5)
        self.resultsSummaryBtn.setAutoFillBackground(True)
        self.resultsSummaryBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.resultsSummaryTip = Tooltip(msg="View summaries of the models and produce reports",parent=self.resultsSummaryBtn)
        hbox.addWidget(self.resultsSummaryBtn)
        self.connect(self.resultsSummaryBtn, QtCore.SIGNAL('clicked()'),lambda x='results summary': self.btn_callback(x))

        ## finalize layout
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox)
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(vbox)

    #def btn_callback(self,value):
    #    self.set_btn_highlight(value)

    def unset_all_highlights(self):
        self.dataProcessingBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.qualityAssuranceBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.modelBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.resultsNavigationBtn.setStyleSheet("QWidget { background-color: %s }" % None)
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
