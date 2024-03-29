# for command-line arguments                                                                                                                                                     
import sys
# Python Qt4 bindings for GUI objects                                                                                                                                            
from PyQt4 import QtGui
# Numpy functions for image creation                                                                                                                                             
import numpy as np
# Matplotlib Figure object                                                                                                                                                       
from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar


class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self, parent):
        # plot definition
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.cos(2*np.pi*t)
        self.axes.plot(t, s)
        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # set the parent widget
        self.setParent(parent)
        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)
class ApplicationWindow(QtGui.QMainWindow):
    """Example main window"""
    def __init__(self):
        # initialization of Qt MainWindow widget
        QtGui.QMainWindow.__init__(self)
        # set window title
        self.setWindowTitle("Matplotlib Figure in a Qt4 Window With NavigationToolbar")
        # instantiate a widget, it will be the main one
        self.main_widget = QtGui.QWidget(self)
        # create a vertical box layout widget
        vbl = QtGui.QVBoxLayout(self.main_widget)
        # instantiate our Matplotlib canvas widget
        qmc = Qt4MplCanvas(self.main_widget)
        # instantiate the navigation toolbar
        ntb = NavigationToolbar(qmc, self.main_widget)
        # pack these widget into the vertical box
        vbl.addWidget(qmc)
        vbl.addWidget(ntb)
        # set the focus on the main widget
        self.main_widget.setFocus()
        # set the central widget of MainWindow to main_widget
        self.setCentralWidget(self.main_widget)


# create the GUI application
qApp = QtGui.QApplication(sys.argv)
# instantiate the ApplicationWindow widget
aw = ApplicationWindow()
# show the widget
aw.show()
# start the Qt main loop execution, exiting from this script
# with the same return code of Qt application
sys.exit(qApp.exec_())



'''
class Qt4MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self,parent):
        # Standard Matplotlib code to generate the plot                                                                                                                          
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        
        # make plot
        self.make_scatter_plot()

        # initialize the canvas where the Figure renders into 
        #FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)



    ## get_mpl_canvas
    def make_scatter_plot(self):#labels=None,root=None,buff=0.02,width=None,height=None,getCanvas=False,altDir=None):

        self.x = np.arange(0.0, 3.0, 0.01)
        self.y = np.cos(2*np.pi*self.x)
        self.axes.plot(self.x, self.y)
   
class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Matplotlib Figure in a Qt4 Window With NavigationToolbar")
        self.main_widget = QtGui.QWidget(self)
        vbl = QtGui.QVBoxLayout(self.main_widget)
        qmc = Qt4MplCanvas(self.main_widget)
        ntb = NavigationToolbar(qmc, self.main_widget)
        vbl.addWidget(qmc)
        vbl.addWidget(ntb)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

qApp = QtGui.QApplication(sys.argv)
aw = ApplicationWindow()
aw.show()
sys.exit(qApp.exec_())
# Create the GUI application                                                                                                                                                     
#qApp = QtGui.QApplication(sys.argv)
# Create the Matplotlib widget                                                                                                                                                   
#mpl = Qt4MplCanvas()
# show the widget                                                                                                                                                                
#mpl.show()
# start the Qt main loop execution, exiting from this script                                                                                                                     
# with the same return code of Qt application                                                                                                                                    
#sys.exit(qApp.exec_())
'''
