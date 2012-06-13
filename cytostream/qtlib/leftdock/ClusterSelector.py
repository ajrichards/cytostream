#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
HighlightClusterSelector 

A combobox widget to select from clusters

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore

class ClusterSelector(QtGui.QWidget):
    '''
    Class that handles the users selection and subsequent visualization of a given cluster.  Upon selection variables 
    corresponding to the selected cluster are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self,clusterList,color='white',parent=None,clusterDefault='None',mainWindow=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.color = color
        self.clusterList = ['None'] + [str(int(f)) for f in clusterList]
        self.parent = parent
        self.mainWindow = mainWindow

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
   
        ## cluster selector
        hbox1.addWidget(QtGui.QLabel('cluster'))
        self.clusterSelector = QtGui.QComboBox(self)
        
        for clusterName in self.clusterList:
            self.clusterSelector.addItem(clusterName)

        hbox1.addWidget(self.clusterSelector)
     
        if clusterDefault != None:
            clusterDefault = str(clusterDefault)
            if self.clusterList.__contains__(clusterDefault):
                self.clusterSelector.setCurrentIndex(self.clusterList.index(clusterDefault))
            else:
                print "ERROR: in cluster selector - bad specified clusterDefault", clusterDefault

        #if selectionFn == None:
        #    selectionFn = self.generic_callback
        self.connect(self.clusterSelector,QtCore.SIGNAL("currentIndexChanged(int)"), self.cluster_selector_callback)    

        ## finalize layout
        vbox.addLayout(hbox1)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def get_selected_cluster(self):
        sfInd = self.clusterSelector.currentIndex()
        sf = str(self.clusterSelector.currentText())

        return sf

    def generic_callback(self):
        print 'callback does not do anything yet'

    def cluster_selector_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            
            selectedFile = self.mainWindow.controller.log.log['selected_file']
            if selectedFile == '':
                return

            self.selectedHighlight = self.get_selected_cluster() 
            numPlots = self.mainWindow.log.log['num_subplots']

            if self.mainWindow.log.log['selected_plot'] == None:
                self.mainWindow.log.log['selected_plot'] = '1'
                self.mainWindow.controller.save()
            selectedPlot = self.mainWindow.log.log['selected_plot']

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

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    clusterList = ['1','2','3']
    cs = ClusterSelector(clusterList)
    cs.show()
    sys.exit(app.exec_())
