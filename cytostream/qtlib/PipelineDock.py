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
        self.btnColor = QtGui.QColor(0, 200, 200)
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

    def btn_callback(self,value):
        self.set_btn_highlight(value)

    def unset_all_highlights(self):
        self.dataProcessingBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.qualityAssuranceBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.modelBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        self.resultsNavigationBtn.setStyleSheet("QWidget { background-color: %s }" % None)
        QtCore.QCoreApplication.processEvents()

    def set_btn_highlight(self,btnName):
        if btnName == 'data processing':
            #self.unset_all_highlights()
            #self.dataProcessingBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            if self.btnCallBacks != None:
                print self.btnCallBacks[0]()
        elif btnName == 'quality assurance':
            #self.unset_all_highlights()
            #self.qualityAssuranceBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            if self.btnCallBacks != None:
                print self.btnCallBacks[1]()
        elif btnName == 'model':
            #self.unset_all_highlights()
            #self.modelBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            if self.btnCallBacks != None:
                print self.btnCallBacks[2]()
        elif btnName == 'results navigation':
            #self.unset_all_highlights()
            #self.resultsNavigationBtn.setStyleSheet("QWidget { background-color: %s }" % self.btnColor.name())
            if self.btnCallBacks != None:
                print self.btnCallBacks[3]()
        else:
            print 'ERROR: Invalid value in button callback - pipelinedock - %s'%value

        QtCore.QCoreApplication.processEvents()

    #def paintEvent(self, event):
    #    
    #    paint = QtGui.QPainter()
    #    print dir(paint)
    #    
    #    ## params for paint rendering
    #    #print 'antialias', paint.Antialiasing
    #    #print 'smooth transform', paint.SmoothPixmapTransform
    #    #print 'high quality', paint.HighQualityAntialiasing
    #    #print 'non cosmetic def', paint.NonCosmeticDefaultPen
    #
    #    paint.begin(self)
    #    
    #    color = QtGui.QColor(0, 0, 0)
    #    color.setNamedColor('#d4d4d4')
    #    #pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
    #    #paint.setPen(pen)
    #    paint.setPen(QtCore.Qt.black)
    #    normalColor = QtGui.QColor(0, 0, 180, 150)
    #    highlightColor = QtGui.QColor(0, 255, 255, 150)
    # 
    #    ## Data processing
    #    paint.setBrush(normalColor)
    #    paint.drawEllipse(0, 0, 2.0*self.eSize, self.eSize)
    #
    #    paint.drawLine(self.eSize, self.eSize, self.eSize, 2.0*self.eSize)
    #
    #    ## Quality Assurance
    #    paint.setBrush(normalColor)
    #    paint.drawEllipse(0, 2.0*self.eSize, 2.0*self.eSize, self.eSize)
    #
    #    paint.drawLine(self.eSize, 3.0*self.eSize, self.eSize, 4.0*self.eSize)
    #
    #    ## Model
    #    paint.setBrush(normalColor)
    #    paint.drawEllipse(0,4.0*self.eSize, 2.0*self.eSize, self.eSize)
    #
    #    paint.drawLine(self.eSize, 5.0*self.eSize, self.eSize, 6.0*self.eSize)
    #
    #    ## Results Navigation
    #    paint.setBrush(normalColor)
    #    paint.drawEllipse(0,6.0*self.eSize, 2.0*self.eSize, self.eSize)
    #    #paint.drawLine(5.0*self.eSize, 0.5*self.eSize, 6.0*self.eSize, 0.5*self.eSize)
    #   
    #    paint.end()
    

### Run the tests                                                                           
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pipelineDoc = PipelineDock()
    pipelineDoc.show()
    sys.exit(app.exec_())
