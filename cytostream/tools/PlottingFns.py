#!/usr/bin/python
#
# to run an example
# python RunMakeFigures.py -p Demo -i 0 -j 1 -f 3FITC_4PE_004.fcs -h ./projects/Demo
#

import getopt,sys,os,re,csv
import numpy as np

## important line to fix popup error in mac osx
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def get_n_color_colorbar(n,cmapName='jet'):# Spectral #gist_rainbow                                                                                                     
    "breaks any matplotlib cmap into n colors"
    cmap = cm.get_cmap(cmapName,n)
    return cmap(np.arange(n))

def rgb_to_hex(rgb):
    """                                                                                                                                                                      
    converts a rgb 3-tuple into hex                                                                                                                                          
    """

    return '#%02x%02x%02x' % rgb[:3]

def pyfcm_load_fcs_file(filePath):
    data = fcm.loadFCS(filePath)
    return data

def get_file_channel_list(filePath):
    data = pyfcm_load_fcs_file(filePath)
    channels = data.channels
    channels = [re.sub("\s","-",c) for c in channels]
    return channels

def make_scatter_plot(filePath,channel1Ind,channel2Ind,fileChannels,subset='all',labels=None,buff=0.02,altDir=None,centroids=None):
    markerSize = 3
    alphaVal = 0.5

    fontName = 'arial'
    fontSize = 12
    plotType = 'png'

    colors = ['b','g','r','c','m','y','b','orange','#AAAAAA','#FF6600','#FFCC00',
              '#FFFFAA','#6622AA','#33FF77','#998800']

    ## prepare figure
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)

    ## specify channels
    index1 = int(channel1Ind)
    index2 = int(channel2Ind)
    
    channel1 = fileChannels[index1]
    channel2 = fileChannels[index2]

    ## exclude scatter
    #data = pyfcm_load_fcs_file(filePath)
    data = read_txt_into_array(filePath)

    ## make plot
    totalPoints = 0
    if labels == None:
        ax.scatter([data[:,index1]],[data[:,index2]],color='blue',s=markerSize)
    else:
        if type(np.array([])) != type(labels):
            labels = np.array(labels)

        numLabels = np.unique(labels).size
        maxLabel = np.max(labels)

        clustCount = -1
        for l in np.sort(np.unique(labels)):
            hexColor = colors[l]
            clustCount += 1

            x = data[:,index1][np.where(labels==l)[0]]
            y = data[:,index2][np.where(labels==l)[0]]
            
            totalPoints+=x.size

            if x.size == 0:
                continue
            ax.scatter(x,y,color=hexColor,s=markerSize)

            ## handle centroids if present
            prefix = ''
            if centroids != None:
                xPos = centroids[l][index1]
                yPos = centroids[l][index2]

                if colors[l] in ['#FFFFAA','y']:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=hexColor)
                            )
                else:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white',
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=hexColor)
                            )

    ## handle data edge buffers
    bufferX = buff * (data[:,index1].max() - data[:,index1].min())
    bufferY = buff * (data[:,index2].max() - data[:,index2].min())
    ax.set_xlim([data[:,index1].min()-bufferX,data[:,index1].max()+bufferX])
    ax.set_ylim([data[:,index2].min()-bufferY,data[:,index2].max()+bufferY])

    ## save file
    fileName = os.path.split(filePath)[-1]
    ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
    ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
    ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)
    
    if altDir == None:
        print "ERROR: must specify altDir, not saving figure"
    else:
        fileName = os.path.join(altDir,"%s_%s_%s.%s"%(re.sub("\.fcs|\.out","",fileName),channel1,channel2,plotType))
        fig.savefig(fileName,transparent=False,dpi=200)
