import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from GeneralWarningDialog import *
from CenteredMessageDialog import *

class CTgeometryPage(QWidget):

    def __init__(self, parent=None):
        super(CTgeometryPage, self).__init__(parent)

        self.parent	= parent
        self.leapct = self.parent.leapct
        self.lctserver = self.parent.lctserver
        
        overall_grid = QGridLayout()
        curRow = 0
        
        ######### GEOMETRY FILE START #########
        geometry_file_button = QPushButton("Geometry File")
        geometry_file_button.setToolTip("This button allows the user to specify a LEAP-CT geometry file (*.txt) to load the geometry parameters.\nNote that geometry files are the only GUI method to specify modular-beam geometries and geometries with non-equi-spaced projection angles.\nGeometry files can be generated with the leapct.save_parameters(...) function.")
        geometry_file_button.clicked.connect(self.browse_geometry_file_Clicked)
        self.geometry_file_edit = QLineEdit()
        overall_grid.addWidget(geometry_file_button, 0, 0, 1, 1)
        overall_grid.addWidget(self.geometry_file_edit, 0, 1, 1, 1)
        ######### GEOMETRY FILE END #########
        
        ######### GEOMETRY TYPE START #########
        # cone flat, cone curved, modular-beam, cone-parallel, parallel, fan
        geometryType_group = QGroupBox("System Geometry Type")
        geometryType_radio_grid = QGridLayout()

        # Cone Flat
        self.cone_flat_radio = QRadioButton("Cone-Beam Flat")
        #self.cone_flat_radio.setToolTip(str())
        self.cone_flat_radio.clicked.connect(self.cone_flat_radio_Clicked)
        geometryType_radio_grid.addWidget(self.cone_flat_radio, 0, 0)

        # Cone Curved
        self.cone_curved_radio = QRadioButton("Cone-Beam Curved")
        #self.cone_curved_radio.setToolTip(str())
        self.cone_curved_radio.clicked.connect(self.cone_curved_radio_Clicked)
        geometryType_radio_grid.addWidget(self.cone_curved_radio, 1, 0)
        
        # Modular
        self.modular_radio = QRadioButton("Modular-Beam")
        #self.modular_radio.setToolTip(str())
        self.modular_radio.clicked.connect(self.modular_radio_Clicked)
        geometryType_radio_grid.addWidget(self.modular_radio, 0, 1)
        
        # Cone Curved
        self.cone_parallel_radio = QRadioButton("Cone-Parallel")
        #self.cone_parallel_radio.setToolTip(str())
        self.cone_parallel_radio.clicked.connect(self.cone_parallel_radio_Clicked)
        geometryType_radio_grid.addWidget(self.cone_parallel_radio, 1, 1)

        # Fan
        self.fan_radio = QRadioButton("Fan-Beam")
        #self.fan_radio.setToolTip(str())
        self.fan_radio.clicked.connect(self.fan_radio_Clicked)
        geometryType_radio_grid.addWidget(self.fan_radio, 0, 2)

        # Parallel
        self.parallel_radio = QRadioButton("Parallel-Beam")
        #self.parallel_radio.setToolTip(str())
        self.parallel_radio.clicked.connect(self.parallel_radio_Clicked)
        geometryType_radio_grid.addWidget(self.parallel_radio, 1, 2)
        
        geometryType_group.setLayout(geometryType_radio_grid)
        overall_grid.addWidget(geometryType_group, 1, 0, 1, 4)
        ######### GEOMETRY TYPE END #########
        
        ######### SYSTEM SPECIFICATIONS START #########
        systemSpecifications_group = QGroupBox("System Specifications")
        systemSpecifications_grid = QGridLayout()
        
        sod_label = QLabel("<div align='right'>sod (mm)</div>")
        self.sod_edit = QLineEdit()
        sod_label.setToolTip("source to object distance, measured in mm; this can also be viewed as the source to center of rotation distance")
        systemSpecifications_grid.addWidget(sod_label, 0, 0)
        systemSpecifications_grid.addWidget(self.sod_edit, 0, 1)
        
        numRows_label = QLabel("<div align='right'>num rows</div>")
        self.numRows_edit = QLineEdit()
        numRows_label.setToolTip("number of rows in the x-ray detector")
        systemSpecifications_grid.addWidget(numRows_label, 1, 0)
        systemSpecifications_grid.addWidget(self.numRows_edit, 1, 1)
        
        pixelHeight_label = QLabel("<div align='right'>pixel height (mm)</div>")
        self.pixelHeight_edit = QLineEdit()
        pixelHeight_label.setToolTip("the detector pixel pitch (i.e., pixel size) between detector rows, measured in mm")
        systemSpecifications_grid.addWidget(pixelHeight_label, 2, 0)
        systemSpecifications_grid.addWidget(self.pixelHeight_edit, 2, 1)
        
        centerRow_label = QLabel("<div align='right'>center row</div>")
        self.centerRow_edit = QLineEdit()
        centerRow_label.setToolTip("the detector pixel row index for the ray that passes from the source, through the origin, and hits the detector")
        systemSpecifications_grid.addWidget(centerRow_label, 3, 0)
        systemSpecifications_grid.addWidget(self.centerRow_edit, 3, 1)
        
        tau_label = QLabel("<div align='right'>tau (mm)</div>")
        self.tau_edit = QLineEdit()
        tau_label.setToolTip("center of rotation offset, measured in mm")
        systemSpecifications_grid.addWidget(tau_label, 4, 0)
        systemSpecifications_grid.addWidget(self.tau_edit, 4, 1)
        
        sdd_label = QLabel("<div align='right'>sdd (mm)</div>")
        self.sdd_edit = QLineEdit()
        sdd_label.setToolTip("source to detector distance, measured in mm")
        systemSpecifications_grid.addWidget(sdd_label, 0, 2)
        systemSpecifications_grid.addWidget(self.sdd_edit, 0, 3)
        
        numCols_label = QLabel("<div align='right'>num columns</div>")
        self.numCols_edit = QLineEdit()
        numCols_label.setToolTip("number of columns in the x-ray detector")
        systemSpecifications_grid.addWidget(numCols_label, 1, 2)
        systemSpecifications_grid.addWidget(self.numCols_edit, 1, 3)
        
        pixelWidth_label = QLabel("<div align='right'>pixel width (mm)</div>")
        self.pixelWidth_edit = QLineEdit()
        pixelWidth_label.setToolTip("the detector pixel pitch (i.e., pixel size) between detector columns, measured in mm")
        systemSpecifications_grid.addWidget(pixelWidth_label, 2, 2)
        systemSpecifications_grid.addWidget(self.pixelWidth_edit, 2, 3)
        
        centerCol_label = QLabel("<div align='right'>center column</div>")
        self.centerCol_edit = QLineEdit()
        centerCol_label.setToolTip("the detector pixel column index for the ray that passes from the source, through the origin, and hits the detector")
        systemSpecifications_grid.addWidget(centerCol_label, 3, 2)
        systemSpecifications_grid.addWidget(self.centerCol_edit, 3, 3)
        
        helicalPitch_label = QLabel("<div align='right'>helical pitch (mm/rad)</div>")
        self.helicalPitch_edit = QLineEdit()
        helicalPitch_label.setToolTip("the helical pitch (mm/radians)")
        systemSpecifications_grid.addWidget(helicalPitch_label, 4, 2)
        systemSpecifications_grid.addWidget(self.helicalPitch_edit, 4, 3)
        
        # Angles
        self.equispaced_angles_check = QCheckBox("equi-spaced angles")
        self.equispaced_angles_check.setToolTip("if the projection angles are non-equi-spaced, you must set them with a geometry file")
        systemSpecifications_grid.addWidget(self.equispaced_angles_check, 0, 4, 1, 2)
        self.equispaced_angles_check.setChecked(True)
        self.equispaced_angles_check.clicked.connect(self.equispaced_angles_check_Clicked)
        
        numAngles_label = QLabel("<div align='right'>num angles</div>")
        self.numAngles_edit = QLineEdit()
        numAngles_label.setToolTip("number of projection angles")
        systemSpecifications_grid.addWidget(numAngles_label, 1, 4)
        systemSpecifications_grid.addWidget(self.numAngles_edit, 1, 5)
        
        initial_angle_label = QLabel("<div align='right'>initial angle (deg)</div>")
        self.initial_angle_edit = QLineEdit()
        initial_angle_label.setToolTip("the angle of the first projection (in degrees)")
        systemSpecifications_grid.addWidget(initial_angle_label, 2, 4)
        systemSpecifications_grid.addWidget(self.initial_angle_edit, 2, 5)
        
        angular_range_label = QLabel("<div align='right'>angular range (deg)</div>")
        self.angular_range_edit = QLineEdit()
        angular_range_label.setToolTip("the angular range of all projections (degrees), i.e., numAngles * angularStep; negative numbers model a reverse direction rotation")
        systemSpecifications_grid.addWidget(angular_range_label, 3, 4)
        systemSpecifications_grid.addWidget(self.angular_range_edit, 3, 5)
        
        #self.rotation_direction_button = QPushButton("Counter Clockwise Rotation")
        #systemSpecifications_grid.addWidget(self.rotation_direction_button, 4, 4, 1, 2)
        
        systemSpecifications_group.setLayout(systemSpecifications_grid)
        overall_grid.addWidget(systemSpecifications_group, 2, 0, 1, 4)
        ######### SYSTEM SPECIFICATIONS END #########
        
        ######### SCAN TYPE START #########
        scan_type_layout = QHBoxLayout()
        self.offsetScan_check = QCheckBox("offset scan")
        self.truncatedScan_check = QCheckBox("truncated scan")
        self.offsetScan_check.clicked.connect(self.offsetScan_check_Clicked)
        self.truncatedScan_check.clicked.connect(self.truncatedScan_check_Clicked)
        scan_type_layout.addWidget(self.offsetScan_check)
        scan_type_layout.addWidget(self.truncatedScan_check)
        overall_grid.addLayout(scan_type_layout, 3, 0, 1, 1)
        ######### SCAN TYPE END #########
        
        self.sod_edit.editingFinished.connect(self.push_sod)
        self.numRows_edit.editingFinished.connect(self.push_numRows)
        self.pixelHeight_edit.editingFinished.connect(self.push_pixelHeight)
        self.centerRow_edit.editingFinished.connect(self.push_centerRow)
        self.tau_edit.editingFinished.connect(self.push_tau)
        self.sdd_edit.editingFinished.connect(self.push_sdd)
        self.numCols_edit.editingFinished.connect(self.push_numCols)
        self.pixelWidth_edit.editingFinished.connect(self.push_pixelWidth)
        self.centerCol_edit.editingFinished.connect(self.push_centerCol)
        self.helicalPitch_edit.editingFinished.connect(self.push_helicalPitch)
        self.numAngles_edit.editingFinished.connect(self.push_numAngles)
        self.angular_range_edit.editingFinished.connect(self.push_angularRange)
        
        self.setLayout(overall_grid)
    
    def refresh(self):
    
        geomTxt = self.leapct.get_geometry()
        detType = self.leapct.get_detectorType()
        if geomTxt == 'CONE':
            if detType == 'FLAT':
                self.cone_flat_radio.setChecked(True)
            else:
                self.cone_curved_radio.setChecked(True)
        elif geomTxt == 'CONE-PARALLEL':
            self.cone_parallel_radio.setChecked(True)
        elif geomTxt == 'MODULAR':
            self.modular_radio.setChecked(True)
        elif geomTxt == 'FAN':
            self.fan_radio.setChecked(True)
        elif geomTxt == 'PARALLEL':
            self.parallel_radio.setChecked(True)
    
        self.sod_edit.setText(str(self.leapct.get_sod()))
        self.numRows_edit.setText(str(self.leapct.get_numRows()))
        self.pixelHeight_edit.setText(str(self.leapct.get_pixelHeight()))
        self.centerRow_edit.setText(str(self.leapct.get_centerRow()))
        self.tau_edit.setText(str(self.leapct.get_tau()))
        self.sdd_edit.setText(str(self.leapct.get_sdd()))
        self.numCols_edit.setText(str(self.leapct.get_numCols()))
        self.pixelWidth_edit.setText(str(self.leapct.get_pixelWidth()))
        self.centerCol_edit.setText(str(self.leapct.get_centerCol()))
        self.helicalPitch_edit.setText(str(self.leapct.get_helicalPitch()))
        
        if self.leapct.angles_are_equispaced() == True:
            self.equispaced_angles_check.setChecked(True)
            if self.leapct.angles_are_defined() and self.leapct.get_geometry() != 'MODULAR':
                initial_angle = self.leapct.get_angles()[0]
                if np.abs(initial_angle) < 1.0e-5:
                    self.initial_angle_edit.setText(str(0.0))
                else:
                    self.initial_angle_edit.setText(str(self.leapct.get_angles()[0]))
                self.angular_range_edit.setText(str(self.leapct.get_angularRange()))
        else:
            self.equispaced_angles_check.setChecked(False)
        self.numAngles_edit.setText(str(self.leapct.get_numAngles()))
        self.equispaced_angles_check_Clicked()
        
        #self.offsetScan_check.setChecked(self.get_offsetScan())
        #self.truncatedScan_check.setChecked(self.get_truncatedScan())
        
    def pushAllParameters(self):
        pass
    
    def offsetScan_check_Clicked(self):
        self.leapct.set_offsetScan(self.offsetScan_check.isChecked())
        
    def truncatedScan_check_Clicked(self):
        self.leapct.set_truncatedScan(self.truncatedScan_check.isChecked())

    def equispaced_angles_check_Clicked(self):
        if self.equispaced_angles_check.isChecked() == True:
            self.numAngles_edit.setEnabled(True)
            self.initial_angle_edit.setEnabled(True)
            self.angular_range_edit.setEnabled(True)
        else:
            self.numAngles_edit.setEnabled(False)
            self.initial_angle_edit.setEnabled(False)
            self.angular_range_edit.setEnabled(False)
    
    def browse_geometry_file_Clicked(self):
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
            openSCTFileDialog.setNameFilters(["Geometry Files (*.txt)"])

            if openSCTFileDialog.exec_():

                sctFile = openSCTFileDialog.selectedFiles()

                inputArg = os.path.abspath(str(sctFile[0]))

                if inputArg.endswith('.txt'):
                    Succeeded = self.lctserver.load_geometry_file(inputArg)
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
    
    def push_numAngles(self):
        if len(self.numAngles_edit.text()) == 0:
            self.leapct.set_numAngles(0)
        else:
            try:
                x = int(self.numAngles_edit.text())
                self.leapct.set_numAngles(x)
            except:
                self.numAngles_edit.setText("")
                self.leapct.set_numAngles(0)
    
    def push_angularRange(self):
        numAngles = self.leapct.get_numAngles()
        if len(self.angular_range_edit.text()) == 0:
            #self.leapct.set_angularRange(0.0)
            pass
        else:
            try:
                x = float(self.angular_range_edit.text())
                phis = self.leapct.setAngleArray(numAngles, x)
                self.leapct.set_angles(phis)
            except:
                self.angular_range_edit.setText("")
                #self.leapct.set_angularRange(0.0)
    
    def push_sod(self):
        if len(self.sod_edit.text()) == 0:
            self.leapct.set_sod(0.0)
        else:
            try:
                x = float(self.sod_edit.text())
                self.leapct.set_sod(x)
            except:
                self.leapct.set_sod(0.0)
                self.sod_edit.setText("")
        
    def push_numRows(self):
        if len(self.numRows_edit.text()) == 0:
            self.leapct.set_numRows(0)
        else:
            try:
                x = int(self.numRows_edit.text())
                self.leapct.set_numRows(x)
            except:
                self.leapct.set_numRows(0)
                self.numRows_edit.setText("")
        
    def push_pixelHeight(self):
        if len(self.pixelHeight_edit.text()) == 0:
            self.leapct.set_pixelHeight(0.0)
        else:
            try:
                x = float(self.pixelHeight_edit.text())
                self.leapct.set_pixelHeight(x)
            except:
                self.leapct.set_pixelHeight(0.0)
                self.pixelHeight_edit.setText("")
        
    def push_centerRow(self):
        if len(self.centerRow_edit.text()) == 0:
            self.leapct.set_centerRow(0.0)
        else:
            try:
                x = float(self.centerRow_edit.text())
                self.leapct.set_centerRow(x)
            except:
                self.leapct.set_centerRow(0.0)
                self.centerRow_edit.setText("")
        
    def push_tau(self):
        if len(self.tau_edit.text()) == 0:
            self.leapct.set_tau(0.0)
        else:
            try:
                x = float(self.tau_edit.text())
                self.leapct.set_tau(x)
            except:
                self.leapct.set_tau(0.0)
                self.tau_edit.setText("")
        
    def push_sdd(self):
        if len(self.sdd_edit.text()) == 0:
            self.leapct.set_sdd(0.0)
        else:
            try:
                x = float(self.sdd_edit.text())
                self.leapct.set_sdd(x)
            except:
                self.sdd_edit.setText("")
                self.leapct.set_sdd(0.0)
        
    def push_numCols(self):
        if len(self.numCols_edit.text()) == 0:
            self.leapct.set_numCols(0)
        else:
            try:
                x = int(self.numCols_edit.text())
                self.leapct.set_numCols(x)
            except:
                self.numCols_edit.setText("")
                self.leapct.set_numCols(0)
        
    def push_pixelWidth(self):
        if len(self.pixelWidth_edit.text()) == 0:
            self.leapct.set_pixelWidth(0.0)
        else:
            try:
                x = float(self.pixelWidth_edit.text())
                self.leapct.set_pixelWidth(x)
            except:
                self.pixelWidth_edit.setText("")
                self.leapct.set_pixelWidth(0.0)
        
    def push_centerCol(self):
        if len(self.centerCol_edit.text()) == 0:
            self.leapct.set_centerCol(0.0)
        else:
            try:
                x = float(self.centerCol_edit.text())
                self.leapct.set_centerCol(x)
            except:
                self.centerCol_edit.setText("")
                self.leapct.set_centerCol(0.0)
        
    def push_helicalPitch(self):
        if len(self.helicalPitch_edit.text()) == 0:
            self.leapct.set_helicalPitch(0.0)
        else:
            try:
                x = float(self.helicalPitch_edit.text())
                self.leapct.set_helicalPitch(x)
            except:
                self.helicalPitch_edit.setText("")
                self.leapct.set_helicalPitch(0.0)
        
    def cone_flat_radio_Clicked(self):
        self.leapct.set_geometry('CONE')
        self.leapct.set_flatDetector()
        self.enable_disable()
        
    def cone_curved_radio_Clicked(self):
        self.leapct.set_geometry('CONE')
        self.leapct.set_curvedDetector()
        self.enable_disable()
        
    def modular_radio_Clicked(self):
        self.leapct.set_geometry('MODULAR')
        self.enable_disable()
        
    def cone_parallel_radio_Clicked(self):
        self.leapct.set_geometry('CONE-PARALLEL')
        self.enable_disable()
    
    def fan_radio_Clicked(self):
        self.leapct.set_geometry('FAN')
        self.enable_disable()
        
    def parallel_radio_Clicked(self):
        self.leapct.set_geometry('PARALLEL')
        self.enable_disable()
        
    def enable_disable(self):
        geom = self.leapct.get_geometry()
        if geom == 'CONE':
            self.sod_edit.setEnabled(True)
            self.sdd_edit.setEnabled(True)
            self.tau_edit.setEnabled(True)
            self.helicalPitch_edit.setEnabled(True)
        elif geom == 'CONE-PARALLEL':
            self.sod_edit.setEnabled(True)
            self.sdd_edit.setEnabled(True)
            self.tau_edit.setEnabled(False)
            self.helicalPitch_edit.setEnabled(True)
        elif geom == 'MODULAR':
            self.sod_edit.setEnabled(False)
            self.sdd_edit.setEnabled(False)
            self.tau_edit.setEnabled(False)
            self.helicalPitch_edit.setEnabled(False)
            
            self.angular_range_edit.setEnabled(False)
            self.initial_angle_edit.setEnabled(False)
            
        elif geom == 'FAN':
            self.sod_edit.setEnabled(True)
            self.sdd_edit.setEnabled(True)
            self.tau_edit.setEnabled(True)
            self.helicalPitch_edit.setEnabled(False)
        elif geom == 'PARALLEL':
            self.sod_edit.setEnabled(False)
            self.sdd_edit.setEnabled(False)
            self.tau_edit.setEnabled(False)
            self.helicalPitch_edit.setEnabled(False)
            
        if self.equispaced_angles_check.isChecked():
            if geom != 'MODULAR':
                self.angular_range_edit.setEnabled(True)
                self.initial_angle_edit.setEnabled(True)
            