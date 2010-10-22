import os,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
from cytostream.tools import FileAligner,make_plots_as_subplots

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
#expListLabels = [np.array(labs)+1 for labs in expListLabels]
beforeStats = fa.get_sample_statistics(expListLabels)
afterStats = fa.get_sample_statistics(fa.newLabelsAll)

print len(expListNames)
print len(fa.expListNames)
print len(expListLabels)
print len(fa.newLabelsAll)

make_plots_as_subplots(expListNames,expListData,expListLabels,centroids=beforeStats['mus'],showCentroids=True,figTitle='Before File Alignment',
                       saveas="TestCasesBefore.png",refFile=fa.refFile,subplotRows=2,subplotCols=3)

make_plots_as_subplots(fa.expListNames,fa.expListData,fa.newLabelsAll,centroids=afterStats['mus'],showCentroids=True,figTitle='After File Alignment',
                       saveas="TestCasesAfter.png", refFile=fa.refFile,subplotRows=2,subplotCols=4)
#fa.show_plots()

newLabelsLists = fa.newLabelsAll

#########################################################################
# calculate intercluster distances
#########################################################################

from cytostream.tools import calculate_intercluster_score
from cytostream.tools import PieChartCreator

interClusterDistance = calculate_intercluster_score(expListNames,expListData,fa.newLabelsAll)
print interClusterDistance

pcc = PieChartCreator(fa.newLabelsAll,expListNames+["copied ref file"],saveas="piefigs.png")
import matplotlib.pyplot as plt
plt.show()
