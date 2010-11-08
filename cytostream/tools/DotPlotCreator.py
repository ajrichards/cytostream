#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from cytostream.tools import get_all_colors
from matplotlib.ticker import MaxNLocator

class DotPlotCreator():
    '''
    the covariates arguemnt assumes that the experiments are listed as below
    covar1, covar1, covar1, ... covar2, covar2, covar2, ...

    '''

    def __init__(self,newLabelLists,expListNames,saveas=None,covariates=None):

        self.newLabelLists = newLabelLists
        self.expListNames = expListNames
        self.saveas = saveas
        self.fontSize = 10
        self.fontName = 'arial'
        self.colors = get_all_colors()
        self.covariates = covariates
        self.masterLabelList = self.get_master_index_list()
        self.create_plot()

    def get_master_index_list(self):
        labelMasterList = set([])
        for labelList in self.newLabelLists:
            fileLabels = np.sort(np.unique(labelList))
            labelMasterList.update(fileLabels)
 
        return np.sort(list(labelMasterList))

    def create_plot(self):

        fig = plt.figure(figsize=(10,8.5))
        ax = fig.add_subplot(111)
        ax.yaxis.grid(True, linestyle='-', which='major', color='grey',
                      alpha=0.8)

        ## figure out which clusters have only 1 match
        matchedIndices = []
        for j in range(len(self.masterLabelList)):
            lab = self.masterLabelList[j]
            numMatchedFiles = 0
            for labels in self.newLabelLists:
                indices = np.where(labels == lab)[0]
                if len(indices) > 0:
                    numMatchedFiles+=1
            if numMatchedFiles > 1:
                matchedIndices.append(j)

        for i in range(len(self.newLabelLists)):
            labels = self.newLabelLists[i]
            totalElements = len(labels)
            colToPlot = [] 
            for lab in self.masterLabelList:
                indices = np.where(labels == lab)[0]
                if len(indices) > 0:
                    colToPlot.append(float(indices.size) / float(totalElements))
                else:
                    colToPlot.append(0)
            
            colToPlot = np.array(colToPlot)[matchedIndices] * 200
            if len(np.where(np.array(colToPlot)==0.0)[0]) <= 1:
                dotColor = '#FF6600'
            else:
                dotColor = '#6600FF'

            usedLabels = self.masterLabelList[matchedIndices]
            ax.scatter(np.array([i+1]).repeat(len(usedLabels)),range(1,len(usedLabels)+1),marker='o',s=colToPlot,alpha=0.7,color=dotColor)

        if self.covariates != None:
            print 'creating line for ', self.covariates
            actualLineBreak = 0
            for group in np.unique(self.covariates):
                lineBreak = len(np.where(np.array(self.covariates) == group)[0]) - 0.5
                actualLineBreak += lineBreak
                if group != np.unique(self.covariates)[-1]:
                    ax.plot(np.array([actualLineBreak+1]).repeat(len(usedLabels)+2),range(0,len(usedLabels)+2),color='k')

        ## format x axis
        ax.set_xlim([0,len(self.newLabelLists) + 1])
        ax.set_xticklabels([" "] + self.expListNames)
        xticklabels = plt.getp(plt.gca(), 'xticklabels')
        plt.setp(xticklabels, fontsize=self.fontSize-1, fontname=self.fontName, rotation=80)
        ax.xaxis.set_major_locator(MaxNLocator(len(self.expListNames)+1))

        ## format y axis
        ax.set_ylim([0,len(usedLabels) + 1])
        ax.set_yticklabels([" "] + usedLabels.tolist())
        yticklabels = plt.getp(plt.gca(), 'yticklabels')
        plt.setp(yticklabels, fontsize=self.fontSize-1, fontname=self.fontName)
        ax.yaxis.set_major_locator(MaxNLocator(len(usedLabels)+1))
        

        
        #ax.yaxis.set_major_locator(MaxNLocator(len(self.newLabelLists)+1))
         #
        #xtickNames = plt.setp(ax, xticklabels=[' ']+self.expListNames)
        #plt.setp(xtickNames, rotation=45, fontsize=8)

        if self.saveas != None:
            fig.savefig(self.saveas)
