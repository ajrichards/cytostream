#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
FileSelector 

A combobox widget to select from different files

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore

class FileSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of files.  Upon selection variables corresponding to the
    selected files are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, fileList, color='white', mainWindow=None, parent=None, modelsRun=None, fileDefault=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.color = color
        self.fileList = fileList
        self.parent = parent
        self.mainWindow = mainWindow

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)     
   
        ## file selector
        hbox1.addWidget(QtGui.QLabel('file'))
        self.fileSelector = QtGui.QComboBox(self)
        
        self.fileList = [re.sub("\.fcs","",f) for f in self.fileList]
        for fileName in self.fileList:
            self.fileSelector.addItem(fileName)

        hbox2.addWidget(self.fileSelector)
     
        if fileDefault != None:
            fileDefault = re.sub("\.fcs","",fileDefault)
            if self.fileList.__contains__(fileDefault):
                self.fileSelector.setCurrentIndex(self.fileList.index(fileDefault))
            else:
                print "ERROR: in file selector - bad specified fileDefault", fileDefault

        self.connect(self.fileSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.file_selector_callback)

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)    
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
        sf = str(self.fileSelector.currentText())
        return sf

    def file_selector_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
            return

        self.mainWindow.transitions.begin_wait()
        selectedFile = self.get_selected_file()
        if selectedFile == '':
            return
        self.mainWindow.log.log['selected_file'] = selectedFile
        self.mainWindow.controller.save()
        numPlots = self.mainWindow.log.log['num_subplots']
            
        if self.mainWindow.log.log['selected_plot'] == None:
            self.mainWindow.log.log['selected_plot'] = '1'
            self.mainWindow.controller.save()
        selectedPlot = self.mainWindow.log.log['selected_plot']
        vizMode = self.mainWindow.vizModeSelector.get_selected()

        if vizMode == 'plot':
            if selectedPlot == '*':
                for selectedPlot in [str(i+1) for i in range(int(numPlots))]:
                    fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                    self.mainWindow.controller.log.log['plots_to_view_files'][int(selectedPlot)-1] = fileIndex
                    self.mainWindow.controller.save()
                    self.mainWindow.nwv.plots[selectedPlot].selectedFile = selectedFile
                    self.mainWindow.nwv.plots[selectedPlot].initialize(selectedFile)
                    self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
            else:
                fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                self.mainWindow.controller.log.log['plots_to_view_files'][int(selectedPlot)-1] = fileIndex
                self.mainWindow.controller.save()
                self.mainWindow.nwv.plots[selectedPlot].selectedFile = selectedFile
                self.mainWindow.nwv.plots[selectedPlot].initialize(selectedFile)
                self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
        elif vizMode == 'thumbnails':
            if self.mainWindow.log.log['current_state'] == 'Quality Assurance':
                self.mainWindow.display_thumbnails()
            else:
                print "Check FileSelector callback for appropriate move"
        else:
            print "ERROR: invalid visMode detected"

        self.mainWindow.transitions.begin_wait()

    def generic_callback(self):
        print 'callback does not do anything yet'


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    fileList = ['file1', 'file2']
    modelsRun = ['fileName_sampleID_modelID1', 'fileName_sampleID_modelID2']
    fs = FileSelector(fileList)
    fs.show()
    sys.exit(app.exec_())
