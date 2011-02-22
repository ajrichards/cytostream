import sys,os
from PyQt4 import QtGui
from PyQt4 import QtCore


class RadioBtnWidget(QtGui.QWidget):

    def __init__(self,btnLabels,parent=None,default=None,callbackFn=None,color='white'):
        QtGui.QWidget.__init__(self,parent)

        if default != None and btnLabels.__contains__(default) == False:
            print "ERROR: RadioBtnWidget - bad default specified",default 
            return None

        vbox = QtGui.QVBoxLayout()
        self.selectedItem = None
        self.btnLabels = btnLabels
        self.btns = {}
        self.btnGroup = QtGui.QButtonGroup(parent)
        self.color = color

        for bLabel in self.btnLabels:
            rad = QtGui.QRadioButton(bLabel)
            self.btns[bLabel] = rad
            self.connect(self.btns[bLabel], QtCore.SIGNAL('clicked()'),lambda item=bLabel:self.set_selected(item))
            vbox.addWidget(self.btns[bLabel])

            if callbackFn != None:
                self.connect(self.btns[bLabel], QtCore.SIGNAL('clicked()'),lambda item=bLabel:callbackFn(item=item))

            if default != None and bLabel == default:
                self.btns[bLabel].setChecked(True)

        self.setLayout(vbox)

    def set_selected(self,item=None):
        if item !=None:
            self.selectedItem = item


class Slider(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Slider')

        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.slider.setGeometry(30, 40, 100, 30)
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self.changeValue)

        self.label = QtGui.QLabel(self)
        self.label.setPixmap(QtGui.QPixmap('mute.png'))
        self.label.setGeometry(160, 40, 80, 30)

    
    def changeValue(self, value):
        pos = self.slider.value()

        if pos == 0:
            self.label.setPixmap(QtGui.QPixmap('mute.png'))
        elif pos > 0 and pos <= 30:
            self.label.setPixmap(QtGui.QPixmap('min.png'))
        elif pos > 30 and pos < 80:
            self.label.setPixmap(QtGui.QPixmap('med.png'))
        else:
            self.label.setPixmap(QtGui.QPixmap('max.png'))

class Imager(QtGui.QWidget):
    def __init__(self, imgPath, parent=None):
        QtGui.QWidget.__init__(self, parent)

        hbox = QtGui.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox = QtGui.QVBoxLayout()
        vbox.setAlignment(QtCore.Qt.AlignCenter)

        if os.path.exists(imgPath) == False:
            print "WARNING: Imager -- image path specified does not exist"

        pixmap = QtGui.QPixmap(imgPath)

        label = QtGui.QLabel(self)
        label.setPixmap(pixmap)

        hbox.addWidget(label)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

class ProgressBar(QtGui.QWidget):
    def __init__(self, parent=None,buttonLabel='Run',withLabel=False):
        QtGui.QWidget.__init__(self, parent)

        self.running = False
        vbl = QtGui.QVBoxLayout()#self
        vbl.setAlignment(QtCore.Qt.AlignTop)
        hbl1 = QtGui.QHBoxLayout()
        hbl1.setAlignment(QtCore.Qt.AlignCenter)
        hbl2 = QtGui.QHBoxLayout()
        hbl2.setAlignment(QtCore.Qt.AlignCenter)
        hbl3 = QtGui.QHBoxLayout()
        hbl3.setAlignment(QtCore.Qt.AlignCenter)
        
        if withLabel != False:
            self.progressLabel = QtGui.QLabel(withLabel)
            hbl3.addWidget(self.progressLabel)

        self.pbar = QtGui.QProgressBar(self)
        hbl1.addWidget(self.pbar)


        if buttonLabel != None:
            self.button = QtGui.QPushButton(buttonLabel, self)
            self.button.setMaximumWidth(150)
            self.button.setMinimumWidth(150)
            self.button.setFocusPolicy(QtCore.Qt.NoFocus)
            hbl2.addWidget(self.button)
            self.connect(self.button,QtCore.SIGNAL('clicked()'), self.onStart)
        else:
            self.button = None

        self.setLayout(vbl)        
        self.timer = QtCore.QBasicTimer()
        self.step = 0;

        ## finalize layout
        vbl.addLayout(hbl3)
        vbl.addLayout(hbl1)
        vbl.addLayout(hbl2)
    
    def onStart(self):
        if self.running == False:
            if self.button != None:
                self.button.setText('Please wait...')
                self.button.setEnabled(False)
                
            self.running = True
            
    def move_bar(self,step):
        self.step = step
        self.pbar.setValue(self.step)
        self.show()
        QtCore.QCoreApplication.processEvents()

    def set_callback(self,callback):
        self.connect(self.button, QtCore.SIGNAL('clicked()'),callback)

class Tooltip(QtGui.QWidget):
    def __init__(self, msg='This is a tooltip', parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setToolTip(msg)
        QtGui.QToolTip.setFont(QtGui.QFont('OldEnglish', 10))
