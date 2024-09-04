from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

from ct_algorithm_parameter_pages import *

class CTalgorithmControlsPage(QWidget):
    def __init__(self, parent=None):
        super(CTalgorithmControlsPage, self).__init__(parent)

        self.parent    = parent
        self.lctserver = self.parent.lctserver
        self.leapct = self.parent.leapct

        # Instantiate the overall grid layout:
        overall_layout = QGridLayout()
        
        #self.algorithmSequenceList = CTalgorithmSeqeunceControlsPage(self)
        self.algorithmSequenceList = QListWidget(self)
        self.algorithmSequenceList.currentItemChanged.connect(self.onCurrentItemChanged)
        self.algorithmSequencePages = []
        
        button_layout = QHBoxLayout()
        self.algorithm_list_combo = QComboBox()
        self.algorithm_list_combo.addItem("Select...")
        self.algorithm_list_combo.addItem("Make Attenuation Radiographs")
        self.algorithm_list_combo.addItem("Crop Projections")
        self.algorithm_list_combo.addItem("Outlier Correction")
        self.algorithm_list_combo.addItem("Find centerCol")
        self.algorithm_list_combo.addItem("Detector Tilt")
        self.algorithm_list_combo.addItem("Ring Removal")
        self.algorithm_list_combo.addItem("Beam Hardening Correction")
        self.algorithm_list_combo.addItem("Parameter Sweep")
        self.algorithm_list_combo.addItem("Save Projection Data")
        self.algorithm_list_combo.addItem("FBP")
        self.algorithm_list_combo.addItem("Median Filter")
        self.algorithm_list_combo.addItem("TV Denoising")
        self.add_algorithm_button = QPushButton("Add")
        self.remove_algorithm_button = QPushButton("Remove")
        button_layout.addWidget(self.algorithm_list_combo)
        button_layout.addWidget(self.add_algorithm_button)
        #button_layout.addStretch(2)
        button_layout.addWidget(self.remove_algorithm_button)
        
        #self.algorithm_list_combo.insertSeparator(1)
        #self.algorithm_list_combo.insertSeparator(7)
        
        self.add_algorithm_button.clicked.connect(self.add_algorithm_button_Clicked)
        self.remove_algorithm_button.clicked.connect(self.remove_algorithm_button_Clicked)
        
        overall_layout.addWidget(self.algorithmSequenceList, 0, 0)
        overall_layout.addLayout(button_layout, 1, 0)
        
        #self.algorithmParameterControls = CTalgorithmStack(self)
        self.algorithmStack = QStackedWidget()
        overall_layout.addWidget(self.algorithmStack, 0, 1)
        
        #overall_layout.addWidget(self.algorithmParameterControls, 0, 1)
        
        self.runningPreviousAlgorithms = False
        
        self.setLayout(overall_layout)
        
    def refresh(self):
        if len(self.algorithmSequencePages) == 0 and self.lctserver.data_type != self.lctserver.ATTENUATION:
            if self.leapct.ct_geometry_defined():
                self.algorithm_list_combo.setCurrentIndex(1)
                self.add_algorithm_button_Clicked()
                self.algorithm_list_combo.setCurrentIndex(3)
                self.add_algorithm_button_Clicked()
                self.algorithm_list_combo.setCurrentIndex(4)
                self.add_algorithm_button_Clicked()
                self.algorithm_list_combo.setCurrentIndex(6)
                self.add_algorithm_button_Clicked()
                
                self.algorithm_list_combo.setCurrentIndex(7)
                self.add_algorithm_button_Clicked()
                
                if self.leapct.ct_volume_defined():
                    self.algorithm_list_combo.setCurrentIndex(10)
                    self.add_algorithm_button_Clicked()
    
    def runPreviousAlgorithms(self):
        retVal = True
        self.runningPreviousAlgorithms = True
        current_index = self.algorithmSequenceList.currentRow()
        for n in range(current_index):
            self.algorithmSequencePages[n].execute_button_Clicked()
            if self.algorithmSequencePages[n].computeState == 0:
                retVal = False
                break
                
        self.runningPreviousAlgorithms = False
        return retVal
    
    def onCurrentItemChanged(self):
        ind = self.algorithmSequenceList.currentRow()
        self.algorithmStack.setCurrentIndex(ind)
    
    def add_algorithm_button_Clicked(self):
        self.add_algorithm(self.algorithm_list_combo.currentIndex())
    
    def add_algorithm(self, algIndex):
        ind = self.algorithmSequenceList.currentRow()
        if len(self.algorithmSequencePages) == 0 or ind == len(self.algorithmSequencePages)-1:
            ind = -1
        if ind >= 0:
            if self.check_any_computed_after(ind):
                ind = -1
        #ind = -1 # uncomment this to not allow insertions in the middle of the list
        if algIndex > 0:
            #self.algorithmSequenceList.addItem(self.algorithm_list_combo.currentText())
            if ind >= 0:
                self.algorithmSequenceList.insertItem(ind, self.algorithm_list_combo.currentText())
            else:
                self.algorithmSequenceList.addItem(self.algorithm_list_combo.currentText())
            
            if algIndex == 1:
                newAlgorithmPage = MakeAttenuationRadiographsParametersPage(self)
            elif algIndex == 2:
                newAlgorithmPage = CropProjectionsParametersPage(self)
            elif algIndex == 3:
                newAlgorithmPage = OutlierCorrectionParametersPage(self)
            elif algIndex == 4:
                newAlgorithmPage = FindCenterColParametersPage(self)
            elif algIndex == 5:
                newAlgorithmPage = EstimateDetectorTiltParametersPage(self)
            elif algIndex == 6:
                newAlgorithmPage = RingRemovalParametersPage(self)
            elif algIndex == 7:
                newAlgorithmPage = BeamHardeningCorrectionParametersPage(self)
            elif algIndex == 8:
                newAlgorithmPage = ParameterSweepParametersPage(self)
            elif algIndex == 9:
                newAlgorithmPage = SaveProjectionDataParametersPage(self)
            elif algIndex == 10:
                newAlgorithmPage = FBPParametersPage(self)
            elif algIndex == 11:
                newAlgorithmPage = MedianFilterParametersPage(self)
            elif algIndex == 12:
                newAlgorithmPage = TVdenoisingParametersPage(self)
                
            #self.algorithmStack.addWidget(newAlgorithmPage)
            #self.algorithmSequencePages.append(newAlgorithmPage)
            #self.algorithmSequenceList.setCurrentRow(len(self.algorithmSequencePages)-1)
            if ind >= 0:
                self.algorithmStack.insertWidget(ind, newAlgorithmPage)
                self.algorithmSequencePages.insert(ind, newAlgorithmPage)
                self.algorithmSequenceList.setCurrentRow(ind)
                #self.algorithmSequenceList.setCurrentRow(len(self.algorithmSequencePages)-1)
            else:
                self.algorithmStack.addWidget(newAlgorithmPage)
                self.algorithmSequencePages.append(newAlgorithmPage)
                self.algorithmSequenceList.setCurrentRow(len(self.algorithmSequencePages)-1)
            
    def check_any_computed_after(self, current_index):
        for n in range(current_index, len(self.algorithmSequencePages)):
            if self.algorithmSequencePages[n].computeState == 1:
                return True
        return False
    
    
    def remove_algorithm_button_Clicked(self):
        ind = self.algorithmSequenceList.currentRow()
        if self.algorithmSequencePages[ind].computeState == 0:
            self.algorithmStack.removeWidget(self.algorithmStack.currentWidget())
            self.algorithmSequenceList.takeItem(ind)
            self.algorithmSequencePages.pop(ind)
            #self.algorithmStack.removeWidget(self.algorithmStack.currentWidget())
            self.algorithmStack.setCurrentIndex(ind)
            #self.algorithmSequenceList.removeCurrentAlgorithm()
    
    #def setAlgorithmRemovalOption(self, selection):
    #    self.remove_algorithm_button.setEnabled(selection)
    