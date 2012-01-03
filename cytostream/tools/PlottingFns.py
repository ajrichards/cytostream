#!/usr/bin/python
#
# to run an example
# python RunMakeFigures.py -p Demo -i 0 -j 1 -f 3FITC_4PE_004.fcs -h ./projects/Demo
#

import getopt,sys,os,re,csv
import numpy as np
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator
from cytostream.tools import read_txt_to_file_channels, read_txt_into_array, get_file_data, get_file_sample_stats
from fcm.core.transforms import _logicle as logicle
import fcm

def get_n_color_colorbar(n,cmapName='jet'):# Spectral #gist_rainbow 
    '''
    breaks any matplotlib cmap into n colors
 
    '''
    cmap = cm.get_cmap(cmapName,n)
    return cmap(np.arange(n))

def rgb_to_hex(rgb):
    '''
    converts a rgb 3-tuple into hex
          
    '''

    return '#%02x%02x%02x' % rgb[:3]

def pyfcm_load_fcs_file(filePath):
    data = fcm.loadFCS(filePath)
    return data

def get_file_channel_list(filePath):
    data = pyfcm_load_fcs_file(filePath)
    channels = data.channels
    channels = [re.sub("\s","-",c) for c in channels]
    return channels

def get_cmap_blues():

    cdict = {'red': ((0.0, 0.0, 0.0),
                     (1.0, 1.0, 0.0)),
             'green': ((0.0, 0.0, 0.0),
                       (1.0, 1.0, 0.0)),
             'blue': ((0.0, 0.0, 0.5),
                      (1.0, 1.0, 1.0))}
    my_cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)

    return my_cmap


def get_all_colors():
    colors =  ['b','#CC6600','g','r','c','m',"#002200",'y','k','orange',"#CC55FF","#990033",'#FF6600',"#CCCCCC","#660033",
               '#FFCC00','#FFFFAA','#6622AA','#33FF77','#998800','#0000FF',"#995599","#00AA00","#777777","#FF0033",'#990066',
               '#FA58AC','#8A0808','#D8D8D8',"#CC2277",'#336666','#996633',"#FFCCCC","#CC0011","#FFBB33","#DDDDDD","#991188",
               "#FF9966","#009999","#FF0099","#996633","#990000","#660000","#9900BB","#330033","#FF5544","#9966CC",
               "#330066","#99FF99","#FF99FF","#333333","#CC3333","#CC9900","#99DD22","#3322BB","#663399","#002255",
               "#003333","#66CCFF","#CCFFFF","#AA11BB","#000011","#FFCCFF","#00EE33","#337722","#CCBBFF","#FF3300",
               "#009999","#110000","#AAAAFF","#990000","#880022","#BBBBBB","#00EE88","#66AA22","#99FFEE","#660022",
               "#FFFF33","#00CCFF","#990066","#006600","#00CCFF",'#AAAAAA',"#33FF00","#0066FF","#FF9900","#FFCC00"]

    return np.array(colors * 3)


def fetch_plotting_events(selectedFile,model,log,subsample,labels=None,modelRunID=None):
    
    ## declare variables
    fontName = log.log['font_name']
    markerSize = int(log.log['scatter_marker_size'])
    fontSize = log.log['font_size']
    plotType = log.log['plot_type']
    modelType = log.log['results_mode']

    if modelRunID != None:
        modelLog = model.load_model_results_log(selectedFile,modelRunID)
        filterUsed = modelLog['filter used']
    else:
        filterUsed = None

    if not re.search('filter', str(filterUsed)):
        filterUsed = None

    ## get events
    if subsample != 'original':
        subsample = str(int(float(subsample)))

    ## ensure the proper events are being loaded
    events = model.get_events(selectedFile,subsample=subsample,filterID=filterUsed)

    if log == None:
        maxScatterSize =  7e04
    else:
        maxScatterSize = float(log.log['setting_max_scatter_display'])

    if events.shape[0] > subsample:
        subsampleIndices = model.get_subsample_indices(maxScatterSize)
        events = events[subsampleIndices,:]
        if labels != None:
            labels = labels[subsampleIndices,:]
   
    return events,labels

class Centroids:
    ''' 
    the finding of centroids is time consuming and to get around this values are stored in a dictionary

    '''

    def __init__(self):

        self.plotDict = {}

    def __check_summary_stats__(self,events,labels,plotID,channelsID):
        if self.plotDict[plotID][channelsID].has_key('centroids') == False:
            centroids,variances,sizes = get_file_sample_stats(events,labels)
            self.plotDict[plotID][channelsID]['centroids'] = centroids
            self.plotDict[plotID][channelsID]['variances'] = variances
            self.plotDict[plotID][channelsID]['sizes'] = sizes

    def get_centroids(self,events,labels,plotID,channelsID):
        self.__check_summary_stats__(events,labels,plotID,channelsID)
   
        if self.plotDict[plotID][channelsID].has_key('centroids') == True:
            centroids = self.plotDict[plotID][channelsID]['centroids']

        return centroids

    def get_variences(self,events,labels,plotID,channelsID):
        self.__check_summary_stats__(events,labels,plotID,channelsID)

        if  self.plotDict[plotID][channelsID].has_key('variences') == True:
            variences = self.plotDict[plotID][channelsID]['variences']

        return variences

    def get_sizes(self,events,labels,plotID,channelsID):
        self.__check_summary_stats__(events,labels,plotID,channelsID)

        if self.plotDict[plotID][channelsID].has_key('sizes') == True:
            sizes = self.plotDict[plotID][channelsID]['sizes']

        return sizes

    def get_ids(self,selectedFile,subsample,modelName,index1,index2):
        if modelName == None:
            plotID = "%s_%s"%(selectedFile,subsample)
        else:
            plotID = "%s_%s_%s"%(selectedFile,subsample,modelName)

        channelsID = "%s-%s"%(index1,index2)
        
        if self.plotDict.has_key(plotID) == False:
            self.plotDict[plotID] = {}
        if self.plotDict[plotID].has_key(channelsID) == False:
            self.plotDict[plotID][channelsID] = {}

        return plotID, channelsID

def set_logicle_transformed_ticks(ax,axis='x',fontsize=10,fontname='Arial'):
    '''
    to map an axis to a scale that immunologists are familar with
    '''

    if axis not in ['x','y','both']:
        print "ERROR set_logicle_transformed_ticks: invalid axis arg"
        return None
    
    ## setup scales
    scale = 262144*logicle(np.array([0, 100, 10**3, 10**4, 10**5]), 262144, 4.5, None, 0.5)
    tickPairs = [(1,9),(10,90),(100,900),(1000,9000),(10000,90000)]
    minorScale = [262144*logicle(np.linspace(ab[0],ab[1],9),262144,4.5,None,0.5) for ab in tickPairs]
    labels = ['$0$', '$10^2$', '$10^3$', '$10^4$', '$10^5$']
    minorTicks = np.array([])

    for mTicks in minorScale:
        minorTicks = np.hstack([minorTicks,np.array(mTicks)])

    ## format the x axix
    if axis in ['x','both']:
        ax.set_xticks(scale)
        ax.set_xticks(minorTicks,minor=True)
        ax.set_xticklabels(labels,fontsize=fontsize-1,fontname=fontname)
        ax.xaxis.set_ticks_position('bottom')
        ax.set_xlim([0, 262144])

    ## format the y axis
    if axis in ['y','both']:
        ax.set_yticks(scale)
        ax.set_yticks(minorTicks, minor=True)
        ax.set_yticklabels(labels,fontsize=fontsize-1,fontname=fontname)
        ax.yaxis.set_ticks_position('left')
        ax.set_ylim([0, 262144])


def set_log_transformed_ticks(ax,axis='x',fontsize=10,fontname='Arial'):
    '''
    to map an axis to a scale that immunologists are familar with
    '''

    if axis not in ['x','y','both']:
        print "ERROR set_logicle_transformed_ticks: invalid axis arg"
        return None
    
    ## setup scales
    scale = np.log10(np.array([1e01,1e02,1e03,1e04,1e05]))
    tickPairs = [(1,9),(10,90),(100,900),(1000,9000),(10000,90000)]
    minorScale = [np.log10(np.linspace(ab[0],ab[1],9)) for ab in tickPairs]
    labels = ['$10^1$', '$10^2$', '$10^3$', '$10^4$','$10^5$']
    minorTicks = np.array([])

    for mTicks in minorScale:
       minorTicks = np.hstack([minorTicks,np.array(mTicks)])

    ## format the x axix
    if axis in ['x','both']:
        ax.set_xticks(scale)
        ax.set_xticks(minorTicks,minor=True)
        ax.set_xticklabels(labels,fontsize=fontsize-1,fontname=fontname)
        ax.xaxis.set_ticks_position('bottom')
        ax.set_xlim([0, np.log10(262144)])

    ## format the y axis
    if axis in ['y','both']:
        ax.set_yticks(scale)
        ax.set_yticks(minorTicks, minor=True)
        ax.set_yticklabels(labels,fontsize=fontsize-1,fontname=fontname)
        ax.yaxis.set_ticks_position('left')
        ax.set_ylim([0, np.log10(262144)])


def set_scatter_ticks(ax,axis,numTicks=6,fontsize=10,fontname='Arial'):
    '''
    formats a scatter axis ticks to the K format
    '''

    if numTicks == 6:
        tickVals = [250000,200000,150000,100000,50000,0]
        tickLabels = ['250K','200K','150K','100K','50K','0']
    elif numTicks == 4:
        tickVals = [250000,150000,50000,0]
        tickLabels = ['250K','150k','50K','0']
    else:
        print "ERROR: set_scatter_ticks: invalid number of ticks"
        return None

    ## format the x axix
    if axis in ['x','both']:
        ax.set_xticks(tickVals)
        ax.set_xticklabels(tickLabels,fontsize=fontsize-1,fontname=fontname)
        ax.yaxis.set_ticks_position('bottom')
        ax.set_xlim([0, 262144])

    ## format the y axis
    if axis in ['y','both']:
        ax.set_yticks(tickVals)
        ax.set_yticklabels(tickLabels,fontsize=fontsize-1,fontname=fontname)
        ax.yaxis.set_ticks_position('left')
        ax.set_ylim([0, 262144])

def get_fontsize(numSubplots):

    if numSubplots in [1]:
        fontSize = 11
    elif numSubplots in [2]:
        fontSize = 10
    elif numSubplots in [3]:
        fontSize = 8
    elif numSubplots in [4]:
        fontSize = 8
    elif numSubplots in [5,6]:
        fontSize = 7
    elif numSubplots in [7,8,9]:
        fontSize = 6
    elif numSubplots in [10,11,12]:
        fontSize = 5
    elif numSubplots in [13,14,15,16]:
        fontSize = 4

    return fontSize

def get_fontname():
    return 'Arial'
