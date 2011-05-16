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



class PolyGateInteractor:
    """
    gate interaction with a polygon

    """

    showverts = True
    epsilon = 5  # max pixel distance to count as a vertex hiy
    def __init__(self, ax, poly, canvas):
        if poly.figure is None:
            raise RuntimeError('You must first add the polygon to a figure or canvas before defining the interactor')
        self.ax = ax
        self.poly = poly
        self.canvas = canvas

        ## fixes error of extra point 
        self.poly.xy = self.poly.xy[:-1]

        ## plots the lines
        x, y = zip(*self.poly.xy)
        x = [i for i in x] + [x[0]]
        y = [i for i in y] + [y[0]]
        self.line = Line2D(x,y,marker='o', markerfacecolor='r', animated=True)
        self.ax.add_line(self.line)

        cid = self.poly.add_callback(self.poly_changed)
        self._ind = None # the active vert  

        self.action1 = canvas.mpl_connect('draw_event', self.draw_callback)
        self.action2 = canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.action3 = canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.action4 = canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)

        ## set original gate
        self.gate = [(x[i],y[i]) for i in range(len(x))]
       
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

    def remove_vert(self):
        self.poly.xy = self.poly.xy[:-1]
        x, y = zip(*self.poly.xy)                                                                                                  
        x = [i for i in x] + [x[0]]  
        y = [i for i in y] + [y[0]] 
        self.line.set_data((x,y))

    def add_vert(self):
        x, y = zip(*self.poly.xy)
        newX = np.random.uniform(min(x), max(x))
        newY = np.random.uniform(min(y), max(y))
        self.poly.xy = np.vstack([self.poly.xy, [newX,newY]])
        x, y = zip(*self.poly.xy)                                                                                                  
        x = [i for i in x] + [x[0]]  
        y = [i for i in y] + [y[0]] 
        self.line.set_data((x,y))
        
    def motion_notify_callback(self, event):
        'on mouse movement'
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        x,y = event.xdata, event.ydata

        self.poly.xy[self._ind] = x,y
        x, y = zip(*self.poly.xy)
        x = [i for i in x] + [x[0]]
        y = [i for i in y] + [y[0]]
        self.line.set_data((x,y))

        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.poly)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)
        
        ## save the gate
        self.gate = [(x[i],y[i]) for i in range(len(x))]

    def clean(self):
        self.line.set_visible(False)
        self.poly.set_visible(False)
        self.canvas.mpl_disconnect(self.action1)
        self.canvas.mpl_disconnect(self.action2)
        self.canvas.mpl_disconnect(self.action3)
        self.canvas.mpl_disconnect(self.action4)

class DrawGateInteractor:
    def __init__(self, ax, canvas,events,chan1,chan2):
        self.ax = ax
        self.canvas = canvas
        self.data = [(e[chan1],e[chan2]) for e in events]
        self.gate = None
        self.action1 = self.canvas.mpl_connect('button_press_event', self.press_callback)
        self.ind = None

    def callback(self, verts):
        self.gate = [v for v in verts]
        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        del self.lasso

        ## plot the gate
        gx = np.array([g[0] for g in self.gate])
        gy = np.array([g[1] for g in self.gate])
        self.line = Line2D(gx,gy,linewidth=2.0,alpha=0.8)
        self.ax.add_line(self.line)

        ## adjust axes
        x = np.array([d[0] for d in self.data])
        y = np.array([d[1] for d in self.data])
        buff = 0.02
        bufferX = buff * (x.max() - x.min())
        bufferY = buff * (y.max() - y.min())
        self.ax.set_xlim([x.min()-bufferX,x.max()+bufferX])
        self.ax.set_ylim([y.min()-bufferY,y.max()+bufferY])

        ## force square axes 
        self.ax.set_aspect(1./self.ax.get_data_ratio())
        self.canvas.draw()

    def press_callback(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        # acquire a lock on the widget drawing  
        self.canvas.widgetlock(self.lasso)

    def clean(self):
        self.line.set_visible(False)
        self.canvas.mpl_disconnect(self.action1)


def get_indices_from_gate(data,gate):
    '''
    returns indices from a gate
    '''


    allData = [(d[0], d[1]) for d in data]
    ind = np.nonzero(points_inside_poly(allData, gate))[0]

    return ind
