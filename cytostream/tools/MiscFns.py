import sys,os,re,csv
import numpy as np

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
