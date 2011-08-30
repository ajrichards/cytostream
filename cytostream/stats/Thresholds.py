#!/usr/bin/env python

import os,sys,re
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from cytostream.stats import two_component_em, EmpiricalCDF


## functions
def get_fscore(positiveEvents,negativeEvents,pdfX,pdfPos,pdfNeg,threshold,bins,beta=1.0):

    beta,threshold = map(float,[beta,threshold])
    thresholdIdx = None

    for i in range(len(pdfX)):
        if pdfX[i] >= threshold:
            thresholdIdx = i
            break

    if thresholdIdx == None:
        print "could not find threshold index"
        return 0.0

    tp,fn = 0,0

    if positiveEvents.size == 0:
        tpfp = np.where(positiveEvents >= pdfX[thresholdIdx])[0].size
    elif negativeEvents.size == 0:
        tpfp = np.where(negativeEvents >= pdfX[thresholdIdx])[0].size
    else:
        tpfp = np.where(positiveEvents >= pdfX[thresholdIdx])[0].size + np.where(negativeEvents >= pdfX[thresholdIdx])[0].size
 
    ## speeding up the process
    negThresholds = np.dot(pdfNeg + np.hstack([pdfNeg[1:],[0]]),0.5)
    posBinCounts = np.digitize(positiveEvents,bins)

    for b in np.arange(thresholdIdx,pdfX.size-1):
        posInds = np.where(posBinCounts == b)[0]
        if posInds.size > 0:
            posEvents = positiveEvents[posInds]
            tp+= np.where(posEvents >= negThresholds[b])[0].size
            
    for b in np.arange(0,thresholdIdx):
        posInds = np.where(posBinCounts == b)[0]
        if posInds.size > 0:
            posEvents = positiveEvents[posInds]
            fn+= np.where(posEvents >= negThresholds[b])[0].size
            
    tp,fn,tpfp = map(float,[tp,fn,tpfp])
    
    if tpfp == 0.0:
        precision = 0.0
    else:
        precision = tp/tpfp
    if tp+fn == 0.0:
        recall = 0.0
    else:
        recall = tp/(tp+fn)
        
    if (beta*beta*precision + recall) == 0.0:
        fscore = 0.0
    else:
        fscore = (1+beta*beta)*(precision*recall)/(beta*beta*precision + recall)
    return fscore

def get_fscore_pdfs(positiveEvents,negativeEvents,numBins=200):
    dataMin = np.min([positiveEvents.min(),negativeEvents.min()])
    dataMax = np.max([positiveEvents.max(),negativeEvents.max()])
    bins = np.linspace(dataMin,dataMax,numBins)
    pdfPos, lowlim1, binsize1, extrapoints1 = stats.relfreq(positiveEvents, numbins=numBins, defaultreallimits=(dataMin,dataMax))
    pdfX = np.linspace(dataMin,dataMax,numBins)
    pdfNeg, lowlim2, binsize2, extrapoints2 = stats.relfreq(negativeEvents, numbins=numBins, defaultreallimits=(dataMin,dataMax))

    return pdfX,pdfPos,pdfNeg,bins

def calculate_fscores(positiveEvents,negativeEvents,pdfX,pdfPos,pdfNeg,searchRange,bins,beta=1.0):
    fscores = np.zeros((searchRange.size),)
    
    for t in range(searchRange.size):
        threshold = searchRange[t]
        fscores[t] = get_fscore(positiveEvents,negativeEvents,pdfX,pdfPos,pdfNeg,threshold,bins,beta=beta)

    return fscores

def make_positivity_plot(nga,fileNameList,cd3ChanIndex,figName,emResults,subset='CD3',filterID=None):

    if len(fileNameList) > 6:
        print "make_positivity_plot only works with six or less subplots not", len(fileNameList)
        return None

    fig = plt.figure()
    fontSize = 8
    pltCount = 0
    for fileName in fileNameList:
        events = nga.get_events(fileName,filterID=filterID)
        cd3Events = events[:,cd3ChanIndex]
        pltCount+=1
        ax = fig.add_subplot(2,3,pltCount)
        eventsInHist = cd3Events[np.where(cd3Events < 800)[0]]
        n, bins, patches = ax.hist(eventsInHist,18,normed=1,facecolor='gray',alpha=0.5)

        maxX1 = cd3Events.max()
        maxX2 = cd3Events.max()
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
        ax.set_xlim(0,10)
        ax.set_title(fileName,fontsize=9)
        xticklabels = plt.getp(plt.gca(),'xticklabels')
        yticklabels = plt.getp(plt.gca(),'yticklabels')
        plt.setp(xticklabels, fontsize=fontSize-1)
        plt.setp(yticklabels, fontsize=fontSize-1)

    fig.subplots_adjust(hspace=0.3,wspace=0.3)
    plt.savefig(figName)

    #return threshX, threshY

def find_positivity_threshold_cd3(cd3ChanIndex,fileList,nga,allLabels,verbose=False,minNumEvents=3,initialGuesses=None,filterID=None):
    '''
    get cd3 positive clusters
    initialGuesses = {'n':cd3Events.size, 'mu1':250, 'mu2':600, 'sig1':5000, 'sig2':5000, 'pi':0.5}

    '''

    cd3Results = {}

    for fileInd in range(len(fileList)):

        fileName = fileList[fileInd]
        cd3Results[fileName] = {'indices':None,'clusters':None,'percent':None}

        #print "\n", fileName

        fileLabels = allLabels[fileInd]
        if filterID != None and re.search('filter',str(filterID)):
            filterIndices = nga.get_filter_indices(fileName,filterID)
            fileLabels = fileLabels[filterIndices]
            
        uniqueLabels = np.sort(np.unique(fileLabels))
        events = nga.get_events(fileName,filterID=filterID)
        cd3Events = events[:,cd3ChanIndex]
        cd3Positive = []

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
        #print fileName, len(cd3Indices),len(fileLabels), cd3Percent, rawPercent

        cd3Results[fileName]['indices'] = cd3Indices
        cd3Results[fileName]['clusters'] = cd3Positive
        cd3Results[fileName]['percent'] = cd3Percent
        cd3Results[fileName]['params'] = tcg['params'].copy()
        cd3Results[fileName]['cutpoint'] = cutpoint
        
    return cd3Results

def find_positivity_threshold_cd8(cd8ChanIndex,fileList,nga,allLabels,cd3Results,verbose=False,minNumEvents=3,initialGuesses=None):
    '''
    get cd8 positive clusters
    initialGuesses = {'n':cd8Events.size, 'mu1':250, 'mu2':600, 'sig1':5000, 'sig2':5000, 'pi':0.5}
    '''

    cd8Results = {}

    for fileInd in range(len(fileList)):        

        fileName = fileList[fileInd]
        cd8Results[fileName] = {'indices':None,'clusters':None,'percent':None}

        #print "\n", fileName

        fileLabels = allLabels[fileInd]
        uniqueLabels = np.sort(np.unique(fileLabels))
        events = nga.get_events(fileName)
        cd8Events = events[:,cd8ChanIndex]
        cd8Positive = []

        ## get lower threshold of larger component 
        tcg,cutpoint = two_component_em(cd8Events,emGuesses=initialGuesses,verbose=verbose,subset='CD8')
        
        ## need to redefine cd8Events?
        cd8Events = events[:,cd8ChanIndex]

        for cid in uniqueLabels:

            ## ensure cluster has at least minnumevents
            clusterEvents = cd8Events[np.where(fileLabels==cid)[0]]
            if len(clusterEvents) < minNumEvents:
                continue

            ## find the cutoff for a given cluster
            eCDF = EmpiricalCDF(clusterEvents)
            percentileCut = eCDF.get_value(0.5)

            ## determine if a cluster falls above the cutoff 
            if percentileCut > cutpoint and cid in cd3Results[fileName]['clusters']:
                cd8Positive.append(cid)
         
        ## count the cd8 clusters
        cd8Indices = np.array([])
        for cd8cid in cd8Positive:
            _cd8Indices = np.where(fileLabels==cd8cid)[0]
            cd8Indices = np.hstack([cd8Indices,_cd8Indices])

        cd8Percent = float(len(cd8Indices)) / float(len(fileLabels))
        rawPercent = float(len(np.where(cd8Events > cutpoint)[0])) / float(len(cd8Events))
        #print fileName, len(cd8Indices),len(fileLabels), cd8Percent, rawPercent

        cd8Results[fileName]['indices'] = cd8Indices
        cd8Results[fileName]['clusters'] = cd8Positive
        cd8Results[fileName]['percent'] = cd8Percent
        cd8Results[fileName]['params'] = tcg['params'].copy()
        cd8Results[fileName]['cutpoint'] = cutpoint
        
    return cd8Results

def find_positivity_threshold_cd4(cd4ChanIndex,fileList,nga,allLabels,cd3Results,cd8Results,verbose=False,minNumEvents=3,initialGuesses=None):
    '''
    get cd4 positive clusters
    initialGuesses = {'n':cd4Events.size, 'mu1':250, 'mu2':600, 'sig1':5000, 'sig2':5000, 'pi':0.5}
    '''

    cd4Results = {}

    for fileInd in range(len(fileList)):        

        fileName = fileList[fileInd]
        cd4Results[fileName] = {'indices':None,'clusters':None,'percent':None}

        #print "\n", fileName

        fileLabels = allLabels[fileInd]
        uniqueLabels = np.sort(np.unique(fileLabels))
        events = nga.get_events(fileName)
        cd4Events = events[:,cd4ChanIndex]
        cd4Positive = []

        ## get lower threshold of larger component 
        tcg,cutpoint = two_component_em(cd4Events,emGuesses=initialGuesses,verbose=verbose,subset='CD4')
        
        ## need to redefine cd4Events?
        cd4Events = events[:,cd4ChanIndex]

        for cid in uniqueLabels:

            ## ensure cluster has at least minnumevents
            clusterEvents = cd4Events[np.where(fileLabels==cid)[0]]
            if len(clusterEvents) < minNumEvents:
                continue

            ## find the cutoff for a given cluster
            eCDF = EmpiricalCDF(clusterEvents)
            percentileCut = eCDF.get_value(0.5)

            ## determine if a cluster falls above the cutoff 
            if percentileCut > cutpoint and cid in cd3Results[fileName]['clusters'] and cid not in cd8Results[fileName]['clusters']:
                cd4Positive.append(cid)
         
        ## count the cd4 clusters
        cd4Indices = np.array([])
        for cd4cid in cd4Positive:
            _cd4Indices = np.where(fileLabels==cd4cid)[0]
            cd4Indices = np.hstack([cd4Indices,_cd4Indices])

        cd4Percent = float(len(cd4Indices)) / float(len(fileLabels))
        rawPercent = float(len(np.where(cd4Events > cutpoint)[0])) / float(len(cd4Events))
        #print fileName, len(cd4Indices),len(fileLabels), cd4Percent, rawPercent

        cd4Results[fileName]['indices'] = cd4Indices
        cd4Results[fileName]['clusters'] = cd4Positive
        cd4Results[fileName]['percent'] = cd4Percent
        cd4Results[fileName]['params'] = tcg['params'].copy()
        cd4Results[fileName]['cutpoint'] = cutpoint
        
    return cd4Results
