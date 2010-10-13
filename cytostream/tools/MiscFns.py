import numpy as np


def calculate_intercluster_score(expListNames,expListData,expListLabels):
    '''
    calculate a global file alignment score

    '''
    
    masterLabelList = get_master_label_list(expListLabels)

    ## get a dict of magnitudes
    magnitudeDict = {}
    for cluster in masterLabelList:
        magnitude = 0
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


def get_master_label_list(expListLabels):

    labelMasterList = set([])
    for labelList in expListLabels:
        fileLabels = np.sort(np.unique(labelList))
        labelMasterList.update(fileLabels)

    masterLabelList = np.sort(np.unique(labelMasterList))

    return masterLabelList
