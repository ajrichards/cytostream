#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
SubsampleSelector

A combobox widget to select from different subsample sizes

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore

class SubsampleSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of subsamples. Upon selection variables corresponding to the
    selected subsamples are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self, subsampleList, color='white', parent=None, subsampleDefault=None, mainWindow=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        subsampleList = [str(int(float(ss))) for ss in subsampleList[:-1]] + [subsampleList[-1]]
        self.mainWindow = mainWindow
        
        ## setup layouts
        self.color = color
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## subsample selector
        hbox1.addWidget(QtGui.QLabel('subsample'))
        self.subsampleSelector = QtGui.QComboBox(self)
        
        for subsampleName in subsampleList:
            self.subsampleSelector.addItem(subsampleName)

        hbox2.addWidget(self.subsampleSelector)

        if self.mainWindow == None:
            subsampleDefault = subsampleList[0]
        else:
            currentState = self.mainWindow.controller.log.log['current_state']
            if currentState == 'Quality Assurance':
                subsampleDefault = self.mainWindow.controller.log.log['subsample_qa']
            else:
                subsampleDefault = self.mainWindow.controller.log.log['subsample_analysis']

        if subsampleDefault != None and subsampleDefault == 'original':
            subsampleDefault = "All Data"
            self.subsampleSelector.setCurrentIndex(subsampleList.index(subsampleDefault))
        else:
            subsampleDefault = str(int(float(subsampleDefault)))
            if subsampleList.__contains__(subsampleDefault):
                self.subsampleSelector.setCurrentIndex(subsampleList.index(subsampleDefault))
            else:
                self.subsampleSelector.setCurrentIndex(0)

        self.connect(self.subsampleSelector, QtCore.SIGNAL("currentIndexChanged(int)"), self.subsample_selector_callback)    

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
        self.connect(self.subsampleSelector, QtCore.SIGNAL("currentIndexChanged(int)"), refreshFn)

    def get_selected_subsample(self):
        sfInd = self.subsampleSelector.currentIndex()
        sf = str(self.subsampleSelector.currentText())

        return sf, sfInd

    def subsample_selector_callback(self):

        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:        
            selectedFile = self.mainWindow.controller.log.log['selected_file']
            if selectedFile == '':
                return

            self.mainWindow.transitions.begin_wait()
            currentState = self.mainWindow.controller.log.log['current_state']
            self.mainWindow.log.log['selected_file'] = selectedFile
            self.mainWindow.controller.save()
            numPlots = self.mainWindow.log.log['num_subplots']
            
            if self.mainWindow.log.log['selected_plot'] == None:
                self.mainWindow.log.log['selected_plot'] = '1'
                self.mainWindow.controller.save()

            selectedPlot = self.mainWindow.controller.log.log['selected_plot']
            vizMode = self.mainWindow.vizModeSelector.get_selected()

            if vizMode == 'thumbnails':
                return
            
            selectedSubsample = self.get_selected_subsample()
            print 'changing subsample for ', selectedPlot, selectedSubsample

            if vizMode == 'plot':
                if selectedPlot == '*':
                    for selectedPlot in [str(i+1) for i in range(int(numPlots))]:
                        fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                        self.mainWindow.controller.log.log['plots_to_view_files'][int(selectedPlot)-1] = fileIndex
                        self.mainWindow.controller.save()
                        self.mainWindow.nwv.plots[selectedPlot].selectedFile = selectedFile
                        self.mainWindow.nwv.plots[selectedPlot].subsample = selectedSubsample
                        self.mainWindow.nwv.plots[selectedPlot].initialize(selectedFile)
                        self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
                else:
                    pass
                    fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                    self.mainWindow.controller.log.log['plots_to_view_files'][int(selectedPlot)-1] = fileIndex
                    self.mainWindow.controller.save()
                    self.mainWindow.nwv.plots[selectedPlot].selectedFile = selectedFile
                    self.mainWindow.nwv.plots[selectedPlot].subsample = selectedSubsample
                    self.mainWindow.nwv.plots[selectedPlot].initialize(selectedFile)
                    self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
            else:
                print "ERROR: invalid visMode detected in subsample detector"

            self.mainWindow.transitions.end_wait()

    def get_selected_subsample(self):
        sf = str(self.subsampleSelector.currentText())
        if sf == 'All Data':
            sf = 'original'
        return sf

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    subsampleList = ['10000', '7500000']
    fs = SubsampleSelector(subsampleList)
    fs.show()
    sys.exit(app.exec_())
