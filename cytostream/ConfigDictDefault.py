'''
configure dictionary defaults

state variables     - deal with stage transitions and stages or specifics of the gui
immutable variables - may be set here but they do not change after a project has been created
analysis variables  - these variables although set here may be changed while cytostream is running

A. Richards
'''

plotsToViewChannels =   [(0,1) for i in range(16)]
plotsToViewFiles =      [0 for i in range(16)]
plotsToViewRuns =       ['run1' for i in range(16)]
plotsToViewHighlights = [None for i in range(16)]

configDictDefault = {
    ########### state variables ##############################################################
    'current_state'                         : 'Initial',            # do not change
    'highest_state'                         : '0',                  # do not change
    'selected_file'                         : 'None',               # do not change
    'selected_model'                        : 'run1',               # do not change
    'models_run_count'                      : '0',                  # do not change
    'filters_run_count'                     : '0',                  # do not change
    'force_single_gpu'                      : 'False',              # do not change

    ########### immutable variables ##########################################################
    'input_data_type'                       : 'fcs',                # fcs, comma, tab, array
    'setting_max_scatter_display'           : '7e4',                # any float, int or string
    'selected_transform'                    : 'logicle',            # log, logicle
    'num_iters_mcmc'                        : '1100',               # an int
    'thumbnail_results_default'             : 'modes',              # modes, components
    'scatter_marker_size'                   : '2',                  # mpl scatter marker size
    'font_size'                             : '12',                 # int
    'font_name'                             : 'arial',              # font name
    'plot_type'                             : 'png',                # png, pdf, jpg

    ########### analysis variables  ########################################################## 
    'subsample_qa'                          : '1e3',                # any float, int or string
    'subsample_analysis'                    : '1e3',                # any float, int or string
    'model_to_run'                          : 'dpmm',               # dpmm, kmeans    
    'dpmm_k'                                : '16',                 # an int divisible by 16
    'dpmm_gamma'                            : '1.0',                # gamma value for dpmm
    'results_mode'                          : 'modes',              # modes, components
    'plots_to_view_channels'                : plotsToViewChannels,  # defined above'
    'plots_to_view_files'                   : plotsToViewFiles,     # defined above'
    'plots_to_view_runs'                    : plotsToViewRuns,      # defined above'
    'plots_to_view_highlights'              : plotsToViewHighlights,# defined above'
    'thumbnails_to_view'                    : 'None',               # None or '[(0,1),(0,3)]'
    'excluded_files'                        : '[]',                 # (indices) !not yet functional
    'excluded_channels_qa'                  : '[]',                 # a list of ints (indices)  
    'excluded_channels_analysis'            : '[]',                 # a list of ints (indices)
    'excluded_files_qa'                     : '[]',                 # a list of ints
    'excluded_files_analysis'               : '[]',                 # a list of ints
    'alternate_channel_labels'              : '[]',                 # a list of labels
    'alternate_file_labels'                 : '[]',                 # a list of labels
    'file_in_focus'                         : 'all',                # all or file name
    'clean_border_events'                   : 'True',               # True, False      
    'model_mode'                            : 'normal',             # normal,onefit,pooled,target
    'model_reference'                       : 'None',               # fileName, pooled
    'model_reference_run_id'                : 'None',               # a run id i.e. run1
    'channel_view'                          : 'normal',             # normal, custom
    'app_color'                             : '#999999',            # a color
    'visualization_mode'                    : 'thumbnails',         # thumbs, 1D-viewer etc
    'fa_phi_range'                          : '[0.4]',              # a list or np.array of phis
    'fa_min_merge_sil_value'                : '0.3',                # min silhouette value for merge    
    'fa_distance_metric'                    : 'mahalanobis',        # mahalanobis or euclidean
    'auto_compensation'                     : 'True'                # True or False
}
