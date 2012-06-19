#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
highlights a given gate

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore

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

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
   
        ## gate selector
        hbox1.addWidget(QtGui.QLabel('gate   '))
        self.gateSelector = QtGui.QComboBox(self)
        
        for gateName in self.gateList:
            self.gateSelector.addItem(gateName)

        hbox1.addWidget(self.gateSelector)
     
        if gateDefault != None:
            gateDefault = str(gateDefault)
            if self.gateList.__contains__(gateDefault):
                self.gateSelector.setCurrentIndex(self.gateList.index(gateDefault))
            else:
                print "ERROR: in gate selector - bad specified gateDefault", gateDefault

        self.connect(self.gateSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.gate_selector_callback)    

        ## finalize layout
        vbox.addLayout(hbox1)
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

    def generic_callback(self):
        print 'callback does not do anything yet'

    def gate_selector_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            
            selectedFile = self.mainWindow.controller.log.log['selected_file']
            if selectedFile == '':
                return

            selectedGate = self.get_selected_gate() 
            numPlots = self.mainWindow.log.log['num_subplots']

            if self.mainWindow.log.log['selected_plot'] == None:
                self.mainWindow.log.log['selected_plot'] = '1'
                self.mainWindow.controller.save()
            selectedPlot = self.mainWindow.log.log['selected_plot']
            
            print 'showing gate', selectedGate

            '''
            if selectedPlot == '*':
                for selectedPlot in [str(i+1) for i in range(int(numPlots))]:
                    fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                    if self.selectedHighlight == 'None':
                        self.mainWindow.controller.log.log['plots_to_view_highlights'][int(selectedPlot)-1] = 'None'
                        self.mainWindow.nwv.plots[selectedPlot].selectedHighlight = self.selectedHighlight
                    else:
                        self.mainWindow.log.log['plots_to_view_highlights'][int(selectedPlot)-1] = int(self.selectedHighlight)
                        self.mainWindow.nwv.plots[selectedPlot].selectedHighlight = [str(self.selectedHighlight)]
                    self.mainWindow.controller.save()
                    self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
            else:
                fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                if self.selectedHighlight == 'None':
                    self.mainWindow.controller.log.log['plots_to_view_highlights'][int(selectedPlot)-1] = 'None'
                    self.mainWindow.nwv.plots[selectedPlot].selectedHighlight = self.selectedHighlight
                else:
                    self.mainWindow.log.log['plots_to_view_highlights'][int(selectedPlot)-1] = int(self.selectedHighlight)
                    self.mainWindow.nwv.plots[selectedPlot].selectedHighlight = [str(self.selectedHighlight)]

                self.mainWindow.controller.save()
                self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
            '''

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    gateList = ['1','2','3']
    cs = GateSelector(gateList)
    cs.show()
    sys.exit(app.exec_())
