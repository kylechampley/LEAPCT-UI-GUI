import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from leapctserver import *

try:
    import pyqtgraph as pg
    has_pg = True
except:
    has_pg = False
import matplotlib.pyplot as plt

from settings_dialog import *
from physics_dialog import *
from GeneralWarningDialog import *
from CenteredMessageDialog import *

class FileNamesPage(QWidget):

    def __init__(self, parent=None):
        super(FileNamesPage, self).__init__(parent)

        self.parent	= parent
        self.leapct = self.parent.leapct
        self.lctserver = self.parent.lctserver
        self.thePhysicsDialog = None
        
        overall_grid = QGridLayout()
        curRow = 0
        
        ######### TOP BUTTONS START #########
        button_layout = QHBoxLayout()
        load_sct_button = QPushButton("Load MetaData")
        settings_button = QPushButton("Settings")
        physics_button = QPushButton("Physics")
        load_sct_button.clicked.connect(self.load_sct_button_Clicked)
        settings_button.clicked.connect(self.settings_button_Clicked)
        physics_button.clicked.connect(self.physics_button_Clicked)
        load_sct_button.setToolTip("Load meta-data from *.sct, *.log, or *.txt files")
        #settings_button.setEnabled(False)
        settings_button.setToolTip("opens dialog for LEAPCT parameters")
        if has_physics:
            physics_button.setEnabled(True)
        else:
            physics_button.setEnabled(False)
        physics_button.setToolTip("set spectra and object model")
        button_layout.addWidget(load_sct_button)
        button_layout.addWidget(settings_button)
        button_layout.addWidget(physics_button)
        overall_grid.addLayout(button_layout, curRow, 0, 1, 3)
        curRow += 1
        ######### TOP BUTTONS END #########
        
        #path_label = QLabel("<div align='right'>path</div>")
        path_button = QPushButton("path")
        path_button.setToolTip("Set the path where the data is stored.  Click button to open file browser.")
        path_button.clicked.connect(self.browse_path_Clicked)
        self.path_edit = QLineEdit()
        
        outputDir_label = QLabel("<div align='right'>output directory:</div>")
        self.outputDir_edit = QLineEdit()
        
        overall_grid.addWidget(path_button, curRow, 0, 1, 1)
        overall_grid.addWidget(self.path_edit, curRow, 1, 1, 2)
        curRow += 1
        overall_grid.addWidget(outputDir_label, curRow, 0, 1, 1)
        overall_grid.addWidget(self.outputDir_edit, curRow, 1, 1, 2)
        curRow += 1
        
        ######### DATA TYPE START #########
        self.dataType_group = QGroupBox("Projection Data Type")
        dataType_radio_vlayout = QVBoxLayout()
        self.dataType_group.setToolTip("These radio buttons specify the state of the given radiographs which informs leap how to convert them into attenuation radiographs which is needed for reconstruction.\nNote that this button just describes the data and does not perform any manipulations.  See the \"Make Atten Rads\" function")

        # Raw, uncalibrated:
        self.raw_radio = QRadioButton("Raw Radiograph")
        self.raw_radio.setToolTip("Attenuation data is calculated by: -log((raw - dark) / (air - dark))")
        self.raw_radio.clicked.connect(self.raw_radio_Clicked)
        dataType_radio_vlayout.addWidget(self.raw_radio)

        # Raw, dark sub:
        self.rawDarkSubtracted_radio = QRadioButton("Raw Dark Subtracted")
        self.rawDarkSubtracted_radio.setToolTip("Attenuation data is calculated by: -log(raw / air)")
        self.rawDarkSubtracted_radio.clicked.connect(self.rawDarkSubtracted_radio_Clicked)
        dataType_radio_vlayout.addWidget(self.rawDarkSubtracted_radio)

        # Transmission Radiograph:
        self.transmissionRadiograph_radio = QRadioButton("Transmission Radiograph")
        self.transmissionRadiograph_radio.setToolTip("Attenuation data is calculated by: -log(transmission)")
        self.transmissionRadiograph_radio.clicked.connect(self.transmissionRadiograph_radio_Clicked)
        dataType_radio_vlayout.addWidget(self.transmissionRadiograph_radio)

        # Attenuation Radiograph:
        self.attenuationRadiograph_radio = QRadioButton("Attenuation Radiograph")
        self.attenuationRadiograph_radio.setToolTip("Given radiographs are in attenuation format")
        self.attenuationRadiograph_radio.clicked.connect(self.attenuationRadiograph_radio_Clicked)
        dataType_radio_vlayout.addWidget(self.attenuationRadiograph_radio)

        self.dataType_group.setLayout(dataType_radio_vlayout)
        overall_grid.addWidget(self.dataType_group, curRow, 0, 1, 2)
        ######### DATA TYPE END #########
        
        
        ######### FILE NAMES START #########
        file_grid = QGridLayout()
        
        volume_button = QPushButton("Volume Files")
        volume_button.clicked.connect(self.browse_volume_Clicked)
        volume_button.setToolTip("Set the base name of the tif sequence where the volume data is stored (if it exists).  Click button to open file browser.")
        self.volume_edit = QLineEdit()
        self.volume_edit.editingFinished.connect(self.push_volume_file)
        self.display_volume_button = QPushButton("display")
        self.display_volume_button.clicked.connect(self.display_volume_button_Clicked)
        self.display_volume_button.setToolTip("Click button to view volume data in napari")
        
        self.raw_button = QPushButton("Raw Radiograph Files")
        self.raw_button.clicked.connect(self.browse_raw_Clicked)
        self.raw_button.setToolTip("Set the base name of the tif sequence where the radiograph data is stored.  Click button to open file browser.")
        self.raw_edit = QLineEdit()
        self.raw_edit.editingFinished.connect(self.push_raw_file)
        self.display_raw_button = QPushButton("display")
        self.display_raw_button.clicked.connect(self.display_raw_button_Clicked)
        self.display_raw_button.setToolTip("Click button to view radiograph data in napari")
        
        self.air_button = QPushButton("Air Scan File")
        self.air_button.clicked.connect(self.browse_air_Clicked)
        self.air_button.setToolTip("Set the base name of the tif file where the air scan radiograph data is stored (if it exists).  Click button to open file browser.")
        self.air_edit = QLineEdit()
        self.air_edit.editingFinished.connect(self.push_air_file)
        self.display_air_button = QPushButton("display")
        self.display_air_button.clicked.connect(self.display_air_button_Clicked)
        self.display_air_button.setToolTip("Click button to view air scan data")
        
        self.dark_button = QPushButton("Dark Scan File")
        self.dark_button.clicked.connect(self.browse_dark_Clicked)
        self.dark_button.setToolTip("Set the base name of the tif file where the dark scan radiograph data is stored (if it exists).  Click button to open file browser.")
        self.dark_edit = QLineEdit()
        self.dark_edit.editingFinished.connect(self.push_dark_file)
        self.display_dark_button = QPushButton("display")
        self.display_dark_button.clicked.connect(self.display_dark_button_Clicked)
        self.display_dark_button.setToolTip("Click button to view dark scan data")
        
        file_grid.addWidget(self.dark_button, 0, 0)
        file_grid.addWidget(self.dark_edit, 0, 1)
        file_grid.addWidget(self.display_dark_button, 0, 2)
        
        file_grid.addWidget(self.air_button, 1, 0)
        file_grid.addWidget(self.air_edit, 1, 1)
        file_grid.addWidget(self.display_air_button, 1, 2)
        
        file_grid.addWidget(self.raw_button, 2, 0)
        file_grid.addWidget(self.raw_edit, 2, 1)
        file_grid.addWidget(self.display_raw_button, 2, 2)
        
        file_grid.addWidget(volume_button, 3, 0)
        file_grid.addWidget(self.volume_edit, 3, 1)
        file_grid.addWidget(self.display_volume_button, 3, 2)
        
        overall_grid.addLayout(file_grid, curRow, 2)
        ######### FILE NAMES END #########
        
        self.setLayout(overall_grid)
        
        self.refresh()
    
    def push_volume_file(self):
        self.lctserver.reconstruction_file = self.volume_edit.text()
    
    def push_raw_file(self):
        if self.transmissionRadiograph_radio.isChecked() or self.attenuationRadiograph_radio.isChecked():
            self.lctserver.projection_file = self.raw_edit.text()
        else:
            self.lctserver.raw_scan_file = self.raw_edit.text()
        if len(self.raw_edit.text()) > 0:
            self.raw_button.setStyleSheet('color: black')
        else:
            self.raw_button.setStyleSheet('color: red')
        
    def push_air_file(self):
        self.lctserver.air_scan_file = self.air_edit.text()
        if len(self.air_edit.text()) > 0:
            self.air_button.setStyleSheet('color: black')
        else:
            self.air_button.setStyleSheet('color: red')
        
    def push_dark_file(self):
        self.lctserver.dark_scan_file = self.dark_edit.text()
        if len(self.dark_edit.text()) > 0:
            self.dark_button.setStyleSheet('color: black')
        else:
            self.dark_button.setStyleSheet('color: red')
    
    def display_volume_button_Clicked(self):
        if self.lctserver.f is None:
            self.lctserver.load_volume_into_memory()
        if self.lctserver.f is not None:
            self.leapct.display(self.lctserver.f)
    
    def display_raw_button_Clicked(self):
        if self.lctserver.g is None:
            self.lctserver.load_projections_into_memory()
        if self.lctserver.g is not None:
            self.leapct.display(self.lctserver.g)
            
    def display_air_button_Clicked(self):
        air_scan = self.lctserver.load_air_scan_into_memory()
        if air_scan is not None and not isinstance(air_scan, float):
            if has_pg and False:
            
                pg.image(air_scan.T)
            else:
                plt.imshow(air_scan, cmap='gray', interpolation='nearest')
                plt.show()
                
    
    def display_dark_button_Clicked(self):
        dark_scan = self.lctserver.load_dark_scan_into_memory()
        if dark_scan is not None and not isinstance(dark_scan, float):
            if has_pg and False:
                pg.image(dark_scan.T)
                #pg.show()
            else:
                plt.imshow(dark_scan, cmap='gray', interpolation='nearest')
                plt.show()
    
    def refresh(self):
        self.path_edit.setText(self.lctserver.path)
        
        if self.lctserver.data_type == self.lctserver.RAW:
            self.raw_radio.setChecked(True)
            self.raw_button.setText("Raw Radiograph Files")
            self.raw_edit.setText(self.lctserver.raw_scan_file)
            self.dataType_group.setStyleSheet('color: black')
        elif self.lctserver.data_type == self.lctserver.RAW_DARK_SUBTRACTED:
            self.rawDarkSubtracted_radio.setChecked(True)
            self.raw_button.setText("Raw Radiograph Files")
            self.raw_edit.setText(self.lctserver.raw_scan_file)
            self.dataType_group.setStyleSheet('color: black')
        elif self.lctserver.data_type == self.lctserver.TRANSMISSION:
            self.transmissionRadiograph_radio.setChecked(True)
            self.raw_button.setText("Projection Files")
            self.raw_edit.setText(self.lctserver.projection_file)
            self.dataType_group.setStyleSheet('color: black')
        elif self.lctserver.data_type == self.lctserver.ATTENUATION:
            self.attenuationRadiograph_radio.setChecked(True)
            self.raw_button.setText("Projection Files")
            self.raw_edit.setText(self.lctserver.projection_file)
            self.dataType_group.setStyleSheet('color: black')
        else:
            self.dataType_group.setStyleSheet('color: red')
        
        self.outputDir_edit.setText(self.lctserver.outputDir)
        
        self.volume_edit.setText(self.lctserver.reconstruction_file)
        
        self.air_edit.setText(self.lctserver.air_scan_file)
        
        self.dark_edit.setText(self.lctserver.dark_scan_file)
        
    def pushAllParameters(self):
        pass
    
    def load_sct_button_Clicked(self):
        if self.lctserver.f is not None or self.lctserver.g is not None:
            warningDialog = GeneralWarningDialog(self.parent)
            if warningDialog.exec_():
                proceedWithOperation = True
            else:
                proceedWithOperation = False
        else:
            proceedWithOperation = True
        if proceedWithOperation == True:
            openSCTFileDialog = QFileDialog()
            openSCTFileDialog.setFileMode(QFileDialog.AnyFile)
            openSCTFileDialog.setNameFilters(["SCT Files (*.sct *log *.txt)"])

            if openSCTFileDialog.exec_():

                sctFile = openSCTFileDialog.selectedFiles()

                #self.lctserver.path = ""
                inputArg = os.path.abspath(str(sctFile[0]))
                """
                if len(self.lctserver.path) == 0:
                    if inputArg.endswith('.sct'):
                        Succeeded = self.lctserver.loadsct(inputArg)
                    elif inputArg.endswith('.log'):
                        Succeeded = self.lctserver.load_skyscan(inputArg)
                    elif inputArg.endswith('.txt'):
                        Succeeded = self.lctserver.load_parameters(inputArg)
                    else:
                        Succeeded = False
                else:
                    archdirStr = self.lctserver.path
                    if len(archdirStr) > 0:
                        if inputArg.find(archdirStr) == 0:
                            inputArg = inputArg[len(archdirStr):len(inputArg)]
                    if inputArg.endswith('.sct'):
                        Succeeded = self.lctserver.loadsct(inputArg)
                    elif inputArg.endswith('.log'):
                        Succeeded = self.lctserver.load_skyscan(inputArg)
                    elif inputArg.endswith('.txt'):
                        Succeeded = self.lctserver.load_parameters(inputArg)
                    else:
                        Succeeded = False
                """
                if inputArg.endswith('.sct'):
                    Succeeded = self.lctserver.loadsct(inputArg)
                elif inputArg.endswith('.log'):
                    Succeeded = self.lctserver.load_skyscan(inputArg)
                elif inputArg.endswith('.txt'):
                    Succeeded = self.lctserver.load_parameters(inputArg)
                else:
                    Succeeded = False

                if Succeeded == False:

                    # Issue the message box to warn the user the sct file failed to load:
                    messageDialog = CenteredMessageDialog("file error", "An error occured while trying to load the file.", self.parent)
                    messageDialog.exec_()

                else:
                    self.refresh()
                    if self.leapct.ct_geometry_defined() == True and self.leapct.ct_volume_defined() == False:
                        self.leapct.set_default_volume()
                    self.parent.refreshAllPages()
    
    def physics_button_Clicked(self):
        self.thePhysicsDialog = PhysicsDialog("LEAP-CT Physics Models", self)
        self.thePhysicsDialog.show()
    
    def settings_button_Clicked(self):
        #self.leapct.print_parameters()
        theSettingsDialog = SettingsDialog("LEAP-CT Settings", self)
        if theSettingsDialog.exec_():
            pass
    
    def raw_radio_Clicked(self):
        self.lctserver.data_type = self.lctserver.RAW
        self.raw_button.setText("Raw Radiograph Files")
        self.raw_edit.setText(self.lctserver.raw_scan_file)
        self.dataType_group.setStyleSheet('color: black')
        if len(self.dark_edit.text()) > 0:
            self.dark_button.setStyleSheet('color: black')
        else:
            self.dark_button.setStyleSheet('color: red')
        if len(self.air_edit.text()) > 0:
            self.air_button.setStyleSheet('color: black')
        else:
            self.air_button.setStyleSheet('color: red')
        if len(self.raw_edit.text()) > 0:
            self.raw_button.setStyleSheet('color: black')
        else:
            self.raw_button.setStyleSheet('color: red')
        
        
    def rawDarkSubtracted_radio_Clicked(self):
        self.lctserver.data_type = self.lctserver.RAW_DARK_SUBTRACTED
        self.raw_button.setText("Raw Radiograph Files")
        self.raw_edit.setText(self.lctserver.raw_scan_file)
        self.dataType_group.setStyleSheet('color: black')
        self.dark_button.setStyleSheet('color: black')
        if len(self.air_edit.text()) > 0:
            self.air_button.setStyleSheet('color: black')
        else:
            self.air_button.setStyleSheet('color: red')
        if len(self.raw_edit.text()) > 0:
            self.raw_button.setStyleSheet('color: black')
        else:
            self.raw_button.setStyleSheet('color: red')
        
    def transmissionRadiograph_radio_Clicked(self):
        self.lctserver.data_type = self.lctserver.TRANSMISSION
        self.raw_button.setText("Projection Files")
        self.raw_edit.setText(self.lctserver.projection_file)
        self.dataType_group.setStyleSheet('color: black')
        self.dark_button.setStyleSheet('color: black')
        self.air_button.setStyleSheet('color: black')
        if len(self.raw_edit.text()) > 0:
            self.raw_button.setStyleSheet('color: black')
        else:
            self.raw_button.setStyleSheet('color: red')
        
    def attenuationRadiograph_radio_Clicked(self):
        self.lctserver.data_type = self.lctserver.ATTENUATION
        self.raw_button.setText("Projection Files")
        self.raw_edit.setText(self.lctserver.projection_file)
        self.dataType_group.setStyleSheet('color: black')
        self.dark_button.setStyleSheet('color: black')
        self.air_button.setStyleSheet('color: black')
        if len(self.raw_edit.text()) > 0:
            self.raw_button.setStyleSheet('color: black')
        else:
            self.raw_button.setStyleSheet('color: red')
        
    def browse_path_Clicked(self):
        openArchdirDialog = QFileDialog()
        openArchdirDialog.setFileMode(QFileDialog.DirectoryOnly)
        if openArchdirDialog.exec_():
            archdirFolder = openArchdirDialog.selectedFiles()
            archdirValue = str(archdirFolder[0])
            if os.path.exists(archdirValue) == False:
                if len(archdirValue) > 8 and archdirValue[len(archdirValue)-8:len(archdirValue)] == "untitled":
                    archdirValue = archdirValue[0:len(archdirValue)-8]
            self.path_edit.setText(os.path.abspath(archdirValue))
            self.lctserver.path = os.path.abspath(archdirValue)
        
    def browse_raw_Clicked(self):
        inputArg = self.openImageFileAndStripPath()
        if len(inputArg) > 0:
            
            baseName, fileExt = os.path.splitext(os.path.basename(inputArg))
            baseName = baseName.rstrip("0123456789").rstrip("_")
            inputArg = baseName + fileExt
            self.raw_edit.setText(inputArg)
            self.push_raw_file()
        
    def browse_volume_Clicked(self):
        inputArg = self.openImageFileAndStripPath()
        if len(inputArg) > 0:
            self.volume_edit.setText(inputArg)
            self.push_volume_file()
        
    def browse_air_Clicked(self):
        inputArg = self.openImageFileAndStripPath()
        if len(inputArg) > 0:
            self.air_edit.setText(inputArg)
            self.push_air_file()
        
    def browse_dark_Clicked(self):
        inputArg = self.openImageFileAndStripPath()
        if len(inputArg) > 0:
            self.dark_edit.setText(inputArg)
            self.push_dark_file()
            
    def openImageFileAndStripPath(self):
        pathStr = self.parent.lctserver.path
        pathStr = os.path.join(pathStr, '')
        
        loadFileDialog = QFileDialog()
        loadFileDialog.setFileMode(QFileDialog.AnyFile)
        loadFileDialog.setNameFilters(["Image Files (*.tif *.tiff *.sdt)"])
        if loadFileDialog.exec_():
            imageFile = loadFileDialog.selectedFiles()
            inputArg = os.path.abspath(str(imageFile[0]))
            if len(inputArg) > 0:
                if len(pathStr) > 0:
                    if inputArg.find(pathStr) == 0:
                        inputArg = inputArg[len(pathStr):len(inputArg)]
            return inputArg
        else:
            return []