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
        
        self.algorithmSequenceList = QListWidget(self)
        self.algorithmSequenceList.currentItemChanged.connect(self.onCurrentItemChanged)
        self.algorithmSequencePages = []
        
        button_layout = QHBoxLayout()
        self.algorithm_list_combo = QComboBox()
        self.algorithm_list_combo.addItem("Select...")
        all_algorithms = ['Make Attenuation Radiographs',
                          'Crop Projections',
                          'Outlier Correction',
                          'Find centerCol',
                          'Detector Tilt',
                          'Ring Removal',
                          'Beam Hardening Correction',
                          'Parameter Sweep',
                          'Save Projection Data',
                          'Tight Volume',
                          'FBP',
                          'Median Filter',
                          'TV Denoising',
                          'Save Volume Data']
        self.algorithm_list_combo.addItems(all_algorithms)
        """                  
        self.algorithm_list_combo.addItem("Make Attenuation Radiographs")
        self.algorithm_list_combo.addItem("Crop Projections")
        self.algorithm_list_combo.addItem("Outlier Correction")
        self.algorithm_list_combo.addItem("Find centerCol")
        self.algorithm_list_combo.addItem("Detector Tilt")
        self.algorithm_list_combo.addItem("Ring Removal")
        self.algorithm_list_combo.addItem("Beam Hardening Correction")
        self.algorithm_list_combo.addItem("Parameter Sweep")
        self.algorithm_list_combo.addItem("Save Projection Data")
        self.algorithm_list_combo.addItem("Tight Volume")
        self.algorithm_list_combo.addItem("FBP")
        self.algorithm_list_combo.addItem("Median Filter")
        self.algorithm_list_combo.addItem("TV Denoising")
        self.algorithm_list_combo.addItem("Save Volume Data")
        """
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
                if self.lctserver.default_algorithms is not None and len(self.lctserver.default_algorithms) > 0:
                    for n in range(len(self.lctserver.default_algorithms)):
                        self.add_algorithm_by_text(self.lctserver.default_algorithms[n])
                else:
                    self.add_algorithm_by_text("Make Attenuation Radiographs")
                    self.add_algorithm_by_text("Outlier Correction")
                    self.add_algorithm_by_text("Find centerCol")
                    self.add_algorithm_by_text("Ring Removal")
                    self.add_algorithm_by_text("Beam Hardening Correction")
                    
                    if self.leapct.ct_volume_defined():
                        self.add_algorithm_by_text("FBP")
    
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
        algText = self.algorithm_list_combo.itemText(algIndex)
        self.add_algorithm_by_text(algText)

    def add_algorithm_by_text(self, algText):
        
        if algText == "Make Attenuation Radiographs":
            newAlgorithmPage = MakeAttenuationRadiographsParametersPage(self)
        elif algText == "Crop Projections":
            newAlgorithmPage = CropProjectionsParametersPage(self)
        elif algText == "Outlier Correction":
            newAlgorithmPage = OutlierCorrectionParametersPage(self)
        elif algText == "Find centerCol":
            newAlgorithmPage = FindCenterColParametersPage(self)
        elif algText == "Detector Tilt":
            newAlgorithmPage = EstimateDetectorTiltParametersPage(self)
        elif algText == "Ring Removal":
            newAlgorithmPage = RingRemovalParametersPage(self)
        elif algText == "Beam Hardening Correction":
            newAlgorithmPage = BeamHardeningCorrectionParametersPage(self)
        elif algText == "Parameter Sweep":
            newAlgorithmPage = ParameterSweepParametersPage(self)
        elif algText == "Save Projection Data":
            newAlgorithmPage = SaveProjectionDataParametersPage(self)
        elif algText == "Tight Volume":
            newAlgorithmPage = TightVolumeParametersPage(self)
        elif algText == "FBP":
            newAlgorithmPage = FBPParametersPage(self)
        elif algText == "Median Filter":
            newAlgorithmPage = MedianFilterParametersPage(self)
        elif algText == "TV Denoising":
            newAlgorithmPage = TVdenoisingParametersPage(self)
        elif algText == "Save Volume Data":
            newAlgorithmPage = SaveVolumeDataParametersPage(self)
        else:
            return
        
        ind = self.algorithmSequenceList.currentRow()
        if len(self.algorithmSequencePages) == 0 or ind == len(self.algorithmSequencePages)-1:
            ind = -1
        if ind >= 0:
            if self.check_any_computed_after(ind):
                ind = -1
        
        if ind >= 0:
            ind += 1
            self.algorithmSequenceList.insertItem(ind, algText)
        else:
            self.algorithmSequenceList.addItem(algText)
            
        if ind >= 0:
            self.algorithmStack.insertWidget(ind, newAlgorithmPage)
            self.algorithmSequencePages.insert(ind, newAlgorithmPage)
            self.algorithmSequenceList.setCurrentRow(ind)
            #self.algorithmSequenceList.setCurrentRow(len(self.algorithmSequencePages)-1)
        else:
            self.algorithmStack.addWidget(newAlgorithmPage)
            self.algorithmSequencePages.append(newAlgorithmPage)
            self.algorithmSequenceList.setCurrentRow(len(self.algorithmSequencePages)-1)
        
    """
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
                ind += 1
                self.algorithmSequenceList.insertItem(ind, self.algorithm_list_combo.currentText())
            else:
                self.algorithmSequenceList.addItem(self.algorithm_list_combo.currentText())
            
            algText = self.algorithm_list_combo.itemText(algIndex)

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
                newAlgorithmPage = TightVolumeParametersPage(self)
            elif algIndex == 11:
                newAlgorithmPage = FBPParametersPage(self)
            elif algIndex == 12:
                newAlgorithmPage = MedianFilterParametersPage(self)
            elif algIndex == 13:
                newAlgorithmPage = TVdenoisingParametersPage(self)
            elif algIndex == 14:
                newAlgorithmPage = SaveVolumeDataParametersPage(self)
                
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
    """
            
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
    