#!/usr/bin/python
'''
This function allows cytostream to break up large jobs by file 
over an arbitrary number of GPUs.

'''

import getopt,sys,os,re,subprocess,time,csv
import numpy as np
import matplotlib as mpl

## important line to fix popup error in mac osx
if mpl.get_backend() != 'agg':
    mpl.use('agg')

try:
    optlist, args = getopt.getopt(sys.argv[1:],'h:f:g:b:')
except getopt.GetoptError:
    print getopt.GetoptError

try:
    from config_cs import CONFIGCS
    pythonPath = CONFIGCS['python_path']
except:
    pythonPath = None

homeDir = None
run = True
gpuDevice = 0
for o, a in optlist:
    if o == '-h':
        homeDir = a
    if o == '-f':
        fileListStr = a
    if o == '-b':
        baseDir = a
    if o == '-g':
        gpuDevice = int(a)

## python path
if pythonPath != None:
    if os.path.exists(pythonPath) == False:
        print "ERROR: bad specified python path in config.py... using default"
        pythonPath = os.path.join(os.path.sep,"usr","bin","python")
    else:
        pythonPath = pythonPath
elif sys.platform == 'win32':
    pythonPath = os.path.join("C:\Python27\python")
elif sys.platform == 'darwin':
    pythonPath = os.path.join("/","usr","local","bin","python")
else:
    pythonPath = os.path.join(os.path.sep,"usr","bin","python")

## transform file list
selectedModel = 'dpmm'
fileList = fileListStr.split(",")
fileCount = 0
percentagesReported = []
totalIters = 1100

def sanitize_check(script):
    if re.search(">|<|\*|\||^\$|;|#|\@|\&",script):
        return False
    else:
        return True
                
for fileName in fileList:
    fileCount += 1

    if fileCount == 1:
        print 'queue_%s_%s'%(gpuDevice,0.001)

    ## create log file to write output too
    writer = csv.writer(open(os.path.join(homeDir,'models',fileName+"_%s_gpu.log"%gpuDevice),'wa'))
    percentsToPrint = range(100)
    alreadyReported = []
    percentDone = 0.0

    if selectedModel == 'dpmm':
        script = os.path.join(baseDir,"RunDPMM.py")
        if os.path.isfile(script) == False:
            print "ERROR: Invalid model run file path ", script 
        cmd = "%s %s -h %s -g %s -f %s"%(pythonPath,script,homeDir,gpuDevice,fileName) 
        isClean = sanitize_check(cmd)
        if isClean == False:
            print "ERROR: An unclean file name or another argument was passed to QueueGPU --- exiting process"
            sys.exit()
            
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
        
        ## wait until job is finished
        output = proc.communicate()

        '''
        THIS DOES NOT WORK AND BREAKS THINGS
        while not proc.poll():
            #try:
            next_line = proc.stdout.readline()
            if re.search("it =",next_line):
                #print "...", next_line
                progress = 1.0 / totalIters
                percentDone+=progress * 100.0
                if int(percentDone) in percentsToPrint and int(percentDone) not in alreadyReported: 
                    writer.writerow([int(percentDone)])    
                    alreadyReported.append(int(percentDone))

                #if next_line == '' and proc.poll() != None:
                #    break

            #except:
            #    break
        '''
    else:
        print "ERROR: invalid selected model", selectedModel

    percentComplete = float(fileCount)/float(len(fileList))
    print 'QueueGPU: has finished task %s out of %s for GPU:%s'%(fileCount,len(fileList),gpuDevice)