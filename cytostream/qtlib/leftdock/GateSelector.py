#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
highlights a given gate
also shows a line plot of the gate

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore
import numpy as np
from cytostream.tools import get_indices_from_gate, get_clusters_via_gate

class GateSelector(QtGui.QWidget):
    '''
    Class that handles the users selection and subsequent visualization of a given gate.  Upon selection variables 
    corresponding to the selected gate are changed.  These actions are carried out by functions in the MainWindow widget.
    '''

    def __init__(self,gateList,color='white',parent=None,gateDefault='None',mainWindow=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.color = color
        self.gateList = ['None'] + gateList
        self.parent = parent
        self.mainWindow = mainWindow
        self.checkBoxes1 = {}
        self.checkBoxes2 = {}

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        col1Box = QtGui.QVBoxLayout()
        col1Box.setAlignment(QtCore.Qt.AlignLeft)
        col2Box = QtGui.QVBoxLayout()
        col2Box.setAlignment(QtCore.Qt.AlignLeft)
       
        ## gate event selector
        hbox1.addWidget(QtGui.QLabel('gate viewer'))
        
        ## gate names
        #for ftr in self.gateList[1:]:
        #    self.checkBoxes0[ftr] = QtGui.QCheckBox(ftr)
        #    self.connect(self.checkBoxes1[ftr],QtCore.SIGNAL('stateChanged(int)'), self.checkbox1_callback)
        
        ## gate line drawer
        for ftr in self.gateList[1:]:
            self.checkBoxes1[ftr] = QtGui.QCheckBox(ftr)
            self.connect(self.checkBoxes1[ftr],QtCore.SIGNAL('stateChanged(int)'), self.checkbox1_callback)

        for ftr in self.gateList[1:]:
            col1Box.addWidget(self.checkBoxes1[ftr])
       
        ## gate event parser
        for ftr in self.gateList[1:]:
            self.checkBoxes2[ftr] = QtGui.QCheckBox(ftr)
            self.connect(self.checkBoxes2[ftr],QtCore.SIGNAL('stateChanged(int)'), self.checkbox2_callback)

        for ftr in self.gateList[1:]:
            col2Box.addWidget(self.checkBoxes2[ftr])
       
        ## finalize layout
        hbox2.addLayout(col1Box)
        hbox2.addLayout(col2Box)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def get_selected_gate(self):
        sfInd = self.gateSelector.currentIndex()
        sf = str(self.gateSelector.currentText())

        return sf

    def get_checked_gates_1(self):
        '''
        returns a 0,1 array of checked gates
        along with the corresponding gate name list
        '''
        
        checkStates = []
        gateNameList = []
        selectedGates = []

        for gateName,cb in self.checkBoxes1.iteritems():
            if cb.isChecked() == True:
                selectedGates.append(gateName)

        return selectedGates

    def get_checked_gates_2(self):
        '''
        returns a 0,1 array of checked gates
        along with the corresponding gate name list
        '''
        
        checkStates = []
        gateNameList = []
        selectedGates = []

        for gateName,cb in self.checkBoxes2.iteritems():
            if cb.isChecked() == True:
                selectedGates.append(gateName)

        return selectedGates


    def generic_callback(self):
        print 'callback does not do anything yet'

    def checkbox1_callback(self):
        '''
        shows the actual gate as a line plot
        '''

        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
            return

        self.mainWindow.transitions.begin_wait()
        selectedFile = self.mainWindow.controller.log.log['selected_file']
        if selectedFile == '':
            return

        selectedGates = self.get_checked_gates_1()     
        numPlots = self.mainWindow.log.log['num_subplots']

        if self.mainWindow.log.log['selected_plot'] == None:
            self.mainWindow.log.log['selected_plot'] = '1'
            self.mainWindow.controller.save()
        selectedPlot = self.mainWindow.log.log['selected_plot']
            
        if selectedPlot == '*':
            fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
            for selectedPlot in [str(i+1) for i in range(int(numPlots))]:
                cp = self.mainWindow.nwv.plots[selectedPlot]
                cp.gate_clear_callback()

                if len(selectedGates) == 0:
                    continue

                for selectedGate in selectedGates:
                    cGate = self.mainWindow.controller.load_gate(selectedGate)
                    if cGate['channel1'] != cp.selectedChannel1:
                        continue
                    if cGate['channel2'] != cp.selectedChannel2:
                        continue

                    cp.gate_set_callback([cGate['verts']])
        else:
            
            cp = self.mainWindow.nwv.plots[selectedPlot]
            fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
            cp.gate_clear_callback()

            if len(selectedGates) > 0:
                for selectedGate in selectedGates:
                    cGate = self.mainWindow.controller.load_gate(selectedGate)
                    if cGate['channel1'] != cp.selectedChannel1:
                        continue
                    if cGate['channel2'] != cp.selectedChannel2:
                        continue

                    cp.gate_set_callback([cGate['verts']])

        self.mainWindow.transitions.end_wait()

    def checkbox2_callback(self):
        '''
        highlights for a given plot the events in a given gate
        '''
  
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
            return

        self.mainWindow.transitions.begin_wait()
        selectedFile = self.mainWindow.controller.log.log['selected_file']
        if selectedFile == '':
            return

        selectedGates = self.get_checked_gates_2()     
        numPlots = self.mainWindow.log.log['num_subplots']

        if self.mainWindow.log.log['selected_plot'] == None:
            self.mainWindow.log.log['selected_plot'] = '1'
            self.mainWindow.controller.save()
        selectedPlot = self.mainWindow.log.log['selected_plot']
        
        if selectedPlot == '*':
            for selectedPlot in [str(i+1) for i in range(int(numPlots))]:
                cp = self.mainWindow.nwv.plots[selectedPlot]
                selectedFile = cp.selectedFileName
                fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                fileEvents = cp.eventsList[fileIndex]
                fileLabels = cp.labels
                currentCentroids = cp.currentCentroids[0]
                meanMat = None
                meanMatLabels = []
                keys = list(set(currentCentroids.keys()))
                keys.sort()
                for key in keys:
                    item = currentCentroids[key]
                    if meanMat == None:
                        meanMat = item
                    else:
                        meanMat = np.vstack([meanMat,item])
                    meanMatLabels.append(key)

                meanMatLabels = np.array(meanMatLabels)
                if len(selectedGates) > 0:
                    allGateClusters = None
                    for selectedGate in selectedGates:
                        cGate = self.mainWindow.controller.load_gate(selectedGate)
                        gateClusters = get_clusters_via_gate(meanMat[:,[cGate['channel1'],cGate['channel2']]],meanMatLabels,cGate['verts'])
                        if allGateClusters == None:
                            allGateClusters = set(gateClusters)
                        else:
                            allGateClusters = allGateClusters.intersection(set(gateClusters))

                    if allGateClusters != None:
                        allGateClusters = list(allGateClusters)
                else:
                    allGateClusters = None

                self.mainWindow.log.log['plots_to_view_highlights'][int(selectedPlot)-1] = allGateClusters
                self.mainWindow.controller.save()
                cp.selectedHighlight = allGateClusters
                cp.draw(selectedFile=selectedFile)
        else:
            cp = self.mainWindow.nwv.plots[selectedPlot]
            selectedFile = cp.selectedFileName
            fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
            fileEvents = cp.eventsList[fileIndex]
            fileLabels = cp.labels
            currentCentroids = cp.currentCentroids[0]
            meanMat = None
            meanMatLabels = []
            keys = list(set(currentCentroids.keys()))
            keys.sort()
            for key in keys:
                item = currentCentroids[key]
                if meanMat == None:
                    meanMat = item
                else:
                    meanMat = np.vstack([meanMat,item])
                meanMatLabels.append(key)
            meanMatLabels = np.array(meanMatLabels)
        
            if len(selectedGates) > 0:
                allGateClusters = None
                for selectedGate in selectedGates:
                    cGate = self.mainWindow.controller.load_gate(selectedGate)
                    gateClusters = get_clusters_via_gate(meanMat[:,[cGate['channel1'],cGate['channel2']]],meanMatLabels,cGate['verts'])
                    if allGateClusters == None:
                        allGateClusters = set(gateClusters)
                    else:
                        allGateClusters = allGateClusters.intersection(set(gateClusters))

                if allGateClusters != None:
                    allGateClusters = list(allGateClusters)
            else:
                allGateClusters = None

            self.mainWindow.log.log['plots_to_view_highlights'][int(selectedPlot)-1] = allGateClusters
            self.mainWindow.controller.save()
            cp.selectedHighlight = allGateClusters
            cp.draw(selectedFile=selectedFile)
            
        self.mainWindow.transitions.end_wait()
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    gateList = ['1','2','3']
    cs = GateSelector(gateList)
    cs.show()
    sys.exit(app.exec_())
