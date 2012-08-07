import sys
import numpy as np
from numpy import linalg
import pylab as pl
import cvxopt
import cvxopt.solvers
from sklearn.preprocessing import Scaler

def linear_kernel(x1, x2):
    return np.dot(x1, x2)

def polynomial_kernel(x, y, p=3):
    return (1 + np.dot(x, y)) ** p

def gaussian_kernel(x, y, sigma=2.0):
    #print x.shape,y.shape
    eDist = np.linalg.norm(x-y)
    return np.exp(-eDist**2 / (2 *(sigma**2)))

#def gaussian_kernel(x, y, sigma=5.0):
#    return np.exp(-linalg.norm(x-y)**2 / (2 * (sigma ** 2)))


#def ggaussian_kernel(x, y,sigma=5.0):
#    return np.exp(-(1.0/sigma) * np.power((x - y), 2) )

def gen_lin_separable_data():
    # generate training data in the 2-d case
    mean1 = np.array([0, 2])
    mean2 = np.array([2, 0])
    cov = np.array([[0.8, 0.6], [0.6, 0.8]])
    X1 = np.random.multivariate_normal(mean1, cov, 100)
    y1 = np.ones(len(X1))
    X2 = np.random.multivariate_normal(mean2, cov, 100)
    y2 = np.ones(len(X2)) * -1
    return X1, y1, X2, y2

def gen_non_lin_separable_data():
    mean1 = [-1, 2]
    mean2 = [1, -1]
    mean3 = [4, -4]
    mean4 = [-4, 4]
    cov = [[1.0,0.8], [0.8, 1.0]]
    X1 = np.random.multivariate_normal(mean1, cov, 50)
    X1 = np.vstack((X1, np.random.multivariate_normal(mean3, cov, 50)))
    y1 = np.ones(len(X1))
    X2 = np.random.multivariate_normal(mean2, cov, 50)
    X2 = np.vstack((X2, np.random.multivariate_normal(mean4, cov, 50)))
    y2 = np.ones(len(X2)) * -1
    return X1, y1, X2, y2

def gen_lin_separable_overlap_data():
    # generate training data in the 2-d case
    mean1 = np.array([0, 2])
    mean2 = np.array([2, 0])
    cov = np.array([[1.5, 1.0], [1.0, 1.5]])
    X1 = np.random.multivariate_normal(mean1, cov, 100)
    y1 = np.ones(len(X1))
    X2 = np.random.multivariate_normal(mean2, cov, 100)
    y2 = np.ones(len(X2)) * -1
    return X1, y1, X2, y2

def split_train_test(X1, y1, X2, y2):
    pTrain = 0.8
    pTest = 1.0 - pTrain    
    X1_train = X1[:np.floor(pTrain*X1.shape[0]),:]
    y1_train = y1[:np.floor(pTrain*y1.shape[0])]
    X2_train = X2[:np.floor(pTrain*X2.shape[0]),:]
    y2_train = y2[:np.floor(pTrain*y2.shape[0])]
    X1_test = X1[-np.ceil(X1.shape[0] - pTrain*X1.shape[0]):,:]
    y1_test = y1[-np.ceil(y1.shape[0] -pTrain*y1.shape[0]):]
    X2_test = X2[-np.ceil(X2.shape[0] - pTrain*X2.shape[0]):,:]
    y2_test = y2[-np.ceil(y2.shape[0] - pTrain*y2.shape[0]):]

    X_train = np.vstack((X1_train, X2_train))
    y_train = np.hstack((y1_train, y2_train))
    X_test = np.vstack((X1_test, X2_test))
    y_test = np.hstack((y1_test, y2_test))

    return X_train, y_train, X_test, y_test

def evaluate_predictions(y_test,y_predict):
    #print 'evaluate', y_test.shape, y_predict.shape

    tp,fp,tn,fn = [],[],[],[]
    for i in range(len(y_test)):
        if y_test[i] == 1 and y_predict[i] == 1:
            tp.append(i)
        elif y_test[i] == 1 and y_predict[i] == 0:
            fn.append(i)
        elif y_test[i] == 0 and y_predict[i] == 1:
            fp.append(i)
        elif y_test[i] == 0 and y_predict[i] == 0:
            tn.append(i)
        else:
            print 'evaluate_predictions -- invalid', y_test[i], y_predict[i]


    return tp,fp,tn,fn

def make_contour_panel_test(X1_train, X2_train,y_predict,y_test,X_test,clf, ax,dims=[0,1],xLab=None,yLab=None):
    tp,fp,tn,fn = evaluate_predictions(y_test,y_predict)
           
    ## tp
    if len(tp) > 0:
        p1 = ax.scatter(X_test[tp,dims[0]],X_test[tp,dims[1]],color='r',marker="+",s=20)
    ## tn
    if len(tn) > 0:
        p2 = ax.scatter(X_test[tn,dims[0]],X_test[tn,dims[1]],color='orange',marker="+",s=20)
    ## fp
    if len(fp) > 0:
        p3 = ax.scatter(X_test[fp,dims[0]],X_test[fp,dims[1]],color='blue',marker="+",s=20)
    ## fn
    if len(fn) > 0:
        p4 = ax.scatter(X_test[fn,dims[0]],X_test[fn,dims[1]],color='m',marker="+",s=20)

    ## add lines
    #X1, X2 = np.meshgrid(np.linspace(-6,6,50), np.linspace(-6,6,50))
    #X = np.array([[x1, x2] for x1, x2 in zip(np.ravel(X1), np.ravel(X2))])
    #Z = clf.project(X,dims=dims).reshape(X1.shape)
    #pl.contour(X1, X2, Z, [0.0], colors='k', linewidths=1, origin='lower')
    #pl.contour(X1, X2, Z + 1, [0.0], colors='grey', linewidths=1, origin='lower')
    #pl.contour(X1, X2, Z - 1, [0.0], colors='grey', linewidths=1, origin='lower')
    
    ## scale axes
    #xLims = ax.get_xlim()
    #yLims = ax.get_ylim()
    if yLab != None:
        ax.set_ylabel(yLab,fontsize=10)
    if xLab != None:
        ax.set_xlabel(xLab,fontsize=10)
    xLims = (np.vstack([X1_train,X2_train])[:,dims[0]].min(),np.vstack([X1_train,X2_train])[:,dims[0]].max())
    yLims = (np.vstack([X1_train,X2_train])[:,dims[1]].min(),np.vstack([X1_train,X2_train])[:,dims[1]].max())
    xran = xLims[1] - xLims[0]
    yran = yLims[1] - yLims[0]
    buf= 0.05
    ax.set_xlim(xLims[0]-(xran*buf),xLims[1]+(xran*buf))
    ax.set_ylim(yLims[0]-(yran*buf),yLims[1]+(yran*buf))
    #ax.set_title("tp:%s,fp:%s,tn:%s,fn:%s"%(len(tp),len(fp),len(tn),len(fn)))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect(1./ax.get_data_ratio())

def make_contour_panel_train(X1_train, X2_train,y_predict,y_test,X_test,clf, ax,dims=[0,1],xLab=None,yLab=None):

    alpha = 0.6
    ax.scatter(clf.sv[:,dims[0]], clf.sv[:,dims[1]], s=50, c="g",alpha=alpha)
    ax.scatter(X1_train[:,dims[0]], X1_train[:,dims[1]], color="r",marker="+",alpha=alpha)
    ax.scatter(X2_train[:,dims[0]], X2_train[:,dims[1]], color='k',marker="+",alpha=alpha)
    
    ## mark the support vectors
    ## add lines
    X1, X2 = np.meshgrid(np.linspace(-6,6,50), np.linspace(-6,6,50))
    X = np.array([[x1, x2] for x1, x2 in zip(np.ravel(X1), np.ravel(X2))])
    Z = clf.project(X,dims=dims).reshape(X1.shape)
    pl.contour(X1, X2, Z, [0.0], colors='k', linewidths=1, origin='lower')
    pl.contour(X1, X2, Z + 1, [0.0], colors='grey', linewidths=1, origin='lower')
    pl.contour(X1, X2, Z - 1, [0.0], colors='grey', linewidths=1, origin='lower')
    
    ## scale axes
    if yLab != None:
        ax.set_ylabel(yLab,fontsize=10)
    if xLab != None:
        ax.set_xlabel(xLab,fontsize=10)
    xLims = (np.vstack([X1_train,X2_train])[:,dims[0]].min(),np.vstack([X1_train,X2_train])[:,dims[0]].max())
    yLims = (np.vstack([X1_train,X2_train])[:,dims[1]].min(),np.vstack([X1_train,X2_train])[:,dims[1]].max())
    xran = xLims[1] - xLims[0]
    yran = yLims[1] - yLims[0]
    buf= 0.05
    ax.set_xlim(xLims[0]-(xran*buf),xLims[1]+(xran*buf))
    ax.set_ylim(yLims[0]-(yran*buf),yLims[1]+(yran*buf))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect(1./ax.get_data_ratio())

def plot_margin(X1_train, X2_train, clf):
    def f(x, w, b, c=0):
        # given x, return y such that [x,y] in on the line
        # w.x + b = c
        return (-w[0] * x - b + c) / w[1]

    pl.plot(X1_train[:,0], X1_train[:,1], "ro")
    pl.plot(X2_train[:,0], X2_train[:,1], "bo")
    pl.scatter(clf.sv[:,0], clf.sv[:,1], s=100, c="g")

    # w.x + b = 0
    a0 = -4; a1 = f(a0, clf.w, clf.b)
    b0 = 4; b1 = f(b0, clf.w, clf.b)
    pl.plot([a0,b0], [a1,b1], "k")

    # w.x + b = 1
    a0 = -4; a1 = f(a0, clf.w, clf.b, 1)
    b0 = 4; b1 = f(b0, clf.w, clf.b, 1)
    pl.plot([a0,b0], [a1,b1], "k--")
    
    # w.x + b = -1
    a0 = -4; a1 = f(a0, clf.w, clf.b, -1)
    b0 = 4; b1 = f(b0, clf.w, clf.b, -1)
    pl.plot([a0,b0], [a1,b1], "k--")

    pl.axis("tight")
    pl.show()

def plot_contour(X1_train, X2_train, X1_test, X2_test, clf):
    pl.plot(X1_train[:,0], X1_train[:,1], "ro")
    pl.plot(X2_train[:,0], X2_train[:,1], "bo")
    pl.scatter(clf.sv[:,0], clf.sv[:,1], s=100, c="g")
    
    #X1, X2 = np.meshgrid(np.linspace(-6,6,50), np.linspace(-6,6,50))
    #X = np.array([[x1, x2] for x1, x2 in zip(np.ravel(X1), np.ravel(X2))])
    #Z = clf.project(X).reshape(X1.shape)
    #pl.contour(X1, X2, Z, [0.0], colors='k', linewidths=1, origin='lower')
    #pl.contour(X1, X2, Z + 1, [0.0], colors='grey', linewidths=1, origin='lower')
    #pl.contour(X1, X2, Z - 1, [0.0], colors='grey', linewidths=1, origin='lower')

    pl.axis("tight")
    pl.savefig(os.path.join(".","results","svm_contour.png"))
    #pl.show()

def get_matched_indices(smallMat,largeMat,cp1,cp2,cp3):
    currentIndex = 0
    matchedIndices = np.zeros((smallMat.shape[0]))
    for i in range(smallMat.shape[0]):
        
        ## debug
        #if i > 50:
        #    continue

        row = smallMat[i,:]
        for e in range(currentIndex,largeMat.shape[0]):
            testRow = largeMat[e,:]
            #if round(row[cp1[0]],5)==round(testRow[cp1[1]],5) and round(row[cp2[0]],5)==round(testRow[cp2[1]],5) and round(row[cp3[0]],5)==round(testRow[cp3[1]],5):
            if row[cp1[0]]==testRow[cp1[1]] and row[cp2[0]]==testRow[cp2[1]] and row[cp3[0]]==testRow[cp3[1]]:
                currentIndex = e
                matchedIndices[i] = e
                break
        
            if e == largeMat.shape[0] - 1:
                print "...hit the end"

        if i % 10000 == 0:
            print "%s/%s"%(i,smallMat.shape[0])

    return matchedIndices

## functions 
def get_valid_unique_clusters(events,runLabels):
    uniqueLabels = np.sort(np.unique(runLabels))
    validUniqueLabels = []

    for i,u in enumerate(uniqueLabels):
        if np.where(runLabels==u)[0].size > 5:
            validUniqueLabels.append(u)

    return np.array(validUniqueLabels)

def get_mean_matrix(events,labels):
    meanMat = None
    uniqueLabels = get_valid_unique_clusters(events,labels)
    for clusterIdx in uniqueLabels:
        clusterIndices = np.where(labels == clusterIdx)[0]
        clusterEvents = events[clusterIndices,:]
        if meanMat == None:
            meanMat = np.array([clusterEvents.mean(axis=0)])
        else:
            meanMat = np.vstack([meanMat,clusterEvents.mean(axis=0)])


    #scaler = Scaler()
    #meanMat= scaler.fit_transform(meanMat)
            
    ## convert to standard normal
    #meanMat = (meanMat - meanMat.mean(axis=0)) / meanMat.std(axis=0)

    return uniqueLabels,meanMat


class SVM(object):

    def __init__(self, kernel=linear_kernel, C=None):
        self.kernel = kernel
        self.C = C
        if self.C is not None: self.C = float(self.C)

    def fit(self, X, y):
        n_samples, n_features = X.shape

        # Gram matrix
        K = np.zeros((n_samples, n_samples))
        for i in range(n_samples):
            for j in range(n_samples):
                K[i,j] = self.kernel(X[i], X[j])

        P = cvxopt.matrix(np.outer(y,y) * K)
        q = cvxopt.matrix(np.ones(n_samples) * -1)
        A = cvxopt.matrix(y, (1,n_samples))
        b = cvxopt.matrix(0.0)

        if self.C is None:
            G = cvxopt.matrix(np.diag(np.ones(n_samples) * -1))
            h = cvxopt.matrix(np.zeros(n_samples))
        else:
            tmp1 = np.diag(np.ones(n_samples) * -1)
            tmp2 = np.identity(n_samples)
            G = cvxopt.matrix(np.vstack((tmp1, tmp2)))
            tmp1 = np.zeros(n_samples)
            tmp2 = np.ones(n_samples) * self.C
            h = cvxopt.matrix(np.hstack((tmp1, tmp2)))

        # solve QP problem
        solution = cvxopt.solvers.qp(P, q, G, h, A, b)

        # Lagrange multipliers
        a = np.ravel(solution['x'])

        # Support vectors have non zero lagrange multipliers
        #print 'DEBUG: sv idendification'
        sv = a > 1e-5
        #sv = a > 0.5

        ind = np.arange(len(a))[sv]
        self.a = a[sv]
        self.sv = X[sv]
        self.sv_y = y[sv]
        print "%d support vectors out of %d points" % (len(self.a), n_samples)

        # Intercept
        self.b = 0
        for n in range(len(self.a)):
            self.b += self.sv_y[n]
            self.b -= np.sum(self.a * self.sv_y * K[ind[n],sv])
        self.b /= len(self.a)

        # Weight vector
        if self.kernel == linear_kernel:
            self.w = np.zeros(n_features)
            for n in range(len(self.a)):
                self.w += self.a[n] * self.sv_y[n] * self.sv[n]
        else:
            self.w = None

    def project(self,X,dims=[0,1]):
        dims=[0,1]
        if self.w is not None:
            return np.dot(X, self.w) + self.b
        else:
            y_predict = np.zeros(len(X))
            for i in range(len(X)):
                s = 0
                for a, sv_y, sv in zip(self.a, self.sv_y, self.sv):
                    #s += a * sv_y * self.kernel(X[i], sv)
                    #print "...",X[i].shape,sv.shape,sv_y.shape
                    s += a * sv_y * self.kernel(X[i][dims], sv[dims])
                y_predict[i] = s
            return y_predict + self.b

    def predict(self, X):
        return np.sign(self.project(X))
