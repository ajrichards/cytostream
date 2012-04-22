import sys,os,time,re
from PyQt4 import QtGui, QtCore
import numpy as np

class ThumbnailViewer(QtGui.QWidget):
    def __init__(self, parent, thumbDir, fileChannels,thumbsClean=True,viewScatterFn=None,mainWindow=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variabels 
        self.thumbDir = thumbDir
        self.fileChannels = fileChannels
        self.btns = {}
        
        thumbs = os.listdir(self.thumbDir)
        hbox = QtGui.QVBoxLayout()
        grid = QtGui.QGridLayout()

        if mainWindow == None:
            channels = self.fileChannels
        else:
            thumbnailsToView = mainWindow.log.log['thumbnails_to_view']
            channelInds = set([])
            for comp in thumbnailsToView:
                channelInds.update(comp)
            channels = np.array(self.fileChannels)[list(channelInds)]

        if len(channels) <= 4:
            self.thumbSize = 210
        elif len(channels) == 5:
            self.thumbSize = 160
        elif len(channels) == 6:
            self.thumbSize = 120
        elif len(channels) == 7:
            self.thumbSize = 90
        elif len(channels) == 8:
            self.thumbSize = 70
        elif len(channels) == 9:
            self.thumbSize = 60
        elif len(channels) == 10:
            self.thumbSize = 50
        elif len(channels) > 10:
            self.thumbSize = 40
        
        #self.thumbSize = int(round(self.thumbSize + (0.5 * float(self.thumbSize))))
        #print self.thumbSize
        
        for k in range(len(channels)):
            chan = channels[k]
            
            if k != len(channels)-1:
                labelCol = QtGui.QLabel(chan)
                labelCol.setMaximumWidth(self.thumbSize)
                labelCol.setMinimumWidth(self.thumbSize)
                labelCol.setAlignment(QtCore.Qt.AlignCenter)
                grid.addWidget(labelCol,0,k+1)
            if k != 0:
                labelRow = QtGui.QLabel(chan)
                labelRow.setMaximumHeight(self.thumbSize)
                labelRow.setMinimumHeight(self.thumbSize) 
                labelRow.setMaximumWidth(100)
                labelRow.setMinimumWidth(100) 
                labelRow.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight)
                grid.addWidget(labelRow,k+1,0)

        i,j = 0,0
        #for i in range(len(self.fileChannels)):
        #    chanI = self.fileChannels[i]
        #    for j in range(len(self.fileChannels)):
        #        chanJ = self.fileChannels[j]
        
        for i,chanI in enumerate(channels):
            for j,chanJ in enumerate(channels):
                if j >= i:
                    continue
                img = None
                for t in thumbs:
                    normalThumb = re.sub("#","_",t)
                    if re.search(chanI,normalThumb) and re.search(chanJ,normalThumb):
                        img = t
                
                imgBtn = QtGui.QPushButton()
                imgBtn.setMinimumSize(QtCore.QSize(self.thumbSize, self.thumbSize))
                imgBtn.setMaximumSize(QtCore.QSize(self.thumbSize, self.thumbSize))
                
                #if os.path.isfile(imgPath) == True:
                if img != None:
                    imgPath = os.path.join(self.thumbDir,img)
                    imgBtn.setIcon(QtGui.QIcon(imgPath))
                
                ## use icon size to add a small border around the button
                iconSize = int(round(self.thumbSize - (0.05 * float(self.thumbSize))))
                
                imgBtn.setIconSize(QtCore.QSize(iconSize, iconSize))
                if viewScatterFn != None and img != None:
                    self.connect(imgBtn, QtCore.SIGNAL('clicked()'),lambda x=img: viewScatterFn(img=x))
        
                grid.addWidget(imgBtn,i+1,j+1)
        
        self.setLayout(grid)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    baseDir = os.path.dirname(__file__)
    mode = 'results'
    homeDir = os.path.join(baseDir,'..','projects','utest')
    imgDir = os.path.join(homeDir,'figs')
    
    if os.path.isdir(homeDir) == False:
        print "ERROR:  home dir not available"

    if os.path.isdir(imgDir) == False:
        print "ERROR: demo image dir not available"

    print imgDir
    fileChannelList = ['FSC-H', 'SSC-H', 'FL1-H', 'FL2-H']
    tv = ThumbnailViewer(None, imgDir,fileChannelList)
    tv.show()
    sys.exit(app.exec_())
