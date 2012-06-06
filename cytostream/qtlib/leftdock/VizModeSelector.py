#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
VizModeSelector

A bar of radio widgets to select from different visualization modes

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget

class VizModeSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of the visualization mode. Upon selection appropriate 
    changes are made to enable smooth transitions from one visualization mode to another.

    '''

    def __init__(self, modeList, color='white',parent=None,modeDefault=None,mainWindow=None,numSubplotsDefault='1'):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## error checking
        if modeDefault != None and modeList.__contains__(modeDefault) == False:
            print "ERROR: ModeSelector - bad default specified",modeDefault
            return None

        ## variables
        self.modeList = modeList
        self.mainWindow = mainWindow
        self.color = color
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)
        self.numSubplotsList = [str(i) for i in range(1,13)]

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.setAlignment(QtCore.Qt.AlignLeft)
        
        ## mode selector
        hbox1.addWidget(QtGui.QLabel('visualization mode'))
        self.modeSelector = RadioBtnWidget(self.modeList,parent=self,callbackFn=self.viz_mode_selector_callback_1)
        hbox2.addWidget(self.modeSelector)
        if modeDefault != None:
            self.set_checked(modeDefault)

        ## num subplots selector 
        self.numSubplotsSelector = QtGui.QComboBox(self)             
        for numSubplots in self.numSubplotsList:
            self.numSubplotsSelector.addItem(numSubplots)
        hbox3.addWidget(QtGui.QLabel('subplots'))
        hbox3.addWidget(self.numSubplotsSelector)

        self.update_num_subplots(numSubplotsDefault)
        self.connect(self.numSubplotsSelector, QtCore.SIGNAL("currentIndexChanged(int)"), self.viz_mode_selector_callback_2) 

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3) 
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def viz_mode_selector_callback_1(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:

            ## ensure num subplots are saved when changed
            numPlots = self.get_num_subplots()
            self.mainWindow.controller.log.log['num_subplots'] = str(numPlots)
            self.mainWindow.controller.save()

            selectedFile = self.mainWindow.controller.log.log['selected_file']
            if selectedFile == '':
                return
            
            if self.mainWindow.controller.log.log['selected_plot'] == None:
                self.mainWindow.controller.log.log['selected_plot'] = '1'
            selectedPlot = self.mainWindow.controller.log.log['selected_plot']
            vizMode = self.get_selected()

            ## make sure plotSelector displays correct options
            self.mainWindow.plotSelector.ensure_correct_options(int(numPlots)) 

            if vizMode == 'plot':
                self.mainWindow.handle_show_plot()
            elif vizMode == 'thumbnails':
                if self.mainWindow.controller.log.log['current_state'] == 'Quality Assurance':
                    self.mainWindow.display_thumbnails()
                else:
                    print "Check VizModeSelector callback for appropriate move"
            else:
                print "ERROR: invalid visMode detected"

    def viz_mode_selector_callback_2(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:

            ## ensure num subplots are saved when changed
            numPlots = self.get_num_subplots()
            self.mainWindow.controller.log.log['num_subplots'] = str(numPlots)
            self.mainWindow.controller.save()

            selectedFile = self.mainWindow.controller.log.log['selected_file']
            if selectedFile == '':
                return
            
            if self.mainWindow.controller.log.log['selected_plot'] == None:
                self.mainWindow.controller.log.log['selected_plot'] = '1'
            selectedPlot = self.mainWindow.controller.log.log['selected_plot']
            vizMode = self.get_selected()

            ## make sure plotSelector displays correct options
            self.mainWindow.plotSelector.ensure_correct_options(int(numPlots)) 

            if vizMode == 'plot':
                self.mainWindow.handle_show_plot()

    def update_num_subplots(self,numSubplotsDefault):
        '''
        force the number of subplots to a value
        '''

        numSubplotsDefault = str(numSubplotsDefault)
        if self.numSubplotsList.__contains__(numSubplotsDefault):
            self.numSubplotsSelector.setCurrentIndex(self.numSubplotsList.index(numSubplotsDefault))
        else:
            print "ERROR: in vizModeSelector - bad specified default", numSubplotsDefault

    def get_selected(self):
        return self.modeSelector.selectedItem

    def set_checked(self,modeLabel):
        if self.modeList.__contains__(modeLabel) == False:
            print "ERROR: ModeSelector - bad mode label in set_checked"
            return None

        self.modeSelector.btns[modeLabel].setChecked(True)
        self.modeSelector.selectedItem = modeLabel

    def generic_callback(self):
        print 'callback does not do anything yet'

    def get_num_subplots(self):
        return str(self.numSubplotsSelector.currentText())


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    modeList = ['mode1', 'mode2']
    ms = VizModeSelector(modeList)
    ms.show()
    sys.exit(app.exec_())
