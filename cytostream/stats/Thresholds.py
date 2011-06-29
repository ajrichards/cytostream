#!/usr/bin/env python

import os,sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from cytostream.stats import two_component_em, EmpiricalCDF


def make_positivity_plot(nga,fileNameList,cd3ChanIndex,figName,emResults):

    if len(fileNameList) != 6:
        print "make_positivity_plot only works with six subplots not", len(fileNameList)
        return None

    fig = plt.figure()
    fontSize = 8
    pltCount = 0
    for fileName in fileNameList:
        events = nga.get_events(fileName)
        cd3Events = events[:,cd3ChanIndex]
        pltCount+=1
        ax = fig.add_subplot(2,3,pltCount)
        eventsInHist = cd3Events[np.where(cd3Events < 800)[0]]
        n, bins, patches = ax.hist(eventsInHist,18,normed=1,facecolor='gray',alpha=0.5)
        maxX1 = 900
        maxX2 = 900
        pdfX1 = np.linspace(0,maxX1,300)
        pdfY1 = stats.norm.pdf(pdfX1,emResults[fileName]['params']['mu1'], np.sqrt(emResults[fileName]['params']['sig1']))
        pdfX2 = np.linspace(0,maxX2,300)
        pdfY2 = stats.norm.pdf(pdfX2,emResults[fileName]['params']['mu2'], np.sqrt(emResults[fileName]['params']['sig2']))
        pdfY1 = pdfY1 * (1.0 - emResults[fileName]['params']['pi'])
        pdfY1[np.where(pdfY1 < 0)[0]] = 0.0
        pdfY2 = pdfY2 * emResults[fileName]['params']['pi']
        pdfY2[np.where(pdfY2 < 0)[0]] = 0.0

        ax.plot(pdfX1, pdfY1, 'k-', linewidth=2)
        ax.plot(pdfX2, pdfY2, 'k-', linewidth=2)
        threshY = np.linspace(0,max([max(pdfY1),max(pdfY2)]),100)
        threshX = np.array([emResults[fileName]['cutpoint']]).repeat(100)
        ax.plot(threshX, threshY, 'r-', linewidth=2)
        #ax.set_ylim([0,max(p2)])
        #ax.set_ylim([0,max(pdfY2)]) 
        ax.set_title(fileName,fontsize=9)
        xticklabels = plt.getp(plt.gca(),'xticklabels')
        yticklabels = plt.getp(plt.gca(),'yticklabels')
        plt.setp(xticklabels, fontsize=fontSize-1)
        plt.setp(yticklabels, fontsize=fontSize-1)

    fig.subplots_adjust(hspace=0.4,wspace=0.3)
    plt.savefig(figName)

def find_positivity_threshold_cd3(cd3ChanIndex,fileList,nga,alignLabels,verbose=False,minNumEvents=3):
    '''
    get cd3 positive clusters

    '''

    cd3Results = {}

    for fileInd in range(len(fileList)):        
        ## debug
        #if fileInd > 5:
        #    continue

        fileName = fileList[fileInd]
        cd3Results[fileName] = {'indices':None,'clusters':None,'percent':None}

        print "\n", fileName

        fileLabels = alignLabels[fileInd]
        uniqueLabels = np.sort(np.unique(fileLabels))
        events = nga.get_events(fileName)
        cd3Events = events[:,cd3ChanIndex]
        cd3Positive = []

        ## make initial guesses
        initialGuesses = {'n':cd3Events.size, 'mu1':200, 'mu2':500, 'sig1':8000, 'sig2':1000, 'pi':0.3}

        ## get lower threshold of larger component 
        tcg,cutpoint = two_component_em(cd3Events,emGuesses=initialGuesses,verbose=verbose)
        
        ## need to redefine cd3Events?
        cd3Events = events[:,cd3ChanIndex]

        for cid in uniqueLabels:

            ## ensure cluster has at least minnumevents
            clusterEvents = cd3Events[np.where(fileLabels==cid)[0]]
            if len(clusterEvents) < minNumEvents:
                continue

            ## find the cutoff for a given cluster
            eCDF = EmpiricalCDF(clusterEvents)
            percentileCut = eCDF.get_value(0.5)

            ## determine if a cluster falls above the cutoff 
            if percentileCut > cutpoint:
                cd3Positive.append(cid)
         
        ## count the cd3 clusters
        cd3Indices = np.array([])
        for cd3cid in cd3Positive:
            _cd3Indices = np.where(fileLabels==cd3cid)[0]
            cd3Indices = np.hstack([cd3Indices,_cd3Indices])

        cd3Percent = float(len(cd3Indices)) / float(len(fileLabels))
        rawPercent = float(len(np.where(cd3Events > cutpoint)[0])) / float(len(cd3Events))
        print fileName, len(cd3Indices),len(fileLabels), cd3Percent, rawPercent

        cd3Results[fileName]['indices'] = cd3Indices
        cd3Results[fileName]['clusters'] = cd3Positive
        cd3Results[fileName]['percent'] = cd3Percent
        cd3Results[fileName]['params'] = tcg['params'].copy()
        cd3Results[fileName]['cutpoint'] = cutpoint
        

    return cd3Results
