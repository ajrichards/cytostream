#!/usr/bin/env python

import os,sys,re,csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from cytostream import SaveSubplots
from cytostream.stats import two_component_em, EmpiricalCDF,scale
from cytostream.tools import get_file_sample_stats

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
        #eventsInHist = cd3Events[np.where(cd3Events < 800)[0]]
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
        #ax.set_ylim([0,max(p2)])
        #ax.set_ylim([0,max(pdfY2)])
        #ax.set_xlim(0,10)
        ax.set_title(fileName,fontsize=9)
        xticklabels = plt.getp(plt.gca(),'xticklabels')
        yticklabels = plt.getp(plt.gca(),'yticklabels')
        plt.setp(xticklabels, fontsize=fontSize-1)
        plt.setp(yticklabels, fontsize=fontSize-1)

        ax.set_xlabel(round(emResults[fileName]['params']['likelihood']))

        ax.set_xticks([])

    fig.subplots_adjust(hspace=0.3,wspace=0.3)
    plt.savefig(figName)

    #return threshX, threshY

def find_positivity_threshold(subset,cd3ChanIndex,fileList,nga,allLabels,verbose=False,minNumEvents=3,initialGuesses=None,filterID=None):
    '''
    get xx positive clusters
    initialGuesses = {'n':cd3Events.size, 'mu1':250, 'mu2':600, 'sig1':5000, 'sig2':5000, 'pi':0.5}

    '''
    subset = subset.lower()

    if subset not in ['cd3','cd8','cd4','fsc','ssc']:
        print "ERROR: in find_positivity_threshold -- invalid subset"
        return False

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
        tcg,cutpoint = two_component_em(cd3Events,emGuesses=initialGuesses,verbose=verbose,subset=subset)
        
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


def perform_automated_gating_basic_subsets(nga,channelIDs,modelRunID='run1',fileList=None,figsDir=None,undumpedClusters=None):

    ## variables
    if fileList == None:
        fileList = nga.get_file_names()
    if figsDir == None:
        figsDir = os.path.join(nga.homeDir,'results',modelRunID,'thresholding')
        if os.path.isdir(figsDir) == False:
            os.mkdir(figsDir)
        
    thresholdLines = {}

    ## prepare output
    writer = csv.writer(open(os.path.join(nga.homeDir,'results','%s_basic_cell_subsets.csv'%modelRunID),'w'))
    writer.writerow(["fileName","subset","totalEvents","percentage","clusterIDs"])

    allLabels = []
    for fileName in fileList:
        statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
        allLabels.append(fileLabels)
 
    ########### CD3 ##################
    print 'getting cd3 events...'
    cd3ChanIndex = channelIDs['cd3']
    cd3Results = find_positivity_threshold('cd3',cd3ChanIndex,fileList,nga,allLabels,verbose=True)
    figName = os.path.join(figsDir,'ThresholdsEM_cd3.png')
    make_positivity_plot(nga,fileList,cd3ChanIndex,figName,cd3Results)

    for fileName in fileList:
        thresholdLines[fileName] = {}

    ## save data
    for fileName in fileList:
        nga.handle_filtering('filter1',fileName,modelRunID,'components',cd3Results[fileName]['clusters'])
        fileEvents = nga.get_events(fileName)
        chanMax = fileEvents[:,channelIDs['ssc']].max()
        cd3ThreshX = np.array([cd3Results[fileName]['cutpoint']]).repeat(25)
        cd3ThreshY = np.linspace(0,chanMax,25)
        thresholdLines[fileName][0] = (cd3ThreshX,cd3ThreshY)

    ########### fsc  ##################
    print 'getting fsc events...'
    fscChanIndex = channelIDs['fsc']
    fscResults = find_positivity_threshold("fsc",fscChanIndex,fileList,nga,allLabels,verbose=True,filterID='filter1')
    figName = os.path.join(figsDir,'ThresholdsEM_fsc.png')
    make_positivity_plot(nga,fileList,fscChanIndex,figName,fscResults,filterID='filter1')

    ## save data
    for fileName in fileList:
        fileEvents = nga.get_events(fileName)
        chanMax = fileEvents[:,fscChanIndex].max()
        fscThreshX = np.array([fscResults[fileName]['cutpoint']]).repeat(25)
        fscThreshY = np.linspace(0,chanMax,25)
        thresholdLines[fileName][1] = (fscThreshY,fscThreshX)

    ########### ssc  ##################
    print 'getting ssc events...'
    sscChanIndex = channelIDs['ssc']
    sscResults = find_positivity_threshold("ssc",sscChanIndex,fileList,nga,allLabels,verbose=True,filterID='filter1')
    figName = os.path.join(figsDir,'ThresholdsEM_ssc.png')
    make_positivity_plot(nga,fileList,sscChanIndex,figName,sscResults,filterID='filter1')

    ## save data
    for fileName in fileList:
        fileEvents = nga.get_events(fileName)
        chanMax = fileEvents[:,sscChanIndex].max()
        sscThreshX = np.array([sscResults[fileName]['cutpoint']]).repeat(25)
        sscThreshY = np.linspace(0,chanMax,25)
        thresholdLines[fileName][2] = (sscThreshY,sscThreshX)

    ########## revised cd3 ###########
    cd3PosClusters = {}
    for fileName in fileList:
        cd3PosClusters[fileName] = []
        statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
        events = nga.get_events(fileName)
        fileInd = fileList.index(fileName)

        for cid in np.unique(fileLabels):
            clusterEventsInds = np.where(fileLabels==cid)[0]
            clusterEventsCD3 = events[clusterEventsInds,cd3ChanIndex]
            clusterEventsSSC = events[clusterEventsInds,sscChanIndex]
            clusterEventsFSC = events[clusterEventsInds,fscChanIndex]
        
            if clusterEventsCD3.mean() < cd3Results[fileName]['cutpoint']:
                continue
            if clusterEventsSSC.mean() > sscResults[fileName]['cutpoint']:
                continue
            if clusterEventsFSC.mean() > fscResults[fileName]['cutpoint']:
                continue

            if undumpedClusters != None and cid not in undumpedClusters[fileInd]:
                continue

            cd3PosClusters[fileName].append(cid)

    for fileName in fileList:
        nga.handle_filtering('filter2',fileName,modelRunID,'components',cd3PosClusters[fileName])
        events1 = nga.get_events(fileName,filterID='filter2')
        events2 = nga.get_events(fileName)
        fPercent = float(events1.shape[0]) / float(events2.shape[0])
        writer.writerow([fileName,"CD3",events1.shape[0],fPercent,str(cd3PosClusters[fileName])])

    ########### CD4 ##################
    cd4ChanIndex = channelIDs['cd4']
    print 'getting cd4 events...'
    cd4Results = find_positivity_threshold('cd4',cd4ChanIndex,fileList,nga,allLabels,verbose=True,filterID='filter2')#filter2
    figName = os.path.join(figsDir,'ThresholdsEM_cd4.png')
    make_positivity_plot(nga,fileList,cd4ChanIndex,figName,cd4Results,filterID='filter2')

    ########### CD8 ##################
    cd8ChanIndex = channelIDs['cd8']
    print 'getting cd8 events...'
    cd8Results = find_positivity_threshold('cd8',cd8ChanIndex,fileList,nga,allLabels,verbose=True,filterID='filter2')
    figName = os.path.join(figsDir,'ThresholdsEM_cd8.png')
    make_positivity_plot(nga,fileList,cd8ChanIndex,figName,cd8Results,filterID='filter2')

    ########## create the cd4-cd8 positive line ##############
    cd4cd8Thresholds = {}
    for fileName in fileList:
        if cd8Results[fileName]['params']['mu2'] > cd8Results[fileName]['params']['mu1']:
            cutpointA = stats.norm.ppf(0.95,loc=cd8Results[fileName]['params']['mu1'],scale=np.sqrt(cd8Results[fileName]['params']['sig1']))
            cutpointB = stats.norm.ppf(0.005,loc=cd8Results[fileName]['params']['mu2'],scale=np.sqrt(cd8Results[fileName]['params']['sig2']))
        else:
            cutpointA = stats.norm.ppf(0.95,loc=cd8Results[fileName]['params']['mu2'],scale=np.sqrt(cd8Results[fileName]['params']['sig2']))
            cutpointB = stats.norm.ppf(0.005,loc=cd8Results[fileName]['params']['mu1'],scale=np.sqrt(cd8Results[fileName]['params']['sig1']))

        #if cutpointB < cutpointA:
        #    cutPointB = cutpointA

        cutpoints = [cutpointA,cutpointB]
        cutpoints.sort()
        cutpointA, cutpointB = cutpoints 

        events1 = nga.get_events(fileName,filterID='filter2')
        chanMax = events1[:,cd4ChanIndex].max()
        threshYA = np.array([cutpointA]).repeat(13)
        threshXA = np.linspace(0,cd4Results[fileName]['cutpoint'],13)
        threshYB = np.array([cutpointB]).repeat(12)
        threshXB = np.linspace(cd4Results[fileName]['cutpoint'],chanMax,12)
        threshX = np.hstack([threshXA,threshXB])
        threshY = np.hstack([threshYA,threshYB])
        cd4cd8Thresholds[fileName] = (cutpointA, cutpointB)
        thresholdLines[fileName][3] = (threshX,threshY)

    cd4PosClusters = {}
    cd8PosClusters = {}
    dpClusters = {}
    for fileName in fileList:
        cd4PosClusters[fileName] = []
        cd8PosClusters[fileName] = []
        dpClusters[fileName] = []
        filterIndices = nga.get_filter_indices(fileName,'filter2')
        statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
        filteredLabels = np.array([int(i) for i in fileLabels[filterIndices]])

        cd3Events = nga.get_events(fileName,filterID='filter2')
        for cid in cd3PosClusters[fileName]:
            clusterEventsInds = np.where(filteredLabels==cid)[0]
            clusterEventsCD8 = cd3Events[clusterEventsInds,cd8ChanIndex]
            clusterEventsCD4 = cd3Events[clusterEventsInds,cd4ChanIndex]
            clusterEventsCD3 = cd3Events[clusterEventsInds,channelIDs['cd3']]
            #clusterEventsCyto = cd3Events[clusterEventsInds,channelIDs['IFNg-IL2']]

            #print cid, clusterEventsCD8.mean(), cd4cd8Thresholds[fileName], clusterEventsCD4.mean(), cd4Results[fileName]['cutpoint']

            ## find double positives
            if clusterEventsCD8.mean() > cd4cd8Thresholds[fileName][1] and clusterEventsCD4.mean() > cd4Results[fileName]['cutpoint']:
                #dpClusters[fileName].append(cid)
                #(a_s,b_s,r,tt,stderr)=stats.linregress(clusterEventsCD3,clusterEventsCyto)
                #
                #if r > 0.5:
                #    continue
                #else:
                cd8PosClusters[fileName].append(cid)
                #continue

            if clusterEventsCD8.mean() > cd4cd8Thresholds[fileName][0] and clusterEventsCD4.mean() < cd4Results[fileName]['cutpoint']:
                cd8PosClusters[fileName].append(cid)
            elif clusterEventsCD8.mean() < cd4cd8Thresholds[fileName][1] and clusterEventsCD4.mean() > cd4Results[fileName]['cutpoint']:
                cd4PosClusters[fileName].append(cid)

    ### save cd4 and cd8 clusters ###
    for fileName in fileList:    
        nga.handle_filtering('filter3',fileName,modelRunID,'components',cd8PosClusters[fileName])
        eventsCD3 = nga.get_events(fileName,filterID='filter2')
        eventsCD8 = nga.get_events(fileName,filterID='filter3')
        if eventsCD8 == None:
            fPercent = np.nan
        else:
            fPercent = float(eventsCD8.shape[0]) / float(eventsCD3.shape[0])
        writer.writerow([fileName,"CD8",eventsCD8.shape[0],fPercent,str(cd8PosClusters[fileName])])

    for fileName in fileList:
        nga.handle_filtering('filter4',fileName,modelRunID,'components',cd4PosClusters[fileName])
        eventsCD3 = nga.get_events(fileName,filterID='filter2')
        eventsCD4 = nga.get_events(fileName,filterID='filter4')
        if eventsCD4 == None:
            fPercent = np.nan
        else: 
            fPercent = float(eventsCD4.shape[0]) / float(eventsCD3.shape[0])
        writer.writerow([fileName,"CD4",eventsCD4.shape[0],fPercent,str(cd4PosClusters[fileName])])

    for fileName in fileList:
        if len(cd8PosClusters[fileName]) == 0:
            cd8PosClusters[fileName] = None

        if len(cd4PosClusters[fileName]) == 0:
            cd4PosClusters[fileName] = None

    ###################################################
    ## plot the gating strategy
    ###################################################
    create = True
    if create == True:
        print 'creating gating strategy figures...'
        ## set channels to view
        plotsToViewChannels = [(cd3ChanIndex,sscChanIndex),
                               (cd3ChanIndex,fscChanIndex),
                               (cd3ChanIndex,sscChanIndex),
                               (cd4ChanIndex,cd8ChanIndex),
                               (cd4ChanIndex,cd8ChanIndex),
                               (cd4ChanIndex,cd8ChanIndex),
                               (cd4ChanIndex,cd8ChanIndex)] + [(0,0)] * 9
        subplotTitles = ["CD3 Threshold (All)","FSC Threshold (CD3)","SSC Threshold (CD3)",
                         "CD8-CD4 Threshold (CD3)", "CD8 Positive","CD4 Positive"]
        nga.set("plots_to_view_channels",plotsToViewChannels)
        plotsToViewRuns = [modelRunID for i in range(16)]
        nga.set('plots_to_view_runs',plotsToViewRuns)
        numSubplots = 6
        nga.set('results_mode','components')

        for fn in range(len(fileList)):
            ## set file names
            actualFileList = nga.get_file_names()
            fileName = fileList[fn]
            fileInd = actualFileList.index(fileName)
            plotsToViewFiles = [fileInd for i in range(16)]
            nga.set("plots_to_view_files",plotsToViewFiles)
            
            ## set highlights
            plotsToViewHighlights = [None for c in range(16)]
            plotsToViewHighlights[1] = cd3Results[fileName]['clusters']
            plotsToViewHighlights[2] = cd3Results[fileName]['clusters']
            plotsToViewHighlights[3] = cd3PosClusters[fileName]
            plotsToViewHighlights[4] = cd8PosClusters[fileName]
            plotsToViewHighlights[5] = cd4PosClusters[fileName]
            nga.set('plots_to_view_highlights',plotsToViewHighlights)

            figName = os.path.join(figsDir,'autoGatingStrategy_%s.png'%fileName)
            figTitle = "Auto Gating Strategy %s"%(fileName)
            for key,item in thresholdLines[fileName].iteritems():
                print key, len(item[0]), len(item[1])
            ss = SaveSubplots(nga.homeDir,figName,numSubplots,figMode='analysis',figTitle=figTitle,forceScale=False,drawState='heat',
                              addLine=thresholdLines[fileName],axesOff=True,subplotTitles=subplotTitles)

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
