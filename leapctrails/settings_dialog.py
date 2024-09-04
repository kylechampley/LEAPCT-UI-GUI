
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
        self.memory_edit = QLineEdit()
        memory_total_label = QLabel("(total: " + str(np.floor(self.lctserver.total_RAM())) + " GB)")
        self.memory_edit.editingFinished.connect(self.push_memory)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_edit)
        memory_layout.addWidget(memory_total_label)
        overallgrid.addLayout(memory_layout, curRow, 0)
        curRow += 1
        
        logging_group = QGroupBox("logging level")
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
        
        self.keyboard_button = QPushButton("keyboard")
        self.keyboard_button.clicked.connect(self.keyboard_button_Clicked)
        overallgrid.addWidget(self.keyboard_button, curRow, 0)
        curRow += 1
        
        self.setLayout(overallgrid)
        #self.resize(500,300)
        self.refresh()

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
        