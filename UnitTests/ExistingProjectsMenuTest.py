import sys,os,unittest,time
sys.path.append(os.path.join(".","cytostream"))
sys.path.append(os.path.join(".","cytostream","MyWidgets"))
from ExistingProjectsMenu import ExistingProjectsMenu
from BuildingBlocks import Quitter
import numpy as np
from matplotlib import pyplot
import Tkinter as tk

## test class for the ImageButtonMagic 
class ExistingProjectsMenuTest(unittest.TestCase):

    def testConstruction(self):
        print 'setting up...'
        existingProjects = self._get_project_names()

        #self.imgDir = os.path.join(".","tests","data","ibmtest")
        #self._create_sample_images()
        self.root = tk.Tk()
        self.existingProjectsMenu = ExistingProjectsMenu(self.root,existingProjects,bg='#333333')#command=view.open_existing_project,loadBtnFn=view.open_existing_project 
        self.existingProjectsMenu.pack()
        self.quit = tk.Button(self.root,text="Quit",command=lambda: self.root.quit())
        self.quit.pack()
  
        ## sleep a bit then kill widget
        self.root.mainloop()
        self.root.destroy()

    def _get_project_names(self):
        projectNamesList = []

        for dirName in os.listdir(os.path.join(".","cytostream","projects")):
            if os.path.isdir(os.path.join(".","cytostream","projects",dirName)) == True:
                projectNamesList.append(dirName)

        return projectNamesList


    
### Run the tests 
if __name__ == '__main__':
    unittest.main()
