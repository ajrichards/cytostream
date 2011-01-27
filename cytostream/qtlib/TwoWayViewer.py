import sys,os,time,re
from PyQt4 import QtGui, QtCore
from random import randint

from cytostream.qtlib import MultiplePlotter

class TwoWayViewer(QtGui.QWidget):

    def __init__(self,homeDir,selectedFile,channel1,channel2,subsample,modelName=None,parent=None,background=False,modelType=None,mode='qa'):

        QtGui.QWidget.__init__(self,parent)

        ## input variables
        self.setWindowTitle('Multiple Plotter')
        self.homeDir = homeDir
        self.subsample = subsample
        self.parent = parent
        self.background = background
        self.modelType = modelType
        self.mode = mode

        ## class variables 
        self.selectedChannel1 = int(channel1)
        self.selectedChannel2 = int(channel2)
        self.selectedFile = selectedFile
        self.selectedModelName = modelName
        self.selectedHighlight = "None"

        ## setup layouts
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl = QtGui.QHBoxLayout()
        self.hbl.setAlignment(QtCore.Qt.AlignCenter)
        
        self.mp1 = MultiplePlotter(self.homeDir,self.selectedFile,self.selectedChannel1,self.selectedChannel2,self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self)
        self.hbl.addWidget(self.mp1)

        self.mp2 = MultiplePlotter(self.homeDir,self.selectedFile,self.selectedChannel1,self.selectedChannel2,self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self)
        self.hbl.addWidget(self.mp2)

        ## finalize layout
        self.vbl.addLayout(self.hbl)
        self.setLayout(self.vbl)

### Run the tests 
if __name__ == '__main__':

    ## check that unittests were run and necessary data is present
    baseDir = os.path.dirname(__file__)
    mode = 'results'
    projectID = 'utest'
    selectedFile = "3FITC_4PE_004"
    modelName = 'run1'
    channel1 = 0
    channel2 = 3
    modelType = 'modes'
    subsample = 1000
    homeDir = os.path.join(baseDir,'..','projects','utest')

    ## check that model is present
    modelChk = os.path.join(baseDir,'..','projects','utest','models','%s_%s.log'%(selectedFile,modelName))
    if os.path.isfile(modelChk) == False:
        print "ERROR: Model not present - (Re)run unit tests"
        print modelChk
        sys.exit()

    app = QtGui.QApplication(sys.argv)

    if mode == 'qa':
        modelType,modelName = None, None

    twv = TwoWayViewer(homeDir,selectedFile,channel1,channel2,subsample,background=True,modelName=modelName,modelType=modelType,mode=mode)

    twv.show()
    sys.exit(app.exec_())

    #app = QtGui.QApplication(sys.argv)
    #bp = TwoWayViewer(None)
    #bp.show()
    #sys.exit(app.exec_())
    
