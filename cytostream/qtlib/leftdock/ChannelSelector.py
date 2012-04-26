#!/usr/bin/python                                                                                                                                                               
'''
Cytostream 
ChannelSelector 

A combobox widget to select from different files

'''
__author__ = "A Richards"


import sys,re
from PyQt4 import QtGui, QtCore

class ChannelSelector(QtGui.QWidget):
    '''
    Class that handles the users selection of channels.  Upon selection variables corresponding to the
    selected channels are changed.  These actions are carried out by functions in the MainWindow widget.

    '''

    def __init__(self,channelList,color='white',parent=None,mainWindow=None,channel1Default=None,channel2Default=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## declare variables
        self.color = color
        self.channelList = channelList
        self.parent = parent
        self.mainWindow = mainWindow

        ## setup layouts
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)

        ## x-ax channel selector
        hbox1.addWidget(QtGui.QLabel('x-ax'))
        self.channel1Selector = QtGui.QComboBox(self)
        for channelName in self.channelList:
            self.channel1Selector.addItem(channelName)
        hbox1.addWidget(self.channel1Selector)
     
        ## handle defaults
        if channel1Default != None:
            if type(channel1Default) == type(1):
                self.channel1Selector.setCurrentIndex(channel1Default)
            else:
                print "ERROR: in channel 1 selector - bad specified channelDefault", channel1Default,type(channel1Default)

        ## y -ax channel selector
        hbox2.addWidget(QtGui.QLabel('y-ax'))
        self.channel2Selector = QtGui.QComboBox(self)
        for channelName in self.channelList:
            self.channel2Selector.addItem(channelName)
        hbox2.addWidget(self.channel2Selector)
     
        if channel2Default != None:
            if type(channel2Default) == type(1):
                self.channel2Selector.setCurrentIndex(channel2Default)
            else:
                print "ERROR: in channel 2 selector - bad specified channelDefault", channel2Default,type(channel1Default)

        ## callbacks
        self.connect(self.channel1Selector,QtCore.SIGNAL("currentIndexChanged(int)"), self.channel1_selector_callback)
        self.connect(self.channel2Selector,QtCore.SIGNAL("currentIndexChanged(int)"), self.channel2_selector_callback)

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def channel1_selector_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            selectedFile = self.mainWindow.controller.log.log['selected_file']
            if selectedFile == '':
                return

            numPlots = self.mainWindow.log.log['num_subplots']

            if self.mainWindow.log.log['selected_plot'] == None:
                self.mainWindow.log.log['selected_plot'] = '1'
                self.mainWindow.controller.save()

            selectedPlot = self.mainWindow.log.log['selected_plot']
            vizMode = self.mainWindow.vizModeSelector.get_selected()

            if vizMode != 'plot':
                return

            channel1,channel2 = self.get_selected_channels()
            
            if selectedPlot == '*':
                for selectedPlot in [str(i+1) for i in range(int(numPlots))]:
                    channel2 = self.mainWindow.nwv.plots[selectedPlot].selectedChannel2
                    self.mainWindow.controller.log.log['plots_to_view_channels'][int(selectedPlot)-1] = (channel1,channel2)
                    self.mainWindow.controller.save()
                    self.mainWindow.nwv.plots[selectedPlot].selectedChannel1 = channel1
                    self.mainWindow.nwv.plots[selectedPlot].selectedFile = selectedFile
                    self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
            else:
                fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                channel2 = self.mainWindow.nwv.plots[selectedPlot].selectedChannel2
                self.mainWindow.controller.log.log['plots_to_view_channels'][int(selectedPlot)-1] = (channel1,channel2)
                self.mainWindow.controller.save()
                self.mainWindow.nwv.plots[selectedPlot].selectedChannel1 = channel1
                self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)


    def channel2_selector_callback(self):
        if self.mainWindow == None:
            print 'callback does not do anything without main widget present'
        else:
            selectedFile = self.mainWindow.controller.log.log['selected_file']
            if selectedFile == '':
                return

            numPlots = self.mainWindow.log.log['num_subplots']

            if self.mainWindow.log.log['selected_plot'] == None:
                self.mainWindow.log.log['selected_plot'] = '1'
                self.mainWindow.controller.save()

            selectedPlot = self.mainWindow.log.log['selected_plot']
            vizMode = self.mainWindow.vizModeSelector.get_selected()

            if vizMode != 'plot':
                return

            channel1,channel2 = self.get_selected_channels()
            
            if selectedPlot == '*':
                for selectedPlot in [str(i+1) for i in range(int(numPlots))]:
                    channel1 = self.mainWindow.nwv.plots[selectedPlot].selectedChannel1
                    self.mainWindow.controller.log.log['plots_to_view_channels'][int(selectedPlot)-1] = (channel1,channel2)
                    self.mainWindow.controller.save()
                    self.mainWindow.nwv.plots[selectedPlot].selectedChannel2 = channel2
                    self.mainWindow.nwv.plots[selectedPlot].selectedFile = selectedFile
                    self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)
            else:
                fileIndex = self.mainWindow.controller.fileNameList.index(selectedFile)
                channel1 = self.mainWindow.nwv.plots[selectedPlot].selectedChannel1
                self.mainWindow.controller.log.log['plots_to_view_channels'][int(selectedPlot)-1] = (channel1,channel2)
                self.mainWindow.controller.save()
                self.mainWindow.nwv.plots[selectedPlot].selectedChannel2 = channel2
                self.mainWindow.nwv.plots[selectedPlot].draw(selectedFile=selectedFile)

    def get_selected_channels(self):
        channel1 = self.channel1Selector.currentIndex()
        channel2 = self.channel2Selector.currentIndex()

        return channel1,channel2

    def generic_callback(self):
        print 'callback does not do anything yet'

    def ensure_correct_options(self,numChannels):
        self.channelSelector.clear()
        self.channelList = [str(i+1) for i in range(numChannels)]
        if len(self.channelList) > 1:
            self.channelList = ['*']+[str(int(f)) for f in self.channelList]
        else:
            self.channelList = [str(int(f)) for f in self.channelList]
      
        for channelName in self.channelList:
            self.channelSelector.addItem(channelName)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    channelList = ['1','2','3']
    modelsRun = ['channelName_sampleID_modelID1', 'channelName_sampleID_modelID2']
    fs = ChannelSelector(channelList)
    fs.show()
    sys.exit(app.exec_())
