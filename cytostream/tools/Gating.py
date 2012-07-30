"""
derived from the lasso routine on matplotlibs website.

"""

import sys,os,re
from PyQt4 import QtGui,QtCore
import fcm
from fcm.core.transforms import _logicle as logicle
from cytostream.tools import officialNames,get_official_name_match

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
        self.line = None

        ## fixes error of extra point 
        self.poly.xy = self.poly.xy[:-1]

        ## plots the lines
        x, y = zip(*self.poly.xy)
        x = [i for i in x] + [x[0]]
        y = [i for i in y] + [y[0]]
        self.line = Line2D(x,y,marker='o', markerfacecolor='r', linewidth=3.0, animated=True)
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
        self.line = None

    def callback(self, verts):
        self.gate = [v for v in verts]
        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        del self.lasso

        ## plot the gate
        gx = np.array([g[0] for g in self.gate])
        gy = np.array([g[1] for g in self.gate])
        self.line = Line2D(gx,gy,linewidth=3.0,alpha=0.8)
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
        if self.line != None:
            self.line.set_visible(False)
        self.canvas.mpl_disconnect(self.action1)


def get_indices_from_gate(data,gate):
    '''
    returns indices from a gate
    '''

    allData = [(d[0], d[1]) for d in data]
    ind = np.nonzero(points_inside_poly(allData, gate))[0]

    return ind

def get_clusters_from_gate(data,labels,gate):
    '''
    returns clusters from a gate
    '''

    ## create a matrix of the mean values
    meanMat = None
    uniqueLabels = np.sort(np.unique(labels))
    for clusterIdx in uniqueLabels:
        clusterIndices = np.where(labels == clusterIdx)[0]
        clusterEvents = data[clusterIndices,:]
        if meanMat == None:
            meanMat = np.array([clusterEvents.mean(axis=0)])
        else:
            meanMat = np.vstack([meanMat,clusterEvents.mean(axis=0)])

    allData = [(d[0], d[1]) for d in meanMat]
    ind = np.nonzero(points_inside_poly(allData, gate))[0]
    if len(ind) > 0:
        clusters = uniqueLabels[ind]
    else:
        clusters = []

    return clusters

def get_clusters_via_gate(meanMat,meanMatLabels,gate):
    '''
    returns clusters from a gate
    '''

    allData = [(d[0], d[1]) for d in meanMat]
    ind = np.nonzero(points_inside_poly(allData, gate))[0]
    if len(ind) > 0:
        clusters = meanMatLabels[ind]
    else:
        clusters = []

    return clusters

class GateImporter:
    '''
    used to import gates from flojo xml files
    '''
    
    def __init__(self,nga,xmlFilePath,modelRunID='run1',transform='logicle'):
        '''
        constructor initalizes all necessary variables
        '''

        ## declare variables
        self.nga = nga
        self.fileNameList = self.nga.get_file_names()
        self.channelNameList = self.nga.get_channel_names()
        self.modelRunID = modelRunID
        self.transform = transform
        self.savedGates = []

        ## specify the default scatters
        self.channelDict = self.nga.channelDict
        if self.channelDict.has_key('SSCA') and self.channelDict.has_key('FSCA'):
            self.sscChanInd = self.channelDict['SSCA']
            self.fscChanInd = self.channelDict['FSCA']
        elif self.channelDict.has_key('SSCH') and self.channelDict.has_key('FSCH'):
            self.sscChanInd = self.channelDict['SSCH']
            self.fscChanInd = self.channelDict['FSCH']
        elif self.channelDict.has_key('SSCW') and self.channelDict.has_key('FSCW'):
            self.sscChanInd = self.channelDict['SSCW']
            self.fscChanInd = self.channelDict['FSCW']
        else:      
            self.sscChanInd = self.channelDict['SSC']
            self.fscChanInd = self.channelDict['FSC']
            
        ## error check
        if os.path.exists(xmlFilePath) == False: 
            print "cannot find xml file", self.xmlFilePath
            return
        if self.transform != 'logicle':
            print "ERROR: GateImporter is only implemented for logicle transforms"
            return

        ## parse out the gates
        self.read_gates(xmlFilePath)

        ## plot gates
        self.plot_gates()

    def plot_gates(self):

        ## make a plot
        for fileName in self.fileNameList[:2]:
            fileInd = self.fileNameList.index(fileName)
            numSubplots = len(self.savedGates)
            self.nga.set("plots_to_view_files",[fileInd for i in range(16)])
            self.nga.set("plots_to_view_runs",[self.modelRunID for i in range(16)])

            ## set titles
            subplotTitles = ["%s\n%s"%(self.savedGates[i]['parent'],self.savedGates[i]['name']) for i in range(numSubplots)]

            ## set gates
            gatesToShow = [[] for c in range(16)]
            for i in range(numSubplots):
                gatesToShow[i] = [self.savedGates[i]['verts']]

            ## set filters
            plotsToViewFilters = [None for c in range(16)]
            for i in range(numSubplots):
                if self.savedGates[i]['parent'] != 'root':
                    plotsToViewFilters[i] = 'iFilter_%s'%self.savedGates[i]['parent']
            
            self.nga.set('plots_to_view_filters',plotsToViewFilters)
            
            ## set channels to view
            plotsToViewChannels = [(0,0)] * 16
            for i in range(numSubplots):
                plotsToViewChannels[i] = (self.savedGates[i]['channel1'],self.savedGates[i]['channel2'])
            self.nga.set('plots_to_view_channels',plotsToViewChannels)

            ## save
            figName = os.path.join('.','figures','xmlfj',self.nga.controller.projectID,'%s_fjxml.png'%(fileName))
            figTitle = "Imported FJ gates %s"%re.sub("\_","-",fileName)
            print '...saving', figName
            self.nga.controller.save_subplots(figName,numSubplots,figMode='analysis',figTitle=figTitle,useScale=False,
                                              drawState='heat',subplotTitles=subplotTitles,gatesToShow=gatesToShow)  

    def logical_transform(self,gateVerts,axis='both',reverse=False):
        '''
        used to logicle transform channels as the gate is imported
        '''
        
        dim0 = [g[0] for g in gateVerts]
        dim1 = [g[1] for g in gateVerts]

        if axis in ['x','both']:
            dim0 = (10**5)*logicle(dim0, 262144, 4.5, None, 0.5)
        if axis in ['y','both']:
            dim1 = (10**5)*logicle(dim1, 262144, 4.5, None, 0.5)
    
        newGate = []
        for g in range(len(gateVerts)):
            if reverse == False:
                newGate.append((dim0[g],dim1[g]))
            else:
                newGate.append((dim1[g],dim0[g]))
   
        return newGate

    def read_fcm_poly_gate(self,pGate):
        verts = pGate.vert
        name  = re.sub("\s+","_",pGate.name)
        name = re.sub("\s+","_",name)
        name = re.sub("\.gate","",name)
        _channel1,_channel2  = pGate.chan

        shortChannels = self.nga.get('short_channel_labels')
        if len(shortChannels) == 0:
            print "ERROR: GateImporter fatal error - no short labels -- exiting..."
            sys.exit()

        channel1Ind = shortChannels.index(_channel1)
        channel2Ind = shortChannels.index(_channel2)
        channel1Name, channel2Name = None,None
        for chanName, chanIndx in self.channelDict.iteritems():
            if int(channel1Ind) == int(chanIndx):
                channel1Name = chanName
            if int(channel2Ind) == int(chanIndx):
                channel2Name = chanName

        scatterList = ['FSC','FSCA','FSCW','FSCH','SSC','SSCA','SSCW','SSCH']
        if channel1Name not in scatterList and not channel2Name in scatterList:
            verts = self.logical_transform(verts,axis='both',reverse=False)
        elif channel1Name not in scatterList:
            verts = self.logical_transform(verts,axis='x',reverse=False)
        elif channel2Name not in scatterList:
            verts = self.logical_transform(verts,axis='y',reverse=False)

        return verts,name,channel1Ind,channel2Ind,channel1Name,channel2Name

    def read_gates(self,xmlFilePath):
        '''
        uses fcm to read in the xmlfile
        this function is very specific to a panel and is not likely to generalize
        '''

        ## read in gates
        fjxml = fcm.load_flowjo_xml(xmlFilePath)
        fjxml = fjxml.flat_gates()
        gates = {}
        resultType = None
        for key, item in fjxml.iteritems():
            key = re.sub("\.fcs","",key)
            normalizedKey = re.sub("\.","_",re.sub("\s+","",key))
            normalizedKey = re.sub("-","_",key)
            
            for fn in self.fileNameList:
                if re.search(fn,normalizedKey):
                    normalizedKey = fn
                gates[normalizedKey] = item
                resultsType = 0
            if not re.search("\D",normalizedKey):
                gates[normalizedKey] = item
                resultsType = 1

        ## assumes that all gates are the same for each file (otherwise create a loop)
        gateList = gates[gates.keys()[1]]
        print 'found %s gates', len(gateList)
        for pGate in gateList:
            print "\n ...................."
            verts,name,channel1Ind,channel2Ind,channel1Name,channel2Name = self.read_fcm_poly_gate(pGate.gate)
            parent = pGate.parent
            parent = re.sub("\s+","_",parent)
            parent = re.sub("\.gate","",parent)
            
            print '\tname', name
            print '\tparent', parent
            print '\tchannels', channel1Ind,channel2Ind,channel1Name,channel2Name, "\n"
            self.nga.controller.save_gate('%s.gate'%name,verts,channel1Ind,channel2Ind,channel1Name,channel2Name,parent)           

            pattern = re.compile("IFN|IFNG|CD27|CD45|CD107|IL2",re.IGNORECASE)
            isCytokine = False
            if re.search(pattern,name):
                isCytokine = True

            gateToSave = {'verts':verts,
                          'name':name,
                          'channel1':channel1Ind,
                          'channel2':channel2Ind,
                          'parent':parent,
                          'cytokine':isCytokine}

            self.savedGates.append(gateToSave)
