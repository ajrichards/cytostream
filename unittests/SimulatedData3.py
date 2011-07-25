#!/usr/bin/env python


import numpy as np
import matplotlib.pyplot as plt

## variables 
largeN = 1000
smallN = 20
smallVar = 0.14


def get_case_and_labels(rmClusters=[]):

    ## cluster 1
    casec1f1 = np.random.normal(2.5,smallVar,smallN)
    casec1f2 = np.random.normal(5.2,smallVar,smallN)
    casec1 = np.vstack((casec1f1,casec1f2)).T

    ## cluster 2
    casec2f1 = np.random.normal(2,smallVar,smallN)
    casec2f2 = np.random.normal(6,smallVar,smallN)
    casec2 = np.vstack((casec2f1,casec2f2)).T
    case = np.vstack((casec1,casec2))
    caseLabels = np.hstack((np.array([1]).repeat(np.shape(casec1)[0]),np.array([2]).repeat(np.shape(casec2)[0])))

    ## cluster 3
    casec3f1 = np.random.normal(3,smallVar,smallN)
    casec3f2 = np.random.normal(6,smallVar,smallN)
    casec3 = np.vstack((casec3f1,casec3f2)).T
    case = np.vstack((case,casec3))
    caseLabels = np.hstack((caseLabels,np.array([3]).repeat(np.shape(casec3)[0])))

    ## cluster 4
    if 4 not in rmClusters:
        casec4f1 = np.random.normal(5.3,smallVar,smallN)
        casec4f2 = np.random.normal(7.8,smallVar,smallN)
        casec4 = np.vstack((casec4f1,casec4f2)).T
        case = np.vstack((case,casec4))
        caseLabels = np.hstack((caseLabels,np.array([4]).repeat(np.shape(casec4)[0])))

    ## cluster 5
    if 5 not in rmClusters:
        casec5f1 = np.random.normal(3.8,smallVar,smallN)
        casec5f2 = np.random.normal(7.5,smallVar,smallN)
        casec5 = np.vstack((casec5f1,casec5f2)).T
        case = np.vstack((case,casec5))
        caseLabels = np.hstack((caseLabels,np.array([5]).repeat(np.shape(casec5)[0])))

    ## cluster 6
    if 6 not in rmClusters:
        casec6f1 = np.random.normal(4.6,smallVar,smallN)
        casec6f2 = np.random.normal(6.5,smallVar,smallN)
        casec6 = np.vstack((casec6f1,casec6f2)).T
        case = np.vstack((case,casec6))
        caseLabels = np.hstack((caseLabels,np.array([6]).repeat(np.shape(casec6)[0])))

    ## cluster 7
    if 7 not in rmClusters:
        casec7f1 = np.random.normal(4.5,smallVar,smallN)
        casec7f2 = np.random.normal(4.2,smallVar,smallN)
        casec7 = np.vstack((casec7f1,casec7f2)).T
        case = np.vstack((case,casec7))
        caseLabels = np.hstack((caseLabels,np.array([7]).repeat(np.shape(casec7)[0])))

    ## cluster 8
    if 8 not in rmClusters:
        casec8f1 = np.random.normal(5.2,smallVar,smallN)
        casec8f2 = np.random.normal(5.0,smallVar,smallN)
        casec8 = np.vstack((casec8f1,casec8f2)).T
        case = np.vstack((case,casec8))
        caseLabels = np.hstack((caseLabels,np.array([8]).repeat(np.shape(casec8)[0])))

    ## cluster 9
    if 9 not in rmClusters:
        casec9f1 = np.random.normal(5.8,smallVar,smallN)
        casec9f2 = np.random.normal(4.3,smallVar,smallN)
        casec9 = np.vstack((casec9f1,casec9f2)).T
        case = np.vstack((case,casec9))
        caseLabels = np.hstack((caseLabels,np.array([9]).repeat(np.shape(casec9)[0])))

    ## cluster 10
    if 10 not in rmClusters:
        casec10f1 = np.random.normal(12.6,smallVar,smallN)
        casec10f2 = np.random.normal(8.2,smallVar,smallN)
        casec10 = np.vstack((casec10f1,casec10f2)).T
        case = np.vstack((case,casec10))
        caseLabels = np.hstack((caseLabels,np.array([10]).repeat(np.shape(casec10)[0])))
 
    ## cluster 11
    if 11 not in rmClusters:
        casec11f1 = np.random.normal(11.6,smallVar,smallN)
        casec11f2 = np.random.normal(8.0,smallVar,smallN)
        casec11 = np.vstack((casec11f1,casec11f2)).T
        case = np.vstack((case,casec11))
        caseLabels = np.hstack((caseLabels,np.array([11]).repeat(np.shape(casec11)[0])))

    ## cluster 12
    if 12 not in rmClusters:
        casec12f1 = np.random.normal(12.6,smallVar,smallN)
        casec12f2 = np.random.normal(7.2,smallVar,smallN)
        casec12 = np.vstack((casec12f1,casec12f2)).T
        case = np.vstack((case,casec12))
        caseLabels = np.hstack((caseLabels,np.array([12]).repeat(np.shape(casec12)[0])))

    ## cluster 13
    if 13 not in rmClusters:
        casec13f1 = np.random.normal(11.5,smallVar,smallN)
        casec13f2 = np.random.normal(4.2,smallVar,smallN)
        casec13 = np.vstack((casec13f1,casec13f2)).T
        case = np.vstack((case,casec13))
        caseLabels = np.hstack((caseLabels,np.array([13]).repeat(np.shape(casec13)[0])))

    ## cluster 14
    if 14 not in rmClusters:
        casec14f1 = np.random.normal(11.2,smallVar,smallN)
        casec14f2 = np.random.normal(5.5,smallVar,smallN)
        casec14 = np.vstack((casec14f1,casec14f2)).T
        case = np.vstack((case,casec14))
        caseLabels = np.hstack((caseLabels,np.array([14]).repeat(np.shape(casec14)[0])))

    ## cluster 15
    if 15 not in rmClusters:
        casec15f1 = np.random.normal(12.2,smallVar,smallN)
        casec15f2 = np.random.normal(5.1,smallVar,smallN)
        casec15 = np.vstack((casec15f1,casec15f2)).T
        case = np.vstack((case,casec15))
        caseLabels = np.hstack((caseLabels,np.array([15]).repeat(np.shape(casec15)[0])))

    ## cluster 16
    if 16 not in rmClusters:
        casec16f1 = np.random.normal(8.8,smallVar,smallN)
        casec16f2 = np.random.normal(12.9,smallVar,smallN)
        casec16 = np.vstack((casec16f1,casec16f2)).T
        case = np.vstack((case,casec16))
        caseLabels = np.hstack((caseLabels,np.array([16]).repeat(np.shape(casec16)[0])))

    ## cluster 17
    if 17 not in rmClusters:
        casec17f1 = np.random.normal(7.2,smallVar,smallN)
        casec17f2 = np.random.normal(13.2,smallVar,smallN)
        casec17 = np.vstack((casec17f1,casec17f2)).T
        case = np.vstack((case,casec17))
        caseLabels = np.hstack((caseLabels,np.array([17]).repeat(np.shape(casec17)[0])))

    ## cluster 18
    if 18 not in rmClusters:
        casec18f1 = np.random.normal(8.3,smallVar,smallN)
        casec18f2 = np.random.normal(13.8,smallVar,smallN)
        casec18 = np.vstack((casec18f1,casec18f2)).T
        case = np.vstack((case,casec18))
        caseLabels = np.hstack((caseLabels,np.array([18]).repeat(np.shape(casec18)[0])))

    ## cluster 19
    if 19 not in rmClusters:
        casec19f1 = np.random.normal(12.1,smallVar,smallN)
        casec19f2 = np.random.normal(12.1,smallVar,smallN)
        casec19 = np.vstack((casec19f1,casec19f2)).T
        case = np.vstack((case,casec19))
        caseLabels = np.hstack((caseLabels,np.array([19]).repeat(np.shape(casec19)[0])))

    ## cluster 20
    if 20 not in rmClusters:
        casec20f1 = np.random.normal(11.7,smallVar,smallN)
        casec20f2 = np.random.normal(11.2,smallVar,smallN)
        casec20 = np.vstack((casec20f1,casec20f2)).T
        case = np.vstack((case,casec20))
        caseLabels = np.hstack((caseLabels,np.array([20]).repeat(np.shape(casec20)[0])))

    ## cluster 21
    if 21 not in rmClusters:
        casec21f1 = np.random.normal(10.9,smallVar,smallN)
        casec21f2 = np.random.normal(11.8,smallVar,smallN)
        casec21 = np.vstack((casec21f1,casec21f2)).T
        case = np.vstack((case,casec21))
        caseLabels = np.hstack((caseLabels,np.array([21]).repeat(np.shape(casec21)[0])))

    ## cluster 22
    if 22 not in rmClusters:
        casec22f1 = np.random.normal(8.5,smallVar,smallN)
        casec22f2 = np.random.normal(11.0,smallVar,smallN)
        casec22 = np.vstack((casec22f1,casec22f2)).T
        case = np.vstack((case,casec22))
        caseLabels = np.hstack((caseLabels,np.array([22]).repeat(np.shape(casec22)[0])))

    ## cluster 23
    if 23 not in rmClusters:
        casec23f1 = np.random.normal(7.1,smallVar,smallN)
        casec23f2 = np.random.normal(10.9,smallVar,smallN)
        casec23 = np.vstack((casec23f1,casec23f2)).T
        case = np.vstack((case,casec23))
        caseLabels = np.hstack((caseLabels,np.array([23]).repeat(np.shape(casec23)[0])))

    ## cluster 24
    if 24 not in rmClusters:
        casec24f1 = np.random.normal(8.0,smallVar,smallN)
        casec24f2 = np.random.normal(10.0,smallVar,smallN)
        casec24 = np.vstack((casec24f1,casec24f2)).T
        case = np.vstack((case,casec24))
        caseLabels = np.hstack((caseLabels,np.array([24]).repeat(np.shape(casec24)[0])))

    ## cluster 25
    if 25 not in rmClusters:
        casec25f1 = np.random.normal(15.2,smallVar,smallN)
        casec25f2 = np.random.normal(6.0,smallVar,smallN)
        casec25 = np.vstack((casec25f1,casec25f2)).T
        case = np.vstack((case,casec25))
        caseLabels = np.hstack((caseLabels,np.array([25]).repeat(np.shape(casec25)[0])))

    ## cluster 26
    if 26 not in rmClusters:
        casec26f1 = np.random.normal(14.71,smallVar,smallN)
        casec26f2 = np.random.normal(5.0,smallVar,smallN)
        casec26 = np.vstack((casec26f1,casec26f2)).T
        case = np.vstack((case,casec26))
        caseLabels = np.hstack((caseLabels,np.array([26]).repeat(np.shape(casec26)[0])))

    ## cluster 27
    if 27 not in rmClusters:
        casec27f1 = np.random.normal(16.0,smallVar,smallN)
        casec27f2 = np.random.normal(5.3,smallVar,smallN)
        casec27 = np.vstack((casec27f1,casec27f2)).T
        case = np.vstack((case,casec27))
        caseLabels = np.hstack((caseLabels,np.array([27]).repeat(np.shape(casec27)[0])))

    return case, caseLabels

case1,case1Labels = get_case_and_labels()
case2,case2Labels = get_case_and_labels(rmClusters=[13])
case3,case3Labels = get_case_and_labels(rmClusters=[13,14,15])

if __name__=='__main__':
    
    fig = plt.figure(figsize=(9,4))
    ax = fig.add_subplot(131)
    ax.scatter(case1[:,0], case1[:,1])
    ax.set_title("Case 1")
    ax.set_xlim([1,17])
    ax.set_ylim([1,15])
    ax.set_aspect(1./ax.get_data_ratio())

    ax = fig.add_subplot(132)
    ax.scatter(case2[:,0], case2[:,1])
    ax.set_title("Case 2")
    ax.set_xlim([1,17])
    ax.set_ylim([1,15])
    ax.set_aspect(1./ax.get_data_ratio())

    ax = fig.add_subplot(133)
    ax.scatter(case3[:,0], case3[:,1])
    ax.set_title("Case 3")
    ax.set_xlim([1,17])
    ax.set_ylim([1,15])
    ax.set_aspect(1./ax.get_data_ratio())


    #ax = fig.add_subplot(132)
    #ax.scatter(case2[:,0], case2[:,1])
    #ax.set_title("Case 2")
    #ax.set_xlim([4,16])
    #ax.set_ylim([4,16])

    #ax = fig.add_subplot(133)
    #ax.scatter(case3[:,0], case3[:,1])
    #ax.set_title("Case 3")
    #ax.set_xlim([4,16])
    #ax.set_ylim([4,16])

    plt.show()
