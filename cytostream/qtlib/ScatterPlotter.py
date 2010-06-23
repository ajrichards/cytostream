import sys,os
sys.path.append(os.path.join(".."))
from PyQt4 import QtGui
import numpy as np
from matplotlib.figure import Figure  
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from Model import Model

class ScatterPlotter(FigureCanvas):

    def __init__(self, parent, projectID, selectedFile, channel1, channel2, subset="All Data",altDir=None, modelName=None):

        ## variables
        if os.path.isdir(os.path.join(".","projects",projectID)) == True:
            homeDir = os.path.join(".","projects",projectID)
        elif os.path.isdir(os.path.join("..","projects",projectID)) == True:
            homeDir = os.path.join("..","projects",projectID)

        # plot definition   
        self.fig = Figure()
        ax = self.fig.add_subplot(111)

        model = Model()
        model.initialize(projectID,homeDir)
        if modelName != None:
            statModel,statModelClasses = model.load_model_results_pickle(modelName)
        else:
            statModel,statModelClasses = None, None

        self.make_scatter_plot(ax,model,selectedFile,channel1,channel2,subset,labels=statModelClasses)
        
        # initialization of the canvas 
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)

    def make_scatter_plot(self,ax,model,selectedFile,channel1,channel2,subset,labels=None,buff=0.02,altDir=None):
        
        markerSize = 5
        fontName = 'arial'
        fontSize = 12
        plotType = 'png'

        fileChannels = model.get_file_channel_list(selectedFile)
        index1 = fileChannels.index(channel1)
        index2 = fileChannels.index(channel2)
        data = model.pyfcm_load_fcs_file(selectedFile)

        ## subset give an numpy array of indices 
        if subset != "All Data":
            subsampleIndices = model.get_subsample_indices(subset)
            data = data[subsampleIndices,:]

        ## make plot 
        totalPoints = 0
        if labels == None:
            ax.scatter([data[:,index1]],[data[:,index2]],color='blue',s=markerSize)
        else:    
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)
            numColors = range(maxLabel)
            print dir(model)
            cmp = model.get_n_color_colorbar(maxLabel)
        
            for l in range(maxLabel):
                rgbVal = tuple([val * 256 for val in cmp[l,:3]])
                hexColor = model.rgb_to_hex(rgbVal)[:7]

                x = data[:,index1][np.where(labels[:,0]==l)[0]]
                y = data[:,index2][np.where(labels[:,0]==l)[0]]

                totalPoints+=x.size

                if x.size == 0:
                    continue

                ax.scatter([x],[y],color=hexColor,s=markerSize)

        ## handle data edge buffers 
        bufferX = buff * (data[:,index1].max() - data[:,index1].min())
        bufferY = buff * (data[:,index2].max() - data[:,index2].min())
        ax.set_xlim([data[:,index1].min()-bufferX,data[:,index1].max()+bufferX])
        ax.set_ylim([data[:,index2].min()-bufferY,data[:,index2].max()+bufferY])

        ### save file 
        fileName = selectedFile
        ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
        ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

        #if altDir == None:
        #    fileName = os.path.join(model.homeDir,'figs',"%s_%s_%s.%s"%(selectedFile[:-4],channel1,channel2,plotType))
        #    fig.savefig(fileName)
        #    #os.system("convert %s %s"%(fileName, fileName[:-4]+".gif"))
        #else:
        #    fileName = os.path.join(altDir,"%s_%s_%s.%s"%(selectedFile[:-4],channel1,channel2,plotType))
        #    fig.savefig(fileName)
        #    #os.system("convert %s %s"%(fileName, fileName[:-4]+".gif"))         


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    parent =  QtGui.QWidget()
    projectID = "Demo"
    selectedFile = "3FITC_4PE_004.fcs"
    channel1 = 'FL1-H' 
    channel2 = 'FL2-H'
    sp = ScatterPlotter(parent, projectID, selectedFile, channel1, channel2)
    sp.show()
    sys.exit(app.exec_())



















    '''
    ## get_mpl_canvas
    def make_scatter_plot(self):#labels=None,root=None,buff=0.02,width=None,height=None,getCanvas=False,altDir=None):
        #fig = pyplot.figure(figsize=(10,7.5))

        #if getCanvas == True:
        #    fig = pyplot.figure(figsize=(7,7))
        #else:
        #    fig = pyplot.figure(figsize=(7,7),facecolor=None)
        #fig = Figure(figsize=(5,4), dpi=100)
        
        markerSize = 7
        #states = self.controller.get_component_states()

        # use the component inds as sorted by pi 
        #if states != None:
        #    sortedInds = states['sortedInds']

        #ax = fig.add_subplot(111)
        #fontName = 'arial'
        #fontSize = 12
        #plotType = 'png'
        
        # determine the type of input
        #if len(channel1tuple) == 2:
        #    channel1,index1 = channel1tuple
        #    channel2,index2 = channel2tuple
        #else:
        #    channel1 = channel1tuple
        #    channel2 = channel2tuple
        
        ##fileChannels = self.get_file_channel_list(selectedFile)
        ##fileSpecificIndices = [fileChannels.index(i) for i in [channel1,channel2]]
        ##index1,index2 = fileSpecificIndices
        index1 = 0
        index2 = 1

        #fileNameFCS = os.path.join("..","Flow-GCMC","example_data","3FITC_4PE_004.fcs")
        #file = fcm.loadFCS(fileNameFCS)

        #self.fig = Figure()
        #self.axes = self.fig.add_subplot(111)
        self.x = np.arange(0.0, 3.0, 0.01)
        self.y = np.cos(2*np.pi*self.x)
        self.axes.plot(self.x, self.y)
       
        ##data = self.pyfcm_load_fcs_file(selectedFile)
        #fileNameFCS = os.path.join("..","Flow-GCMC","example_data","3FITC_4PE_004.fcs")
        #data = fcm.loadFCS(fileNameFCS)

        ## subset give an numpy array of indices
        #if self.controller.subsampleIndices != None:
        #    data = data[self.controller.subsampleIndices,:]
            
        ## make plot

        totalPoints = 0
        if labels == None:
             ax.scatter([data[:,index1]],[data[:,index2]],color='blue',s=markerSize)
        else:
            
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)
            numColors = range(maxLabel)
            cmp = self.get_n_color_colorbar(maxLabel)
            print 'dbg',maxLabel, len(cmp), type(cmp), np.shape(cmp)
            print cmp[0,:]

            for l in range(maxLabel):
                rgbVal = tuple([val * 256 for val in cmp[l,:3]])
                hexColor = self.rgb_to_hex(rgbVal)[:7]

                # used the sorted index
                if states != None:
                    si = sortedInds[l]
                else:
                    si = l

                print "\t", l, si, hexColor
                x = data[:,index1][np.where(labels[:,0]==si)[0]]
                y = data[:,index2][np.where(labels[:,0]==si)[0]]

                totalPoints+=x.size

                if x.size == 0:
                    continue

                # check to see if user turned off cluster visualization
                if states != None and states['id'][l] == 1:
                    continue

                ax.scatter([x],[y],color=hexColor,s=markerSize)

            ## add means if specified
            for l in range(maxLabel):
                rgbVal = tuple([val * 256 for val in cmp[l]])
                hexColor = self.rgb_to_hex(rgbVal)[:7]

                if states != None:
                    val = states['mu'][l]
                    if val == 1:
                        xPos, yPos = [float(v) for v in re.sub('\s','',states['muVals'][l]).split(',')]
                        colorShade = np.array([float(v) for v in rgbVal])[:-1].sum()

                        print 'mean colorShade', colorShade
                        if colorShade < 385 or colorShade > 700:
                            textColor = 'white'
                        else:
                            textColor = 'black'

                        ax.text(xPos, yPos, 'c%s'%l, color=textColor,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=hexColor)
                                )
            
        fileName = self.controller.log.log['selectedFile'] 
        ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize = fontSize)
        ax.set_xlabel(channel1,fontname=self.controller.fontName,fontsize=fontSize)
        ax.set_ylabel(channel2,fontname=self.controller.fontName,fontsize=fontSize)
        
        ## handle data edge buffers
        bufferX = buff * (data[:,index1].max() - data[:,index1].min())
        bufferY = buff * (data[:,index2].max() - data[:,index2].min())
        ax.set_xlim([data[:,index1].min()-bufferX,data[:,index1].max()+bufferX])
        ax.set_ylim([data[:,index2].min()-bufferY,data[:,index2].max()+bufferY])

        if altDir == None:
            fileName = os.path.join(self.controller.homeDir,'figs',"%s_%s_%s.%s"%(selectedFile[:-4],channel1,channel2,plotType))
            fig.savefig(fileName)
            os.system("convert %s %s"%(fileName, fileName[:-4]+".gif"))
        else:
            if os.path.isdir(altDir) == False:
                print "ERROR: specified alternative dir does not exist\n", altDir
            else:
                fileName = os.path.join(altDir,"%s_%s_%s.%s"%(selectedFile[:-4],channel1,channel2,plotType))
                fig.savefig(fileName)
                os.system("convert %s %s"%(fileName, fileName[:-4]+".gif"))

        if getCanvas == True:
            canvas = FigureCanvasTkAgg(fig,master=root)
            canvas.get_tk_widget().pack(side=tk.TOP) #fill=tk.BOTH, expand=1
            toolbar = NavigationToolbar2TkAgg(canvas, root)
            toolbar.update()

            return canvas
        else:
            return None

    # 'spectral', 'Paired'
    def get_n_color_colorbar(self,n):
        cmap = cm.get_cmap('Spectral', n)
        return cmap(np.arange(n))

    def rgb_to_hex(self,rgb):
        return '#%02x%02x%02x' % rgb[:3]
    '''
