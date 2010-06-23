import sys,os,time
from PyQt4 import QtGui, QtCore

class FileSelector(QtGui.QWidget):
    def __init__(self, fileList, color='white', parent=None, fileDefault=None, selectionFn=None):
        QtGui.QWidget.__init__(self,parent)

        self.color = color
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QVBoxLayout()
        hbox2 = QtGui.QVBoxLayout()
        
        ## file selector
        hbox1.addWidget(QtGui.QLabel('File Selector'))
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox1)
        self.fileSelector = QtGui.QComboBox(self)
        self.fileSelector.setMaximumWidth(150)
        for fileName in fileList:
            self.fileSelector.addItem(fileName)

        hbox2.addWidget(self.fileSelector)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(hbox2)

        if fileDefault != None:
            if fileList.__contains__(fileDefault):
                self.fileSelector.setCurrentIndex(fileList.index(fileDefault))
            else:
                print "ERROR: in file selector - bad specified fileDefault"

        if selectionFn != None:
            #self.connect(self.fileSelector,QtCore.SIGNAL('activated(QString)'), selectionFn)
            #self.connect(self.fileSelector,QtCore.SIGNAL('clicked()'), selectionFn)
            self.connect(self.fileSelector, QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)


        ## finalize layout                                                                                                                                                 
        vbox.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)


    def get_selected_file(self):
        sfInd = self.fileSelector.currentIndex()
        sf = str(self.fileSelector.currentText())

        return sf, sfInd


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    fileList = ['file1', 'file2']
    
    fs = FileSelector(fileList)
    fs.show()
    sys.exit(app.exec_())
