#!/usr/bin/python
'''
file indices begin with 0
cluster indices are forced to begin with 1

'''

import os, sys,cPickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons
from scipy.spatial.distance import pdist,cdist,squareform
import scipy.stats as stats

class FileAligner():

    def __init__(self,expListNames,expListData,expListLabels,modelName,minPercentOverlap=0.15,minMergeSilValue=0.95, mkPlots=True,refFile=None,verbose=False):
        self.expListNames = expListNames
        self.expListData = expListData
        self.expListLabels = expListLabels
        self.modelName = modelName
        self.mkPlots = mkPlots
        self.minPercentOverlap = minPercentOverlap
        self.minMergeSilValue = minMergeSilValue
        self.verbose = True

        ## figure variables
        self.markerSize = 5
        self.colors = ['b','g','r','c','m','y','k','orange','#AAAAAA','#FF6600',
                       '#FFCC00','#FFFFAA','#6622AA','#33FF77','#998800','#0000FF','#FA58AC', '#8A0808','#D8D8D8']
        ## preprocessing of data
        if self.verbose == True:
            print "transforming data and getting sample statistics"
        self.get_silhouette_values(self.expListData[0], self.expListLabels[0])
        self.transform_labels()
        self.sampleStats = self.get_sample_statistics(self.expListLabels)

        ## determine reference file
        if self.verbose == True:
            print "Determining referene file"
        if refFile != None and self.expListNames.__contains__(refFile) == False:
            print "INPUT ERROR: invalid reference file name"
        elif refFile != None and self.expListNames.__contains__(refFile) == True:
            if self.verbose == True:
                print "INFO: using input reference file name"
            self.refFile = refFile
        else:
            if self.verbose == True:
                print "INFO: using generated reference file name"
            self.refFile = self.get_reference_file()

        ### ici
        ##print 'refFile..', self.refFile
        #print self.sampleStats['silvalues'].keys()
        #print 'shape', np.shape(self.sampleStats['silvalues']['case1'])
        #
        #sys.exit()

        ## align files
        self.perform_file_alignment(self.refFile)

    def get_silhouette_values(self,mat,labels):
        
        ## make sure labels are ints
        labels = np.array([int(l) for l in labels])

        values = pdist(mat,'sqeuclidean')
        dMat = squareform(values)
        silValList = []
        n,d = np.shape(dMat)
        
        withinDist = np.zeros((n,1),)
        minBetweenDist = np.zeros((n,1),)
        silVals = np.zeros((n,1),)
        uniqueLabs = np.sort(np.unique(labels))

        for i in range(len(uniqueLabs)):
            k = uniqueLabs[i]
            notK =  np.array(list(set(labels[np.where(labels!=k)[0]])))
            kInds = np.where(labels==k)[0]
            withinDist[i] = dMat[i,kInds].mean()
            minBetweenDist[i] = np.array([dMat[i,np.where(labels==j)[0]].mean() for j in notK]).min()
        
        ## adjust for zero division
        minBetweenDist = minBetweenDist + 1e-08
        silVals = (minBetweenDist - withinDist) / np.hstack([[minBetweenDist,withinDist]]).max(axis=0)
        
        return silVals


    def transform_labels(self):
        ## ensure that labels begin at 1 and not 0
        newExpListLabels = []
        for labels in self.expListLabels:
            #if labels.__contains__(0) == True:
            labels = 1 + np.array(labels)
            newExpListLabels.append(labels.tolist())
            #else:
            #    newExpListLabels.append(labels)
        self.expListLabels = newExpListLabels

    def get_sample_statistics(self,expListLabels):

        centroids, variances, silValues, numClusts, numDataPoints = {},{},{},{},{}
        for expName in self.expListNames:
            centroids[expName] = {}
            variances[expName] = {}
            silValues[expName] = None
            numClusts[expName] = None
            numDataPoints[expName] = {}

        for c in range(len(self.expListNames)):
            expName = self.expListNames[c]
            expData = self.expListData[c]
            expLabels = expListLabels[c]

            for cluster in np.sort(np.unique(expLabels)):
                centroids[expName][cluster] = np.array([expData[:,0][np.where(expLabels==cluster)[0]].mean(),np.array(expData[:,1][np.where(expLabels==cluster)[0]]).mean()])
                variances[expName][cluster] = np.array([expData[:,0][np.where(expLabels==cluster)[0]].var(),np.array(expData[:,1][np.where(expLabels==cluster)[0]]).var()])
                numDataPoints[expName][cluster] = len(np.where(expLabels==cluster)[0])

            numClusts[expName] = len(np.unique(expLabels))
            silValues[expName] = self.get_silhouette_values(expData,expLabels)
        return {'mus':centroids,'sigmas':variances,'silvalues':silValues,'k':numClusts,'n':numDataPoints}

    def get_reference_file(self):
        '''
        get a reference data file or patient
        '''

        modeClusters = int(stats.mode(np.array(self.sampleStats['k'].values()))[0][0])
        medianClusters = np.median(np.array(self.sampleStats['k'].values()))
        minNumClusters = np.min(np.array(self.sampleStats['k'].values()))
        maxNumClusters = np.max(np.array(self.sampleStats['k'].values()))
        
        ## choose a cluster with the median for the number of clusters 
        refFile = None
        minScore = 100
        for c in range(len(self.expListNames)):
            expName = self.expListNames[c]
            k = self.sampleStats['k'][expName]
            if k <= medianClusters:
                score = medianClusters - k
            if k > medianClusters:
                score = k - medianClusters

            if score < minScore:
                minScore = score
                refFile = expName
        
        return refFile

    def perform_file_alignment(self,refFile):
        '''
        compare all pairwise clusters
        
        '''
        matchResults = None
        criticalVals = {}
        for expName in self.expListNames:
            criticalVals[expName] = {}
        
        for pIndex1 in range(len(self.expListNames)):
            for pIndex2 in range(len(self.expListNames)):
                if pIndex2 >= pIndex1:
                    continue

                patient1 = self.expListNames[pIndex1]
                patient2 = self.expListNames[pIndex2]
                dataPatient1 = self.expListData[pIndex1]
                dataPatient2 = self.expListData[pIndex2]
                labelsPatient1 = self.expListLabels[pIndex1]
                labelsPatient2 = self.expListLabels[pIndex2]

                for cluster1 in np.sort(np.unique(labelsPatient1)):
                    for cluster2 in np.sort(np.unique(labelsPatient2)):
            
                        ## take events in the clusters and find their euclidean distance from their centers
                        eventsPatient1 = dataPatient1[np.where(labelsPatient1==cluster1)[0]]
                        eventsPatient2 = dataPatient2[np.where(labelsPatient2==cluster2)[0]]

                        euclidDist1 = (eventsPatient1 - eventsPatient1.mean(axis=0))**2.0
                        euclidDist1 = np.sqrt(euclidDist1.sum(axis=1))

                        euclidDist2 = (eventsPatient2 - eventsPatient2.mean(axis=0))**2.0
                        euclidDist2 = np.sqrt(euclidDist2.sum(axis=1))

                        ## determine the number of events that overlap
                        overlap1 = (eventsPatient1 - eventsPatient2.mean(axis=0))**2.0
                        overlap1 = np.sqrt(overlap1.sum(axis=1))

                        overlap2 = (eventsPatient2 - eventsPatient1.mean(axis=0))**2.0
                        overlap2 = np.sqrt(overlap2.sum(axis=1))
                
                        threshold1 = stats.norm.ppf(0.975,loc=euclidDist1.mean(),scale=euclidDist1.std())
                        threshold2 = stats.norm.ppf(0.975,loc=euclidDist2.mean(),scale=euclidDist2.std())

                        if criticalVals[patient1].has_key(cluster1) == False:
                            criticalVals[patient1][cluster1] = threshold1
                        if criticalVals[patient2].has_key(cluster2) == False:
                            criticalVals[patient2][cluster2] = threshold2

                        overlappingInds1 = np.where(overlap1<threshold2)[0]
                        overlappingInds2 = np.where(overlap1<threshold1)[0]
                        percentOverlap1 = float(len(overlappingInds1)) / float(len(eventsPatient1))
                        percentOverlap2 = float(len(overlappingInds2)) / float(len(eventsPatient2))
                        percentOverlap = np.max([percentOverlap1, percentOverlap2])

                        ## save the results
                        #print pIndex1, pIndex2, cluster1,cluster2, percentOverlap

                        results = np.array(([pIndex1, pIndex2, cluster1,cluster2, percentOverlap]))

                        if matchResults == None:
                            matchResults = results
                        else:
                            matchResults = np.vstack((matchResults, results))

        ## go through the results and keep only the results that have values >0
        numRows, numCols = np.shape(matchResults)
        filteredResults = None
        totalNumClusters = 0
        matchDict = {}
        uniqueClusters = []
        for compareNum in range(numRows):
            results = matchResults[compareNum]
            if results[4] > 0:

                if filteredResults == None:
                    filteredResults = results
                else:
                    filteredResults = np.vstack((filteredResults,results))

        ## create variables for newLabels
        self.newLabelsAll = []                                                                                     
        for labInd in range(len(self.expListLabels)):
            labels = self.expListLabels[labInd]
            self.newLabelsAll.append(-1.0 * np.array(labels).copy())

        ## make reference file comparisons
        print refFile
        refFileInd = self.expListNames.index(refFile)
        refFileLabels = self.expListLabels[refFileInd]
        refFileData = self.expListData[refFileInd]
        refLabels = np.sort(np.unique(refFileLabels))
        self._make_reference_comparisons(refFile,filteredResults)
        
        ## make a collection of clusters without matches to ref file
        frows, fcols = np.shape(filteredResults)
        #for rowNum in range(frows):
        #    results = filteredResults[rowNum,:]
        #    print results
        #print np.shape(filteredResults)

        clustersYetToLabel = []
        for altInd in range(len(self.newLabelsAll)):
            if int(altInd) == int(refFileInd):
                continue
            labels = self.newLabelsAll[altInd] 
            uniqueLabels = np.sort(np.unique(labels))
            negClusters = uniqueLabels[np.where(uniqueLabels < 0)[0]]
            for negInd in negClusters:
                clustersYetToLabel.append((altInd,negInd))

        ## label clusters that do not match a label
        clustersLeft = [clust for clust in clustersYetToLabel]
        nextLabel =  np.max(refFileLabels) + 1

        ## check for remaining matching clusters
        for negCluster in clustersYetToLabel:
            fileInd = negCluster[0]
            clusterInd = negCluster[1]

            bestMatchList = []
            for rowNum in range(frows):
                results = filteredResults[rowNum,:]
                if results[0] == fileInd and int(results[2]) == int(-1 * clusterInd):
                    bestMatch = (results[1],results[3],results[4])
                    bestMatchList.append(bestMatch)
                elif results[1] == fileInd and int(results[3]) == int(-1 * clusterInd):
                    bestMatch = (results[0],results[2],results[4])
                    bestMatchList.append(bestMatch)

            if len(bestMatchList) > 0:
                if clustersLeft.__contains__((fileInd,clusterInd)) == True:
                    indicesToChange = np.where((self.newLabelsAll[fileInd]) == clusterInd)[0]
                    self.newLabelsAll[fileInd][indicesToChange] = nextLabel
                    clustersLeft.remove((fileInd,clusterInd))
                 
                for bestMatch in bestMatchList:
                    if clustersLeft.__contains__((bestMatch[0],-1*bestMatch[1])) == True:
                        indicesToChange = np.where((self.newLabelsAll[int(bestMatch[0])]) == -1*bestMatch[1])[0]
                        self.newLabelsAll[int(bestMatch[0])][indicesToChange] = nextLabel
                        clustersLeft.remove((bestMatch[0],-1*bestMatch[1]))                
                
                nextLabel += 1
        
        for negCluster in clustersLeft:
            fileInd = negCluster[0]
            clusterInd = negCluster[1]
            indicesToChange = np.where((self.newLabelsAll[fileInd]) == clusterInd)[0]
            self.newLabelsAll[fileInd][indicesToChange] = nextLabel
            nextLabel += 1

        ## change back to positive the ref labels and ensure labels are ints
        self.newLabelsAll[refFileInd] = -1 * self.newLabelsAll[refFileInd]
        self.newLabelsAll = [[int(l) for l in labels] for labels in self.newLabelsAll]

        ## normalize labels starting at 1
        allLabels = []
        for labels in self.newLabelsAll:
            allLabels+=labels
        uniqueLabels = np.sort(np.unique(allLabels)).tolist()
        normalizedLabels = range(1,len(uniqueLabels)+1)
    

        if len(uniqueLabels) != len(normalizedLabels):
            print "ERROR: normalization could not complete"

        self.newLabelsAll = [np.array(newLabels) for newLabels in self.newLabelsAll]
        for fileInd in range(len(self.expListNames)):
            expName = self.expListNames[fileInd]
            for clusterInd in np.sort(np.unique(self.newLabelsAll[fileInd])):
                newLabel = normalizedLabels[uniqueLabels.index(clusterInd)]
                indicesToChange = np.where((self.newLabelsAll[fileInd]) == clusterInd)[0]
                self.newLabelsAll[fileInd][indicesToChange] = newLabel
        self.newLabelsAll = [newLabels.tolist() for newLabels in self.newLabelsAll]
        
    def _make_reference_comparisons(self,refFile,filteredResults):
        ## given a reference cluster figure out which clusters match
        refFileInd = self.expListNames.index(refFile)
        refFileLabels = self.expListLabels[refFileInd]
        refFileData = self.expListData[refFileInd]
        refLabels = np.sort(np.unique(refFileLabels))
        frows, fcols = np.shape(filteredResults)
        clusterCompares = {}

        for rowNum in range(frows):
            results = filteredResults[rowNum,:]
            if results[0] != refFileInd and results[1] != refFileInd:
                continue
            
            if results[0] == refFileInd:
                refCluster = results[2]
                altCluster = results[3]
                altFile = results[1]
                
            elif results[1] == refFileInd:
                refCluster = results[3]
                altCluster = results[2]
                altFile = results[0]

            if clusterCompares.has_key(refCluster) == False:
                clusterCompares[refCluster] = {'values': [results[4]],'file-cluster':[(int(altFile),int(altCluster))]}
            else:
                clusterCompares[refCluster]['values'].append(results[4])
                clusterCompares[refCluster]['file-cluster'].append((int(altFile),int(altCluster)))

        ## make decisions about merging for reference comparisons
        for key, item in clusterCompares.iteritems():
            key = int(key)

            count = -1
            for fileCluster in item['file-cluster']:
                count += 1
                altFile = fileCluster[0]
                altFileName =  self.expListNames[altFile]
                altCluster = -1 * fileCluster[1]
                
                percentOverlap = item['values'][count]

                ## make index changes based on minimum perscribed percent overlap
                if percentOverlap < self.minPercentOverlap:
                    if self.verbose == True:
                        print '\t\tnot merging percent overlap < threshold'
                    continue

                if self.verbose == True:
                    print '\t changing %s to %s in file %s'%(altCluster,key,altFile)

                indicesToChange = np.where((self.newLabelsAll[altFile]) == altCluster)[0]
                
                ## before merging a cluster ensure the clusters silhouette value is > the minimum threshold
                clusterSilValue = self.sampleStats['silvalues'][altFileName][indicesToChange].mean()
                if clusterSilValue < self.minMergeSilValue:
                    if self.verbose == True:
                        print '\t\tnot merging - cluster sil value < sil value threshold'
                    continue

                self.newLabelsAll[altFile][indicesToChange] = key

    def makePlotsAsSubplots(self,expListNames,expListData,expListLabels,centroids=None,showCentroids=True,figTitle=None):
        fig = plt.figure(figsize=(6.5,9))
        subplotCount = 0
        for c in range(len(expListNames)):
            expData = expListData[c]
            labels = expListLabels[c]
            expName = expListNames[c]
            subplotCount += 1
            ax = fig.add_subplot(3,2,subplotCount)
        
            totalPoints = 0
            for l in np.sort(np.unique(labels)):
                try:
                    hexColor = self.colors[l]
                except:
                    print 'WARNING not enough colors in self.colors looking for ', l
                    hexColor = 'black'

                x = expData[:,0][np.where(labels==l)[0]]
                y = expData[:,1][np.where(labels==l)[0]]

                if x.size == 0:
                    continue
                ax.scatter(x,y,color=hexColor,s=self.markerSize)

                totalPoints+=x.size

                ## handle centroids if present 
                prefix = ''
                if centroids != None and showCentroids == True:
                    xPos = centroids[expName][l][0]
                    yPos = centroids[expName][l][1]
            
                    if hexColor in ['#FFFFAA','y','#33FF77']:
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=8.0,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=hexColor,alpha=0.8)
                                )
                    else:
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=8.0,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=hexColor,alpha=0.8)
                                )

            ## error check that all point were plotted
            if totalPoints != expData[:,0].size:
                print "ERROR: the correct number of point were not plotted %s/%s"%(totalPoints,expData[:,0].size)

            ax.set_title("Experiment %s"%subplotCount)
            ax.set_xlim([0,14])
            ax.set_ylim([0,14])
        
        if figTitle != None:
            fig.suptitle(figTitle, fontsize=12)

        plt.subplots_adjust(wspace=0.3, hspace=0.3)


    def makePlotsSameAxis(self,expListNames,expListData,expListLabels,colors,centroids,showCentroids=True):
        fig = plt.figure(figsize=(7,7))
        ax = fig.add_subplot(111)
        plotCount = -1
        plotMarkers = ["o","+","^","s"]
        plotDict = {}

        for c in range(len(expListNames)):
            plotCount += 1
            expData = expListData[c]
            labels = expListLabels[c]
            expName = expListNames[c]

            if plotCount == 0:
                visible = True
            else:
                visible = False

            x = expData[:,0]
            y = expData[:,1]

            plotDict[plotCount] = ax.scatter(x,y,color=colors[plotCount],s=self.markerSize,visible=visible)
            #ax.set_title("Case %s"%subplotCount)
            ax.set_xlim([0,14])
            ax.set_ylim([0,14])

        rax = plt.axes([0.15, 0.12, 0.15, 0.15])
        check = CheckButtons(rax, ('Case1', 'Case2', 'Case3','Case4'), (True, False, False, False))

        def func(label):
            if label == 'Case1': plotDict[0].set_visible(not plotDict[0].get_visible())
            elif label == 'Case2': plotDict[1].set_visible(not plotDict[1].get_visible())
            elif label == 'Case3': plotDict[2].set_visible(not plotDict[2].get_visible())
            elif label == 'Case4': plotDict[3].set_visible(not plotDict[3].get_visible())
            plt.draw()
        check.on_clicked(func)


    def show_plots(self):
        plt.show()
