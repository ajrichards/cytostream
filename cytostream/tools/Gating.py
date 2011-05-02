"""
derived from the lasso routine on matplotlibs website.

"""
from matplotlib.widgets import Lasso
import matplotlib.mlab
from matplotlib.nxutils import points_inside_poly
from matplotlib.colors import colorConverter
from matplotlib.collections import RegularPolyCollection

from matplotlib.pyplot import figure, show
from numpy import nonzero
from numpy.random import rand

class Datum:
    colorin = colorConverter.to_rgba('red')
    colorout = colorConverter.to_rgba('green')
    def __init__(self, x, y, include=False):
        self.x = x
        self.y = y
        if include: self.color = self.colorin
        else: self.color = self.colorout

class LassoManager:
    def __init__(self, ax, data):
        self.axes = ax
        self.canvas = ax.figure.canvas
        self.data = data

        self.Nxy = len(data)

        facecolors = [d.color for d in data]
        self.xys = [(d.x, d.y) for d in data]
        fig = ax.figure
        self.collection = RegularPolyCollection(
            fig.dpi, 6, sizes=(100,),
            facecolors=facecolors,
            offsets = self.xys,
            transOffset = ax.transData)

        ax.add_collection(self.collection)

        self.cid = self.canvas.mpl_connect('button_press_event', self.onpress)
        self.ind = None

    def callback(self, verts):
        facecolors = self.collection.get_facecolors()
        ind = nonzero(points_inside_poly(self.xys, verts))[0]
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
        self.axes.plot([pt[0] for pt in self.gate],[pt[1] for pt in self.gate],linewidth=2.0)

        
    def onpress(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        self.lasso = Lasso(event.inaxes, (event.xdata, event.ydata), self.callback)
        # acquire a lock on the widget drawing
        self.canvas.widgetlock(self.lasso)
    

class Gater:
    def __init__(self,data):
        
        data = [Datum(*xy) for xy in data]
        fig = figure()
        ax = fig.add_subplot(111, xlim=(0,1), ylim=(0,1), autoscale_on=False)
        self.lman = LassoManager(ax, data)
        show()

    def get_indices(self):
        return self.lman.ind

    def get_gate(self):
        return self.lman.gate


def get_indices_from_gate(data,gate):
    
    print 'newIndices'





if __name__ == '__main__':
    data = rand(1000, 2)
    gate = Gater(data)

    ## how to get indices or gate
    print gate.get_indices()
    print gate.get_gate()


    ## get indices from a new file with same gate
    newData = rand(1000,2)
    indFromGate = get_indices_from_gate(newData,gate)
