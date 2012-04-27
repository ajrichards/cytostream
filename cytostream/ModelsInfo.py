## define the possible models
# shortname : (longname, runfilename, preferences file name)

modelsInfo = {'kmeans':('k-means clustering',"RunModelKmeans.py","PreferencesKmeans.py"),
              'dpmm-mcmc':('"Dirichlet Process Mixture Model - MCMC"',"RunModelDPMM-MCMC.py","PreferencesDPMM-MCMC.py"),
              'dpmm-bem':('"Dirichlet Process Mixture Model - BEM"',"RunModelDPMM-BEM.py","PreferencesDPMM-BEM.py"),
              'dpmm-mcmc':('Hierarchical Dirichlet Process Mixture Model - MCMC"',"RunModelHDP-MCMC.py","PreferencesHDP-MCMC.py")
}
