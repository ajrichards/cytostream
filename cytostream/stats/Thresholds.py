#!/usr/bin/env python

import os,sys,re,csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from cytostream import SaveSubplots
from cytostream.stats import two_component_em, EmpiricalCDF,scale
from cytostream.tools import get_file_sample_stats

from DistanceCalculator import DistanceCalculator
from Kmeans import run_kmeans_with_sv
from cytostream.tools import get_all_colors
try:
    from SpectralMix import SpectralCluster
except:
    pass


def get_optimal_num_bins(x, binRange, method='freedman'):
    """
    Find the optimal number of bins.
    Modified versions of Freedman, Scott
    """
    N = x.shape[0]
    if method.lower()=='freedman':
        s=np.sort(x)
        IQR = s[int(N*.75)] - s[int(N*.25)] # Interquantile range (75% -25%)
        width = 2* IQR*N**(-1./3)
    elif method.lower()=='scott':
        width = 3.49 * x.std()* N**(-1./3)
    else:
        raise 'Method must be Scott or Freedman', method

    optimalNumBins = int(np.diff(binRange)/width)
    #print '\t (1)', optimalNumBins
    optimalNumBins = int(scale(optimalNumBins,(0,600),(100,300)))
    #print '\t (2)', optimalNumBins
    if optimalNumBins > 300 or optimalNumBins < 100:
        print "WARNING: extreme value for optimal num bins obtained", optimalNumBins

    return optimalNumBins
    

## functions
def _calculate_fscores(neg_pdf, pos_pdf, beta=1.0, theta=10.0):
    n = len(neg_pdf)
    #print '...beta:%s,theta:%s'%(beta,theta)
    fpos = np.where(pos_pdf > theta*neg_pdf, pos_pdf-neg_pdf, 0)
    tp = np.array([np.sum(fpos[i:]) for i in range(n)])
    fn = np.array([np.sum(fpos[:i]) for i in range(n)])
    fp = np.array([np.sum(neg_pdf[i:]) for i in range(n)])
    precision = tp/(tp+fp)
    precision[tp==0]=0
    recall = tp/(tp+fn)
    recall[recall==0]=0
    fscores = (1+beta*beta)*(precision*recall)/(beta*beta*precision + recall)
    fscores[np.where(np.isnan(fscores)==True)[0]]=0

    return fscores,precision,recall

def calculate_fscores(neg,pos,numBins=100,beta=1.0,theta=10.0,fullOutput=True):

    neg = neg.copy()
    pos = pos.copy()

    allEvents = np.hstack((neg,pos))
    #numBins1 = get_optimal_num_bins(allEvents,(allEvents.min(),allEvents.max()))
    numBins = int(np.sqrt(np.max([neg.shape[0],pos.shape[0]])))
    #theta = 100.0
    #beta = 0.1
    #print '\tnum bins',numBins
    #print '\ttheta   ',theta
    #print '\tbeta    ',beta


    pdfNeg, bins = np.histogram(neg, bins=numBins, normed=True)
    pdfPos, bins = np.histogram(pos, bins=bins, normed=True)
    xs = (bins[:-1]+bins[1:])/2.0
    fscores,precision,recall = _calculate_fscores(pdfNeg, pdfPos,beta=beta, theta=theta)
    fThreshold = xs[np.argmax(fscores)]

    if fullOutput == True:
        return {'threshold':fThreshold, 'fscores':fscores, 'pdfx': xs, 'pdfpos':pdfPos, 'pdfneg':pdfNeg,
                'precision':precision,'recall':recall}
    else:
        return fThreshold

def make_positivity_plot(nga,fileNameList,cd3ChanIndex,figName,emResults,subset='CD3',filterID=None):

    filesToPlot = fileNameList
    if len(fileNameList) > 6:
        filesToPlot = fileNameList[:6]

    fig = plt.figure()
    fontSize = 8
    pltCount = 0

    for fileName in filesToPlot:
        events = nga.get_events(fileName)
        if filterID != None:
            filterIndices = nga.get_filter_indices(fileName,filterID)
            events = events[filterIndices,:] 

        cd3Events = events[:,cd3ChanIndex]
        pltCount+=1
        if pltCount > 6:
            continue

        ax = fig.add_subplot(2,3,pltCount)
        eCDF = EmpiricalCDF(cd3Events)
        thresholdLow = eCDF.get_value(0.05)
        eventsInHist = cd3Events[np.where(cd3Events > thresholdLow)[0]]
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
        ax.set_title(fileName,fontsize=9)
        xticklabels = plt.getp(plt.gca(),'xticklabels')
        yticklabels = plt.getp(plt.gca(),'yticklabels')
        plt.setp(xticklabels, fontsize=fontSize-1)
        plt.setp(yticklabels, fontsize=fontSize-1)

        ax.set_xlabel(round(emResults[fileName]['params']['likelihood']))

        ax.set_xticks([])

    fig.subplots_adjust(hspace=0.3,wspace=0.3)
    plt.savefig(figName)


def get_cluster_coeff_var(nga,channelIDs,fileName,clusterID,sscChanInd,modelRunID='run1'):
    events = nga.get_events(fileName)
    filterIndices = nga.get_filter_indices(fileName,'filterCD3a')
    events = events[filterIndices,:]
    statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
    filteredLabels = np.array([int(i) for i in fileLabels[filterIndices]])
    clusterEventsInds = np.where(filteredLabels==clusterID)[0]
    cd3CoeffVar = events[clusterEventsInds,channelIDs['cd3']].std() / np.abs(events[clusterEventsInds,channelIDs['cd3']].mean())
    sscChanKey = None
    for key,item in channelIDs.iteritems():
        if item == sscChanInd:
            sscChanKey = key
    sscCoeffVar = events[clusterEventsInds,channelIDs[sscChanKey]].std() / np.abs(events[clusterEventsInds,channelIDs[sscChanKey]].mean())
   
    return cd3CoeffVar, sscCoeffVar

def examine_double_positive(nga,channelIDs,fscChanInd,sscChanInd,fileName,clusterID,figsDir,modelRunID='run1'):
    create = False
    plotsToViewChannels = [(channelIDs['cd4'],channelIDs['cd8']),
                           (channelIDs['cd3'],sscChanInd),
                           (channelIDs['cd3'],fscChanInd),
                           (channelIDs['cd3'],channelIDs['cd4']),
                           (channelIDs['cd3'],channelIDs['cd8']),
                           (fscChanInd,sscChanInd),
                           (fscChanInd,sscChanInd)] + [(0,0)] * 9

    events = nga.get_events(fileName)
    filterIndices = nga.get_filter_indices(fileName,'filterCD3')
    events = events[filterIndices,:]
    statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
    filteredLabels = np.array([int(i) for i in fileLabels[filterIndices]])
    clusterEventsInds = np.where(filteredLabels==clusterID)[0]
    rValues = []
    cd3CoeffVar = events[clusterEventsInds,channelIDs['cd3']].std() / np.abs(events[clusterEventsInds,channelIDs['cd3']].mean())
    for channels in plotsToViewChannels[:7]:
        (a_s,b_s,r,tt,stderr)=stats.linregress(events[clusterEventsInds,channels[0]],events[clusterEventsInds,channels[1]])
        rValues.append(r)
    
    if create == True:
        ## set channels to view
        subplotTitles = ["r=%s,cv=%s"%(round(rVal,2),round(cd3CoeffVar,2)) for rVal in rValues]
        nga.set("plots_to_view_channels",plotsToViewChannels)
        plotsToViewRuns = [modelRunID for i in range(16)]
        nga.set('plots_to_view_runs',plotsToViewRuns)
        numSubplots = 6
        nga.set('results_mode','components')

        ## set file names
        actualFileList = nga.get_file_names()
        fileInd = actualFileList.index(fileName)
        plotsToViewFiles = [fileInd for i in range(16)]
        nga.set("plots_to_view_files",plotsToViewFiles)

        ## set highlights 
        plotsToViewHighlights = [None for c in range(16)]
        plotsToViewHighlights[0] = [clusterID]
        plotsToViewHighlights[1] = [clusterID]
        plotsToViewHighlights[2] = [clusterID]
        plotsToViewHighlights[3] = [clusterID]
        plotsToViewHighlights[4] = [clusterID]
        plotsToViewHighlights[5] = [clusterID]
        nga.set('plots_to_view_highlights',plotsToViewHighlights)

        figName = os.path.join(figsDir,'dp_%s_%s.png'%(fileName,clusterID))
        figTitle = "Double positive cluster %s"%(fileName)
        ss = SaveSubplots(nga.homeDir,figName,numSubplots,figMode='analysis',figTitle=figTitle,forceScale=False,drawState='heat',
                          axesOff=True,subplotTitles=subplotTitles)

def get_mean_matrix(events,labels):
    meanMat = None
    uniqueLabels = np.sort(np.unique(labels))
    for clusterIdx in uniqueLabels:
        clusterIndices = np.where(labels == clusterIdx)[0]
        clusterEvents = events[clusterIndices,:]
        if meanMat == None:
            meanMat = np.array([clusterEvents.mean(axis=0)])
        else:
            meanMat = np.vstack([meanMat,clusterEvents.mean(axis=0)])

    return meanMat

def handle_dump_filtering(nga,channelInds,modelRunID='run1',fileList=None, figsDir=None):
    
    if figsDir == None:
        figsDir = os.path.join(nga.homeDir,'results',modelRunID)
    elif os.path.isdir(figsDir) == None:
        print "WARNING: handle_dump_filtering -- bad specified figsDirs... using default"
        figsDir = os.path.join(nga.homeDir,'results',modelRunID)

    if os.path.isdir(figsDir) == False:
        os.mkdir(figsDir)

    if fileList == None:
        fileList = nga.get_file_names()

    undumpedClusters = {}
    thresholdLines = {}
    for fileName in fileList:
        print fileName
    
        fileData = nga.get_events(fileName)
        fscData = fileData[:,channelInds['fsc']]
        dumpData = fileData[:,channelInds['dump']]
        undumpedClusters[fileName] = []
        statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
        centroids,variances,sizes = get_file_sample_stats(fileData,fileLabels)

        a = 0.15
        b = 1.2
        numBins = 400
        curveX = np.linspace(a * np.median(fscData),fscData.max(),numBins)
        curveY = np.arctan(curveX)
        curveY = np.array([scale(val, (curveY.min(),curveY.max()),(dumpData.min(),b*np.median(dumpData))) for val in curveY])
        allCentroids = None
        allCentroidLabels = []

        for key,item in centroids.iteritems():
            x = item[channelInds['fsc']]
            y = item[channelInds['dump']]

            if allCentroids == None:
                allCentroids = item
            else:
                allCentroids = np.vstack([allCentroids,item])

            allCentroidLabels.append(key)

        fscCounts = np.digitize(allCentroids[:,channelInds['fsc']],curveX)
        dumpThresholds = np.dot(curveY + np.hstack([curveY[1:],[0]]),0.5)
        for i in range(numBins):
            possibleClusters = np.where(fscCounts == i)[0]

            for pc in possibleClusters:
                if allCentroids[pc,channelInds['dump']] < dumpThresholds[i]:
                    undumpedClusters[fileName].append(int(allCentroidLabels[pc]))

        subsampleInds = np.array(map(int,map(round,np.linspace(0,399,35))))
        thresholdLines[fileName] = {0:(curveX[subsampleInds],curveY[subsampleInds])}
        nga.handle_filtering('dump',fileName,modelRunID,'components',undumpedClusters[fileName])

    create = True
    if create == True:
        print 'creating gating strategy figures...'
        ## set channels to view
        plotsToViewChannels = [(channelInds['fsc'],channelInds['dump']),
                               (channelInds['fsc'],channelInds['dump'])]+ [(0,0)] * 14
        subplotTitles = ["Threshold","Subset"]
        nga.set("plots_to_view_channels",plotsToViewChannels)
        plotsToViewRuns = [modelRunID for i in range(16)]
        nga.set('plots_to_view_runs',plotsToViewRuns)
        numSubplots = 2
        nga.set('results_mode','components')
        actualFileList = nga.get_file_names()

        for fn in range(len(fileList)):
            ## set file names
            fileName = fileList[fn]
            fileInd = actualFileList.index(fileName)
            plotsToViewFiles = [fileInd for i in range(16)]
            nga.set("plots_to_view_files",plotsToViewFiles)
            
            ## set highlights
            plotsToViewHighlights = [None for c in range(16)]
            plotsToViewHighlights[1] = undumpedClusters[fileName]
            nga.set('plots_to_view_highlights',plotsToViewHighlights)

            figName = os.path.join(figsDir,'viability_%s.png'%fileName)
            print '...saving', figName
            figTitle = "Auto Gating Strategy %s"%(fileName)
            ss = SaveSubplots(nga.homeDir,figName,numSubplots,figMode='analysis',figTitle=figTitle,forceScale=False,drawState='heat',
                              addLine=thresholdLines[fileName],axesOff=True,subplotTitles=subplotTitles)

def get_cytokine_threshold(nga,posControlFile,negControlFile,cytoIndex,filterID,beta,fullOutput=True,numBins=150,theta=10.0):
    '''
    returns a dict of results for cytokine threshold analysis
    '''

    fileList = nga.get_file_names()

    try:
        posFileIdx = fileList.index(posControlFile)
        negFileIdx = fileList.index(negControlFile)
    except:
        print "ERROR file list does not contain either the positive or negative control -- get_cytokine_threshold"
        return None

    _posEvents = nga.get_events(fileList[posFileIdx])
    if filterID != None:
        filterInds = nga.get_filter_indices(posControlFile,filterID)
        _posEvents = _posEvents[filterInds,:]
    posEvents = _posEvents[:,cytoIndex]

    _negEvents = nga.get_events(fileList[negFileIdx])
    if filterID != None:
        filterInds = nga.get_filter_indices(negControlFile,filterID)
        _negEvents = _negEvents[filterInds,:]
    negEvents = _negEvents[:,cytoIndex]

    #print "\n",posControlFile,negControlFile,negEvents.shape,posEvents.shape,cytoIndex
    fResults = calculate_fscores(negEvents,posEvents,numBins=numBins,beta=beta,fullOutput=fullOutput,theta=theta)

    return fResults


def get_cytokine_positive_events(nga,cytoIndex,fThreshold,filterID,fileList=None):
    '''
    function works for both pregated and automated data
    '''

    ## check for valid file list
    if fileList == None:
        fileList = nga.get_file_names()
    else:
        for fn in fileList:
            _fileList = nga.get_file_names()
            if fn not in _fileList:
                print "WARNING: Cytostream.stats.thresholds -- %s not found in project"%(fn)

    ## declare variables
    percentages = {}
    counts = {}
    idx = {}
    filterInds = np.array([])

    ## determine and save percentages, counts and indices
    for fileName in fileList:
        events = nga.get_events(fileName)
        if filterID != None:
            filterInds = nga.get_filter_indices(fileName,filterID)
            #print filterInds
            if type(filterInds) != type([]):
                pass
            elif len(filterInds) > 0:
                events = events[filterInds,:]
        
        data = events[:,cytoIndex]
        positiveEventInds = np.where(data > fThreshold)[0]

        if events.shape[0] == 0 or len(positiveEventInds) == 0:
            percentages[fileName] = 0.0
        else:
            percentages[fileName] = (float(positiveEventInds.size)/float(events.shape[0])) * 100.0
        counts[fileName] = positiveEventInds.size
        idx[fileName] = positiveEventInds

    return percentages, counts, idx
