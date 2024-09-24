
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ctypes
import os
import sys
import numpy as np
from io import StringIO


class MyMessageBox(QDialog):
    def __init__(self, title, text, parent = None):
        super(MyMessageBox, self).__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)

        textLabel = QPlainTextEdit()
        textLabel.setReadOnly(True)
        textLabel.setPlainText(text)

        overallGrid = QGridLayout()
        overallGrid.addWidget(textLabel, 0, 0)
        self.setLayout(overallGrid)
        self.resize(750,600)

class SettingsDialogControls(QWidget):
    def __init__(self, parent = None):
        super(SettingsDialogControls, self).__init__(parent)

        self.parent = parent
        self.lctserver = self.parent.lctserver
        self.leapct = self.lctserver.leapct
        
        overallgrid = QGridLayout()
        curRow = 0
        
        number_of_gpus = self.leapct.number_of_gpus()
        
        GPUs_group = QGroupBox("GPUs")
        GPUs_layout = QHBoxLayout()
        self.gpu_one_check = QCheckBox("GPU 0")
        self.gpu_two_check = QCheckBox("GPU 1")
        self.gpu_three_check = QCheckBox("GPU 2")
        self.gpu_four_check = QCheckBox("GPU 3")
        self.gpu_one_check.clicked.connect(self.gpu_clicked)
        self.gpu_two_check.clicked.connect(self.gpu_clicked)
        self.gpu_three_check.clicked.connect(self.gpu_clicked)
        self.gpu_four_check.clicked.connect(self.gpu_clicked)
        
        if number_of_gpus < 4:
            self.gpu_four_check.setChecked(False)
            self.gpu_four_check.setEnabled(False)
        if number_of_gpus < 3:
            self.gpu_three_check.setChecked(False)
            self.gpu_three_check.setEnabled(False)
        if number_of_gpus < 2:
            self.gpu_two_check.setChecked(False)
            self.gpu_two_check.setEnabled(False)
        if number_of_gpus < 1:
            self.gpu_one_check.setChecked(False)
            self.gpu_one_check.setEnabled(False)
        
        GPUs_layout.addWidget(self.gpu_one_check)
        GPUs_layout.addWidget(self.gpu_two_check)
        GPUs_layout.addWidget(self.gpu_three_check)
        GPUs_layout.addWidget(self.gpu_four_check)
        GPUs_group.setLayout(GPUs_layout)
        overallgrid.addWidget(GPUs_group, curRow, 0)
        curRow += 1
        
        memory_layout = QHBoxLayout()
        memory_label = QLabel("Usable CPU RAM (GB)")
        memory_label.setToolTip("specifies how much total CPU RAM LEAP is allowed to use")
        self.memory_edit = QLineEdit()
        memory_total_label = QLabel("(total: " + str(np.floor(self.lctserver.total_RAM())) + " GB)")
        self.memory_edit.editingFinished.connect(self.push_memory)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_edit)
        memory_layout.addWidget(memory_total_label)
        overallgrid.addLayout(memory_layout, curRow, 0)
        curRow += 1
        
        TV_group = QGroupBox("Total Variation")
        TV_group.setToolTip("Using 26 neighbors produces better results,\nbut computations take about twice as long as using only 6 neighbors")
        TV_layout = QGridLayout()
        numTVneighbors_label = QLabel("<div align='right'>number of neighbors</div>") #set_numTVneighbors
        self.numTVneighbors_combo = QComboBox()
        self.numTVneighbors_combo.addItems(["6","26"])
        if self.leapct.get_numTVneighbors() == 6:
            self.numTVneighbors_combo.setCurrentIndex(0)
        else:
            self.numTVneighbors_combo.setCurrentIndex(1)
        self.numTVneighbors_combo.currentIndexChanged.connect(self.numTVneighbors_combo_selectionchange)
        TV_layout.addWidget(numTVneighbors_label, 0, 0)
        TV_layout.addWidget(self.numTVneighbors_combo, 0, 1)
        TV_group.setLayout(TV_layout)
        overallgrid.addWidget(TV_group, curRow, 0)
        curRow += 1
        
        backprojector_group = QGroupBox("Backprojector Model")
        backprojector_group.setToolTip("SF backprojection is more accurate and causes the projectors to be \"matched\",\nbut VD backprojection is about twice as fast.")
        backprojector_layout = QGridLayout()
        self.backprojector_SF_radio = QRadioButton("SF")
        self.backprojector_VD_radio = QRadioButton("VD")
        self.backprojector_SF_radio.clicked.connect(self.push_backprojector_SF_radio)
        self.backprojector_VD_radio.clicked.connect(self.push_backprojector_VD_radio)
        if self.leapct.get_projector() == 'VD':
            self.backprojector_VD_radio.setChecked(True)
        else:
            self.backprojector_SF_radio.setChecked(True)
        backprojector_layout.addWidget(self.backprojector_SF_radio, 0, 0)
        backprojector_layout.addWidget(self.backprojector_VD_radio, 0, 1)
        backprojector_group.setLayout(backprojector_layout)
        overallgrid.addWidget(backprojector_group, curRow, 0)
        curRow += 1
        
        logging_group = QGroupBox("logging level")
        logging_group.setToolTip("specifies the level of detail given in print statements")
        logging_layout = QGridLayout()
        self.log_debug_radio = QRadioButton("debug")
        self.log_status_radio = QRadioButton("status")
        self.log_warning_radio = QRadioButton("warning")
        self.log_error_radio = QRadioButton("error")
        self.log_debug_radio.clicked.connect(self.push_log_debug_radio)
        self.log_status_radio.clicked.connect(self.push_log_status_radio)
        self.log_warning_radio.clicked.connect(self.push_log_warning_radio)
        self.log_error_radio.clicked.connect(self.push_log_error_radio)
        self.log_status_radio.setChecked(True)
        logging_layout.addWidget(self.log_debug_radio, 0, 0)
        logging_layout.addWidget(self.log_status_radio, 0, 1)
        logging_layout.addWidget(self.log_warning_radio, 1, 0)
        logging_layout.addWidget(self.log_error_radio, 1, 1)
        logging_group.setLayout(logging_layout)
        overallgrid.addWidget(logging_group, curRow, 0)
        curRow += 1
        
        ######### COMPRESS VOLUME FILE START #########
        #"""
        compress_file_group = QGroupBox("Compress/ Quantize Volume TIFF Sequence")
        compress_file_group.setToolTip("this feature re-saves the volume TIFF file sequence using different levels of bit depth")
        compress_file_layout = QHBoxLayout()
        self.file_dtype_combo = QComboBox()
        self.file_dtype_combo.addItem("uint8")
        self.file_dtype_combo.addItem("uint16")
        self.file_dtype_combo.addItem("float32")
        self.file_dtype_combo.setCurrentIndex(1)
        #self.file_dtype_combo.currentIndexChanged.connect(self.file_dtype_combo_selectionchange)
        window_label = QLabel("<div align='right'>window:</div>")
        window_label.setToolTip("We highly recommend specifying a minimum and maximum value for consistency across slices.\nThe maximum value of the volume is printed to the screen after reconstruction completes.")
        to_label = QLabel("to")
        self.wmin_edit = QLineEdit()
        #self.wmin_edit.setText("0.0")
        self.wmax_edit = QLineEdit()
        self.compress_button = QPushButton("compress")
        self.compress_button.clicked.connect(self.compress_button_Clicked)
        if self.lctserver.reconstruction_file is None or len(self.lctserver.reconstruction_file) == 0:
            self.compress_button.setEnabled(False)
            self.compress_button.setToolTip("reconstruction_file not defined")
        #self.wmin_edit.editingFinished.connect(self.push_wmin)
        #self.wmax_edit.editingFinished.connect(self.push_wmax)
        if self.leapct.wmin is not None:
            self.wmin_edit.setText(str(self.leapct.wmin))
        if self.leapct.wmax is not None:
            self.wmax_edit.setText(str(self.leapct.wmax))
        compress_file_layout.addWidget(self.file_dtype_combo)
        compress_file_layout.addWidget(window_label)
        compress_file_layout.addWidget(self.wmin_edit)
        compress_file_layout.addWidget(to_label)
        compress_file_layout.addWidget(self.wmax_edit)
        compress_file_layout.addWidget(self.compress_button)
        compress_file_group.setLayout(compress_file_layout)
        overallgrid.addWidget(compress_file_group, curRow, 0)
        curRow += 1
        #"""
        
        bottum_button_layout = QHBoxLayout()
        self.keyboard_button = QPushButton("keyboard")
        self.save_defaults_button = QPushButton("save defaults")
        self.keyboard_button.clicked.connect(self.keyboard_button_Clicked)
        self.save_defaults_button.clicked.connect(self.save_defaults_button_Clicked)
        bottum_button_layout.addWidget(self.keyboard_button)
        bottum_button_layout.addWidget(self.save_defaults_button)
        overallgrid.addLayout(bottum_button_layout, curRow, 0)
        curRow += 1
        
        self.setLayout(overallgrid)
        #self.resize(500,300)
        self.refresh()

    def compress_button_Clicked(self):
        if len(self.wmin_edit.text()) > 0:
            try:
                wmin = float(self.wmin_edit.text())
            except:
                wmin = None
        else:
            wmin = self.leapct.wmin
        if len(self.wmax_edit.text()) > 0:
            try:
                wmax = float(self.wmax_edit.text())
            except:
                wmax = None
        else:
            wmax = self.leapct.wmax
        if self.file_dtype_combo.currentIndex() == 0:
            dtype = np.uint8
        elif self.file_dtype_combo.currentIndex() == 1:
            dtype = np.uint16
        else:
            dtype = np.float32
        #print('wmin = ', wmin)
        #print('wmax = ', wmax)
        #self.leapct.set_fileIO_parameters(dtype, wmin, wmax)
        print('compressing volume file sequence...')
        self.lctserver.compress_volume(dtype, wmin, wmax)
        #self.leapct.file_dtype = np.float32
    
    def push_backprojector_SF_radio(self):
        self.leapct.set_projector('SF')
    
    def push_backprojector_VD_radio(self):
        self.leapct.set_projector('VD')
    
    def numTVneighbors_combo_selectionchange(self):
        if self.numTVneighbors_combo.currentIndex() == 0:
            self.leapct.set_numTVneighbors(6)
        else:
            self.leapct.set_numTVneighbors(26)
    
    def refresh(self):
        gpuList = self.leapct.get_gpus()
        if 0 in gpuList:
            self.gpu_one_check.setChecked(True)
        else:
            self.gpu_one_check.setChecked(False)
        if 1 in gpuList:
            self.gpu_two_check.setChecked(True)
        else:
            self.gpu_two_check.setChecked(False)
        if 2 in gpuList:
            self.gpu_three_check.setChecked(True)
        else:
            self.gpu_three_check.setChecked(False)
        if 3 in gpuList:
            self.gpu_four_check.setChecked(True)
        else:
            self.gpu_four_check.setChecked(False)
        self.memory_edit.setText(str(self.lctserver.max_CPU_memory_usage))
        
    def save_defaults_button_Clicked(self):
        self.lctserver.save_defaults()
    
    def gpu_clicked(self):
        gpuList = []
        if self.gpu_one_check.isChecked():
            gpuList.append("0")
        if self.gpu_two_check.isChecked():
            gpuList.append("1")
        if self.gpu_three_check.isChecked():
            gpuList.append("2")
        if self.gpu_four_check.isChecked():
            gpuList.append("3")
        if len(gpuList) == 0:
            gpuList.append("-1")
        self.leapct.set_gpus(gpuList)
        
    def push_memory(self):
        if len(self.memory_edit.text()) > 0:
            try:
                val = float(self.memory_edit.text())
                if val > 0.0:
                    self.lctserver.max_CPU_memory_usage = val
            except:
                pass
        
    def push_log_debug_radio(self):
        self.leapct.set_log_debug()
        
    def push_log_status_radio(self):
        self.leapct.set_log_status()
        
    def push_log_warning_radio(self):
        self.leapct.set_log_warning()
        
    def push_log_error_radio(self):
        self.leapct.set_log_error()
        
    def keyboard_button_Clicked(self):
        leapct = self.leapct
        lctserver = self.lctserver
        print("You have entered the LEAP-CT debugging mode, enter \"c\" to return control to the GUI")
        breakpoint()
        
class SettingsDialog(QDialog):
    def __init__(self, title, parent = None):
        super(SettingsDialog, self).__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle(title)

        self.parent = parent
        self.lctserver = self.parent.lctserver
        self.leapct = self.lctserver.leapct

        # Instantiate the volume controls widget, passing this class as the parent:
        self.controls = SettingsDialogControls(self)
        overallGrid = QGridLayout()
        overallGrid.addWidget(self.controls, 0, 0)
        self.setLayout(overallGrid)
        