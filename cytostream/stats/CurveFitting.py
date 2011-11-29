import numpy as np
from scipy import interpolate, linalg


def spline_1d(x,y,numKnots=4,splineOrder=3,removeRepeats=False):
    '''
    find a 1d spline
    '''

    if type(x) != type(np.array([])):
        print "ERROR find_spline_1d - bad x input"
        return None
    if type(y) != type(np.array([])):
        print "ERROR find_spline_1d - bad y input"
        return None
    if len(x) <= 8:
        print "ERROR find_spline_1d - not enought points"
        return None
    if numKnots < 1:
        print "ERROR find_spline_1d - Invalid number of knots"
        return None

    if removeRepeats == True:
        _x = np.unique(x.copy())
        _y = []
        for i in _x:
            _y.append(np.median(y[np.where(x==i)[0]]))
        y = np.array(_y) 
        x = _x

    ## get the knots
    knots = np.linspace(x.min(),x.max(),numKnots+2)[1:-1]
    
    ## spline range
    xs = np.arange(x.min(),x.max(),1.0/500)

    ## Find the B-spline representation of 1-D curve.
    tck = interpolate.splrep(x,y,s=0.0,k=splineOrder,t=knots,task=-1)

    ## Evaluate a B-spline or its derivatives 
    ys = interpolate.splev(xs,tck,der=0)

    return xs,ys
