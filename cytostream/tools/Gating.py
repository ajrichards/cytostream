"""
derived from the lasso routine on matplotlibs website.

"""

import sys
from PyQt4 import QtGui,QtCore

import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.figure import Figure
from matplotlib.widgets import Lasso
import matplotlib.mlab
from matplotlib.nxutils import points_inside_poly
from matplotlib.colors import colorConverter
from matplotlib.collections import RegularPolyCollection, PolyCollection
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from matplotlib.artist import Artist
from matplotlib.patches import Polygon, CirclePolygon
from matplotlib.mlab import dist_point_to_segment
from matplotlib.lines import Line2D


import numpy as np


class Datum:
    colorin = colorConverter.to_rgba('red')
    colorout = colorConverter.to_rgba('green')
    def __init__(self, x, y, include=False):
        self.x = x
        self.y = y
        if include: self.color = self.colorin
        else: self.color = self.colorout

class PolygonInteractor:
    """

    An polygon editor.
    Key-bindings
      't' toggle vertex markers on and off.  When vertex markers are on,
          you can move them, delete them
      'd' delete the vertex under point
      'i' insert a vertex at point.  You must be within epsilon of the
     line connecting two existing vertices
    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hiy
    def __init__(self, ax, poly, canvas):
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.ax = ax
        #canvas = poly.figure.canvas
        self.poly = poly
        self.canvas = canvas

        x, y = zip(*self.poly.xy)
        self.line = Line2D(x,y,marker='o', markerfacecolor='r', animated=True)
        self.ax.add_line(self.line)

        cid = self.poly.add_callback(self.poly_changed)
        self._ind = None # the active vert  

        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('key_press_event', self.key_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
       
    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    def poly_changed(self, poly):
        'this method is called whenever the polygon object is called'
        # only copy the artist props to the line (except visibility)

        vis = self.line.get_visible()
        Artist.update_from(self.line, poly)
        self.line.set_visible(vis)  # don't use the poly visibility state 

    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'

        # display coords
        xy = np.asarray(self.poly.xy)
        xyt = self.poly.get_transform().transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]
        d = np.sqrt((xt-event.x)**2 + (yt-event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]

        if d[ind]>=self.epsilon:
            ind = None

        return ind

    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        if not self.showverts: return
        if event.inaxes==None: return
        if event.button != 1: return
        self._ind = self.get_ind_under_point(event)
        
    def button_release_callback(self, event):
        'whenever a mouse button is released'
        if not self.showverts: return
        if event.button != 1: return
        self._ind = None

    def key_press_callback(self, event):
        'whenever a key is pressed'
        if not event.inaxes: return
        if event.key=='t':
            self.showverts = not self.showverts
            self.line.set_visible(self.showverts)
            if not self.showverts: self._ind = None
        elif event.key=='d':
            ind = self.get_ind_under_point(event)
            if ind is not None:
                self.poly.xy = [tup for i,tup in enumerate(self.poly.xy) if i!=ind]
                self.line.set_data(zip(*self.poly.xy))
        elif event.key=='i':
            xys = self.poly.get_transform().transform(self.poly.xy)
            p = event.x, event.y # display coords                                                                                                                                                                                            
            for i in range(len(xys)-1):
                s0 = xys[i]
                s1 = xys[i+1]
                d = dist_point_to_segment(p, s0, s1)
                if d<=self.epsilon:
                    self.poly.xy = np.array(
                        list(self.poly.xy[:i]) +
                        [(event.xdata, event.ydata)] +
                        list(self.poly.xy[i:]))
                    self.line.set_data(zip(*self.poly.xy))
                    break

        self.canvas.draw()

    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x,y
        self.line.set_data(zip(*self.poly.xy))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

class LassoManager:
    def __init__(self, ax, canvas, origData):
        
        self.origData = origData
        self.data = [Datum(*xy) for xy in origData]
        self.axes = ax
        self.canvas = canvas

        self.Nxy = len(data)

        facecolors = [d.color for d in self.data]
        self.xys = [(d.x, d.y) for d in self.data]
        fig = ax.figure

        self.collection = RegularPolyCollection(
            fig.dpi, 6, sizes=(5,),
            facecolors=facecolors,
            offsets = self.xys,
            transOffset = ax.transData)
       
        ax.add_collection(self.collection)

    def activate(self):
        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
        self.ind = None

    def callback(self, verts):
        facecolors = self.collection.get_facecolors()
        ind = np.nonzero(points_inside_poly(self.xys, verts))[0]
        for i in range(self.Nxy):
            if i in ind:
                facecolors[i] = Datum.colorin
            else:
                facecolors[i] = Datum.colorout

        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        self.gate = verts

        del self.lasso
        self.ind = ind
    
        ## draw the gate
        self.axes.plot([pt[0] for pt in self.gate],[pt[1] for pt in self.gate],linewidth=4.0)

        ## handle axes
        buff = 0.02
        bufferX = buff * (self.origData[:,0].max() - self.origData[:,0].min())
        bufferY = buff * (self.origData[:,1].max() - self.origData[:,1].min())
        self.axes.set_xlim([self.origData[:,0].min()-bufferX,self.origData[:,0].max()+bufferX])
        self.axes.set_ylim([self.origData[:,1].min()-bufferY,self.origData[:,1].max()+bufferY])

    def onpress(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
    
class GateDraw(FigureCanvas):

    def __init__(self, origData,  parent=None):
        
        self.background = True
        self.parent = parent
        self.origData = origData
        self.lman = None
        self.poly = None
        self.ployInt = None

        ## prepare plot environment
        self.fig = Figure()
        self.reset_axes()

        ## initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.parent)

        ## notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def reset_axes(self):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        self.fig.set_frameon(self.background)

    def draw_events(self,gateType):

        ## reset
        self.reset_axes()
        
        if self.lman != None:
            del self.lman
            self.lman = None

        if self.poly in self.ax.patches:
            self.ax.patches.remove(self.poly)
            self.canvas.draw()
            #del self.poly
            #del self.polyInt
            #self.poly, self.polyInt = None, None

        print dir(self.ax)


        ## prepare some ref points for polys
        mid1 = 0.5 * self.origData[0].max()
        mid2 = 0.5 * self.origData[1].max()
        a = mid1 - (mid1 * 0.5)
        b = mid1 + (mid1 * 0.5)
        c = mid2 - (mid2 * 0.5)
        d = mid2 + (mid2 * 0.5)
        e = mid2 + (mid2 * 0.6)
        f = mid2 - (mid2 * 0.6)

        if gateType == 'Free':
            self.lman = LassoManager(self.ax, self.canvas, self.origData)
            self.lman.activate()
        elif gateType == 'Poly3':
            #self.poly = Polygon(([a,c],[b,c],[b,d]), animated=True,alpha=0.2)
            self.poly = Polygon(([b,c],[b,d]), animated=True,alpha=0.2)
            self.ax.add_patch(self.poly)
            self.polyIn = PolygonInteractor(self.ax, self.poly, self.canvas)
        elif gateType == 'Poly4':
            self.poly = Polygon(([a,c],[b,c],[b,d],[a,d]), animated=True,alpha=0.2)
            self.ax.add_patch(self.poly)
            self.polyIn = PolygonInteractor(self.ax, self.poly, self.canvas)
        elif gateType == 'Poly5':
            self.poly = Polygon(([a,c],[b,c],[b,d],[mid1,e],[a,d]), animated=True,alpha=0.2)
            self.ax.add_patch(self.poly)
            self.polyIn = PolygonInteractor(self.ax, self.poly, self.canvas)
        elif gateType == 'Poly6':
            poly = Polygon(([a,c],[mid1,f],[b,c],[b,d],[mid1,e],[a,d]), animated=True,alpha=0.2)
            self.ax.add_patch(self.poly)
            self.polyIn = PolygonInteractor(self.ax, self.poly, self.canvas)

        ## handle axes
        buff = 0.02
        bufferX = buff * (self.origData[:,0].max() - self.origData[:,0].min())
        bufferY = buff * (self.origData[:,1].max() - self.origData[:,1].min())
        self.ax.set_xlim([self.origData[:,0].min()-bufferX,self.origData[:,0].max()+bufferX])
        self.ax.set_ylim([self.origData[:,1].min()-bufferY,self.origData[:,1].max()+bufferY])
        self.canvas.draw()

class Gater(QtGui.QWidget):

    def __init__(self, data,  parent=None, mainWindow=None):
        QtGui.QWidget.__init__(self,parent)
        
        self.mainWindow = mainWindow
        self.gateType = 'Free'

        ## setup layouts
        hl = QtGui.QHBoxLayout()
        hl.setAlignment(QtCore.Qt.AlignCenter)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignCenter)
        vbox2 = QtGui.QVBoxLayout()
        vbox2.setAlignment(QtCore.Qt.AlignCenter)
        hbox1 = QtGui.QHBoxLayout()
        hbox1.setAlignment(QtCore.Qt.AlignCenter)
        hbox2 = QtGui.QHBoxLayout()
        hbox2.setAlignment(QtCore.Qt.AlignCenter)
        hbox3 = QtGui.QHBoxLayout()
        hbox3.setAlignment(QtCore.Qt.AlignCenter)
        hbox4 = QtGui.QHBoxLayout()
        hbox4.setAlignment(QtCore.Qt.AlignCenter)

        ## gate selector
        gateTypes = ['Free','Poly3','Poly4','Poly5','Poly6']
        self.gateTypeSelector = QtGui.QComboBox(self)
        self.gateTypeSelector.setMaximumWidth(180)
        self.gateTypeSelector.setMinimumWidth(180)

        for gt in gateTypes:
            self.gateTypeSelector.addItem(gt)

        if gateTypes.__contains__(self.gateType):
            self.gateTypeSelector.setCurrentIndex(gateTypes.index(self.gateType))
        else:
            print "ERROR: gate type selector - bad specified default", self.gateType

        self.connect(self.gateTypeSelector, QtCore.SIGNAL("currentIndexChanged(int)"), self.set_gate_type)

        hbox2.addWidget(self.gateTypeSelector)
        hbox2.setAlignment(QtCore.Qt.AlignCenter)

        self.saveBtn = QtGui.QPushButton("Save Gate")
        self.saveBtn.setMaximumWidth(100)
        self.connect(self.saveBtn, QtCore.SIGNAL('clicked()'),self.save_callback)
        hbox2.addWidget(self.saveBtn)

        self.removeBtn = QtGui.QPushButton("Remove Gate")
        self.removeBtn.setMaximumWidth(100)
        self.connect(self.removeBtn, QtCore.SIGNAL('clicked()'),self.remove_callback)
        hbox2.addWidget(self.removeBtn)

        ## add gatedraw widget
        self.gateDraw = GateDraw(data)
        self.gateDraw.draw_events(self.gateType)

        hbox3.addWidget(self.gateDraw.canvas)
        
        ## add a mpl navigation toolbar
        ntb = NavigationToolbar(self.gateDraw.canvas,self)
        hbox4.addWidget(ntb)

        ## finalize layout   
        vbox2.addLayout(hbox2)
        vbox2.addLayout(hbox3)
        vbox2.addLayout(hbox4)
        hl.addLayout(vbox1)
        hl.addLayout(vbox2)
        self.setLayout(hl)

    def save_callback(self):
        if self.get_indices() == None:
            msg = "No gate has been drawn"
            reply = QtGui.QMessageBox.information(self,'Information',msg)
        elif self.mainWindow == None:
            print 'there are %s indices selected'%(len(self.get_indices()))
            print 'the gate has %s points in the gate'%(len(self.get_gate()))
        else:
            print "need to handle save callback"

    def remove_callback(self):
        print 'removing events'
        self.gateDraw.draw_events(self.gateType)
        self.gateDraw.lman.ind = None
        self.gateDraw.lman.gate = None

    def get_indices(self):
        return self.gateDraw.lman.ind

    def get_gate(self):
        return self.gateDraw.lman.gate

    def set_gate_type(self):
        gtInd = self.gateTypeSelector.currentIndex()
        gt = str(self.gateTypeSelector.currentText())
        self.gateType = gt
        self.gateDraw.draw_events(self.gateType)

        if self.mainWindow == None:
            print "changed gate type to", self.gateType
            
def get_indices_from_gate(data,gate):
    
    allData = [(d[0], d[1]) for d in data]
    ind = np.nonzero(points_inside_poly(allData, gate))[0]

    return ind


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    data = np.random.rand(10000, 2)
    gtr = Gater(data)

    gtr.show()


    ## how to get indices or gate
    #inds = gtr.get_indices()
    #gate = gtr.get_gate()

    ## get indices from a new file with same gate
    #newData = np.random.rand(1000,2)
    #indFromGate = get_indices_from_gate(newData,gate)
    
    #print 'orig inds', inds
    #print 'new ind  ', indFromGate


    sys.exit(app.exec_())

