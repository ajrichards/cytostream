import os,sys
import numpy as np
from cytostream.tools import FileAligner
BASEDIR = os.path.dirname(__file__)

from SimulatedData import case1, case2, case3, case4, case5, case6
from SimulatedData import case1Labels, case2Labels, case3Labels, case4Labels, case5Labels, case6Labels

## declare variables 
modelName = 'cdp'
mkPlots = True
showCentroids = True
expListNames = ['case1','case2','case3','case4','case5','case6']
expListData = [case1,case2,case3,case4,case5,case6]
expListLabels = [case1Labels,case2Labels,case3Labels,case4Labels,case5Labels,case6Labels]

## run it
fa = FileAligner(expListNames,expListData,expListLabels,modelName,minPercentOverlap=0.20,minMergeSilValue=0.95,refFile=None)

## make plots
expListLabels = [np.array(labs)+1 for labs in expListLabels]
beforeStats = fa.get_sample_statistics(expListLabels)
fa.makePlotsAsSubplots(expListNames,expListData,expListLabels,centroids=beforeStats['mus'],showCentroids=True,figTitle='Before File Alignment')
afterStats = fa.get_sample_statistics(fa.newLabelsAll)
fa.makePlotsAsSubplots(expListNames,expListData,fa.newLabelsAll,centroids=afterStats['mus'],showCentroids=True,figTitle='After File Alignment')
#fa.show_plots()

newLabelsLists = fa.newLabelsAll

## calculate a score
#labelMasterList = set([])
#for labelList in expListLabels:
#    fileLabels = np.sort(np.unique(labelList))
#    labelMasterList.update(fileLabels)
#
#sortedLabels = np.sort(np.unique(labelMasterList))

#########################################################################
# calculate intercluster distances
#########################################################################

from cytostream.tools import calculate_intercluster_score
from cytostream.tools import PieChartCreator

interClusterDistance = calculate_intercluster_score(expListNames,expListData,fa.newLabelsAll)
print interClusterDistance

pcc = PieChartCreator(fa.newLabelsAll,expListNames)
import matplotlib.pyplot as plt
plt.show()




