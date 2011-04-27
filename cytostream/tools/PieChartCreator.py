#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from cytostream.tools import get_all_colors

class PieChartCreator():

    def __init__(self,newLabelsLists,expListNames,saveas=None,subplotRows=3,subplotCols=4,fontSize=9):

        ## error checking
        if subplotRows * subplotCols < len(expListNames):
            print "ERROR: bad subplot size specified - need %s only %s specified"%(len(expListNames), subplotRows*subplotCols)
            return None

        self.newLabelsLists = newLabelsLists
        self.expListNames = expListNames
        self.saveas = saveas
        self.fontName = 'arial'
        self.fontSize = fontSize
        self.subplotRows = subplotRows
        self.subplotCols = subplotCols
        self.colors = get_all_colors()
        self.masterLabelList = self.get_master_index_list()
        self.allClusterFractions = self.get_cluster_fractions()
        self.create_plot()

    def get_master_index_list(self):
        labelMasterList = set([])
        for labelList in self.newLabelsLists:
            fileLabels = np.sort(np.unique(labelList))
            labelMasterList.update(fileLabels)
 
        return np.sort(list(labelMasterList))

    def get_cluster_fractions(self):
        allClusterFractions = []
        for fileInd in range(len(self.newLabelsLists)):
            labelList = self.newLabelsLists[fileInd]
            clusterFractions = []

            for clusterID in self.masterLabelList:
                eventCount =  np.where(np.array(labelList) == clusterID)[0].size
                clusterFractions.append(eventCount / float(len(labelList)))

            allClusterFractions.append(clusterFractions)

        return allClusterFractions

    def create_plot(self):

        if self.subplotRows > self.subplotCols:
            fig = plt.figure(figsize=(6.5,10))
        elif self.subplotCols > self.subplotRows:
            fig = plt.figure(figsize=(10,6.5))
        else:
            fig = plt.figure(figsize=(9,8))

        subplotCount = 0
        for fileInd in range(len(self.allClusterFractions)):
            subplotCount+=1
            ax = fig.add_subplot(self.subplotRows,self.subplotCols,subplotCount)

            labels = ['%s'%l for l in self.masterLabelList]
            fracs = self.allClusterFractions[fileInd]
            nonZeroInds = np.where(np.array(fracs) != 0.0)[0]
            labels = np.array(labels)[nonZeroInds]
            fracs = np.array(fracs)[nonZeroInds]
            colorList = [self.colors[int(l)] for l in labels]
            explode = [0 for l in labels]
            ax.pie(fracs, explode=explode, labels=None, colors=colorList, shadow=True) #  autopct='%1.1f%%'
            ax.set_title(self.expListNames[fileInd], bbox={'facecolor':'0.8', 'pad':5},fontsize=self.fontSize,fontname=self.fontName)  

        if self.saveas != None:
            fig.savefig(self.saveas)
