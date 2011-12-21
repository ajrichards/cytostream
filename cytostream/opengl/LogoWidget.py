#!/usr/bin/python

'''
Created on Jul 7, 2009
spiral example from
  author: Stou Sandalski (stou@icapsid.net)
  license:  Public Domain

'''

import math,sys
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4 import QtGui,QtCore
from PyQt4.QtOpenGL import *


class Helper:
    def __init__(self):
    
        gradient = QtGui.QLinearGradient(QtCore.QPointF(50, -20), QtCore.QPointF(80, 20))
        gradient.setColorAt(0.0, QtCore.Qt.white)
        #gradient.setColorAt(1.0, QtGui.QColor(0xa6, 0xce, 0x39))
        gradient.setColorAt(1.0, QtGui.QColor(10, 0, 80))

        self.background = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        self.circleBrush = QtGui.QBrush(gradient)
        self.circlePen = QtGui.QPen(QtCore.Qt.black)
        self.circlePen.setWidth(1)
        self.textPen = QtGui.QPen(QtCore.Qt.white)
        self.textFont = QtGui.QFont()
        self.textFont.setPixelSize(50)
    
    def paint(self, painter, event, elapsed):
        painter.fillRect(event.rect(), self.background)
        painter.translate(100, 100)

        painter.save()
        painter.setBrush(self.circleBrush)
        painter.setPen(self.circlePen)
        painter.rotate(elapsed * 0.030)

        r = elapsed/1000.0
        n = 30
        for i in range(n):
            painter.rotate(30)
            radius = 0 + 120.0*((i+r)/n)
            circleRadius = 1 + ((i+r)/n)*20
            painter.drawEllipse(QtCore.QRectF(radius, -circleRadius,
                                       circleRadius*2, circleRadius*2))
        
        painter.restore()
        
        painter.setPen(self.textPen)
        painter.setFont(self.textFont)
        painter.drawText(QtCore.QRect(-50, -50, 320, 400), QtCore.Qt.AlignCenter, "Cytostream")

class Widget(QtGui.QWidget):

    def __init__(self, helper, parent = None):
    
        QtGui.QWidget.__init__(self, parent)
        self.helper = helper
        self.elapsed = 0
        self.setFixedSize(400, 350)
    
    def animate(self):
        self.elapsed = (self.elapsed + self.sender().interval()) % 1000
        self.repaint()
    
    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.helper.paint(painter, event, self.elapsed)
        painter.end()

class Window(QtGui.QWidget):

    def __init__(self, parent = None):
    
        QtGui.QWidget.__init__(self, parent)
        
        helper = Helper()
        native = Widget(helper, self)
        layout = QtGui.QGridLayout()
        layout.addWidget(native, 0, 0)
        self.setLayout(layout)

        timer = QtCore.QTimer(self)
        self.connect(timer, QtCore.SIGNAL("timeout()"), native.animate)
        timer.start(50)

        self.setWindowTitle(self.tr("2D Painting on Native and OpenGL Widgets"))

class LogoWidget(QtGui.QWidget):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)

        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignCenter)

        ## initialize widget
        self.shapes = Window(self)

        ## add to layout
        hbox.addWidget(self.shapes)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    os = LogoWidget()
    os.show()
    sys.exit(app.exec_())
