import sys,os,time,re
from PyQt4 import QtGui, QtCore

class FileSelector(QtGui.QWidget):
    def __init__(self, fileList, color='white', parent=None, modelsRun=None, fileDefault=None, selectionFn=None, showModelSelector=False, modelDefault=None):
        QtGui.QWidget.__init__(self,parent)
        self.modelSelector = None
        self.modelsRun = modelsRun
        self.color = color
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        
        ## error checking
        if showModelSelector == True and self.modelsRun == None:
            print "ERROR: must specify modelsRun if ModelSelector is true"

        ## file selector
        hbox1.addWidget(QtGui.QLabel('File Selector'))
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        self.fileSelector = QtGui.QComboBox(self)
        self.fileSelector.setMaximumWidth(150)
        for fileName in fileList:
            self.fileSelector.addItem(fileName)

        hbox2.addWidget(self.fileSelector)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)

        if fileDefault != None:
            if fileList.__contains__(fileDefault):
                self.fileSelector.setCurrentIndex(fileList.index(fileDefault))
            else:
                print "ERROR: in file selector - bad specified fileDefault"

        if selectionFn == None:
            selectionFn = self.generic_callback
        self.connect(self.fileSelector, QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)    

        if showModelSelector != False:
            ## model selector label
            self.modelsRun = [re.sub("\.pickle|\.csv","",mr) for mr in self.modelsRun]
            self.modelsRun = list(set([re.split("_",mr)[-2] + "_" + re.split("_",mr)[-1] for mr in self.modelsRun]))
            hbox3 = QtGui.QHBoxLayout()
            hbox4 = QtGui.QHBoxLayout()
            hbox3.addWidget(QtGui.QLabel('Model Selector'))
            hbox3.setAlignment(QtCore.Qt.AlignCenter)

            ## model selector combobox  
            self.modelSelector = QtGui.QComboBox(self)
            self.modelSelector.setMaximumWidth(180)
            self.modelSelector.setMinimumWidth(180)
            for model in self.modelsRun:
                self.modelSelector.addItem(model)
            hbox4.addWidget(self.modelSelector)
            hbox4.setAlignment(QtCore.Qt.AlignCenter)

            if modelDefault != None:
                if self.modelsRun.__contains__(modelDefault):
                    self.modelSelector.setCurrentIndex(self.modelsRun.index(modelDefault))
                else:
                    print "ERROR: in dpd - bad specified modelDefault"

            if selectionFn != None:
                self.selectionFn = self.generic_callback
            self.connect(self.modelSelector,QtCore.SIGNAL("currentIndexChanged(int)"), selectionFn)

        ## finalize layout                           
        vbox.setAlignment(QtCore.Qt.AlignTop)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        if showModelSelector == True:
             vbox.addLayout(hbox3)
             vbox.addLayout(hbox4)
    
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def set_refresh_thumbs_fn(self,refreshFn):
        self.connect(self.fileSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn)
        if self.modelSelector != None:
            self.connect(self.modelSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn) 
        

    def get_selected_file(self):
        sfInd = self.fileSelector.currentIndex()
        sf = str(self.fileSelector.currentText())

        return sf, sfInd

    def get_selected_model(self):
        smInd = self.modelSelector.currentIndex()
        sm = str(self.modelSelector.currentText())
        print 'inside model selector (fileselector)'
        print self.modelsRun,sm
        
        return sm, smInd

    def generic_callback(self):
        print 'callback does not do anything yet'


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    fileList = ['file1', 'file2']
    modelsRun = ['model1', 'model2']
    fs = FileSelector(fileList,modelsRun = modelsRun, showModelSelector=True)
    fs.show()
    sys.exit(app.exec_())
