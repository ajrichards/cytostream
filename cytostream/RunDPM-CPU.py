#!/usr/bin/python

import sys,getopt,os,re,cPickle,time,csv
import fcm
import fcm.statistics

if len(sys.argv) < 3:
    print sys.argv[0] + " -f fileName -p projName -k numClusters"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:p:k:')
except getopt.GetoptError:
    print sys.argv[0] + "-f fileName -p projName"
    print "Note: fileName (-s) must be the full path"
    print "      projName (-p) can be any existing proj name"
    print "             k (-k) the desired number of components"
    print " longModelName (-l) the long descriptive model name"
    print "          name (-n) user given name for model run"
    sys.exit()

k = 16
name = None
for o, a in optlist:
    if o == '-f':
        fileName = a
    if o == '-p':
        projName = a
    if o == '-k':
        k = a
    if o == '-n':
        name = a

print 'running dpmm with %s'%k

longModelName = "Dirichlet Process Mixture Model - CPU Version"
longProjName = os.path.join(".","projects",projName)
longFileName = os.path.join(longProjName,"data",fileName)

## error checking
if os.path.isdir(longProjName) == False:
    print "INPUT ERROR: not a valid project", os.path.join(".","projects",longProjName)
    sys.exit()

if os.path.isfile(longFileName) == False:
    print "INPUT ERROR: not a valid file name", longFileName
    sys.exit()

if re.search('\D',str(k)):
    print "INPUT ERROR: k must be numeric"
else:
    k = int(k)

## load the data into py-fcm
if re.search("\.fcs",longFileName):
    data = fcm.loadFCS(longFileName)
elif re.search("\.pickle",longFileName):
    data= cPickle.load(open(longFileName,'r'))
    
mod = fcm.statistics.DPMixtureModel(data,k,last=1)
modelRunStart = time.time()
mod.fit(verbose=True)
modelRunStop = time.time()
full = mod.get_results()
#print "..........................................................................................................."
#print 'full', type(full)
classify = full.classify(data)
#print 'classify', type(classify)


print 'dumping fit'
if name == None:
    tmp1 = open(os.path.join(".","projects",projName,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-cpu.pickle"),'w')
    tmp2 = open(os.path.join(".","projects",projName,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-cpu_classify.pickle"),'w')
else:
    tmp1 = open(os.path.join(".","projects",projName,'models',re.sub("\.fcs|\.pickle","",fileName)+name+".pickle"),'w')
    tmp2 = open(os.path.join(".","projects",projName,'models',re.sub("\.fcs|\.pickle","",fileName)+name+"_classify.pickle"),'w')

cPickle.dump(full,tmp1)
cPickle.dump(classify,tmp2)
tmp1.close()
tmp2.close()

## write a log file
if name == None:
    writer = csv.writer(open(os.path.join(".","projects",projName,'models',re.sub("\.fcs|\.pickle","",fileName)+"_dpmm-cpu.log"),'w'))
else:
    writer = csv.writer(open(os.path.join(".","projects",projName,'models',re.sub("\.fcs|\.pickle","",fileName)+name+".log"),'w'))

runTime = modelRunStop - modelRunStart
writer.writerow(["timestamp", time.asctime()])
writer.writerow(["project id", projName])
writer.writerow(["file name", fileName])
writer.writerow(["full model name", longModelName])
writer.writerow(["model runtime",str(round(runTime,4))])
writer.writerow(["number components",str(k)])
