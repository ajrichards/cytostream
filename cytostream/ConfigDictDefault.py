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
    'highest_State'                         : '0',                  # do not change
    'selected_file'                         : None,                 # do not change
    'selected_model'                        : None,                 # do not change
    'data_processing_mode'                  : 'channel select',     # do not change   
    'models_run_count'                      : '0',                    # do not change

    ########### immutable variables ##########################################################
    'input_data_type'                       : 'fcs',                # fcs, txt
    'setting_max_scatter_display'           : '2e4',                # any float, int or string
    'selected_transform'                    : 'log',                # log, logicle
    'num_filter_steps'                      : '0',                  # not yet implemented
    'num_iters_mcmc'                        : '1100',                 # an int

    ########### analysis variables  ########################################################## 
    'subsample_qa'                          : '1e3',                # any float, int or string
    'subsample_analysis'                    : '1e3',                # any float, int or string
    'model_to_run'                          : 'dpmm',               # dpmm, kmeans    
    'selected_k'                            : '16',                 # an int divisible by 8
    'results_mode'                          : 'modes',              # modes, components
    'thumbnail_view'                        : 'pairwise',           # pairwise, custom
    'excluded_files_qa'                     : '[]',                   # a list of ints (indices)
    'excluded_files_analysis'               : '[]',                   # a list of ints (indices)
    'excluded_channels_qa'                  : '[]',                   # a list of ints (indices)  
    'excluded_channels_analysis'            : '[]',                   # a list of ints (indices)
}
