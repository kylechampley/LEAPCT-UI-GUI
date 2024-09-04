import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class CTvolumePage(QWidget):

    def __init__(self, parent=None):
        super(CTvolumePage, self).__init__(parent)

        self.parent	= parent
        self.leapct = self.parent.leapct
        self.lctserver = self.parent.lctserver
        
        overall_grid = QGridLayout()
        curRow = 0
        
        ######### Default Samples Start #########
        default_volume_layout = QGridLayout()
        default_volume_button = QPushButton("Set Default Volume")
        default_volume_button.clicked.connect(self.default_volume_button_Clicked)
        self.default_volume_scale_edit = QLineEdit()
        self.default_volume_scale_edit.editingFinished.connect(self.default_volume_button_Clicked)
        default_volume_button.setMaximumWidth(120)
        self.default_volume_scale_edit.setMaximumWidth(30)
        default_volume_layout.addWidget(default_volume_button, 0, 0)
        default_volume_layout.addWidget(self.default_volume_scale_edit, 0, 1)
        blank_label = QLabel(" ")
        default_volume_layout.addWidget(blank_label, 0, 2)
        default_volume_button.setToolTip("Set the volume parameters with the nominal voxel size that fills the field of view")
        self.default_volume_scale_edit.setToolTip("this value scales the nominal voxel size by this value to create denser or sparser voxel representations")
        ######### Default Samples End #########
        
        ######### X Samples Start #########
        x_group = QGroupBox("X Samples")
        x_grid = QGridLayout()
        
        x_count_label = QLabel("<div align='right'>count</div>")
        self.x_count_edit = QLineEdit()
        self.x_count_edit.editingFinished.connect(self.push_numX)
        x_grid.addWidget(x_count_label, 0, 0)
        x_grid.addWidget(self.x_count_edit, 0, 1)
        
        x_pitch_label = QLabel("<div align='right'>pitch (mm)</div>")
        self.x_pitch_edit = QLineEdit()
        self.x_pitch_edit.editingFinished.connect(self.push_Tx)
        x_grid.addWidget(x_pitch_label, 1, 0)
        x_grid.addWidget(self.x_pitch_edit, 1, 1)
        
        x_offset_label = QLabel("<div align='right'>offset (mm)</div>")
        self.x_offset_edit = QLineEdit()
        self.x_offset_edit.editingFinished.connect(self.push_offsetX)
        x_grid.addWidget(x_offset_label, 2, 0)
        x_grid.addWidget(self.x_offset_edit, 2, 1)
        
        x_count_label.setToolTip("number of voxels in the x-dimension")
        x_pitch_label.setToolTip("voxel pitch (size) in the x and y dimensions, measured in mm")
        x_offset_label.setToolTip(" shift the volume in the x-dimension, measured in mm")
        
        x_group.setLayout(x_grid)
        ######### X Samples End #########
        
        ######### Y Samples Start #########
        y_group = QGroupBox("Y Samples")
        y_grid = QGridLayout()
        
        y_count_label = QLabel("<div align='right'>count</div>")
        self.y_count_edit = QLineEdit()
        self.y_count_edit.editingFinished.connect(self.push_numY)
        y_grid.addWidget(y_count_label, 0, 0)
        y_grid.addWidget(self.y_count_edit, 0, 1)
        
        y_pitch_label = QLabel("<div align='right'>pitch (mm)</div>")
        self.y_pitch_edit = QLineEdit()
        self.y_pitch_edit.editingFinished.connect(self.push_Ty)
        y_grid.addWidget(y_pitch_label, 1, 0)
        y_grid.addWidget(self.y_pitch_edit, 1, 1)
        
        y_offset_label = QLabel("<div align='right'>offset (mm)</div>")
        self.y_offset_edit = QLineEdit()
        self.y_offset_edit.editingFinished.connect(self.push_offsetY)
        y_grid.addWidget(y_offset_label, 2, 0)
        y_grid.addWidget(self.y_offset_edit, 2, 1)
        
        y_count_label.setToolTip("number of voxels in the y-dimension")
        y_pitch_label.setToolTip("voxel pitch (size) in the x and y dimensions, measured in mm")
        y_offset_label.setToolTip(" shift the volume in the y-dimension, measured in mm")
        
        y_group.setLayout(y_grid)
        ######### Y Samples End #########
        
        ######### Z Samples Start #########
        z_group = QGroupBox("Z Samples")
        z_grid = QGridLayout()
        
        z_count_label = QLabel("<div align='right'>count</div>")
        self.z_count_edit = QLineEdit()
        self.z_count_edit.editingFinished.connect(self.push_numZ)
        z_grid.addWidget(z_count_label, 0, 0)
        z_grid.addWidget(self.z_count_edit, 0, 1)
        
        z_pitch_label = QLabel("<div align='right'>pitch (mm)</div>")
        self.z_pitch_edit = QLineEdit()
        self.z_pitch_edit.editingFinished.connect(self.push_Tz)
        z_grid.addWidget(z_pitch_label, 1, 0)
        z_grid.addWidget(self.z_pitch_edit, 1, 1)
        
        z_offset_label = QLabel("<div align='right'>offset (mm)</div>")
        self.z_offset_edit = QLineEdit()
        self.z_offset_edit.editingFinished.connect(self.push_offsetZ)
        z_grid.addWidget(z_offset_label, 2, 0)
        z_grid.addWidget(self.z_offset_edit, 2, 1)
        
        z_count_label.setToolTip("number of voxels in the z-dimension")
        z_pitch_label.setToolTip("voxel pitch (size) in the z-dimension, measured in mm")
        z_offset_label.setToolTip(" shift the volume in the z-dimension, measured in mm")
        
        z_group.setLayout(z_grid)
        ######### Z Samples End #########
        
        ct_volume_parameters_layout = QHBoxLayout()
        ct_volume_parameters_layout.addWidget(x_group)
        ct_volume_parameters_layout.addWidget(y_group)
        ct_volume_parameters_layout.addWidget(z_group)
        
        ######### FOV DIAMETER START #########
        dFOV_group = QGroupBox("Diameter of the Field of View Mask (mm)")
        dFOV_grid = QGridLayout()
        
        self.dFOV_default_radio = QRadioButton("use default")
        self.dFOV_off_radio = QRadioButton("turn off")
        self.dFOV_specify_radio = QRadioButton("custom")
        self.dFOV_default_radio.clicked.connect(self.dFOV_default_radio_Clicked)
        self.dFOV_off_radio.clicked.connect(self.dFOV_off_radio_Clicked)
        self.dFOV_specify_radio.clicked.connect(self.dFOV_specify_radio_Clicked)
        self.dFOV_edit = QLineEdit()
        self.dFOV_edit.editingFinished.connect(self.push_dFOV)
        dFOV_grid.addWidget(self.dFOV_default_radio, 0, 0)
        dFOV_grid.addWidget(self.dFOV_off_radio, 0, 1)
        dFOV_grid.addWidget(self.dFOV_specify_radio, 0, 2)
        dFOV_grid.addWidget(self.dFOV_edit, 0, 3)
        self.dFOV_default_radio.setChecked(True)
        self.dFOV_edit.setEnabled(False)
        self.dFOV_edit.setMaximumWidth(120)
        
        dFOV_group.setLayout(dFOV_grid)
        self.dFOV_default_radio.clicked.connect(self.dFOV_default_radio_Clicked)
        self.dFOV_off_radio.clicked.connect(self.dFOV_off_radio_Clicked)
        self.dFOV_specify_radio.clicked.connect(self.dFOV_specify_radio_Clicked)
        dFOV_group.setToolTip("Set the diameter of the cylindrical field of view (FOV) mask")
        self.dFOV_default_radio.setToolTip("This option automatically sets the FOV mask based on the CT geometry and voxel volume position")
        self.dFOV_off_radio.setToolTip("This option turns off the FOV mask completely")
        self.dFOV_specify_radio.setToolTip("This option allows the user to specify the diameter of the field of view mask, measured in mm")
        ######### FOV DIAMETER END #########
        
        ######### RAMP FILTER START #########
        ramp_layout = QHBoxLayout()
        ramp_label = QLabel("<div align='right'>Ramp Filter</div>")
        self.ramp_combo = QComboBox()
        self.ramp_combo.addItem("Smooth")
        self.ramp_combo.addItem("Standard")
        self.ramp_combo.addItem("Sharp")
        self.ramp_combo.addItem("Ultra-Sharp")
        self.ramp_combo.setCurrentIndex(1)
        self.ramp_combo.currentIndexChanged.connect(self.ramp_combo_selectionchange)
        ramp_layout.addWidget(ramp_label)
        ramp_layout.addWidget(self.ramp_combo)
        ramp_label.setToolTip("Sets the sharpness of the ramp filter used in FBP reconstruction")
        ######### RAMP FILTER END #########
        
        ######### COMPRESS VOLUME FILE START #########
        compress_file_group = QGroupBox("Volume File Settings")
        compress_file_layout = QHBoxLayout()
        self.file_dtype_combo = QComboBox()
        self.file_dtype_combo.addItem("uint8")
        self.file_dtype_combo.addItem("uint16")
        self.file_dtype_combo.addItem("float32")
        self.file_dtype_combo.setCurrentIndex(2)
        self.file_dtype_combo.currentIndexChanged.connect(self.file_dtype_combo_selectionchange)
        window_label = QLabel("<div align='right'>window:</div>")
        to_label = QLabel("to")
        self.wmin_edit = QLineEdit()
        #self.wmin_edit.setText("0.0")
        self.wmax_edit = QLineEdit()
        self.wmin_edit.editingFinished.connect(self.push_wmin)
        self.wmax_edit.editingFinished.connect(self.push_wmax)
        compress_file_layout.addWidget(self.file_dtype_combo)
        compress_file_layout.addWidget(window_label)
        compress_file_layout.addWidget(self.wmin_edit)
        compress_file_layout.addWidget(to_label)
        compress_file_layout.addWidget(self.wmax_edit)
        compress_file_group.setLayout(compress_file_layout)
        self.wmin_edit.setEnabled(False)
        self.wmax_edit.setEnabled(False)
        compress_file_group.setEnabled(False)
        compress_file_group.setToolTip("Not yet implemented")
        ######### COMPRESS VOLUME FILE END #########
        
        # Next section should be FBP settings, including offsetScan, truncatedScan, and ramp filter specification
        # Could also include axis of symmetry
        
        curRow = 0
        overall_grid.addLayout(default_volume_layout, 0, 0)
        curRow += 1
        
        overall_grid.addLayout(ct_volume_parameters_layout, curRow, 0, 1, 2)
        curRow += 1
        
        overall_grid.addWidget(dFOV_group, curRow, 0, 1, 1)
        overall_grid.addLayout(ramp_layout, curRow, 1, 1, 1)
        curRow += 1
        
        overall_grid.addWidget(compress_file_group, curRow, 0, 1, 1)
        curRow += 1
        
        self.setLayout(overall_grid)
        self.refresh()
    
    def refresh(self):
    
        if self.leapct.ct_geometry_defined() == True and self.leapct.ct_volume_defined() == False:
            self.leapct.set_default_volume()
            
        self.refresh_volume_params()
    
        if self.leapct.get_rampFilter() == 0:
            self.ramp_combo.setCurrentIndex(0)
        elif self.leapct.get_rampFilter() == 2:
            self.ramp_combo.setCurrentIndex(1)
        elif self.leapct.get_rampFilter() == 4:
            self.ramp_combo.setCurrentIndex(2)
        elif self.leapct.get_rampFilter() == 10:
            self.ramp_combo.setCurrentIndex(3)
        
        #"""
        if self.leapct.file_dtype == np.uint8:
            self.file_dtype_combo.setCurrentIndex(0)
        elif self.leapct.file_dtype == np.uint16:
            self.file_dtype_combo.setCurrentIndex(1)
        elif self.leapct.file_dtype == np.float32:
            self.file_dtype_combo.setCurrentIndex(2)
        
        if self.leapct.wmin is not None:
            self.wmin_edit.setText(str(self.leapct.wmin))
        if self.leapct.wmax is not None:
            self.wmax_edit.setText(str(self.leapct.wmax))
        #"""
        
    def pushAllParameters(self):
        pass
    
    def dFOV_default_radio_Clicked(self):
        self.push_dFOV()
        
    def dFOV_off_radio_Clicked(self):
        self.push_dFOV()
        
    def dFOV_specify_radio_Clicked(self):
        self.push_dFOV()
    
    def push_dFOV(self):
        d = self.string_to_float(self.dFOV_edit.text())
        if self.dFOV_default_radio.isChecked():
            self.leapct.set_diameterFOV(0.0)
        elif self.dFOV_off_radio.isChecked():
            self.leapct.set_diameterFOV(1.0e16)
        else:
            if d is not None:
                self.leapct.set_diameterFOV(d)
    
    def file_dtype_combo_selectionchange(self):
        if self.file_dtype_combo.currentIndex() == 0 or self.file_dtype_combo.currentIndex() == 1:
            self.wmin_edit.setEnabled(True)
            self.wmax_edit.setEnabled(True)
        elif self.file_dtype_combo.currentIndex() == 2:
            self.wmin_edit.setEnabled(False)
            self.wmax_edit.setEnabled(False)
        self.update_file_compression_parameters()
    
    def push_wmin(self):
        self.update_file_compression_parameters()
        
    def push_wmax(self):
        self.update_file_compression_parameters()
    
    def update_file_compression_parameters(self):
        wmin = self.string_to_float(self.wmin_edit.text())
        if wmin is None:
            wmin = 0.0
        wmax = self.string_to_float(self.wmax_edit.text())
        if self.file_dtype_combo.currentIndex() == 0:
            self.leapct.set_fileIO_parameters(np.uint8, wmin, wmax)
        elif self.file_dtype_combo.currentIndex() == 1:
            self.leapct.set_fileIO_parameters(np.uint16, wmin, wmax)
        else:
            self.leapct.set_fileIO_parameters(np.float32, wmin, wmax)
    
    def ramp_combo_selectionchange(self):
        if self.ramp_combo.currentIndex() == 0:
            self.leapct.set_rampFilter(0)
        elif self.ramp_combo.currentIndex() == 1:
            self.leapct.set_rampFilter(2)
        elif self.ramp_combo.currentIndex() == 2:
            self.leapct.set_rampFilter(4)
        elif self.ramp_combo.currentIndex() == 3:
            self.leapct.set_rampFilter(10)
    
    def dFOV_default_radio_Clicked(self):
        self.dFOV_edit.setEnabled(False)
        
    def dFOV_off_radio_Clicked(self):
        self.dFOV_edit.setEnabled(False)
        
    def dFOV_specify_radio_Clicked(self):
        self.dFOV_edit.setEnabled(True)
    
    def default_volume_button_Clicked(self):
        scale = 1.0
        if len(self.default_volume_scale_edit.text()) > 0:
            try:
                scale = float(self.default_volume_scale_edit.text())
            except:
                scale = 1.0
        self.leapct.set_default_volume(scale)
        self.refresh()
        
    def push_numX(self):
        if len(self.x_count_edit.text()) == 0:
            self.leapct.set_numX(0)
        else:
            try:
                x = int(self.x_count_edit.text())
                self.leapct.set_numX(x)
            except:
                self.leapct.set_numX(0)
                self.x_count_edit.setText("")
                
    def push_Tx(self):
        if len(self.x_pitch_edit.text()) == 0:
            self.leapct.set_voxelWidth(0.0)
        else:
            try:
                x = float(self.x_pitch_edit.text())
                self.leapct.set_voxelWidth(x)
            except:
                self.leapct.set_voxelWidth(0.0)
                self.x_pitch_edit.setText("")
        self.y_pitch_edit.setText(self.x_pitch_edit.text())
        
    def push_offsetX(self):
        if len(self.x_offset_edit.text()) == 0:
            self.leapct.set_offsetX(0.0)
        else:
            try:
                x = float(self.x_offset_edit.text())
                self.leapct.set_offsetX(x)
            except:
                self.leapct.set_offsetX(0.0)
                self.x_offset_edit.setText("")
    
    def push_numY(self):
        if len(self.y_count_edit.text()) == 0:
            self.leapct.set_numY(0)
        else:
            try:
                y = int(self.y_count_edit.text())
                self.leapct.set_numY(y)
            except:
                self.leapct.set_numY(0)
                self.y_count_edit.setText("")
                
    def push_Ty(self):
        if len(self.y_pitch_edit.text()) == 0:
            self.leapct.set_voxelWidth(0.0)
        else:
            try:
                y = float(self.y_pitch_edit.text())
                self.leapct.set_voxelWidth(y)
            except:
                self.leapct.set_voxelWidth(0.0)
                self.y_pitch_edit.setText("")
        self.x_pitch_edit.setText(self.y_pitch_edit.text())
        
    def push_offsetY(self):
        if len(self.y_offset_edit.text()) == 0:
            self.leapct.set_offsetY(0.0)
        else:
            try:
                y = float(self.y_offset_edit.text())
                self.leapct.set_offsetY(y)
            except:
                self.leapct.set_offsetY(0.0)
                self.y_offset_edit.setText("")
    
    def push_numZ(self):
        if len(self.z_count_edit.text()) == 0:
            self.leapct.set_numZ(0)
        else:
            try:
                z = int(self.z_count_edit.text())
                self.leapct.set_numZ(z)
            except:
                self.leapct.set_numZ(0)
                self.z_count_edit.setText("")
                
    def push_Tz(self):
        if len(self.z_pitch_edit.text()) == 0:
            self.leapct.set_voxelHeight(0.0)
        else:
            try:
                z = float(self.z_pitch_edit.text())
                self.leapct.set_voxelHeight(z)
            except:
                self.leapct.set_voxelHeight(0.0)
                self.z_pitch_edit.setText("")
        
    def push_offsetZ(self):
        if len(self.z_offset_edit.text()) == 0:
            self.leapct.set_offsetZ(0.0)
        else:
            try:
                z = float(self.z_offset_edit.text())
                self.leapct.set_offsetZ(z)
            except:
                self.leapct.set_offsetZ(0.0)
                self.z_offset_edit.setText("")
        
    def refresh_volume_params(self):
        if self.leapct.get_numX() > 0:
            self.x_count_edit.setText(str(self.leapct.get_numX()))
        else:
            self.x_count_edit.setText(str(""))
        if self.leapct.get_voxelWidth() > 0.0:
            self.x_pitch_edit.setText(str(self.leapct.get_voxelWidth()))
        else:
            self.x_pitch_edit.setText(str(""))
        if self.leapct.get_offsetX() != 0.0 or self.leapct.get_numX() > 0:
            self.x_offset_edit.setText(str(self.leapct.get_offsetX()))
        else:
            self.x_offset_edit.setText(str(""))
        
        if self.leapct.get_numY() > 0:
            self.y_count_edit.setText(str(self.leapct.get_numY()))
        else:
            self.y_count_edit.setText(str(""))
        if self.leapct.get_voxelWidth() > 0.0:
            self.y_pitch_edit.setText(str(self.leapct.get_voxelWidth()))
        else:
            self.y_pitch_edit.setText(str(""))
        if self.leapct.get_offsetY() != 0.0 or self.leapct.get_numY() > 0:
            self.y_offset_edit.setText(str(self.leapct.get_offsetY()))
        else:
            self.y_offset_edit.setText(str(""))
        
        if self.leapct.get_numZ() > 0:
            self.z_count_edit.setText(str(self.leapct.get_numZ()))
        else:
            self.z_count_edit.setText(str(""))
        if self.leapct.get_voxelHeight() > 0.0:
            self.z_pitch_edit.setText(str(self.leapct.get_voxelHeight()))
        else:
            self.z_pitch_edit.setText(str(""))
        if self.leapct.get_offsetZ() != 0.0 or self.leapct.get_numZ() > 0:
            self.z_offset_edit.setText(str(self.leapct.get_offsetZ()))
        else:
            self.z_offset_edit.setText(str(""))
            
    def string_to_float(self, txt):
        if txt is None:
            return None
        elif len(txt) == 0:
            return None
        else:
            try:
                x = float(txt)
                return x
            except:
                return None
                