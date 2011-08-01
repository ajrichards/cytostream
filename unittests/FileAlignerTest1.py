#!/usr/bin/env python

import os,sys,time,unittest,getopt,re
import matplotlib
import numpy as np
if matplotlib.get_backend() != 'Agg':
    matplotlib.use('Agg')
from cytostream.tools import PieChartCreator,DotPlotCreator
from cytostream.stats import FileAligner,TemplateFileCreator,get_saved_template
from cytostream import NoGuiAnalysis,SaveSubplots
from SimulatedData1 import case1, case2, case3, case4, case5, case6
from SimulatedData1 import case1Labels, case2Labels, case3Labels, case4Labels, case5Labels, case6Labels

## debugging the low num events
case1 = np.vstack([case1,np.array([15,6])])
case1Labels = np.hstack([case1Labels,np.array([99])])

## check for verbose flag
VERBOSE=False
optlist, args = getopt.getopt(sys.argv[1:], 'v')
for o, a in optlist:
    if o == '-v':
        VERBOSE = True

class FileAlignerTest1(unittest.TestCase):
    '''
    test class for 6 different simulated cases

    '''

    _initialized = False

    def setUp(self):
        if self._initialized == False:
            self._initialize()

    def _initialize(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## run the no gui analysis
        self.__class__.expListData = [case1,case2,case3,case4,case5,case6]
        channelList = ['channel1','channel2']
        projectID = 'falign1'
        self.__class__.homeDir =  os.path.join(BASEDIR,"cytostream","projects", projectID)
        self.__class__.phiRange = [0.1,0.6,0.9]
        self.useDPMM = False
        
        ## setup class to run model
        self.__class__.nga = NoGuiAnalysis(self.homeDir,self.expListData,useSubsample=True,makeQaFigs=False,record=False,dType='array',
                                           inputChannels=channelList)
        self.nga.set("subsample_analysis", "original")
        self.nga.set("thumbnail_results_default","components")
        self.__class__.expListNames = self.nga.get_file_names()

        if self.useDPMM == True:    
            self.expListLabels = []
            self.nga.run_model()
            
            for fileName in ['array1', 'array2', 'array3','array4','array5','array6']:
                statModel, statModelClasses = self.nga.get_model_results(fileName,'run1','components')
                self.expListLabels.append(statModelClasses)
        else:
            self.expListLabels = [case1Labels,case2Labels,case3Labels,case4Labels,case5Labels,case6Labels]
        
        self.__class__.expListLabels = self.expListLabels

        ## make the non-aligned figures
        self._make_nonaligned_figures()
        self._create_template_file()

        ## toggle the redo flag 
        self.__class__._initialized = True

    def _make_nonaligned_figures(self):
        ## save the plots 
        print 'making original figures without labels...'
        self.nga.set("subsample_analysis", "original")
        plotsToViewChannels = [(0,1) for i in range(16)]
        self.nga.set("plots_to_view_channels",plotsToViewChannels)
        plotsToViewFiles = range(16)
        self.nga.set("plots_to_view_files",plotsToViewFiles)
        
        figsDir = os.path.join(self.homeDir,'figs')
        self.__class__.numSubplots = 6
        figName = os.path.join(figsDir,'subplots_orig_qa.png')
        figTitle = "unittest fa1 - unaligned qa"
        ss = SaveSubplots(self.homeDir,figName,self.numSubplots,figMode='qa',figTitle=figTitle,forceScale=True,drawState='heat')

        print 'making original figures with labels...'
        figName = os.path.join(figsDir,'subplots_orig_dpmm.png')
        if self.useDPMM == True:
            figTitle = "unittest fa1 - unaligned dpmm"
        else:
            figTitle = "Clustered labels"
        plotsToViewRuns = self.nga.controller.log.log['plots_to_view_runs']
        if self.useDPMM == False:
            ss = SaveSubplots(self.homeDir,figName,self.numSubplots,figMode='analysis',figTitle=figTitle,forceScale=True,inputLabels=self.expListLabels)
        else:
            ss = SaveSubplots(self.homeDir,figName,self.numSubplots,figMode='analysis',figTitle=figTitle,forceScale=True)

    def _create_template_file(self):
        tfc = TemplateFileCreator(self.expListData,self.expListLabels,savePath=os.path.join(self.homeDir,"results"))
        figName = os.path.join(self.homeDir,'figs','templates.png')
        tfc.draw_templates(saveas=figName)
        #templateFile = (tfc.templateMat, tfc.bestModeLabels[0])
        templateData,templateComponents,templateModes = get_saved_template(self.homeDir)        
        self.__class__.templateFile = (templateData,templateModes[0])

    def test_by_rank(self):
        evaluator = 'rank'
        figsDir = os.path.join(self.homeDir,'results')

        print "Running file alignment..........%s"%evaluator
        fa = FileAligner(self.templateFile,self.expListNames,self.expListLabels,self.expListData,self.phiRange,verbose=VERBOSE,homeDir=self.homeDir,
                              alignmentDir=evaluator)
        fa.run(evaluator=evaluator)
            
        for phi in self.phiRange:
            alignLabels = fa.alignLabels[str(phi)]
            figName = os.path.join(figsDir,'aligned_%s_%s.png'%(phi,evaluator))
            figTitle = "Aligned Modes %s"%phi
            ss = SaveSubplots(self.homeDir,figName,self.numSubplots,figMode='analysis',figTitle=figTitle,forceScale=True,inputLabels=alignLabels)

        ## tests
        self.failIf(len(fa.noiseClusters['array1']) != 1) 
        self.failIf(len(fa.noiseClusters['array6']) != 1) 
        bestPhi, bestScore = fa.get_best_match()
        self.assertEqual(bestPhi,0.1)
    
    
    def test_by_kld(self):
        evaluator = 'kldivergence'
        figsDir = os.path.join(self.homeDir,'results')

        print "Running file alignment..........%s"%evaluator
        fa = FileAligner(self.templateFile,self.expListNames,self.expListLabels,self.expListData,self.phiRange,verbose=VERBOSE,homeDir=self.homeDir,
                              alignmentDir=evaluator)
        fa.run(evaluator=evaluator)
        
        ## make figurs
        for phi in self.phiRange:
            alignLabels = fa.alignLabels[str(phi)]
            figName = os.path.join(figsDir,'aligned_%s_%s.png'%(phi,evaluator))
            figTitle = "Aligned Modes %s"%phi
            ss = SaveSubplots(self.homeDir,figName,self.numSubplots,figMode='analysis',figTitle=figTitle,forceScale=True,inputLabels=alignLabels)

        ## tests
        self.failIf(len(fa.noiseClusters['array1']) != 1) 
        self.failIf(len(fa.noiseClusters['array6']) != 1) 
        bestPhi, bestScore = fa.get_best_match()
        self.assertEqual(bestPhi,0.1)

    def test_by_mixpdf(self):
        ## run file alignment
        evaluator = 'mixpdf'
        figsDir = os.path.join(self.homeDir,'results')

        print "Running file alignment..........%s"%evaluator
        fa = FileAligner(self.templateFile,self.expListNames,self.expListLabels,self.expListData,self.phiRange,verbose=VERBOSE,homeDir=self.homeDir,
                              alignmentDir=evaluator)
        fa.run(evaluator=evaluator)
        
        ## make figurs
        for phi in self.phiRange:
            alignLabels = fa.alignLabels[str(phi)]
            figName = os.path.join(figsDir,'aligned_%s_%s.png'%(phi,evaluator))
            figTitle = "Aligned Modes %s"%phi
            ss = SaveSubplots(self.homeDir,figName,self.numSubplots,figMode='analysis',figTitle=figTitle,forceScale=True,inputLabels=alignLabels)

        ### test that we picked up the noise cluster
        self.failIf(len(fa.noiseClusters['array1']) != 1) 
        self.failIf(len(fa.noiseClusters['array6']) != 1) 
        bestPhi, bestScore = fa.get_best_match()
        self.assertEqual(bestPhi,0.1)

### Run the tests
if __name__ == '__main__':
    unittest.main()
