import sys,os,time,re
from PyQt4 import QtGui, QtCore

class ThumbnailViewer(QtGui.QWidget):
    def __init__(self, parent, thumbDir, fileChannels,thumbsClean=True,viewScatterFn=None):
        QtGui.QWidget.__init__(self,parent)

        ## declare variabels 
        self.thumbDir = thumbDir

        if len(fileChannels) <= 4:
            self.thumbSize = 210
        elif len(fileChannels) == 5:
            self.thumbSize = 160
        elif len(fileChannels) == 6:
            self.thumbSize = 120
        elif len(fileChannels) == 7:
            self.thumbSize = 90
        elif len(fileChannels) > 7:
            self.thumbSize = 70

        self.fileChannels = fileChannels
        self.btns = {}
        
        thumbs = os.listdir(self.thumbDir)
        hbox = QtGui.QVBoxLayout()
        grid = QtGui.QGridLayout()
        
        for k in range(len(self.fileChannels)):
            chan = self.fileChannels[k]
            
            if k != len(self.fileChannels)-1:
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
        for i in range(len(self.fileChannels)):
            chanI = self.fileChannels[i]
            for j in range(len(self.fileChannels)):
                chanJ = self.fileChannels[j]
                if j >= i:
                    continue
                img = None
                for t in thumbs:
                    if re.search(chanI,t) and re.search(chanJ,t):
                        img = t
                
                imgBtn = QtGui.QPushButton()
                imgBtn.setMinimumSize(QtCore.QSize(self.thumbSize, self.thumbSize))
                imgBtn.setMaximumSize(QtCore.QSize(self.thumbSize, self.thumbSize))
                imgBtn.setIcon(QtGui.QIcon(os.path.join(self.thumbDir,img)))
                imgBtn.setIconSize(QtCore.QSize(self.thumbSize, self.thumbSize))
                if viewScatterFn != None:
                    self.connect(imgBtn, QtCore.SIGNAL('clicked()'),lambda x=img: viewScatterFn(img=x))
        
                grid.addWidget(imgBtn,i+1,j+1)
        
        self.setLayout(grid)

class ImgButton(QtGui.QAbstractButton):
    def __init__(self, pixmap, parent=None):
        super(ImgButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    if os.path.isdir(os.path.join("..","projects","Demo","figs")):
        imgDir = os.path.join("..","projects","Demo","figs")
    elif os.path.isdir(os.path.join(".","projects","Demo","figs")):
        imgDir = os.path.join(".","projects","Demo","figs")
    elif os.path.isdir(os.path.join("..","Flow-GCMC","projects","Demo","figs")):
        imgDir = os.path.join(".","projects","Demo","figs")
    else:
        print "ERROR: demo image dir not available"

    print imgDir
    fileChannelList = ['FSC-H', 'SSC-H', 'FL1-H', 'FL2-H']
    tv = ThumbnailViewer(None, imgDir,fileChannelList)
    tv.show()
    sys.exit(app.exec_())
