#!/usr/bin/env python


import numpy as np
import matplotlib.pyplot as plt

## variables 
largeN = 2000
smallN = 50

## case 1
case1c1f1 = np.random.normal(3,0.5,largeN)
case1c1f2 = np.random.normal(10,0.5,largeN)
case1c1 = np.vstack((case1c1f1,case1c1f2)).T

case1c2f1 = np.random.normal(10,1.0,largeN)
case1c2f2 = np.random.normal(10,0.5,largeN)
case1c2 = np.vstack((case1c2f1,case1c2f2)).T

case1c3f1 = np.random.normal(10,0.5,smallN)
case1c3f2 = np.random.normal(3,0.5,smallN)
case1c3 = np.vstack((case1c3f1,case1c3f2)).T

case1 = np.vstack((case1c1,case1c2))
case1 = np.vstack((case1,case1c3))

case1Labels = np.hstack((np.array([0]).repeat(np.shape(case1c1)[0]),np.array([1]).repeat(np.shape(case1c2)[0])))
case1Labels = np.hstack((case1Labels,np.array([2]).repeat(np.shape(case1c3)[0])))

## case 2 (missing cluster 1)
case2c2f1 = np.random.normal(10,1.0,largeN)
case2c2f2 = np.random.normal(10,0.5,largeN)
case2c2 = np.vstack((case2c2f1,case2c2f2)).T

case2c3f1 = np.random.normal(10,0.5,smallN)
case2c3f2 = np.random.normal(3,0.5,smallN)
case2c3 = np.vstack((case2c3f1,case2c3f2)).T

case2 = np.vstack((case2c2,case2c3))
case2Labels = np.hstack((np.array([7]).repeat(np.shape(case2c2)[0]),np.array([np.random.randint(12,15)]).repeat(np.shape(case1c3)[0])))

## case 3 (shifted cluster 1)
case3c1f1 = np.random.normal(3,0.5,largeN)
case3c1f2 = np.random.normal(8.5,0.5,largeN)
case3c1 = np.vstack((case3c1f1,case3c1f2)).T

case3c2f1 = np.random.normal(10,1.0,largeN)
case3c2f2 = np.random.normal(10,0.5,largeN)
case3c2 = np.vstack((case3c2f1,case3c2f2)).T

case3c3f1 = np.random.normal(10,0.5,smallN)
case3c3f2 = np.random.normal(3,0.5,smallN)
case3c3 = np.vstack((case3c3f1,case3c3f2)).T

case3 = np.vstack((case3c1,case3c2))
case3 = np.vstack((case3,case3c3))

case3Labels = np.hstack((np.array([0]).repeat(np.shape(case3c1)[0]),np.array([1]).repeat(np.shape(case3c2)[0])))
case3Labels = np.hstack((case3Labels,np.array([2]).repeat(np.shape(case3c3)[0])))
case3Labels = 3 + case3Labels

## case 4 (split cluster 2)
case4c1f1 = np.random.normal(3,0.5,largeN)
case4c1f2 = np.random.normal(10,0.5,largeN)
case4c1 = np.vstack((case4c1f1,case4c1f2)).T

case4c2f1 = np.random.normal(9,0.25,int(round(largeN/2.0)))
case4c2f2 = np.random.normal(10,0.25,int(round(largeN/2.0)))
case4c2 = np.vstack((case4c2f1,case4c2f2)).T

case4c4f1 = np.random.normal(11,0.25,int(round(largeN/2.0)))
case4c4f2 = np.random.normal(10,0.25,int(round(largeN/2.0)))
case4c4 = np.vstack((case4c4f1,case4c4f2)).T

case4c3f1 = np.random.normal(10,0.5,smallN)
case4c3f2 = np.random.normal(3,0.5,smallN)
case4c3 = np.vstack((case4c3f1,case4c3f2)).T

case4 = np.vstack((case4c1,case4c2))
case4 = np.vstack((case4,case4c3))
case4 = np.vstack((case4,case4c4))

case4Labels = np.hstack((np.array([0]).repeat(np.shape(case4c1)[0]),np.array([1]).repeat(np.shape(case4c2)[0])))
case4Labels = np.hstack((case4Labels,np.array([2]).repeat(np.shape(case4c3)[0])))
case4Labels = np.hstack((case4Labels,np.array([3]).repeat(np.shape(case4c4)[0])))
case4Labels = 6 + case4Labels

## case 5
case5c1f1 = np.random.normal(3,0.5,largeN)
case5c1f2 = np.random.normal(10,0.5,largeN)
case5c1 = np.vstack((case5c1f1,case5c1f2)).T

case5c2f1 = np.random.normal(10,1.0,largeN)
case5c2f2 = np.random.normal(10,0.5,largeN)
case5c2 = np.vstack((case5c2f1,case5c2f2)).T

case5c3f1 = np.random.normal(10,0.5,smallN)
case5c3f2 = np.random.normal(3,0.5,smallN)
case5c3 = np.vstack((case5c3f1,case5c3f2)).T

case5c4f1 = np.random.normal(3,0.5,smallN)
case5c4f2 = np.random.normal(3,0.5,smallN)
case5c4 = np.vstack((case5c4f1,case5c4f2)).T

case5 = np.vstack((case5c1,case5c2))
case5 = np.vstack((case5,case5c3))
case5 = np.vstack((case5,case5c4))

case5Labels = np.hstack((np.array([np.random.randint(1,3)]).repeat(np.shape(case5c1)[0]),np.array([0]).repeat(np.shape(case5c2)[0])))
case5Labels = np.hstack((case5Labels,np.array([np.random.randint(12,15)]).repeat(np.shape(case5c3)[0])))
case5Labels = np.hstack((case5Labels,np.array([np.random.randint(4,7)]).repeat(np.shape(case5c4)[0])))

## case 6

## noise cluster
case6c1f1 = np.random.normal(6,4.0,smallN)
case6c1f2 = np.random.normal(6,4.0,smallN)
case6c1 = np.vstack((case6c1f1,case6c1f2)).T

## remove negative numbers from noise
case6c1 = case6c1[np.where(case6c1[:,0] > 0)[0]]
case6c1 = case6c1[np.where(case6c1[:,1] > 0)[0]]

case6c2f1 = np.random.normal(10,1.0,largeN)
case6c2f2 = np.random.normal(10,0.5,largeN)
case6c2 = np.vstack((case6c2f1,case6c2f2)).T

case6c3f1 = np.random.normal(10,0.5,smallN)
case6c3f2 = np.random.normal(3,0.5,smallN)
case6c3 = np.vstack((case6c3f1,case6c3f2)).T

case6c4f1 = np.random.normal(3,0.5,smallN)
case6c4f2 = np.random.normal(3,0.5,smallN)
case6c4 = np.vstack((case6c4f1,case6c4f2)).T

case6 = np.vstack((case6c1,case6c2))
case6 = np.vstack((case6,case6c3))
case6 = np.vstack((case6,case6c4))

case6Labels = np.hstack((np.array([42]).repeat(np.shape(case6c1)[0]),np.array([np.random.randint(1,3)]).repeat(np.shape(case6c2)[0])))
case6Labels = np.hstack((case6Labels,np.array([np.random.randint(4,7)]).repeat(np.shape(case6c3)[0])))
case6Labels = np.hstack((case6Labels,np.array([np.random.randint(12,15)]).repeat(np.shape(case6c4)[0])))


if __name__=='__main__':
    
    fig = plt.figure()
    ax = fig.add_subplot(231)
    ax.scatter(case1[:,0], case1[:,1])
    ax.set_title("Case 1")
    ax.set_xlim([0,14])
    ax.set_ylim([0,14])
    
    ax = fig.add_subplot(232)
    ax.scatter(case2[:,0], case2[:,1])
    ax.set_title("Case 2")
    ax.set_xlim([0,14])
    ax.set_ylim([0,14])

    ax = fig.add_subplot(233)
    ax.scatter(case3[:,0], case3[:,1])
    ax.set_title("Case 3")
    ax.set_xlim([0,14])
    ax.set_ylim([0,14])

    ax = fig.add_subplot(234)
    ax.scatter(case4[:,0], case4[:,1])
    ax.set_title("Case 4")
    ax.set_xlim([0,14])
    ax.set_ylim([0,14])

    ax = fig.add_subplot(235)
    ax.scatter(case5[:,0], case5[:,1])
    ax.set_title("Case 5")
    ax.set_xlim([0,14])
    ax.set_ylim([0,14])

    ax = fig.add_subplot(236)
    ax.scatter(case6[:,0], case6[:,1])
    ax.set_title("Case 6")
    ax.set_xlim([0,14])
    ax.set_ylim([0,14])

    plt.show()
