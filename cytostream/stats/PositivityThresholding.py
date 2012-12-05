import os, sys, re
import numpy as np
import matplotlib as mpl
from fcm.graphics import bilinear_interpolate
from fcm.core.transforms import _logicle as logicle

def calculate_fscores(neg_pdf,pos_pdf,beta=1.0,theta=2.0):
    '''
    The f-score is calculated as (precision*recall)/((beta^2*precision)+recall). 
    The TP, FP an FN are estimated from the overlayed probability density functions (pdf) from 
    the positive and negative event distributions.
    '''
    n = len(neg_pdf)
    fpos = np.where(pos_pdf > theta*neg_pdf, pos_pdf-neg_pdf, 0)
    tp = np.array([np.sum(fpos[i:]) for i in range(n)])
    fn = np.array([np.sum(fpos[:i]) for i in range(n)])
    fp = np.array([np.sum(neg_pdf[i:]) for i in range(n)])
    precision = tp/(tp+fp)
    precision[tp==0]=0
    recall = tp/(tp+fn)
    recall[recall==0]=0
    fscores = (1+beta*beta)*(precision*recall)/(beta*beta*precision + recall)
    fscores[np.where(np.isnan(fscores)==True)[0]]=0

    return fscores,precision,recall

def get_positivity_threshold(neg,pos,channelIndex,beta=1.0,theta=2.0,fullOutput=True):
    '''
    In order to calculate the f-score the pdfs are found using histogram representations of the 
    data. The number of bins numBins controls how smoothly the pdf fits the actual distribution 
    of events.
    '''

    def move_mean(x, window):
        xs = np.cumsum(x)
        x1 = xs[(window-1):]
        x2 = np.concatenate([[0], xs[:-window]])
        return np.concatenate([[np.nan]*(window-1), (x1-x2)/float(window)])

    neg,pos = neg[:,channelIndex].copy(),pos[:,channelIndex].copy()
    numBins = int(np.sqrt(np.max([neg.shape[0],pos.shape[0]])))
    
    allEvents = np.hstack((neg,pos))

    pdfNeg, bins = np.histogram(neg, bins=numBins, normed=True)
    pdfPos, bins = np.histogram(pos, bins=bins, normed=True)

    width = 10
    pdfNeg = move_mean(pdfNeg, window=width)
    pdfPos = move_mean(pdfPos, window=width)

    xs = (bins[:-1]+bins[1:])/2.0
    fscores,precision,recall = calculate_fscores(pdfNeg,pdfPos,beta=beta,theta=theta)
    fThreshold = xs[np.argmax(fscores)]

    if fullOutput == True:
        return {'threshold':fThreshold, 'fscores':fscores, 'pdfx': xs,
                'pdfpos':pdfPos, 'pdfneg':pdfNeg,
                'precision':precision,'recall':recall,
                'bins': bins}
    else:
        return fThreshold

    return {'threshold':fThreshold, 'fscores':fscores,'pdfx':xs,'pdfpos':pdfPos,'pdfneg':pdfNeg,
            'precision':precision,'recall':recall}

def get_positive_events(fileNames,cytoIndex,fThreshold,eventsList):
    '''
    INPUT:
        fileNames   -- a list of file names
        cytoIndex   -- is the numeric index of the cytokine
        fThreshold  -- the threshold value
        eventsList  -- a list of np.arrays of events (all dims)
    
    OUTPUT:
        returns the percentages and indices of positive events
    '''
    
    ## error check
    if len(eventsList) != len(fileNames):
        print "ERROR: get_positive events dimension mismatch", len(eventsList),len(fileNames)
        return None, None

    ## declare variables
    percentages = {}
    idx = {}
    filterInds = np.array([])

    ## determine and save percentages, counts and indices
    for fileInd,events in enumerate(eventsList):
        fileName = fileNames[fileInd]
        data = events[:,cytoIndex]
        positiveEventInds = np.where(data > fThreshold)[0]

        if events.shape[0] == 0 or len(positiveEventInds) == 0:
            percentages[fileName] = 0.0
        else:
            percentages[fileName] = (float(positiveEventInds.size)/float(events.shape[0])) * 100.0
        idx[fileName] = positiveEventInds

    return percentages, idx
