from libSVM import *

def get_sl_training_data(nga,childFilterID,parentFilterID,fileNameList,modelRunID='run1'):
    '''
    the parent gate is used to define the non-target centroids or events
    so it does not necessarly have to be the direct parent
    '''

    ## get indices        
    #trainingIndices = nga.get_filter_indices(fileName,'iFilter_%s'%_cd3GateName)  
    #gate = nga.controller.load_gate(filterID)
    #if parentFilterID != 'root':
    #    parentGate = nga.controller.load_gate(parentFilterID)

    print 'loading training data'
    #print '...',gate['name']

    for fileName in fileNameList:
        fileEvents = nga.get_events(fileName)
        fileLabels = nga.get_labels(fileName,modelRunID,modelType='components',subsample='original',getLog=False)
        childIndices = nga.get_filter_indices(fileName,'cFilter_%s'%childFilterID)  
        childClusters = np.unique(fileLabels[childIndices])
        if parentFilterID == 'root':
            parentIndices = np.arange(fileEvents.shape[0])
        else:
            parentIndices = nga.get_filter_indices(fileName,'cFilter_%s'%parentFilterID)
            parentClusters = np.unique(fileLabels[parentClusterIndices])

        print childClusters
        childClusters, chileMeanMat = get_mean_matrix(fileEvents,fileLabels)
        print childClusters
        


    '''
    nga = NoGuiAnalysis(homeDir,loadExisting=True)
    fileList = nga.get_file_names()
    projectData = {}
    for f in fileList:
        projectData[f] = {}
        for s in subsetList:
            projectData[f][s] = {}

    channelDict = get_channel_dict(projectID)
    cd3ChanInd = channelDict['cd3']
    if projectID in ['101a','101b','101c']:
        sscChanInd = channelDict['ssch']
        fscChanInd = channelDict['fsch']
    else:
        sscChanInd = channelDict['ssca']
        fscChanInd = channelDict['fsca']
    cd4ChanInd = channelDict['cd4']
    cd8ChanInd = channelDict['cd8']
    cytoChanInd = channelDict['ifng+il2']

    for fileName in fileList:
        print '\tadding...', fileName
        fileEvents = nga.get_events(fileName)
        fileInd = fileList.index(fileName)
        fileModel,fileLabels = nga.get_model_results(fileName,'run1','components')
        uniqueClusters, meanMat = get_mean_matrix(fileEvents,fileLabels)
        cd3aGate,cd3bGate,cd4Gate,cd8Gate = extract_gates_by_xml(projectID)

        ## get cd3 clusters
        clustersCD3a = get_clusters_from_gate(fileEvents[:,[fscChanInd,sscChanInd]],fileLabels,cd3aGate)
        clustersCD3b = get_clusters_from_gate(fileEvents[:,[cd3ChanInd,sscChanInd]],fileLabels,cd3bGate)
        _clustersCD3 = list(set(clustersCD3a).intersection(set(clustersCD3b)))
        clustersCD3 = []
        for cid in _clustersCD3:
            if cid in uniqueClusters:
                clustersCD3.append(cid)
        clustersNotCD3 = list(set(uniqueClusters).difference(set(clustersCD3)))

        ## get cd4 clusters
        clustersCD4a = get_clusters_from_gate(fileEvents[:,[cd4ChanInd,cd8ChanInd]],fileLabels,cd4Gate)
        clustersCD4 = list(set(clustersCD4a).intersection(set(clustersCD3)))
        _clustersCD4 = []
        clustersNotCD4 = list(set(clustersCD3).difference(set(clustersCD4)))

        ## get cd8 clusters
        clustersCD8a = get_clusters_from_gate(fileEvents[:,[cd4ChanInd,cd8ChanInd]],fileLabels,cd8Gate)
        clustersCD8 = list(set(clustersCD8a).intersection(set(clustersCD3)))
        _clustersCD8 = []
        clustersNotCD8 = list(set(clustersCD3).difference(set(clustersCD8)))

        ## save all
        clusterIndsCD3 = []
        clusterIndsNotCD3 = []
        clusterIndsCD4 = []
        clusterIndsNotCD4 = []
        clusterIndsCD8 = []
        clusterIndsNotCD8 = []

        for i in clustersCD3:
            clusterIndsCD3.append(np.where(uniqueClusters==i)[0][0])
        for i in clustersNotCD3:
            clusterIndsNotCD3.append(np.where(uniqueClusters==i)[0][0])

        for i in clustersCD4:
            clusterIndsCD4.append(np.where(uniqueClusters==i)[0][0])
        for i in clustersNotCD4:
            clusterIndsNotCD4.append(np.where(uniqueClusters==i)[0][0])

        for i in clustersCD8:
            clusterIndsCD8.append(np.where(uniqueClusters==i)[0][0])
        for i in clustersNotCD8:
            clusterIndsNotCD8.append(np.where(uniqueClusters==i)[0][0])

        projectData[fileName]['CD3'] = {"X1":meanMat[clusterIndsCD3,:],
                                        "y1":np.array([1.]).repeat(len(clusterIndsCD3)),
                                        "X2":meanMat[clusterIndsNotCD3,:],
                                        "y2":np.array([-1.]).repeat(len(clusterIndsNotCD3))}
        projectData[fileName]['CD4'] = {"X1":meanMat[clusterIndsCD4,:],
                                        "y1":np.array([1.]).repeat(len(clusterIndsCD4)),
                                        "X2":meanMat[clusterIndsNotCD4,:],
                                        "y2":np.array([-1.]).repeat(len(clusterIndsNotCD4))}
        projectData[fileName]['CD8'] = {"X1":meanMat[clusterIndsCD8,:],
                                        "y1":np.array([1.]).repeat(len(clusterIndsCD8)),
                                        "X2":meanMat[clusterIndsNotCD8,:],
                                        "y2":np.array([-1.]).repeat(len(clusterIndsNotCD8))}
    
    cPickle.dump(projectData,tmp1)
    tmp1.close()
    '''
