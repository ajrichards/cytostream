#!/usr/bin/env python

import os,sys,time,unittest,getopt,re
import matplotlib
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from cytostream.tools import calculate_intercluster_score,PieChartCreator,DotPlotCreator
from cytostream.stats import FileAlignerII
from cytostream import NoGuiAnalysis,SaveSubplots
from SimulatedData1 import case1, case2, case3, case4, case5, case6
from SimulatedData1 import case1Labels, case2Labels, case3Labels, case4Labels, case5Labels, case6Labels

## check for verbose flag
VERBOSE=False
optlist, args = getopt.getopt(sys.argv[1:], 'v')
for o, a in optlist:
    if o == '-v':
        VERBOSE = True


colors = ['r','g','b','c','orange','k','m']
cases = [case1, case2, case3, case4,case5, case6]
caseLabels = [case1Labels, case2Labels, case3Labels, case4Labels,case5Labels, case6Labels]


fig = Figure()
canvas = FigureCanvas(fig)
ax1 = fig.add_subplot(221)
clrs = [colors[l] for l in case1Labels]
x1,y1 = (case1[:,0],case1[:,1])
ax1.scatter(x1,y1, c=clrs, edgecolor='none')

x2,y2 = (case1[:,0] + 6.0,case1[:,1] + 10.0)
ax2 = fig.add_subplot(222)
ax2.scatter(x2,y2, c=clrs, edgecolor='none')

x3,y3 = x1-np.median(x1), y1-np.median(y1)
ax3 = fig.add_subplot(223)
ax3.scatter(x3,y3, c=clrs, edgecolor='none')

x4,y4 = x2-np.median(x2), y2-np.median(y2)
ax3 = fig.add_subplot(224)
ax3.scatter(x4,y4, c=clrs, edgecolor='none')


canvas.print_figure('toy1')
os.system("eog toy1.png")



#fig.show()


### Run the tests 
#if __name__ == '__main__':
#    unittest.main()
