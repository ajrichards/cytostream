#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from cytostream.tools import get_all_colors
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Polygon


class BoxPlotByCovariate():
    '''
    the covariates arguemnt assumes that the experiments are listed as below
    covar1, covar1, covar1, ... covar2, covar2, covar2, ...

    '''

    def __init__(self,newLabelLists,expListNames,covariates,saveas=None,subplotRows=3,subplotCols=4,fontSize=10):

        self.newLabelLists = newLabelLists
        self.expListNames = expListNames
        self.saveas = saveas
        self.subplotRows = subplotRows
        self.subplotCols = subplotCols
        self.fontSize = fontSize
        self.fontName = 'arial'
        self.colors = get_all_colors()
        self.covariates = covariates
        self.masterLabelList = self.get_master_index_list()
        self.get_all_percentages()
        self.create_plot()

    def get_master_index_list(self):
        labelMasterList = set([])
        for labelList in self.newLabelLists:
            fileLabels = np.sort(np.unique(labelList))
            labelMasterList.update(fileLabels)
 
        return np.sort(list(labelMasterList))

    def get_all_percentages(self):
        
        allPercentages = {}
        matchedIndices = []
        for j in range(len(self.masterLabelList)):
            lab = self.masterLabelList[j]
            numMatchedFiles = 0
            allPercentages[str(lab)] = np.zeros(len(self.newLabelLists))

        
            for l in range(len(self.newLabelLists)):
                labels = self.newLabelLists[l]
                indices = np.where(labels == lab)[0]
    
                if len(indices) > 0:
                    numMatchedFiles+=1
                    allPercentages[str(lab)][l] = float(indices.size) / float(len(labels))

            if numMatchedFiles > 1:
                matchedIndices.append(j)

        self.matchedIndices = matchedIndices
        self.allPercentages = allPercentages

    def create_plot(self):

        if self.subplotRows > self.subplotCols:
            fig = plt.figure(figsize=(6.5,10))
        elif self.subplotCols > self.subplotRows:
            fig = plt.figure(figsize=(10,6.5))
        else:
            fig = plt.figure(figsize=(9,8))

        subplotCount = 0
        usedLabels = self.masterLabelList[self.matchedIndices]

        ## error check
        if self.subplotRows * self.subplotCols < len(usedLabels):
            print "ERROR: not enough subplots specified -- need at least %s"%len(usedLabels)
            return None


        for lab in usedLabels:
            data = []
            emptyBoxes = []
            subplotCount+=1
            ax = fig.add_subplot(self.subplotRows,self.subplotCols,subplotCount)

            boxCount = -1
            for cov in np.unique(self.covariates):
                boxCount +=1
                covIndices = np.where(np.array(self.covariates) == cov)[0]
                covIndices = [int(c) for c in covIndices]
                covPercentages = self.allPercentages[str(lab)][covIndices]
                nonZeroPercentages = covPercentages[np.where(covPercentages > 0)[0]]
                data.append(nonZeroPercentages) 
                if nonZeroPercentages.size == 0:
                    emptyBoxes.append(boxCount)

            bp =ax.boxplot(data,0)
            plt.setp(bp['boxes'], color='black')
            plt.setp(bp['whiskers'], color='black')
            plt.setp(bp['fliers'], color='red', marker='*')
            
            # Now fill the boxes with desired colors
            boxColors = ['darkkhaki','royalblue']
            numBoxes = 2
            medians = range(numBoxes)
 
            for i in range(numBoxes):
                try:
                    box = bp['boxes'][i]
                except:
                    continue
                boxX = []
                boxY = []
                for j in range(5):
                    boxX.append(box.get_xdata()[j])
                    boxY.append(box.get_ydata()[j])
                boxCoords = zip(boxX,boxY)

                # Alternate between Dark Khaki and Royal Blue
                k = i % 2
                boxPolygon = Polygon(boxCoords, facecolor=boxColors[k])
                ax.add_patch(boxPolygon)
                # Now draw the median lines back over what we just filled in
                med = bp['medians'][i]
                medianX = []
                medianY = []
                for j in range(2):
                    medianX.append(med.get_xdata()[j])
                    medianY.append(med.get_ydata()[j])
                    plt.plot(medianX, medianY, 'k')
                    medians[i] = medianY[0]
    
                ax.plot([np.average(med.get_xdata())], [np.average(data[i])],
                        color='w', marker='*', markeredgecolor='k')
            
            # Set the axes ranges and axes labels
            if len(emptyBoxes) == 0:
                fullBoxes = range(numBoxes)
                topValue = np.array([np.max(np.array(dataSet)) for dataSet in data]).max()
                bottomValue = np.array([np.min(np.array(dataSet)) for dataSet in data]).min()
            else:
                fullBoxes = list(set(range(numBoxes)).difference(set(emptyBoxes)))
                topValue,bottomValue = 0,1

                for boxInd in fullBoxes:
                    _topValue = np.max(np.array(data[boxInd]))
                    _bottomValue = np.min(np.array(data[boxInd]))
                    if _topValue > topValue:
                        topValue = _topValue
                    if _bottomValue < bottomValue:
                        bottomValue = _bottomValue

            if len(fullBoxes) > 0:
                ax.set_xlim(0.5, numBoxes+0.5)            
                top = (0.05 * topValue) + topValue          
                bottom = bottomValue - (0.05 * bottomValue)
                ax.set_ylim(bottom, top)
                pos = np.arange(numBoxes)+1
                upperLabels = [str(np.round(s, 3)) for s in medians]
                weights = ['bold', 'semibold']
                for tick,label in zip(range(numBoxes),ax.get_xticklabels()):
                    k = tick % 2
                    ax.text(pos[tick], top, upperLabels[tick],
                            horizontalalignment='center', fontsize=self.fontSize, weight=weights[k],
                            color=boxColors[k])

            ## handle axes
            ## format axis and title
            #faceColor = self.colors[lab]
            #if faceColor in ['k']:
            #    fontColor = 'white'
            #else:
            #    fontColor = '#333333'
             
            faceColor = 'white'
            fontColor = 'black'
   
            ax.set_xticklabels([])
            ax.xaxis.set_major_locator(MaxNLocator(1))
            ax.yaxis.set_major_locator(MaxNLocator(1))
            ax.set_yticklabels([])
            ax.set_title(lab, bbox={'facecolor':faceColor,'color':fontColor,'pad':5},fontsize=self.fontSize,fontname=self.fontName)
            #yticklabels = plt.getp(plt.gca(), 'yticklabels')
            #plt.setp(yticklabels, fontsize=self.fontSize-2, fontname=self.fontName)
            #ax.yaxis.set_major_locator(MaxNLocator(3))

            fig.subplots_adjust(hspace=0.3,wspace=0.2)

        if self.saveas != None:
            fig.savefig(self.saveas)
