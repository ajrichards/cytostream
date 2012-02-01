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
from SpectralMix import SpectralCluster


## functions
def _calculate_fscores(neg_pdf, pos_pdf, beta=1, theta=2.0):
    n = len(neg_pdf)
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

def calculate_fscores(neg,pos,numBins=100,beta=1.0, theta=2.0, fullOutput=True):
    neg = neg.copy()
    pos = pos.copy()
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

        fileLabels = allLabels[fileInd]
        events = nga.get_events(fileName)

        if filterID != None and re.search('filter',str(filterID)):
            filterIndices = nga.get_filter_indices(fileName,filterID)
            fileLabels = fileLabels[filterIndices]
            events = events[filterIndices,:]
            
        uniqueLabels = np.sort(np.unique(fileLabels))
            
        cd3Events = events[:,cd3ChanIndex]
        cd3Positive = []

        ## get lower threshold of larger component 
        tcg,cutpoint = two_component_em(cd3Events,emGuesses=initialGuesses,verbose=verbose,subset=subset)
        
        ## need to redefine cd3Events?
        cd3Events = events[:,cd3ChanIndex]

        for cid in uniqueLabels:
            ## ensure cluster has at least the minNumEvents
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
        #print 'debug', fileName, len(cd3Indices),len(fileLabels), cd3Percent, rawPercent

        cd3Results[fileName]['indices'] = cd3Indices
        cd3Results[fileName]['clusters'] = cd3Positive
        cd3Results[fileName]['percent'] = cd3Percent
        cd3Results[fileName]['params'] = tcg['params'].copy()
        cd3Results[fileName]['cutpoint'] = cutpoint
        
    return cd3Results


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

def alternative_cd3_filtering(nga,fileName,runLabels,channelDict,writer,modelRunID='run1'):
    ## functions
    
    def get_mode_labels(evts,modeLabels,parentLabels):
        newLabels = np.zeros(evts.shape[0])
        for i, modeLab in enumerate(modeLabels):
            clusterLab = parentLabels[i]
            clusterIndices = np.where(parentLabels == clusterLab)[0]
            newLabels[clusterIndices] = modeLab
        newLabels = np.array([int(l) for l in newLabels])

        return newLabels

    ## create an array where each row corresponds to the cluster means
    events = nga.get_events(fileName)
    uniqueLabels = np.sort(np.unique(runLabels))
    clusterMeanList = []

    meanMat = get_mean_matrix(events,runLabels)
    print "...getting cd3 subset -- spectral clustering"
    numRepeats = 5
    for i in range(numRepeats):
        try:
            includedChannels = [channelDict['cd3'],channelDict['ssca'],channelDict['fsca']]
            sc1 = SpectralCluster(meanMat[:,includedChannels],k=6,labels=None,sigma=0.05)
            modeLabels = sc1.clustResults['labels']
            break
        except:
            "\tspectral clustering being rerun..."
            modeLabels = None
    newLabels = get_mode_labels(events,modeLabels,runLabels)
    masterColorList = get_all_colors()
    fig = plt.figure()
    ax = fig.add_subplot(131)
    dataX,dataY = (events[:,channelDict['cd3']],events[:,channelDict['ssca']])
    colorList = masterColorList[newLabels]
    ax.scatter([dataX],[dataY],c=colorList,s=1,edgecolor='none')
    ax.set_aspect(1./ax.get_data_ratio())
    ax.set_yticks([])
    ax.set_xticks([])

    meansCD3 = []
    for v in np.unique(newLabels):
        clusterIndices = np.where(newLabels==v)[0]
        cd3Mean = events[clusterIndices,channelDict['cd3']].mean()
        meansCD3.append(cd3Mean)
        #print v,masterColorList[v],clusterIndices.size,cd3Mean
        
    cd3MeanRanks = np.argsort(np.array(meansCD3))
    indicesToRemove = np.where(newLabels==cd3MeanRanks[0])[0] #[cd3MeanRanks[0]]
    indicesToRetain = np.array(list(set(range(events.shape[0])).difference(set(indicesToRemove.tolist()))))
    newEvents = events[indicesToRetain,:]
    newLabels = runLabels[indicesToRetain]
    filteredMeanMat = get_mean_matrix(newEvents,newLabels)

    print "...getting cd3 subset -- kmeans clustering"
    kmeansResults = run_kmeans_with_sv(newEvents[:,[channelDict['cd3'],channelDict['ssca'],channelDict['fsca']]],kRange=[3],subsample=5000)

    meansCD3 = []
    for v in np.sort(np.unique(kmeansResults['labels'])):
        clusterIndices = np.where(kmeansResults['labels']==v)[0]
        cd3Mean = newEvents[clusterIndices,channelDict['cd3']].mean()
        meansCD3.append(cd3Mean)
        #print v,masterColorList[v],clusterIndices.size,cd3Mean
    cd3MeanRanks = np.argsort(np.array(meansCD3))

    ax = fig.add_subplot(132)
    dataX,dataY = (newEvents[:,channelDict['cd3']],newEvents[:,channelDict['ssca']])
    colorList = masterColorList[kmeansResults['labels']]
    ax.scatter([dataX],[dataY],c=colorList,s=1,edgecolor='none')
    ax.set_aspect(1./ax.get_data_ratio())
    ax.set_yticks([])
    ax.set_xticks([])
    figsDir = os.path.join(nga.homeDir,'results',modelRunID,'thresholding')
    if os.path.isdir(os.path.join(nga.homeDir,'results',modelRunID)) == False:
        os.mkdir(os.path.join(nga.homeDir,'results',modelRunID))
    if os.path.isdir(figsDir) == False:
        os.mkdir(figsDir)

    ## save data
    normalizedIndices = np.where(kmeansResults['labels']==cd3MeanRanks[-1])[0]
    normalizedIndices = indicesToRetain[normalizedIndices]
    nga.handle_filtering('filterCD3',fileName,modelRunID,'components',normalizedIndices,asIndices=True)
    fPercent = float(normalizedIndices.size) / float(events.shape[0]) * 100
    writer.writerow([fileName,"CD3",normalizedIndices.size,fPercent,"[]"])
    print indicesToRetain.shape
    print normalizedIndices.shape

    ax = fig.add_subplot(133)
    dataX,dataY = (events[normalizedIndices,channelDict['cd3']],events[normalizedIndices,channelDict['ssca']])
    #colorList = masterColorList[newLabels]
    ax.scatter([dataX],[dataY],c='b',s=1,edgecolor='none')
    ax.set_aspect(1./ax.get_data_ratio())
    ax.set_yticks([])
    ax.set_xticks([])

    figName = os.path.join(figsDir,'Thresholding_cd3_%s.png'%fileName)
    plt.savefig(os.path.join(figName))


def perform_automated_gating_basic_subsets(nga,channelIDs,modelRunID='run1',fileList=None,figsDir=None,undumpedClusters=None):

    ## variables
    if fileList == None:
        fileList = nga.get_file_names()
    if figsDir == None:
        if os.path.isdir(os.path.join(nga.homeDir,'results',modelRunID)) == False:
            os.mkdir(os.path.join(nga.homeDir,'results',modelRunID))
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
 
    #########################################
    for i,fileName in enumerate(fileList):
        runLabels = allLabels[i]
        alternative_cd3_filtering(nga,fileName,runLabels,channelIDs,writer)

    cd3PosClusters = {}
    
    for fileName in fileList:
        cd3PosClusters[fileName] = []
        statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
        fileEvents = nga.get_events(fileName)
        ##fileInd = fileList.index(fileName)
        indsCD3 = nga.get_filter_indices(fileName,'filterCD3')
        meanCD3 = fileEvents[indsCD3,:].mean(axis=0)
        meanMat = get_mean_matrix(fileEvents,fileLabels)
        dc = DistanceCalculator()
        iChannels = [channelIDs['cd3']] 
        dc.calculate(meanMat[:,iChannels],matrixMeans=meanCD3[iChannels])
        distances = dc.get_distances()
        
        uniqueLabels = np.sort(np.unique(fileLabels))
        for i,centroid in enumerate(uniqueLabels):
            print i,distances[i]

        #allDistances = None
        #uniqueLabels = np.sort(np.unique(fileLabels))
        #for centroid in uniqueLabels:
        #    centroidIndices = np.where(fileLabels == centroid)[0]
        #    centroidMean = fileEvents[centroidIndices,:].mean(axis=0)
        #    dc = DistanceCalculator()
        #    dc.calculate(events,matrixMeans=centroidMean)
        #    distances = dc.get_distances()
        #    #distances = whiten(distances)                                                                          
        #    distances = np.array([distances]).T
        #    if allDistances == None:
        #        allDistances =  distances
        #    else:
        #        allDistances = np.hstack([allDistances,distances])
        # 
        #newLabels = np.zeros(mat.shape[0])

        #for i in range(allDistances.shape[0]):
        #    newLabels[i] = uniqueLabels[np.argmin(allDistances[i,:])]

    sys.exit()



    #########################################
    '''
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
        nga.handle_filtering('filterCD3a',fileName,modelRunID,'components',cd3Results[fileName]['clusters'])
        fileEvents = nga.get_events(fileName)
        chanMax = fileEvents[:,channelIDs['cd3']].max()
        cd3ThreshX = np.array([cd3Results[fileName]['cutpoint']]).repeat(25)
        cd3ThreshY = np.linspace(0,chanMax,25)
        thresholdLines[fileName][0] = (cd3ThreshX,cd3ThreshY)

    ########### fsc  ##################
    print 'getting fsc events...'
    if channelIDs.has_key('fsca'):
        fscChanIndex = channelIDs['fsca']
    elif channelIDs.has_key('fsch'):
        fscChanIndex = channelIDs['fsch']
    elif channelIDs.has_key('fscw'):
        fscChanIndex = channelIDs['fscw']
    elif channelIDs.has_key('fsc'):
        fscChanIndex = channelIDs['fsc']
    else:
        print "ERROR: perform_automated_gating_basic_subsets cannot find fsc"

    fscResults = find_positivity_threshold("fsc",fscChanIndex,fileList,nga,allLabels,verbose=True,filterID='filterCD3a')
    figName = os.path.join(figsDir,'ThresholdsEM_fsc.png')
    make_positivity_plot(nga,fileList,fscChanIndex,figName,fscResults,filterID='filterCD3a')

    ## save data
    for fileName in fileList:
        fileEvents = nga.get_events(fileName)
        chanMax = fileEvents[:,fscChanIndex].max()
        fscThreshX = np.array([fscResults[fileName]['cutpoint']]).repeat(25)
        fscThreshY = np.linspace(0,chanMax,25)
        thresholdLines[fileName][1] = (fscThreshY,fscThreshX)

    ########### ssc  ##################
    print 'getting ssc events...'
    if channelIDs.has_key('ssca'):
        sscChanIndex = channelIDs['ssca']
    elif channelIDs.has_key('ssch'):
        sscChanIndex = channelIDs['ssch']
    elif channelIDs.has_key('sscw'):
        sscChanIndex = channelIDs['sscw']
    elif channelIDs.has_key('ssc'):
        sscChanIndex = channelIDs['ssc']
    else:
        print "ERROR: perform_automated_gating_basic_subsets cannot find ssc"
    sscResults = find_positivity_threshold("ssc",sscChanIndex,fileList,nga,allLabels,verbose=True,filterID='filterCD3a')
    figName = os.path.join(figsDir,'ThresholdsEM_ssc.png')
    make_positivity_plot(nga,fileList,sscChanIndex,figName,sscResults,filterID='filterCD3a')

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
            ## filter based on coefficient of variation
            #cvCD3,cvSSC = get_cluster_coeff_var(nga,channelIDs,fileName,cid,sscChanIndex,modelRunID='run1')
            #
            #if cvCD3 > 0.2:# or cvSSC > 0.25:
            #    continue

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
        nga.handle_filtering('filterCD3',fileName,modelRunID,'components',cd3PosClusters[fileName])
        indsCD3 = nga.get_filter_indices(fileName,'filterCD3')
        eventsOrig = nga.get_events(fileName)
        fPercent = float(indsCD3.size) / float(eventsOrig.shape[0]) * 100.0
        writer.writerow([fileName,"CD3",indsCD3.size,fPercent,str(cd3PosClusters[fileName])])

    '''
    ########### CD4 ##################
    # split CD4 into CD4 Pos and CD4 Neg

    cd4ChanIndex = channelIDs['cd4']
    print 'getting cd4 events...'
    cd4Results = find_positivity_threshold('cd4',cd4ChanIndex,fileList,nga,allLabels,verbose=True,filterID='filterCD3')#filter2
    for fileName in fileList:
        positiveCD4 = [i for i in cd3PosClusters[fileName]]
        negativeCD4 = [i for i in cd3PosClusters[fileName]]
        fileEvents = nga.get_events(fileName)
        filterIndices = nga.get_filter_indices(fileName,'filterCD3')
        fileEvents = fileEvents[filterIndices,:]

        statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
        filteredLabels = np.array([int(i) for i in fileLabels[filterIndices]])

        for cid in cd3PosClusters[fileName]:
            clusterEventsInds = np.where(filteredLabels==cid)[0]
            clusterMean = fileEvents[clusterEventsInds,cd4ChanIndex].mean()
            if clusterMean < cd4Results[fileName]['cutpoint']:
                positiveCD4.remove(cid)
            else:
                negativeCD4.remove(cid)

        nga.handle_filtering('filterCD4p',fileName,modelRunID,'components',positiveCD4)#filter2a
        nga.handle_filtering('filterCD4n',fileName,modelRunID,'components',negativeCD4)#filter2b
        
    figName = os.path.join(figsDir,'ThresholdsEM_cd4.png')
    make_positivity_plot(nga,fileList,cd4ChanIndex,figName,cd4Results,filterID='filterCD3')


    ########### CD8 ##################
    cd8ChanIndex = channelIDs['cd8']
    print 'getting cd8 events...' 
    cd8ResultsA = find_positivity_threshold('cd8',cd8ChanIndex,fileList,nga,allLabels,verbose=True,filterID='filterCD4n')

    ########## create the cd4-cd8 positive line ##############
    cd4cd8Thresholds = {}
    for fileName in fileList:

        ## specify cutpoint A
        if cd8ResultsA[fileName]['params']['mu2'] > cd8ResultsA[fileName]['params']['mu1']:
            cutpointA = stats.norm.ppf(0.00001,loc=cd8ResultsA[fileName]['params']['mu2'],
                                       scale=np.sqrt(cd8ResultsA[fileName]['params']['sig2']))
        else:
            cutpointA = stats.norm.ppf(0.00001,loc=cd8ResultsA[fileName]['params']['mu1'],
                                       scale=np.sqrt(cd8ResultsA[fileName]['params']['sig1']))

        ## specify cutpoint B
        eventsCD4p = nga.get_events(fileName)
        filterIndices = nga.get_filter_indices(fileName,'filterCD4p')
        eventsCD4p = eventsCD4p[filterIndices,:]
        eCDF = EmpiricalCDF(eventsCD4p[:,cd8ChanIndex])
        print type(eventsCD4p)
        print eventsCD4p
        cutpointB = eCDF.get_value(0.98)
        
        events1 = nga.get_events(fileName)
        filterIndices = nga.get_filter_indices(fileName,'filterCD3')
        events1 = events1[filterIndices,:]

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
    cd3ToRemove = {}
    for fileName in fileList:
        cd4PosClusters[fileName] = []
        cd8PosClusters[fileName] = []
        dpClusters[fileName] = []
        cd3ToRemove[fileName] = []
        filterIndices = nga.get_filter_indices(fileName,'filterCD3')
        statModel, fileLabels = nga.get_model_results(fileName,modelRunID,'components')
        filteredLabels = np.array([int(i) for i in fileLabels[filterIndices]])

        cd3Events = nga.get_events(fileName)
        cd3Inds = nga.get_filter_indices(fileName,'filterCD3')
        cd3Events = cd3Events[cd3Inds,:]
        for cid in cd3PosClusters[fileName]:
            clusterEventsInds = np.where(filteredLabels==cid)[0]
            clusterEventsCD8 = cd3Events[clusterEventsInds,cd8ChanIndex]
            clusterEventsCD4 = cd3Events[clusterEventsInds,cd4ChanIndex]
            clusterEventsCD3 = cd3Events[clusterEventsInds,channelIDs['cd3']]
            
            ## find double positives
            if clusterEventsCD8.mean() > cd4cd8Thresholds[fileName][1] and clusterEventsCD4.mean() > cd4Results[fileName]['cutpoint']:
                
                dpFlag = examine_double_positive(nga,channelIDs,fscChanIndex,sscChanIndex,fileName,cid,figsDir,modelRunID=modelRunID)
                #if dpFlag == True:
                #    dpClusters[fileName].append(cid)
                #else:
                #    cd3ToRemove[fileName].append(cid)
        
                cd8PosClusters[fileName].append(cid)

            if clusterEventsCD8.mean() > cd4cd8Thresholds[fileName][0] and clusterEventsCD4.mean() < cd4Results[fileName]['cutpoint']:
                cd8PosClusters[fileName].append(cid)
            elif clusterEventsCD8.mean() < cd4cd8Thresholds[fileName][1] and clusterEventsCD4.mean() > cd4Results[fileName]['cutpoint']:
                cd4PosClusters[fileName].append(cid)

    ### save the cd3 positive clusters
    #for fileName in fileList:
        ## remove cd3 events that do not pass filtering
        #refinedCD3 = cd3PosClusters[fileName]
        #for cid in cd3ToRemove:
        #    if cid in refinedCD3:
        #        refinedCD3.remove(cid)
        #nga.handle_filtering('filterCD3',fileName,modelRunID,'components',refinedCD3)
        #events1 = nga.get_events(fileName,filterID='filterCD3')
        #events2 = nga.get_events(fileName)
        #fPercent = float(events1.shape[0]) / float(events2.shape[0])
        #origEvents = nga.get_events(fileName)
        #indsCD3 = nga.get_filter_indices(fileName,'filterCD3')
        #if indsCD3 == None or indsCD3.size == 0:
        #    fPercent = np.nan
        #else:
        #    fPercent = float(indsCD3.size) / float(origEvents.shape[0])
        
        #writer.writerow([fileName,"CD3",events1.shape[0],fPercent,str(cd3PosClusters[fileName])])

    ### save cd4 and cd8 clusters ###
    for fileName in fileList:    
        nga.handle_filtering('filterCD8',fileName,modelRunID,'components',cd8PosClusters[fileName])
        indsCD3 = nga.get_filter_indices(fileName,'filterCD3')
        indsCD8 = nga.get_filter_indices(fileName,'filterCD8')
        if indsCD8 == None or indsCD8.size == 0:
            fPercent = np.nan
        else:
            fPercent = float(indsCD8.size) / float(indsCD3.size) * 100.0
        writer.writerow([fileName,"CD8",indsCD8.size,fPercent,str(cd8PosClusters[fileName])])

    for fileName in fileList:
        nga.handle_filtering('filterCD4',fileName,modelRunID,'components',cd4PosClusters[fileName])
        indsCD3 = nga.get_filter_indices(fileName,'filterCD3')
        indsCD4 = nga.get_filter_indices(fileName,'filterCD4')

        if indsCD4 == None or indsCD4.size == 0:
            fPercent = np.nan
        else: 
            fPercent = float(indsCD4.size) / float(indsCD3.size) * 100.0
        writer.writerow([fileName,"CD4",indsCD4.size,fPercent,str(cd4PosClusters[fileName])])

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

            if undumpedClusters != None:
                plotsToViewHighlights[0] = undumpedClusters[fileInd]

            plotsToViewHighlights[1] = cd3Results[fileName]['clusters']
            plotsToViewHighlights[2] = cd3Results[fileName]['clusters']
            plotsToViewHighlights[3] = cd3PosClusters[fileName]
            plotsToViewHighlights[4] = cd8PosClusters[fileName]
            plotsToViewHighlights[5] = cd4PosClusters[fileName]
            nga.set('plots_to_view_highlights',plotsToViewHighlights)

            figName = os.path.join(figsDir,'autoGatingStrategy_%s.png'%fileName)
            figTitle = "Auto Gating Strategy %s"%(fileName)

            ss = SaveSubplots(nga.controller,figName,numSubplots,figMode='analysis',figTitle=figTitle,useScale=True,drawState='scatter',
                              subplotTitles=subplotTitles,addLine=thresholdLines[fileName])

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


def get_cytokine_threshold(nga,posControlFile,negControlFile,cytoIndex,filterID,beta,fullOutput=True,numBins=150):
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

    fResults = calculate_fscores(negEvents,posEvents,numBins=numBins,beta=beta,fullOutput=fullOutput)

    return fResults


def get_cytokine_positive_events(nga,cytoIndex,fThreshold,filterID,fileList=None):
    '''
    function works for both pregated and automated data
    '''

    if fileList == None:
        fileList = nga.get_file_names()

    percentages = {}
    counts = {}
    idx = {}
    for fileName in fileList:
        events = nga.get_events(fileName)
        if filterID != None:
            filterInds = nga.get_filter_indices(fileName,filterID)
            events = events[filterInds,:]
        
        data = events[:,cytoIndex]
        positiveEventInds = np.where(data > fThreshold)[0]
        if events.shape[0] == 0:
            percentages[fileName] = 0
        else:
            percentages[fileName] = (float(positiveEventInds.size)/float(events.shape[0])) * 100.0
        counts[fileName] = positiveEventInds.size
        idx[fileName] = positiveEventInds

    return percentages, counts, idx
