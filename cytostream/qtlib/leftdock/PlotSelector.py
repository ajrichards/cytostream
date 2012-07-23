#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
PlotSelector 

A combobox widget to select from different files

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore
import numpy as np

class PlotSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of plots.  Upon selection variables corresponding to the
    selected plots are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self,plotList,color='white',parent=None,modelsRun=None,plotDefault='1',mainWindow=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.color = color
        self.plotList = plotList
        self.parent = parent
        self.mainWindow = mainWindow

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
   
        ## plot selector
        hbox1.addWidget(QtGui.QLabel('selected plot'))
        self.plotSelector = QtGui.QComboBox(self)
        
        if len(self.plotList) > 1:
            self.plotList = ['*']+[str(int(f)) for f in self.plotList]
        else:
            self.plotList = [str(int(f)) for f in self.plotList]
        for plotName in self.plotList:
            self.plotSelector.addItem(plotName)

        hbox1.addWidget(self.plotSelector)
     
        if plotDefault != None:
            plotDefault = str(plotDefault)
            if self.plotList.__contains__(plotDefault):
                self.plotSelector.setCurrentIndex(self.plotList.index(plotDefault))
            else:
                print "ERROR: in plot selector - bad specified plotDefault", plotDefault

        self.connect(self.plotSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.plot_selector_callback)    

        ## finalize layout
        vbox.addLayout(hbox1)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def get_selected_plot(self):
        sfInd = self.plotSelector.currentIndex()
        sf = str(self.plotSelector.currentText())

        return sf,sfInd

    def generic_callback(self):
        print 'callback does not do anything yet'

    def ensure_correct_options(self,numPlots):
        self.plotSelector.clear()
        self.plotList = [str(i+1) for i in range(numPlots)]
        if len(self.plotList) > 1:
            self.plotList = ['*']+[str(int(f)) for f in self.plotList]
        else:
            self.plotList = [str(int(f)) for f in self.plotList]
      
        for plotName in self.plotList:
            self.plotSelector.addItem(plotName)

    def plot_selector_callback(self):
        '''
        callback function for PlotSelector movement
        '''
        selectedPlot,selectedPlotInd = self.get_selected_plot()
        if selectedPlot == '':
            return None
        selectedPlot = str(selectedPlot)

        if self.mainWindow == None:
            print "INFO: PlotSelector does nothing without main window"
            return 

        self.mainWindow.transitions.begin_wait()
        self.mainWindow.controller.log.log['selected_plot'] = selectedPlot
        self.mainWindow.controller.save()

        ## adjust x and y axes as different plots are selected
        if selectedPlot != '*' and selectedPlot != None:
            cp = self.mainWindow.nwv.plots[selectedPlot]
            channel1 = cp.selectedChannel1
            channel2 = cp.selectedChannel2
            self.mainWindow.channelSelector.channel1Selector.setCurrentIndex(channel1)
            self.mainWindow.channelSelector.channel2Selector.setCurrentIndex(channel2)

        self.mainWindow.transitions.end_wait()
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    plotList = ['1','2','3']
    modelsRun = ['plotName_sampleID_modelID1', 'plotName_sampleID_modelID2']
    fs = PlotSelector(plotList)
    fs.show()
    sys.exit(app.exec_())
