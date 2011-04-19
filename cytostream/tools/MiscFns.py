import sys,os,re,csv,cPickle
import numpy as np
import fcm

def calculate_intercluster_score(expListNames,expListData,expListLabels):
    '''
    calculate a global file alignment score

    '''
    
    masterLabelList = get_master_label_list(expListLabels)

    ## get a dict of magnitudes
    magnitudeDict = {}
    for cluster in masterLabelList:
        magnitude = -1
        for fileInd in range(len(expListNames)):
            fileName = expListNames[fileInd]
            fileLabels = expListLabels[fileInd]
            uniqueLabels = np.sort(np.unique(fileLabels)).tolist()
            if uniqueLabels.__contains__(cluster):
                magnitude+=1
        
        magnitudeDict[cluster] = magnitude
    
    ## calculate a score
    goodnessScore = 0
    for cluster in masterLabelList:
        totalEventsAcrossFiles = 0
        for fileInd in range(len(expListNames)):
            fileName = expListNames[fileInd]
            fileLabels = expListLabels[fileInd]
            fileData = expListData[fileInd]
            clusterEvents = fileData[np.where(fileLabels==cluster)[0],:]
            n,k = np.shape(clusterEvents)
            totalEventsAcrossFiles+=n
        
        goodnessScore += (magnitudeDict[cluster] * float(totalEventsAcrossFiles))    
    
    return goodnessScore


def get_file_data(dataPath,dataType='fcs',channelsOnly=False):

    print 'data path', dataPath

    if dataType not in ['fcs','txt','pickle']:
        print "ERROR in tools.get_file_data -- bad data type ", dataType
        return None, None

    if os.path.isfile(dataPath) == False:
        print "WARNING in tools.get_file_data -- cannot get fcs data bad file path"
        return None,None

    fcsData,fileChannels = None, None

    if dataType == 'fcs':
        if channelsOnly == False:
            fcsData = fcm.loadFCS(dataPath)
        fileChannels = fcsData.channels
    elif dataType == 'pickle':
        if channelsOnly == False:
            fid = open(dataPath,'rb')
            fcsData = cPickle.load(fid)
            fid.close()
        fileChannels = None
    else:
        if channelsOnly == False:
            fcsData = read_txt_into_array(dataPath)
        fileChannels = fileChannels = read_txt_to_file_channels(re.sub("\.out",".txt",dataPath))

    return fcsData, fileChannels


def get_sample_statistics(expListLabels,expListNames,expListDataPaths,dataType='fcs'):
 
    if len(expListLabels) != len(expListNames) or len(expListLabels) != len(expListDataPaths):
        print "ERROR: bad input data in get_sample_statistics", len(expListLabels), len(expListNames), len(expListDataPaths)
        return None
                                                                  
    centroids, variances, numClusts, numDataPoints = {},{},{},{}
    for expInd in range(len(expListLabels)):
        expName = expListNames[expInd]
        centroids[expName] = {}
        variances[expName] = {}
        numClusts[expName] = None
        numDataPoints[expName] = {}

    for expInd in range(len(expListLabels)):
        expName = expListNames[expInd]
        expData,fileChannels = get_file_data(expListDataPaths[expInd],dataType=dataType)
        expLabels = expListLabels[expInd]

        for cluster in np.sort(np.unique(expLabels)):
            clusterInds = np.where(expLabels==cluster)[0]
            centroids[expName][str(cluster)] = expData[clusterInds,:].mean(axis=0)
            variances[expName][str(cluster)] = expData[clusterInds,:].var(axis=0)
            numDataPoints[expName][str(cluster)] = len(np.where(expLabels==cluster)[0])

        numClusts[expName] = len(np.unique(expLabels))

    return {'mus':centroids,'sigmas':variances,'k':numClusts,'n':numDataPoints}

def get_master_label_list(expListLabels):

    labelMasterList = set([])
    for labelList in expListLabels:
        fileLabels = np.sort(np.unique(labelList))
        labelMasterList.update(fileLabels)

    masterLabelList = np.sort(np.unique(labelMasterList))

    return masterLabelList


def read_txt_to_file_channels(filePath):
    if os.path.isfile(filePath) == False:
        print "ERROR: bad file name in read_txt_into_array"
        return

    fileChannels = []
    fid = open(filePath,'r')

    for linja in fid:
        if re.search('\w',linja):
            linja = re.sub('\s','',linja)
            fileChannels.append(linja)

    fid.close()

    return fileChannels


def read_txt_into_array(filePath,header=False,delim='\t'):
    if os.path.isfile(filePath) == False:
        print "ERROR: bad file name in read_txt_into_array"
        return

    ## get the number of lines
    fid = open(filePath,'r')
    rowCount,colCount = 0,0
    for linja in fid:
        linja = re.split(delim,linja)
        if len(linja) > 1:
            rowCount +=1

        if rowCount == 1:
            colCount = len(linja)

    fid.close()

    ## error check
    if rowCount == 0 or colCount == 0:
        print "ERROR: either row or cols were zeros"
        return

    ## read results into array 
    results = np.zeros((rowCount,colCount),dtype=float)

    fid = open(filePath,'r')
    row = -1
    for linja in fid:
        linja = re.split(delim,linja)
        linja = [float(re.sub("\s+","",element)) for element in linja]

        if len(linja) <= 1:
            continue

        row +=1
        results[row,:] = linja

    fid.close()

    return results


def fetch_plotting_events(selectedFile,model,log,subsample,labels=None):
    
    ## declare variables
    fontName = log.log['font_name']
    markerSize = int(log.log['scatter_marker_size'])
    fontSize = log.log['font_size']
    plotType = log.log['plot_type']
    filterInFocus = log.log['filter_in_focus']

    ## get events                                                                                                                       
    if re.search('filter',str(subsample)):
        pass
    elif subsample != 'original':
        subsample = str(int(float(subsample)))

    ## ensure the proper events are being loaded 
    if re.search('original',str(subsample)) and re.search('filter',str(subsample)):
        if log == None:
            subsample = 2e04
        else:
            subsample = log.log['setting_max_scatter_display']

        events = model.get_events(selectedFile,subsample='original')
        subsampleIndices = model.get_subsample_indices(subsample)
        events = events[subsampleIndices,:]
    elif filterInFocus != None and filterInFocus != 'None' and re.search('filter',filterInFocus):
        events = model.get_events(selectedFile,subsample=filterInFocus)
    elif re.search('original',str(subsample)):
        if log == None:
            subsample = 2e04
        else:
            subsample = log.log['setting_max_scatter_display']

        subsampleIndices = model.get_subsample_indices(subsample)
        if labels != None:
            labels = labels[subsampleIndices]

        events = model.get_events(selectedFile,subsample=subsample)
    else:
        events = model.get_events(selectedFile,subsample=subsample)

    return events,labels

def get_file_sample_stats(events,labels):

    if type(labels) != type(np.array([])):
        labels = np.array([l for l in labels])

    centroids = {}
    variances = {}
    n         = {}

    for cluster in np.sort(np.unique(labels)):
        clusterInds = np.where(labels==cluster)[0]
        centroids[str(int(cluster))] = events[clusterInds,:].mean(axis=0)
        variances[str(int(cluster))] = events[clusterInds,:].var(axis=0)
        n[str(int(cluster))] = len(np.where(labels==cluster)[0])

    return centroids,variances,n 
