## define the possible models
# shortname : (longname, runfilename, preferences file name)

modelsInfo = {'kmeans':('k-means clustering',"RunModelKmeans.py","PreferencesKmeans"),
              'dpmm-mcmc':('"Dirichlet Process Mixture Model - MCMC"',"RunModelDPMM.py","PreferencesDPMM"),
              'dpmm-bem':('"Dirichlet Process Mixture Model - BEM"',"RunModelDPMM.py","PreferencesDPMM"),
              'dpmm-hdp':('Hierarchical Dirichlet Process Mixture Model - MCMC"',"RunModelHDP.py","PreferencesHDP")
}
