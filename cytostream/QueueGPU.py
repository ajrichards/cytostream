#!/usr/bin/python
'''
This function allows cytostream to break up large jobs by file 
over an arbitrary number of GPUs.

'''

import getopt,sys,os,re
import numpy as np
import matplotlib as mpl

## important line to fix popup error in mac osx
if mpl.get_backend() != 'agg':
    mpl.use('agg')

#from cytostream import SaveSubplots

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
fileList = fileListStr.split(";")
fileCount = 0
for fileName in fileList:
    fileCount += 1
    if selectedModel == 'dpmm':
        script = os.path.join(baseDir,"RunDPMM.py")
        if os.path.isfile(script) == False:
            print "ERROR: Invalid model run file path ", script 
            proc = subprocess.Popen("%s %s -h %s -g %s -f %s -k %s -s %s"%(pythonPath,script,homeDir,gpuDevice
                                                                           fileName,numComponents,subsample), 
                                shell=True,
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        while True:
            try:
                next_line = proc.stdout.readline()
                if next_line == '' and proc.poll() != None:
                    break
                       
                ## to debug uncomment the following 2 lines
                if not re.search("it =",next_line):
                    print next_line
                        
                if re.search("error",next_line,flags=re.IGNORECASE) and view != None:
                    view.display_error("There is a problem with your cuda device(s)\n%s"%next_line)

                if re.search("it =",next_line):
                    progress = 1.0 / totalIters
                    percentDone+=progress * 100.0
                    if progressBar != None:
                        progressBar.move_bar(int(round(percentDone)))
                    else:
                        if int(round(percentDone)) not in percentagesReported:
                            percentagesReported.append(int(round(percentDone)))
                            if int(round(percentDone)) != 100: 
                                print "\r",int(round(percentDone)),"percent complete",
                            else:
                                print "\r",int(round(percentDone)),"percent complete"
            except:
                break
    else:
        print "ERROR: invalid selected model", selectedModel

    ## output progress 
    #if modelMode == 'onefit':
    #    percentDone = float(fileCount) / float(len(fileList)) * 100.0
    #            
    #    if progressBar != None:
    #        progressBar.move_bar(int(round(percentDone)))
    #    else:
    #        if int(round(percentDone)) != 100: 
    #            print "\r",int(round(percentDone)),"percent complete",
    #        else:
    #            print "\r",int(round(percentDone)),"percent complete"


