"""
derived from the lasso routine on matplotlibs website.

"""

import sys,os,re
from PyQt4 import QtGui,QtCore
import fcm
from fcm.core.transforms import _logicle as logicle
from cytostream.tools import officialNames,get_official_name_match
from cytostream.tools import cytokinePattern, scatterPattern

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

    allData = [(d[0]+10000, d[1]+10000) for d in data]
    gate = [(g[0]+10000, g[1]+10000) for g in gate]
    pip = points_inside_poly(allData, gate)
    ind = np.where(pip==True)[0]

    return ind

def get_clusters_from_gate(data,labels,gate):
    '''
    returns clusters from a gate
    '''

    if labels == None:
        print "WARNING: GateImporter.get_clusters_from_gate -- labels were 'None'"
        return []

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
    
    def __init__(self,nga,xmlFilePath,modelRunID='run1',transform='logicle',plotGates=False,
                 regex="\s+",force=False):
        '''
        constructor initalizes all necessary variables
        regex = a regexpression (str) that converts original file names to appropriate file names
        '''

        ## declare variables
        self.nga = nga
        self.regex = regex
        self.fileNameList = self.nga.get_file_names()
        self.channelNameList = self.nga.get_channel_names()
        self.modelRunID = modelRunID
        self.transform = transform
        self.savedGates = {}
        self.plotGates = plotGates
        self.force = force

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
            print "cannot find xml file", xmlFilePath
            return
        if self.transform != 'logicle':
            print "ERROR: GateImporter is only implemented for logicle transforms"
            return

        ## parse out the gates
        self.read_gates(xmlFilePath)

    def plot_gates(self,fileName,viaSubset=True):
        basicSubsets = ["CD4","CD8"]
        gateNames = [g['name'] for g in self.savedGates[fileName]]
        def get_gates_to_plot(bsubset):
            gatesToPlot = []
            if bsubset == 'CD4':
                for gind, gname in enumerate(gateNames):
                    if re.search('CD8',gname,flags=re.IGNORECASE):
                        pass
                    else:
                        gatesToPlot.append(self.savedGates[fileName][gind])
            else:
                for gind, gname in enumerate(gateNames):
                    if re.search('CD4',gname,flags=re.IGNORECASE):
                        pass
                    else:
                        gatesToPlot.append(self.savedGates[fileName][gind])

            return gatesToPlot

        if viaSubset == True:
            gatesToPlotList = [get_gates_to_plot(bs) for bs in basicSubsets]
        else:
            gatesToPlotList = self.savedGates[fileName]
        
        fileInd = self.fileNameList.index(fileName)
        fileEvents = self.nga.get_events(fileName)
        for gind, gatesToPlot in enumerate(gatesToPlotList):
            gateNamesToPlot = [g['name'] for g in gatesToPlot]
            print 'plotting',basicSubsets[gind],gateNamesToPlot
    
            numSubplots = len(gatesToPlot)
            self.nga.set("plots_to_view_files",[fileInd for i in range(16)])
            self.nga.set("plots_to_view_runs",[self.modelRunID for i in range(16)])

            ## set titles
            gtp = gatesToPlot
            nsp = numSubplots
            subplotTitles = [re.sub(fileName,"","%s (%s)"%(gtp[i]['parent'],gtp[i]['name'])) for i in range(nsp)]

            ## set gates
            gatesToShow = [[] for c in range(16)]
            for i in range(numSubplots):
                gatesToShow[i] = [gatesToPlot[i]['verts']]

            ## set filters
            plotsToViewFilters = [None for c in range(16)]
            for i in range(numSubplots):
                if gatesToPlot[i]['parent'] != 'root':
                    plotsToViewFilters[i] = gatesToPlot[i]['parent']
            self.nga.set('plots_to_view_filters',plotsToViewFilters)
            
            ## unhighlight all events except positive ones
            if len(gatesToPlotList) > 1:
                plotsToViewHighlights = [None for c in range(16)]
                for i in range(numSubplots):
                    plotsToViewHighlights[i] = []    
                self.nga.set('plots_to_view_highlights',plotsToViewHighlights)
                
                cytokinePosLabels = self.nga.load_labels(fileName,gatesToPlot[-1]['name'],getLog=False)
                cytokinePosInds = np.where(cytokinePosLabels==1)[0] 
                positiveToShow = [None for c in range(16)]
                for i in range(numSubplots):
                    positiveToShow[i] = cytokinePosInds
    
                ## add gate percentages
                textToShow = [None for c in range(16)]
                for i in range(numSubplots):
                    if gatesToPlot[i]['parent'] == 'root':
                        parentIndices = range(fileEvents.shape[0])
                    else:
                        parentLabels = self.nga.load_labels(fileName,gatesToPlot[i]['parent'],getLog=False)
                        parentIndices = np.where(parentLabels==1)[0]

                    childLabels = self.nga.load_labels(fileName,gatesToPlot[i]['name'],getLog=False)
                    childIndices = np.where(childLabels==1)[0]
                    if len(childIndices) == 0 or len(parentIndices) == 0:
                        textToShow[i] = '0.0'
                    textToShow[i] = str(round((float(len(childIndices)) / float(len(parentIndices))) * 100.0,4))

            ## set channels to view
            plotsToViewChannels = [(0,0)] * 16
            for i in range(numSubplots):
                plotsToViewChannels[i] = (gatesToPlot[i]['channel1'],gatesToPlot[i]['channel2'])
            self.nga.set('plots_to_view_channels',plotsToViewChannels)

            ## save
            figDir = os.path.join(self.nga.homeDir,'results','imported-xml')
            if os.path.isdir(figDir) == False:
                os.mkdir(figDir)
            if len(gatesToPlotList) > 1:
                figName = os.path.join(figDir,'%s_%s_xml.png'%(fileName,basicSubsets[gind]))
                figTitle = "Imported FJ gates %s - %s"%(re.sub("\_","-",fileName),basicSubsets[gind])
            else:

                figName = os.path.join(figDir,'%s_xml.png'%(fileName))
                figTitle = "Imported FJ gates %s"%re.sub("\_","-",fileName)
            print '...saving', figName

            self.nga.controller.save_subplots(figName,numSubplots,figMode='qa',figTitle=figTitle,useScale=False,
                                              drawState='heat',subplotTitles=subplotTitles,gatesToShow=gatesToShow,
                                              positiveToShow=positiveToShow,drawLabels=False,textToShow=textToShow,
                                              fontSize=8)

    def logical_transform(self,gateVerts,axis='both',reverse=False):
        '''
        used to logicle transform channels as the gate is imported
        '''

        dim0 = [g[0] for g in gateVerts]
        dim1 = [g[1] for g in gateVerts]

        if axis in ['x','both']:
            dim0 = (10**5)*(logicle(dim0, 262144, 4.5, None, 0.5))
        if axis in ['y','both']:
            dim1 = (10**5)*(logicle(dim1, 262144, 4.5, None, 0.5))
    
        newGate = []
        for g in range(len(gateVerts)):
            if reverse == False:
                newGate.append((dim0[g],dim1[g]))
            else:
                newGate.append((dim1[g],dim0[g]))
   
        return newGate

    def read_fcm_poly_gate(self,pGate,fileName):
        print 'reading fcm_poly_gate'
        verts = pGate.vert
        name  = re.sub("\s+","_",pGate.name)
        #name  = re.sub(self.regex,"",pGate.name)
        name = re.sub("\s+","_",name)
        name = re.sub("\.gate","",name)
        name = name + "_" + fileName
        _channel1,_channel2  = pGate.chan
        dimX = np.array([g[0] for g in verts])
        dimY = np.array([g[1] for g in verts])
        
        shortChannels = self.nga.get('short_channel_labels')
        
        if len(shortChannels) == 0:
            print "ERROR: GateImporter fatal error - no short labels -- exiting..."
            sys.exit()

        if not shortChannels.__contains__(_channel1):
            print "channel 1 could not be matched to short channels", _channel1
            channel1Ind = 'NA'
        else:
            channel1Ind = shortChannels.index(_channel1)

        if not shortChannels.__contains__(_channel2):
            print "channel 2 could not be matched to short channels", _channel2
            channel2Ind = 'NA'
        else:
            channel2Ind = shortChannels.index(_channel2)

        ## find the channel name using the exact match
        channel1Name,channel2Name = None,None
        for chanName, chanIndx in self.channelDict.iteritems():
            if channel1Ind == 'NA':
                channel1Name = 'NA'
            elif int(channel1Ind) == int(chanIndx):
                channel1Name = chanName

            if channel2Ind == 'NA':
                channel2Name = 'NA'  
            elif int(channel2Ind) == int(chanIndx):
                channel2Name = chanName
        
        ## transform the channels
        if not re.search(scatterPattern,channel1Name) and not re.search(scatterPattern,channel2Name):
            verts = self.logical_transform(verts,axis='both',reverse=False)
        elif not re.search(scatterPattern,channel1Name):
            verts = self.logical_transform(verts,axis='x',reverse=False)
        elif not re.search(scatterPattern,channel2Name):
            verts = self.logical_transform(verts,axis='y',reverse=False)

        ## add the point to the end
        verts = verts + [verts[0]]
                            
        return verts,name,channel1Ind,channel2Ind,channel1Name,channel2Name

    def read_gates(self,xmlFilePath):
        '''
        uses fcm to read in the xmlfile
        this function is very specific to a panel and is not likely to generalize
        '''

        ## read in gates
        gates = {}
        fjxml = fcm.load_flowjo_xml(xmlFilePath)
        fjxml = fjxml.flat_gates()
        resultType = None
        for key, item in fjxml.iteritems():
            key = re.sub("\.fcs","",key)
            normalizedKey = re.sub("\.","_",re.sub(self.regex,"",key))
            normalizedKey = re.sub("-","_",key)
            
            for fn in self.fileNameList:
                if re.search(fn,normalizedKey):
                    normalizedKey = fn
                gates[normalizedKey] = item
                resultsType = 0
            if not re.search("\D",normalizedKey):
                gates[normalizedKey] = item
                resultsType = 1

        ## ensure we have the correct number of matches
        matchedNames = []
        unmatchedNames = []
        matchedIndices = []
        for fileNameToMatch in gates.keys():
            fileNameToMatch = re.sub(self.regex,"",fileNameToMatch)
            matchedName = None
            for fileName in self.fileNameList:
                if fileName == fileNameToMatch:
                   matchedName = fileName

            if matchedName == None:
                print "WARNING: gate importer unmatched name"
                unmatchedNames.append(fileNameToMatch)
                print fileNameToMatch
                #for fn in self.fileNameList:
                #    print "...", fn

                if self.force == False:
                    continue
            else:
                matchedIndices.append(self.fileNameList.index(matchedName))
            matchedNames.append(fileNameToMatch)

        matchedIndices = list(set(matchedIndices))
        if len(matchedIndices) != len(self.fileNameList):
            print "WARNING: either not all files could be matched or there was an invalid number of matchs"
            #matchedNames.sort()
            #unmatchedNames.sort()
            #print "From XML -- matched names\n", matchedNames
            #print "From XML -- unmatched names\n", unmatchedNames
            #print "From nga -- unmatched names\n"
            #print np.array(self.fileNameList)[list(set(range(len(self.fileNameList))).difference(set(matchedIndices)))]
            #print len(matchedIndices),len(self.fileNameList)
            #return

        matches = 0
        for _fileNameToMatch in gates.keys():
            fileNameToMatch = re.sub(self.regex,"",_fileNameToMatch)
            matchedName = None
            for fileName in self.fileNameList:
                if fileName == fileNameToMatch:
                   matchedName = fileName

            if matchedName == None:
                matchedName = fileNameToMatch
                
                if self.force == False:
                    print "skipping gates for %s..."%fileNameToMatch
                    continue
                    
            matches += 1
            print "Extracting gates for %s"%matchedName
            gateList = gates[_fileNameToMatch]
            fileName = matchedName
            self.savedGates[fileName] = []

            ## for a given file import all of its gates
            for pGate in gateList:
                verts,name,chan1Ind,chan2Ind,chan1Name,chan2Name = self.read_fcm_poly_gate(pGate.gate,matchedName)
                parent = pGate.parent
                parent = re.sub("\s+","_",parent)
                parent = re.sub("\.gate","",parent)
                if parent != 'root':
                    parent = parent + "_" + fileName
            
                ## fixes the bug where the parent gate is marked as another cytokine 
                #if re.search(cytokinePattern,parent):
                #    print "WARNING: detected cytokine as parent -- using root"
                #parent = 'root'

                ## debug by filtering on a specific file name
                #if not re.search("_A01",fileName):
                #    continue

                print '\tname', name
                print '\tparent', parent
                print '\tchannels', chan1Ind,chan2Ind,chan1Name,chan2Name, "\n"
                if self.force == True:
                    saveLabels = False
                else:
                    saveLabels = True

                self.nga.controller.save_gate('%s.gate'%name,verts,chan1Ind,chan2Ind,
                                              chan1Name,chan2Name,parent,fileName,saveLabels=saveLabels)
                isCytokine = False
                if re.search(cytokinePattern,name):
                    isCytokine = True

                gateToSave = {'verts':verts,
                              'name':name,
                              'channel1':chan1Ind,
                              'channel2':chan2Ind,
                              'parent':parent,
                              'cytokine':isCytokine}

                self.savedGates[fileName].append(gateToSave)

            ## plot gates
            if self.plotGates == True:
                self.plot_gates(matchedName)
