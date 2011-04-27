#!/usr/bin/python                                                                                                                                                               
'''
Cytostream
textEntrySelector

A simple text entry box

'''

__author__ = "A Richards"

import sys,re
from PyQt4 import QtGui, QtCore
from cytostream.qtlib import RadioBtnWidget

class TextEntry(QtGui.QWidget):
    '''
    Class that handles the text entry.

    '''

    def __init__(self, label, color='white', parent=None, textEntryDefault=None, textEntryCallback=None):
        '''
        class constructor used to initialize this Qwidget child class
        '''

        QtGui.QWidget.__init__(self,parent)

        ## variables
        self.color = color

        ## setup layout
        vbox = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignLeft)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignLeft)
        
        ## text entry widgets
        self.mainLabel = QtGui.QLabel(label)
        self.entryBox = QtGui.QLineEdit()
        hbox1.addWidget(self.mainLabel)
        hbox2.addWidget(self.entryBox)

        ## handle default
        if textEntryDefault != None:
            self.entryBox.setText(textEntryDefault)

        ## finalize layout
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

        ## color the background
        palette = self.palette()
        role = self.backgroundRole()
        palette.setColor(role, QtGui.QColor(self.color))
        self.setPalette(palette)

    def get_text(self):
        '''
        returns current text
        '''

        return str(self.entryBox.text())

    def set_label(self,newLabel):
        '''
        sets or resets the widget label
        
        '''

        self.mainLabel.setText(newLabel)

    def generic_callback(self):
        print 'callback does not do anything yet'

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    label = 'example text'
    defaultText = '1000'
    te = TextEntry(label,textEntryDefault=defaultText)
    te.show()
    sys.exit(app.exec_())
