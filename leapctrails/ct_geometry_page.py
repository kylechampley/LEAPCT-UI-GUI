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
        self.systemSpecifications_grid = QGridLayout()
        
        self.sod_label = QLabel("<div align='right'>sod (mm)</div>")
        self.sod_edit = QLineEdit()
        self.sod_label.setToolTip("source to object distance, measured in mm; this can also be viewed as the source to center of rotation distance")
        self.systemSpecifications_grid.addWidget(self.sod_label, 0, 0)
        self.systemSpecifications_grid.addWidget(self.sod_edit, 0, 1)
        
        self.numRows_label = QLabel("<div align='right'>num rows</div>")
        self.numRows_edit = QLineEdit()
        self.numRows_label.setToolTip("number of rows in the x-ray detector")
        self.systemSpecifications_grid.addWidget(self.numRows_label, 1, 0)
        self.systemSpecifications_grid.addWidget(self.numRows_edit, 1, 1)
        
        self.pixelHeight_label = QLabel("<div align='right'>pixel height (mm)</div>")
        self.pixelHeight_edit = QLineEdit()
        self.pixelHeight_label.setToolTip("the detector pixel pitch (i.e., pixel size) between detector rows, measured in mm")
        self.systemSpecifications_grid.addWidget(self.pixelHeight_label, 2, 0)
        self.systemSpecifications_grid.addWidget(self.pixelHeight_edit, 2, 1)
        
        self.centerRow_label = QLabel("<div align='right'>center row</div>")
        self.centerRow_edit = QLineEdit()
        self.centerRow_label.setToolTip("the detector pixel row index for the ray that passes from the source, through the origin, and hits the detector")
        self.shift_detector_row_button = QPushButton("vertical shift (mm)")
        self.centerRow_stack = QStackedWidget()
        self.centerRow_stack.addWidget(self.centerRow_label)
        self.centerRow_stack.addWidget(self.shift_detector_row_button)
        #self.systemSpecifications_grid.addWidget(self.centerRow_label, 3, 0)
        self.systemSpecifications_grid.addWidget(self.centerRow_stack, 3, 0)
        self.systemSpecifications_grid.addWidget(self.centerRow_edit, 3, 1)
        
        self.tau_label = QLabel("<div align='right'>tau (mm)</div>")
        self.tau_edit = QLineEdit()
        self.tau_label.setToolTip("center of rotation offset, measured in mm")
        self.systemSpecifications_grid.addWidget(self.tau_label, 4, 0)
        self.systemSpecifications_grid.addWidget(self.tau_edit, 4, 1)
        
        self.sdd_label = QLabel("<div align='right'>sdd (mm)</div>")
        self.sdd_edit = QLineEdit()
        self.sdd_label.setToolTip("source to detector distance, measured in mm")
        self.systemSpecifications_grid.addWidget(self.sdd_label, 0, 2)
        self.systemSpecifications_grid.addWidget(self.sdd_edit, 0, 3)
        
        self.numCols_label = QLabel("<div align='right'>num columns</div>")
        self.numCols_edit = QLineEdit()
        self.numCols_label.setToolTip("number of columns in the x-ray detector")
        self.systemSpecifications_grid.addWidget(self.numCols_label, 1, 2)
        self.systemSpecifications_grid.addWidget(self.numCols_edit, 1, 3)
        
        self.pixelWidth_label = QLabel("<div align='right'>pixel width (mm)</div>")
        self.pixelWidth_edit = QLineEdit()
        self.pixelWidth_label.setToolTip("the detector pixel pitch (i.e., pixel size) between detector columns, measured in mm")
        self.systemSpecifications_grid.addWidget(self.pixelWidth_label, 2, 2)
        self.systemSpecifications_grid.addWidget(self.pixelWidth_edit, 2, 3)
        
        self.centerCol_label = QLabel("<div align='right'>center column</div>")
        self.centerCol_edit = QLineEdit()
        self.centerCol_label.setToolTip("the detector pixel column index for the ray that passes from the source, through the origin, and hits the detector")
        self.shift_detector_col_button = QPushButton("horizontal shift (mm)")
        self.centerCol_stack = QStackedWidget()
        self.centerCol_stack.addWidget(self.centerCol_label)
        self.centerCol_stack.addWidget(self.shift_detector_col_button)
        self.systemSpecifications_grid.addWidget(self.centerCol_stack, 3, 2)
        self.systemSpecifications_grid.addWidget(self.centerCol_edit, 3, 3)
        
        self.helicalPitch_label = QLabel("<div align='right'>helical pitch (mm/rad)</div>")
        self.helicalPitch_edit = QLineEdit()
        self.normalizedHelicalPitch_label = QLabel()
        self.helicalPitch_label.setToolTip("the helical pitch (mm/radians)\nhelical pitch = (normalized helical pitch) * (numRows * pixelHeight * sod / sdd) / (2 * pi)")
        #h = h_normalized * (numRows * pixelHeight * sod / sdd) / (2.0*PI)
        self.systemSpecifications_grid.addWidget(self.helicalPitch_label, 4, 2)
        self.systemSpecifications_grid.addWidget(self.helicalPitch_edit, 4, 3)
        self.systemSpecifications_grid.addWidget(self.normalizedHelicalPitch_label, 4, 4, 1, 2)
        
        # Angles
        self.equispaced_angles_check = QCheckBox("equi-spaced angles")
        self.equispaced_angles_check.setToolTip("if the projection angles are non-equi-spaced, you must set them with a geometry file")
        self.systemSpecifications_grid.addWidget(self.equispaced_angles_check, 0, 4, 1, 2)
        self.equispaced_angles_check.setChecked(True)
        self.equispaced_angles_check.clicked.connect(self.equispaced_angles_check_Clicked)
        
        self.numAngles_label = QLabel("<div align='right'>num angles</div>")
        self.numAngles_edit = QLineEdit()
        self.numAngles_label.setToolTip("number of projection angles")
        self.systemSpecifications_grid.addWidget(self.numAngles_label, 1, 4)
        self.systemSpecifications_grid.addWidget(self.numAngles_edit, 1, 5)
        
        self.initial_angle_label = QLabel("<div align='right'>initial angle (deg)</div>")
        self.initial_angle_edit = QLineEdit()
        self.initial_angle_label.setToolTip("the angle of the first projection (in degrees)")
        self.systemSpecifications_grid.addWidget(self.initial_angle_label, 2, 4)
        self.systemSpecifications_grid.addWidget(self.initial_angle_edit, 2, 5)
        
        self.angular_range_label = QLabel("<div align='right'>angular range (deg)</div>")
        self.angular_range_edit = QLineEdit()
        self.angular_range_label.setToolTip("the angular range of all projections (degrees), i.e., numAngles * angularStep; negative numbers model a reverse direction rotation")
        self.systemSpecifications_grid.addWidget(self.angular_range_label, 3, 4)
        self.systemSpecifications_grid.addWidget(self.angular_range_edit, 3, 5)
        
        #self.rotation_direction_button = QPushButton("Counter Clockwise Rotation")
        #self.systemSpecifications_grid.addWidget(self.rotation_direction_button, 4, 4, 1, 2)
        
        systemSpecifications_group.setLayout(self.systemSpecifications_grid)
        overall_grid.addWidget(systemSpecifications_group, 2, 0, 1, 4)
        ######### SYSTEM SPECIFICATIONS END #########
        
        """
        shift_group = QGroupBox()
        shift_layout = QHBoxLayout()
        self.shift_detector_button = QPushButton("shift detector (mm)")
        self.shift_detector_row_edit = QLineEdit()
        self.shift_detector_col_edit = QLineEdit()
        shift_layout.addWidget(self.shift_detector_col_button)
        shift_layout.addWidget(self.shift_detector_row_edit)
        shift_layout.addWidget(self.shift_detector_col_edit)
        shift_group.setLayout(shift_layout)
        """
        
        ######### SCAN TYPE START #########
        scan_type_layout = QHBoxLayout()
        #scan_type_layout.addWidget(shift_group)
        self.offsetScan_check = QCheckBox("offset scan")
        self.truncatedScan_check = QCheckBox("truncated scan")
        self.offsetScan_check.clicked.connect(self.offsetScan_check_Clicked)
        self.truncatedScan_check.clicked.connect(self.truncatedScan_check_Clicked)
        self.sketch_system_button = QPushButton("sketch system")
        self.sketch_system_button.clicked.connect(self.sketch_system_button_Clicked)
        scan_type_layout.addWidget(self.offsetScan_check)
        scan_type_layout.addWidget(self.truncatedScan_check)
        blank_label = QLabel("             ")
        scan_type_layout.addWidget(blank_label)
        scan_type_layout.addWidget(self.sketch_system_button)
        overall_grid.addLayout(scan_type_layout, 3, 0, 1, 1)
        ######### SCAN TYPE END #########
        
        self.shift_detector_row_button.clicked.connect(self.shift_detector_row_button_Clicked)
        self.shift_detector_col_button.clicked.connect(self.shift_detector_col_button_Clicked)
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
        if geomTxt == 'MODULAR':
            self.centerRow_edit.setText("")
        else:
            self.centerRow_edit.setText(str(self.leapct.get_centerRow()))
        self.tau_edit.setText(str(self.leapct.get_tau()))
        self.sdd_edit.setText(str(self.leapct.get_sdd()))
        self.numCols_edit.setText(str(self.leapct.get_numCols()))
        self.pixelWidth_edit.setText(str(self.leapct.get_pixelWidth()))
        if geomTxt == 'MODULAR':
            self.centerCol_edit.setText("")
        else:
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
        self.set_text_color()
        self.enable_disable()
        
        #self.offsetScan_check.setChecked(self.get_offsetScan())
        #self.truncatedScan_check.setChecked(self.get_truncatedScan())
        
    def set_text_color(self):
        if self.cone_flat_radio.isChecked() or self.cone_curved_radio.isChecked() or self.cone_parallel_radio.isChecked():
            if self.leapct.get_sod() > 0.0:
               self.sod_label.setStyleSheet('color: black')
            else:
               self.sod_label.setStyleSheet('color: red')
            if self.leapct.get_sdd() > 0.0:
               self.sdd_label.setStyleSheet('color: black')
            else:
               self.sdd_label.setStyleSheet('color: red')
        elif self.modular_radio.isChecked():
            self.sod_label.setStyleSheet('color: black')
            self.sdd_label.setStyleSheet('color: black')
        elif self.fan_radio.isChecked():
            if self.leapct.get_sod() > 0.0:
               self.sod_label.setStyleSheet('color: black')
            else:
               self.sod_label.setStyleSheet('color: red')
            if self.leapct.get_sdd() > 0.0:
               self.sdd_label.setStyleSheet('color: black')
            else:
               self.sdd_label.setStyleSheet('color: red')
        elif self.parallel_radio.isChecked():
            self.sod_label.setStyleSheet('color: black')
            self.sdd_label.setStyleSheet('color: black')
        else:
            self.sod_label.setStyleSheet('color: black')
            self.sdd_label.setStyleSheet('color: black')
            
        if self.leapct.get_numAngles() > 0:
            self.numAngles_label.setStyleSheet('color: black')
        else:
            self.numAngles_label.setStyleSheet('color: red')
        if self.leapct.get_numRows() > 0:
            self.numRows_label.setStyleSheet('color: black')
        else:
            self.numRows_label.setStyleSheet('color: red')
        if self.leapct.get_numCols() > 0:
            self.numCols_label.setStyleSheet('color: black')
        else:
            self.numCols_label.setStyleSheet('color: red')
        if self.leapct.get_pixelWidth() > 0:
            self.pixelWidth_label.setStyleSheet('color: black')
        else:
            self.pixelWidth_label.setStyleSheet('color: red')
        if self.leapct.get_pixelHeight() > 0:
            self.pixelHeight_label.setStyleSheet('color: black')
        else:
            self.pixelHeight_label.setStyleSheet('color: red')
            
        if self.leapct.ct_geometry_defined():
            self.sketch_system_button.setEnabled(True)
        else:
            self.sketch_system_button.setEnabled(False)
    
    def sketch_system_button_Clicked(self):
        if self.leapct.ct_geometry_defined():
            self.leapct.sketch_system(0)        
        
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
        self.set_text_color()
    
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
        self.set_text_color()
        
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
        self.set_text_color()
        
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
        self.set_text_color()
    
    def shift_detector_row_button_Clicked(self):
        if len(self.centerRow_edit.text()) == 0:
            shift = 0.0
        else:
            try:
                shift = float(self.centerRow_edit.text())
            except:
                shift = 0.0
        if shift != 0.0:
            self.leapct.shift_detector(shift, 0.0)
        self.centerRow_edit.setText("")
            
    def shift_detector_col_button_Clicked(self):
        if len(self.centerCol_edit.text()) == 0:
            shift = 0.0
        else:
            try:
                shift = float(self.centerCol_edit.text())
            except:
                shift = 0.0
        if shift != 0.0:
            self.leapct.shift_detector(0.0, shift)
        self.centerCol_edit.setText("")
        
    def push_centerRow(self):
        if self.leapct.get_geometry() != 'MODULAR':
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
        self.set_text_color()
        
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
        self.set_text_color()
        
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
        self.set_text_color()
        
    def push_centerCol(self):
        if self.leapct.get_geometry() != 'MODULAR':
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
        if self.leapct.get_helicalPitch() != 0.0 and self.leapct.get_numRows() > 0 and self.leapct.get_pixelHeight() > 0.0 and self.leapct.get_sod() > 0.0 and self.leapct.get_sdd() > 0.0:
            text = str(f'{self.leapct.get_normalizedHelicalPitch():.4f}')
            self.normalizedHelicalPitch_label.setText('normalized pitch = ' + str(text))
        else:
            self.normalizedHelicalPitch_label.setText("")
        
    def update_detector_center(self):
        if self.leapct.get_geometry() == 'MODULAR':
            self.centerRow_edit.setText("")
            self.centerCol_edit.setText("")
        else:
            self.centerRow_edit.setText(str(self.leapct.get_centerRow()))
            self.centerCol_edit.setText(str(self.leapct.get_centerCol()))
    
    def cone_flat_radio_Clicked(self):
        self.leapct.set_geometry('CONE')
        self.leapct.set_flatDetector()
        self.update_detector_center()
        self.enable_disable()
        self.set_text_color()
        
    def cone_curved_radio_Clicked(self):
        self.leapct.set_geometry('CONE')
        self.leapct.set_curvedDetector()
        self.update_detector_center()
        self.enable_disable()
        self.set_text_color()
        
    def modular_radio_Clicked(self):
        self.leapct.set_geometry('MODULAR')
        self.update_detector_center()
        self.enable_disable()
        self.set_text_color()
        
    def cone_parallel_radio_Clicked(self):
        self.leapct.set_geometry('CONE-PARALLEL')
        self.update_detector_center()
        self.enable_disable()
        self.set_text_color()
    
    def fan_radio_Clicked(self):
        self.leapct.set_geometry('FAN')
        self.update_detector_center()
        self.enable_disable()
        self.set_text_color()
        
    def parallel_radio_Clicked(self):
        self.leapct.set_geometry('PARALLEL')
        self.update_detector_center()
        self.enable_disable()
        self.set_text_color()
        
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
            
        if geom == 'MODULAR':
            self.centerRow_stack.setCurrentIndex(1)
            self.centerCol_stack.setCurrentIndex(1)
        else:
            self.centerRow_stack.setCurrentIndex(0)
            self.centerCol_stack.setCurrentIndex(0)
        
        