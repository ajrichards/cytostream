'''
configure dictionary defaults

state variables     - deal with stage transitions and stages or specifics of the gui
immutable variables - may be set here but they do not change after a project has been created
analysis variables  - these variables although set here may be changed while cytostream is running

A. Richards
'''

configDictDefault = {
    ########### state variables ##############################################################
    'current_state'                         : 'Data Processing',    # do not change
    'highest_state'                         : '0',                  # do not change
    'selected_file'                         : 'None',               # do not change
    'selected_model'                        : 'None',               # do not change
    'data_processing_mode'                  : 'channel select',     # do not change   
    'models_run_count'                      : '0',                  # do not change
    'filters_run_count'                     : '{}',                 # do not change

    ########### immutable variables ##########################################################
    'input_data_type'                       : 'fcs',                # fcs, txt
    'setting_max_scatter_display'           : '2e4',                # any float, int or string
    'selected_transform'                    : 'log',                # log, logicle
    'num_iters_mcmc'                        : '1100',               # an int
    'thumbnail_results_default'             : 'modes',              # modes, components
    'scatter_marker_size'                   : '1',                  # mpl scatter marker size
    'font_size'                             : '12',                 # int
    'font_name'                             : 'arial',              # font name
    'plot_type'                             : 'png',                # png, pdf, jpg

    ########### analysis variables  ########################################################## 
    'subsample_qa'                          : '1e3',                # any float, int or string
    'subsample_analysis'                    : '1e3',                # any float, int or string
    'model_to_run'                          : 'dpmm',               # dpmm, kmeans    
    'selected_k'                            : '16',                 # an int divisible by 8
    'results_mode'                          : 'modes',              # modes, components
    'thumbnails_to_view'                    : 'None',               # None or '[(0,1),(0,3)]'
    'excluded_files'                        : '[]',                 # (indices) !not yet functional
    'excluded_channels_qa'                  : '[]',                 # a list of ints (indices)  
    'excluded_channels_analysis'            : '[]',                 # a list of ints (indices)
    'alternate_channel_labels'              : '[]',                 # a list of labels
    'alternate_file_labels'                 : '[]',                 # a list of labels
    'file_in_focus'                         : 'all',                # all or file name
    'filter_in_focus'                       : 'None',               # all or e.g. '1000_filter1'
    'model_mode'                            : 'normal',             # normal, onefit, pooled
    'model_reference'                       : 'None',               # fileName, pooled
    'model_reference_run_id'                : 'None',               # a run id i.e. run1
    'channel_view'                          : 'normal',             # normal, custom
    'app_color'                             : '#999999',            # a color
}
