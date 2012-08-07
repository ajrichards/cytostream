from libSVM import *
import matplotlib.pyplot as plt
from scikits.learn import svm


import numpy as np
import pylab as pl

from sklearn.svm import SVC
from sklearn.preprocessing import Scaler
from sklearn.datasets import load_iris
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
from matplotlib.nxutils import points_inside_poly

'''
def _run_svm(X_train,y_train,X_test,y_test):
    clf = SVM(kernel=gaussian_kernel,C=4.0)
    clf.fit(X_train, y_train)
    y_predict = clf.predict(X_test)
    correct = np.sum(y_predict == y_test)
    print "%d out of %d predictions correct" % (correct, len(y_predict))
    return clf,y_predict
'''

def gaussian_kernel(x, y):
    print x.shape,y.shape
    sigma = 2.0
    eDist = np.linalg.norm(x-y)
    return np.exp(-eDist**2 / (2 *(sigma**2)))

#def gaussian_kernel(x, y, sigma=5.0):
#    return np.exp(-linalg.norm(x-y)**2 / (2 * (sigma ** 2)))

#def kernel_gaussian(x,y):
#    print 'shape',np.exp(-np.sum((x-y)**2) / 20.0)
#    return np.exp(-np.sum((x-y)**2) / 20.0)

def my_kernel(x, y):
    """
    We create a custom kernel:

                 (2  0)
    k(x, y) = x  (    ) y.T
                 (0  1)
    """
    M = np.array([[2, 0], [0, 1.0]])
    print 'return',np.dot(np.dot(x, M), y.T).shape
    return np.dot(np.dot(x, M), y.T)

def train_svm(X1,y1,X2,y2,C=1.0,gamma=0.7):
    X_train = np.vstack((X1, X2))
    y_train = np.hstack((y1, y2))
    #svc = svm.SVC(kernel='poly',degree=3,C=1.0)
    svc = svm.SVC(kernel='rbf',gamma=gamma,C=C) #gamma=10.0
    #svc = svm.SVC(kernel=my_kernel) #gamma=10.0
    #svc = svm.SVC(kernel=gaussian_kernel) #gamma=10.0
    svc.fit(X_train, y_train)
   
    return svc

def run_svm(svc,X1,y1,X2,y2):
    X_test = np.vstack((X1, X2))
    y_test = np.hstack((y1, y2))
    y_predict = svc.predict(X_test)
    #for i in range(len(y_test)):
    #    print y_test[i], y_predict[i]

    #print "SVM: %d out of %d predictions correct" % (correct, len(y_predict))
    tp,fp,tn,fn = evaluate_predictions(y_test,y_predict)
    print "\t...tp",len(tp)
    print "\t...tn",len(tn)
    print "\t...fp",len(fp)
    print "\t...fn",len(fn)

def run_svm_validation(X1,y1,X2,y2,gammaRange=[0.5],cRange=[0.005],useLinear=False):
    X_train,y_train,X_test,y_test = split_train_test(X1,y1,X2,y2)


    if useLinear == True:
        svc = svm.LinearSVC()
        svc.fit(X_train, y_train)

        y_predict = svc.predict(X_test)
        
        tp,fp,tn,fn = evaluate_predictions(y_test,y_predict)
        if len(tp) == 0 and len(fp) == 0:
            precision = 0.0
        else:
            precision = float(len(tp))/(float(len(tp))+float(len(fp)))
        if len(tp) == 0 and len(fn) == 0:
            recall = 0.0
        else:
            recall = float(len(tp))/(float(len(tp))+float(len(fn)))

        return (precision,recall)

    cRange = [0.001,0.01,0.1,1.0,10.0]
    gammaList = [0.0001,0.001,0.01,0.1,1.0,10.0]
    bestResults = None

    for C in cRange:
        for gamma in gammaList:

            svc = svm.SVC(kernel='rbf',gamma=gamma,C=C)
            svc.fit(X_train, y_train)
            y_predict = svc.predict(X_test)        
            tp,fp,tn,fn = evaluate_predictions(y_test,y_predict)
            #print "\t...tp",len(tp)
            #print "\t...tn",len(tn)
            #print "\t...fp",len(fp)
            #print "\t...fn",len(fn)
            if len(tp) == 0 and len(fp) == 0:
                precision = 0.0
            else:
                precision = float(len(tp))/(float(len(tp))+float(len(fp)))
            if len(tp) == 0 and len(fn) == 0:
                recall = 0.0
            else:
                recall = float(len(tp))/(float(len(tp))+float(len(fn)))
            #print "\t...precision", precision
            #print "\t...recall", recall

            if bestResults == None:
                bestResults = (gamma,C,precision,recall)
                continue

            if bestResults[2] + bestResults[3] < precision + recall:
                bestResults = (gamma,C,precision,recall)

    return bestResults

def get_sl_data(nga,childFilterIDList,parentFilterIDList,fileNameList,modelRunID='run1',subsample=None,useMeans=True,useIndices=False):
    '''
    the parent gate is used to define the non-target centroids or events
    so it does not necessarly have to be the direct parent
    '''

    ## error check
    if len(childFilterIDList) != len(parentFilterIDList):
        print "ERROR in get_sl_data -- dims must match"

    ## declare variables
    toReturnX1 = None
    toReturnX2 = None
    toReturnY1 = None
    toReturnY2 = None

    for filterIndex in range(len(childFilterIDList)):
        childFilterID = childFilterIDList[filterIndex]
        parentFilterID = parentFilterIDList[filterIndex]
        fileName = fileNameList[filterIndex]

        ## get indices 
        gate = nga.controller.load_gate(childFilterID)
        channel1 = gate['channel1']
        channel2 = gate['channel2']
        includedChannels = [channel1,channel2]
    
        trainingData = {}
        
        #for fileName in fileNameList:
        fileEvents = nga.get_events(fileName)
        fileLabels = nga.get_labels(fileName,modelRunID,modelType='components',subsample='original',getLog=False)
        if useIndices == False:
            childIndices = nga.get_filter_indices(fileName,'cFilter_%s'%childFilterID)  
        else:
            childIndices = nga.get_filter_indices(fileName,'iFilter_%s'%childFilterID)  
        if parentFilterID == 'root':
            parentIndices = np.arange(fileEvents.shape[0])
        else:
            if useIndices == False:
                parentIndices = nga.get_filter_indices(fileName,'cFilter_%s'%parentFilterID)
            else:
                parentIndices = nga.get_filter_indices(fileName,'iFilter_%s'%parentFilterID)

        nonChildIndices1 = list(set(parentIndices).difference(set(childIndices)))

        ## double check that points are not inside the gate
        allData = [(d[0], d[1]) for d in fileEvents[:,includedChannels]]
        indicesInGate = np.nonzero(points_inside_poly(allData, gate['verts']))[0]
        nonChildIndices2 = list(set(parentIndices).difference(set(indicesInGate)))
        nonChildIndices = np.array(list(set(nonChildIndices1).intersection(set(nonChildIndices2))))

        #print 'check', nonChildIndices.shape, nonChildIndices2.shape

        if subsample == None:
            pass
        elif parentIndices.shape[0] > subsample and childIndices.shape[0] > subsample:
            randIndices =  np.random.randint(0,childIndices.shape[0],subsample)
            childIndices = childIndices[randIndices]
            randIndices =  np.random.randint(0,nonChildIndices.shape[0],subsample)
            nonChildIndices = nonChildIndices[randIndices]
      
        X1 = fileEvents[childIndices,:].copy()
        X1 = X1[:,includedChannels].copy()
        X2 = fileEvents[nonChildIndices,:].copy()
        X2 = X2[:,includedChannels].copy()

        ## scale the data
        #scaler  = Scaler()
        #X1 = scaler.fit_transform(X1)
        #X2 = scaler.fit_transform(X2)

        if useMeans == True:
            uLabelsX1,X1 = get_mean_matrix(X1,fileLabels[childIndices])
            uLabelsX2,X2 = get_mean_matrix(X2,fileLabels[nonChildIndices])

        ## convert to standard normal
        #print X1.shape,X2.shape
        #X1 = (X1 - X1.mean(axis=0)) / X1.std(axis=0)
        #X2 = (X2 - X2.mean(axis=0)) / X2.std(axis=0)
        #X1 = (X1 - X1.mean(axis=0)) / X1.std(axis=0)
        #X2 = (X2 - X2.mean(axis=0)) / X2.std(axis=0)

        y1 = np.array([1.]).repeat(X1.shape[0])
        y2 = np.array([0.]).repeat(X2.shape[0])

        if toReturnX1 == None:
            toReturnX1 = X1
        else:
            toReturnX1 = np.vstack((toReturnX1,X1))
        if toReturnX2 == None:
            toReturnX2 = X2
        else:
            toReturnX2 = np.vstack((toReturnX2,X2))
        if toReturnY1 == None:
            toReturnY1 = y1
        else:
            toReturnY1 = np.hstack((toReturnY1,y1))
        if toReturnY2 == None:
            toReturnY2 = y2
        else:
            toReturnY2 = np.hstack((toReturnY2,y2))

    ## transform the data
    X = np.vstack((toReturnX1, toReturnX2))
    y = np.hstack((toReturnY1, toReturnY2))
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    toReturnX1 = X[np.where(y==1)[0]].copy()
    toReturnX2 = X[np.where(y==0)[0]].copy()
    
    trainingData =  {"X1":toReturnX1,
                     "y1":toReturnY1,
                     "X2":toReturnX2,
                     "y2":toReturnY2}    

    return trainingData

def make_basic_sl_plot(ax,data,gate,fileName,nga):
    buff = 0.2
    X1 = data['X1']
    X2 = data['X2']
    y1 = data['y1']
    y2 = data['y2']
    X = np.vstack((X1, X2))
    Y = np.hstack((y1, y2))

    ax.scatter(X1[:,0], X1[:,1],c='#FF6600',s=5,edgecolor='none',alpha=0.7) 
    ax.scatter(X2[:,0], X2[:,1],c='#0066FF',s=5,edgecolor='none',alpha=0.7)
    
    #ax.set_xlabel(channelNames[gate['channel1']])
    #x.set_ylabel(channelNames[gate['channel2']])
    #pl.xlim(xx.min(), xx.max()) 
    #pl.ylim(yy.min(), yy.max())
    ax.set_xticks(())
    ax.set_yticks(())

    #shortChannels = self.nga.get('short_channel_labels')
    channel1Ind = gate['channel1']
    channel2Ind = gate['channel2']
    channel1Name, channel2Name = None,None
    for chanName, chanIndx in nga.channelDict.iteritems():
        if int(channel1Ind) == int(chanIndx):
            channel1Name = chanName
        if int(channel2Ind) == int(chanIndx):
            channel2Name = chanName

    ax.set_xlabel(channel1Name)
    ax.set_ylabel(channel2Name)
    
    scatterList = ['FSC','FSCA','FSCW','FSCH','SSC','SSCA','SSCW','SSCH']

    bufferX = buff * (X[:,0].max() - X[:,0].min())
    ax.set_xlim([X[:,0].min()-bufferX,X[:,0].max()+bufferX])

    bufferY = buff * (X[:,1].max() - X[:,1].min())
    ax.set_ylim([X[:,1].min()-bufferY,X[:,1].max()+bufferY])

    ax.set_aspect(1./ax.get_data_ratio())

    
def svm_optimize_parameters(X1,y1,X2,y2,figPath1,figPath2):

    ##############################################################################
    # Load and prepare data set
    #
    # dataset for grid search
    iris = load_iris()
    X = iris.data
    Y = iris.target

    X = np.vstack((X1, X2))
    Y = np.hstack((y1, y2))

    print 'X',X.shape
    print 'Y',Y.shape
    print Y

    # dataset for decision function visualization
    X_2d = X[:, :2]
    X_2d = X_2d[Y > 0]
    Y_2d = Y[Y > 0]
    Y_2d -= 1

    # It is usually a good idea to scale the data for SVM training.
    # We are cheating a bit in this example in scaling all of the data,
    # instead of fitting the transformation on the training set and
    # just applying it on the test set.

    scaler = Scaler()

    X = scaler.fit_transform(X)
    X_2d = scaler.fit_transform(X_2d)

    ##############################################################################
    # Train classifier
    #
    # For an initial search, a logarithmic grid with basis
    # 10 is often helpful. Using a basis of 2, a finer
    # tuning can be achieved but at a much higher cost.
    
    C_range = 10.0 ** np.arange(-2, 9)
    gamma_range = 10.0 ** np.arange(-5, 4)
    param_grid = dict(gamma=gamma_range, C=C_range)

    grid = GridSearchCV(SVC(), param_grid=param_grid, cv=StratifiedKFold(y=Y, k=3))
    grid.fit(X, Y)

    print("The best classifier is: ", grid.best_estimator_)
 
    # Now we need to fit a classifier for all parameters in the 2d version
    # (we use a smaller set of parameters here because it takes a while to train)
    C_2d_range = [1, 1e2, 1e4]
    gamma_2d_range = [1e-1, 1, 1e1]
    classifiers = []
    for C in C_2d_range:
        for gamma in gamma_2d_range:
            clf = SVC(C=C, gamma=gamma)
            clf.fit(X_2d, Y_2d)
            classifiers.append((C, gamma, clf))

    ##############################################################################
    # visualization
    #
    # draw visualization of parameter effects
    pl.figure(figsize=(8, 6))
    xx, yy = np.meshgrid(np.linspace(-5, 5, 200), np.linspace(-5, 5, 200))
    for (k, (C, gamma, clf)) in enumerate(classifiers):
        # evaluate decision function in a grid
        Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        # visualize decision function for these parameters
        pl.subplot(len(C_2d_range), len(gamma_2d_range), k + 1)
        pl.title("gamma 10^%d, C 10^%d" % (np.log10(gamma), np.log10(C)),
                 size='medium')

        # visualize parameter's effect on decision function
        pl.pcolormesh(xx, yy, -Z, cmap=pl.cm.jet)
        pl.scatter(X_2d[:, 0], X_2d[:, 1], c=Y_2d, cmap=pl.cm.jet)
        pl.xticks(())
        pl.yticks(())
        pl.axis('tight')

    pl.savefig(figPath1)

    # plot the scores of the grid
    # grid_scores_ contains parameter settings and scores
    score_dict = grid.grid_scores_

    # We extract just the scores
    scores = [x[1] for x in score_dict]
    scores = np.array(scores).reshape(len(C_range), len(gamma_range))

    # draw heatmap of accuracy as a function of gamma and C
    pl.figure(figsize=(8, 6))
    pl.subplots_adjust(left=0.05, right=0.95, bottom=0.15, top=0.95)
    pl.imshow(scores, interpolation='nearest', cmap=pl.cm.spectral)
    pl.xlabel('gamma')
    pl.ylabel('C')
    pl.colorbar()
    pl.xticks(np.arange(len(gamma_range)), gamma_range, rotation=45)
    pl.yticks(np.arange(len(C_range)), C_range)

    pl.savefig(figPath2)
