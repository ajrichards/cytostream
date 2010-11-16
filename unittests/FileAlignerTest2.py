import os,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
from cytostream.tools import FileAligner,make_plots_as_subplots,calculate_intercluster_score,PieChartCreator

BASEDIR = os.path.dirname(__file__)
from SimulatedData2 import case1, case2, case3
from SimulatedData2 import case1Labels, case2Labels, case3Labels

## declare variables 
modelName = 'cdp'
mkPlots = True
showCentroids = True
expListNames = ['case1','case2','case3']
expListData = [case1,case2,case3]
expListLabels = [case1Labels,case2Labels,case3Labels]
phiRange = [0.2,0.6,0.8] 

## ensure directories are present
if os.path.isdir(os.path.join(".","figures")) == False:
    os.mkdir(os.path.join(".","figures"))
for phi in phiRange:
    if os.path.isdir(os.path.join(".","figures",str(phi))) == False:
        os.mkdir(os.path.join(".","figures",str(phi)))
if os.path.isdir(os.path.join(".","figures",'unaligned')) == False:
    os.mkdir(os.path.join(".","figures",'unaligned'))
if os.path.isdir(os.path.join(".","figures",'pies')) == False:
    os.mkdir(os.path.join(".","figures",'pies'))

## run it
fa = FileAligner(expListNames,expListData,expListLabels,modelName,phiRange=phiRange,refFile=None,excludedChannels=[],verbose=True)

print 'alignment complete.'
print 'creating figures'

## make plots
beforeStats = fa.get_sample_statistics(expListLabels)
beforeFig = os.path.join(".","figures","unaligned","DoubleAlignmentsBefore.png")
make_plots_as_subplots(expListNames,expListData,expListLabels,centroids=beforeStats['mus'],showCentroids=True,
                       figTitle='Before File Alignment',saveas=beforeFig,refFile=fa.refFile,subplotRows=1,subplotCols=3,asData=True)
for phi in phiRange:
    afterStats = fa.get_sample_statistics(fa.newLabelsAll[str(round(phi,4))])
    interClusterDistance = calculate_intercluster_score(expListNames,expListData,fa.newLabelsAll[str(round(phi,4))])
    pieChartSave = os.path.join(".","figures","pies","piefigs_%s.png"%(phi))
    pcc = PieChartCreator(fa.newLabelsAll[str(round(phi,4))],expListNames,saveas=pieChartSave,subplotRows=1,subplotCols=3)
    print phi, interClusterDistance
    afterFig = os.path.join(".","figures",str(phi),"DoubleAlignmentsAfter.png")
    make_plots_as_subplots(fa.expListNames,fa.expListData,fa.newLabelsAll[str(round(phi,4))],centroids=afterStats['mus'],showCentroids=True,
                           figTitle='After File Alignment',saveas=afterFig,refFile=fa.refFile,subplotRows=1,subplotCols=3,asData=True)