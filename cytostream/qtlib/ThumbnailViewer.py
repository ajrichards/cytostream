import sys,os,time,re
import Image
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.tools import get_official_name_match


class Thumbnail(QtGui.QWidget):
    def __init__(self, imgPath, thumbSize,xLabel=None,yLabel=None,parent=None,isDiagonal=False,callbackFn=None):
        QtGui.QWidget.__init__(self,parent)

        imgBtn = QtGui.QPushButton()
        grid = QtGui.QGridLayout()
        iconSize = thumbSize

        if os.path.isfile(imgPath) == True:
            imgBtn.setIcon(QtGui.QIcon(imgPath))
            img = os.path.split(imgPath)[-1]
            if callbackFn != None and isDiagonal == False:
                self.connect(imgBtn, QtCore.SIGNAL('clicked()'),lambda x=img: callbackFn(img=x))
        else:
            imgBtn.setIcon(QtGui.QIcon.fromTheme("image-missing"))

        imgBtn.setIconSize(QtCore.QSize(iconSize,iconSize))
        imgBtn.setMinimumSize(QtCore.QSize(iconSize,iconSize))
        imgBtn.setMaximumSize(QtCore.QSize(iconSize,iconSize))
       
        if yLabel != None and xLabel != None:
            grid.addWidget(QtGui.QLabel(yLabel),1,0)
            grid.addWidget(QtGui.QLabel(xLabel),0,1,QtCore.Qt.AlignCenter)
            grid.addWidget(imgBtn,1,1,QtCore.Qt.AlignCenter)
        elif yLabel != None:
            grid.addWidget(QtGui.QLabel(yLabel),0,0,QtCore.Qt.AlignCenter)
            grid.addWidget(imgBtn,1,0,QtCore.Qt.AlignCenter)
        elif xLabel != None:
            grid.addWidget(QtGui.QLabel(xLabel),0,0,QtCore.Qt.AlignCenter)
            grid.addWidget(imgBtn,0,1,QtCore.Qt.AlignCenter)
        else:
            grid.addWidget(imgBtn,0,0,QtCore.Qt.AlignCenter)

        ## finalize layout
        self.setLayout(grid)

class ThumbnailViewer(QtGui.QWidget):
    def __init__(self, parent, thumbDir,fileChannels,channelDict,thumbsClean=True,mainWindow=None):
        QtGui.QWidget.__init__(self,parent)

        if parent == None:
            self.parent = self
        else:
            self.parent = parent

        ## declare variabels 
        self.thumbDir = thumbDir
        self.fileChannels = fileChannels
        self.mainWindow = mainWindow
        self.btns = {}
        
        thumbs = os.listdir(self.thumbDir)
        grid = QtGui.QGridLayout()

        if mainWindow == None:
            channels = self.fileChannels
            callbackFn = None
            self.thumbSize = 100
        else:
            channels = self.mainWindow.log.log['default_thumb_channels']
            im = Image.open(os.path.join(self.thumbDir,thumbs[0]))
            self.thumbSize = max(im.size)
            callbackFn =  self.mainWindow.handle_show_plot

        ## get thumbsize
        for i in range(len(channels)):
            for j in range(len(channels)):
                img = "."

                chanI = channels[i]
                chanJ = channels[j]
                indI = channelDict[chanI]
                indJ = channelDict[chanJ]

                if i == j:
                    for t in thumbs:
                        if re.search("\_"+channels[i]+"\_thumb",t):
                            img = t
                else:
                    for t in thumbs:
                        if re.search("%s\_%s\_thumb"%(indJ,indI),t):
                            img = t
                            break
            
                xLabel,yLabel = None,None
                if j == 0:
                    xLabel = channels[i]
                if i == 0:
                    yLabel = channels[j]
            
                isDiagonal = False
                if i == j:
                    isDiagonal = True

                imgPath = os.path.join(self.thumbDir,img)

                #print i,channels[i],j,channels[j],imgPath

                if os.path.exists(imgPath) == False:
                    print "WARNING: Can not find imgPath in ThumbnailViewer", imgPath

                thumbWidget = Thumbnail(imgPath,self.thumbSize,parent=None,xLabel=xLabel,yLabel=yLabel,
                                        isDiagonal=isDiagonal,callbackFn=callbackFn) 
                grid.addWidget(thumbWidget,i,j)
        
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
