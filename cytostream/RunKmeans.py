#!/usr/bin/python

import sys,getopt,os,re,cPickle,time,csv
import fcmgpu
import fcmgpu.statistics

if len(sys.argv) < 3:
    print sys.argv[0] + " -f fileName -p projName -k numClusters -h homeDir"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:k:n:')
except getopt.GetoptError:
    print sys.argv[0] + "-f fileName -p projName"
    print "Note: fileName (-f) must be the full" 
    print "      homeDir  (-h) home directory for current project"
    print "             k (-k) the desired number of components"
    print " longModelName (-l) the long descriptive model name"
    print "          name (-n) user given name for model run"
    sys.exit()

k = 16
name = None
for o, a in optlist:
    if o == '-f':
        fileName = a
    if o == '-h':
        homeDir = a
    if o == '-k':
        k = a
    if o == '-n':
        name = a

print 'running dpmm with %s'%k

## initial error checking
if os.path.isdir(homeDir) == False:
    print "INPUT ERROR: not a valid project", homeDir
    sys.exit()

longModelName = "Dirichlet Process Mixture Model - GPU Version"
projName = os.path.split(homeDir)[-1]
longFileName = os.path.join(homeDir,"data",fileName)

## more error checking
if os.path.isfile(longFileName) == False:
    print "INPUT ERROR: not a valid file name", longFileName
    sys.exit()

if re.search('\D',str(k)):
    print "INPUT ERROR: k must be numeric"
else:
    k = int(k)

## load the data into py-fcm
if re.search("\.fcs",longFileName):
    data = fcmgpu.loadFCS(longFileName)
elif re.search("\.pickle",longFileName):
    data= cPickle.load(open(longFileName,'r'))
    
mod = fcmgpu.statistics.DPMixtureModel(data,k,last=1)
modelRunStart = time.time()
mod.fit(verbose=True)
modelRunStop = time.time()
full = mod.get_results()

#print dir(modes)
#print modes.modes()

## classify the components
classifyComponents = full.classify(data)
print 'dumping components fit'
if name == None:
    tmp1 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-gpu_components.pickle"),'w')
    tmp2 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-gpu_classify_components.pickle"),'w')
else:
    tmp1 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+name+"_components.pickle"),'w')
    tmp2 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+name+"_classify_components.pickle"),'w')

cPickle.dump(full,tmp1)
cPickle.dump(classifyComponents,tmp2)
tmp1.close()
tmp2.close()

## classify the modes
modes = full.make_modal()
classifyModes = modes.classify(data)
print 'dumping modes fit'
if name == None:
    tmp3 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-gpu_modes.pickle"),'w')
    tmp4 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-gpu_classify_modes.pickle"),'w')
else:
    tmp3 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+name+"_modes.pickle"),'w')
    tmp4 = open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+name+"_classify_modes.pickle"),'w')

cPickle.dump(modes,tmp3)
cPickle.dump(classifyModes,tmp4)
tmp3.close()
tmp4.close()

## write a log file
if name == None:
    writer = csv.writer(open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-gpu.log"),'w'))
else:
    writer = csv.writer(open(os.path.join(homeDir,'models',re.sub("\.fcs|\.pickle","",fileName)+name+".log"),'w'))

runTime = modelRunStop - modelRunStart
writer.writerow(["timestamp", time.asctime()])
writer.writerow(["project id", projName])
writer.writerow(["file name", fileName])
writer.writerow(["full model name", longModelName])
writer.writerow(["model runtime",str(round(runTime,4))])
writer.writerow(["number components",str(k)])
writer.writerow(["number modes",str(len(list(set(classifyModes))))])
