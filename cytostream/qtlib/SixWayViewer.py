import sys,os,time,re
from PyQt4 import QtGui, QtCore
from random import randint

from cytostream.qtlib import MultiplePlotter

class SixWayViewer(QtGui.QWidget):

    def __init__(self,homeDir,selectedFile,chans1,chans2,subsample,modelName=None,parent=None,background=False,modelType=None,mode='qa'):

        QtGui.QWidget.__init__(self,parent)

        ## input variables
        self.setWindowTitle('Six Way Plotter')
        self.homeDir = homeDir
        self.subsample = subsample
        self.parent = parent
        self.background = background
        self.modelType = modelType
        self.mode = mode

        ## class variables 
        self.selectedFile = selectedFile
        self.selectedModelName = modelName
        self.selectedHighlight = "None"

        ## setup layouts
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl1 = QtGui.QHBoxLayout()
        self.hbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.hbl2 = QtGui.QHBoxLayout()
        self.hbl2.setAlignment(QtCore.Qt.AlignCenter)

        self.mp1 = MultiplePlotter(self.homeDir,self.selectedFile,chans1[0],chans2[0],self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self,
                                   showNavBar=False)
        self.hbl1.addWidget(self.mp1)

        self.mp2 = MultiplePlotter(self.homeDir,self.selectedFile,chans1[1],chans2[1],self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self,
                                   showNavBar=False)
        self.hbl1.addWidget(self.mp2)

        self.mp3 = MultiplePlotter(self.homeDir,self.selectedFile,chans1[2],chans2[2],self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self,
                                   showNavBar=False)
        self.hbl1.addWidget(self.mp3)

        self.mp4 = MultiplePlotter(self.homeDir,self.selectedFile,chans1[3],chans2[3],self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self,
                                   showNavBar=False)
        self.hbl2.addWidget(self.mp4)

        self.mp5 = MultiplePlotter(self.homeDir,self.selectedFile,chans1[4],chans2[4],self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self,
                                   showNavBar=False)
        self.hbl2.addWidget(self.mp5)

        self.mp6 = MultiplePlotter(self.homeDir,self.selectedFile,chans1[5],chans2[5],self.subsample,background=self.background,
                                   modelName=self.selectedModelName,modelType=self.modelType,mode=self.mode,parent=self,
                                   showNavBar=False)
        self.hbl2.addWidget(self.mp6)

        ## finalize layout
        self.vbl.addLayout(self.hbl1)
        self.vbl.addLayout(self.hbl2)
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
        sys.exit()

    app = QtGui.QApplication(sys.argv)

    if mode == 'qa':
        modelType,modelName = None, None

    chans1 = [channel1,channel1,channel1,channel1,channel1,channel1]
    chans2 = [channel2,channel2,channel2,channel2,channel2,channel2]
    swv = SixWayViewer(homeDir,selectedFile,chans1,chans2,subsample,background=True,modelName=modelName,modelType=modelType,mode=mode)

    swv.show()
    sys.exit(app.exec_())
