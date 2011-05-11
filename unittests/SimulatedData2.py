#!/usr/bin/env python


import numpy as np
import matplotlib.pyplot as plt

## variables 
largeN = 1000
smallN = 100

## case 1
case1c1f1 = np.random.normal(10,0.5,largeN)
case1c1f2 = np.random.normal(12,0.5,largeN)
case1c1 = np.vstack((case1c1f1,case1c1f2)).T

case1c2f1 = np.random.normal(10,1.0,smallN)
case1c2f2 = np.random.normal(8,0.5,smallN)
case1c2 = np.vstack((case1c2f1,case1c2f2)).T

case1 = np.vstack((case1c1,case1c2))
case1Labels = np.hstack((np.array([0]).repeat(np.shape(case1c1)[0]),np.array([1]).repeat(np.shape(case1c2)[0])))

## case 2
case2c2f1 = np.random.normal(10,0.5,largeN)
case2c2f2 = np.random.normal(10,1.0,largeN)
case2c2 = np.vstack((case2c2f1,case2c2f2)).T

case2 = np.vstack((case2c2))
case2Labels = np.hstack((np.array([7]).repeat(np.shape(case2c2)[0])))

## case 3
case3c1f1 = np.random.normal(10,0.5,largeN)
case3c1f2 = np.random.normal(8,0.5,largeN)
case3c1 = np.vstack((case3c1f1,case3c1f2)).T

case3c2f1 = np.random.normal(10,1.0,smallN)
case3c2f2 = np.random.normal(12,0.5,smallN)
case3c2 = np.vstack((case3c2f1,case3c2f2)).T

case3 = np.vstack((case3c1,case3c2))
case3Labels = np.hstack((np.array([0]).repeat(np.shape(case3c1)[0]),np.array([1]).repeat(np.shape(case3c2)[0])))
case3Labels = 3 + case3Labels

if __name__=='__main__':
    
    fig = plt.figure(figsize=(9,4))
    ax = fig.add_subplot(131)
    ax.scatter(case1[:,0], case1[:,1])
    ax.set_title("Case 1")
    ax.set_xlim([4,16])
    ax.set_ylim([4,16])
    
    ax = fig.add_subplot(132)
    ax.scatter(case2[:,0], case2[:,1])
    ax.set_title("Case 2")
    ax.set_xlim([4,16])
    ax.set_ylim([4,16])

    ax = fig.add_subplot(133)
    ax.scatter(case3[:,0], case3[:,1])
    ax.set_title("Case 3")
    ax.set_xlim([4,16])
    ax.set_ylim([4,16])

    plt.show()
