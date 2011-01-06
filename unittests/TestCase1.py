#!/usr/bin/env python                                                                                                                                                                                                                       
import sys,os,unittest,time,re
from cytostream import NoGuiAnalysis, configDictDefault

'''
configDict - arg is not required although custom analyses are carried out using a custom dict as shown

notes:
    to retrieve file names and events from a given file see the method 'testFiles'

A. Richards
'''                                                                                                                                                                                      
class TestCase1(unittest.TestCase):
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        ## run the no gui analysis
        filePathList = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        projectID = 'utest'
        
        self.nga = NoGuiAnalysis(projectID,filePathList)

    def tests(self):
        self.assertTrue(os.path.isfile(os.path.join(self.nga.controller.homeDir,"%s.log"%self.nga.controller.projectID)))
        self.failIf(len(os.listdir(os.path.join(self.nga.controller.homeDir,"data"))) < 2)
        
        ## get file names 
        fileNameList = self.nga.get_file_names()
        self.assertEqual(len(fileNameList),1)
        
        events = self.nga.get_events(fileNameList[0],subsample=self.nga.controller.log.log['subsample_qa'])
        self.assertEqual(events.shape[0], int(float(self.nga.controller.log.log['subsample_qa']))) 

### Run the tests 
if __name__ == '__main__':
    unittest.main()


'''
#!/usr/bin/env python

import sys,os,unittest,re

#if sys.platform == 'darwin':
#    import matplotlib
#    matplotlib.use('Agg')

from cytostream import Controller

## test class for the main window function
class TestCase1(unittest.TestCase):
    
    def setUp(self):
        cwd = os.getcwd()
        if os.path.split(cwd)[1] == 'unittests':
            BASEDIR = os.path.split(cwd)[0]
        elif os.path.split(cwd)[1] == 'cytostream':
            BASEDIR = cwd
        else:
            print "ERROR: Model test cannot find home dir -- cwd", cwd

        self.projectID = 'utest'
        self.homeDir = os.path.join(BASEDIR,"cytostream","projects",self.projectID)
        self.controller = Controller()
        self.controller.initialize_project("utest")
        self.fcsFileName = os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")

    def testTestCase1(self):
        self.controller.load_files_handler([self.fcsFileName])
        self.failIf(len(os.listdir(os.path.join(self.controller.homeDir,"data"))) != 2)
       
        #self.projectID = 'utest'
        #self.allFiles = [os.path.join(BASEDIR,"cytostream","example_data", "3FITC_4PE_004.fcs")]
        #self.subsample = '1e3'
        #self.controller = Controller()
        #self.controller.initialize_project(self.projectID)

        #firstFile = True
        #goFlag = True
        #for fileName in self.allFiles:
        #    if os.path.isfile(fileName) == False:
        #        print 'ERROR: Bad file name skipping', fileName
        #        continue
        #
        #    fileName = str(fileName)
        #    if firstFile == True:
        #        self.controller.create_new_project(fileName)
        #        firstFile = False
        #    else:
        #        goFlag = self.controller.load_additional_fcs_files(fileName)
        #
        #if self.controller.homeDir == None:
        #    print "ERROR: project failed to initialize"
        #    return
        #else:
        #    print "project created."
        #
        ## handle subsampling 
        #self.controller.log.log['subsample'] = self.subsample
        #self.controller.handle_subsampling()
        #self.controller.save()
        #
        ## create quality assurance images
        #self.controller.process_images('qa')
        # 
        ### run models
        #for fileName in self.allFiles:
        #    self.failIf(os.path.isfile(fileName) == False)
        #    self.controller.log.log['selectedFile'] = os.path.split(fileName)[-1]
        #    print 'running model on', self.controller.log.log['selectedFile']
        #    self.runSelectedModel()
        #
        ### create figures 
        #print 'creating results images'
        #self.controller.process_images('results')

    def verifyModelRun(self,modelName,modelType):
       statModel,statModelClasses = self.controller.model.load_model_results_pickle(modelName,modelType)    
       return statModelClasses

    def runSelectedModel(self):
        # numcomponents
        self.controller.log.log['numComponents'] = 16
        self.controller.log.log['modelToRun'] = 'dpmm'
        self.controller.run_selected_model()
        selectedFile = self.controller.log.log['selectedFile']
        modelName = "%s_sub%s_dpmm"%(re.sub("\.fcs|\.pickle","",selectedFile),int(float(self.subsample)))
        classesComponents = self.verifyModelRun(modelName,'components')
        classesModes = self.verifyModelRun(modelName,'modes')
        self.assertEqual(len(classesComponents),int(float(self.subsample)))
        self.assertEqual(len(classesModes),int(float(self.subsample)))

        # check image creation
        self.controller.process_images('results')
   
'''
