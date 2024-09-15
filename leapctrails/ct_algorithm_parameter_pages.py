from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

import os
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
from leapctserver import *

from help_preview_execute_button_box import *
from progress_dialog import *


class AlgorithmParameterPage(QWidget):
    """ 
    This is the base class for all of the algorithm control pages i.e. the
    widgets that allow the user to set the parameters for each algorithm.
    """

    def __init__(self, parent = None):
        super(AlgorithmParameterPage, self).__init__(parent)

        self.parent = parent
        self.lctserver = self.parent.lctserver
        self.leapct = self.parent.leapct
        self.computeState = 0

        # Add an instance of "HelpPreviewExecuteButtonBox" that all inheriting algorithm classes will use:
        self.buttonBox = HelpPreviewExecuteButtonBox(self)
      
    def previewAlgorithm(self):
        tryIndex = self.buttonBox.get_previewIndex()
        if tryIndex is None:
            tryIndex = -1
        self.execute_algorithm(tryIndex)
        if self.lctserver.lastImage is not None:
            plt.imshow(self.lctserver.lastImage, cmap='gray', interpolation='nearest')
            plt.show()

    def executeAlgorithm(self):
        print("AlgorithmParameterPage::executeAlgorithm!")
        
    def completedSuccessfully(self):
        self.buttonBox.previewButton.setEnabled(False)
        self.buttonBox.executeButton.setEnabled(False)
        self.computeState = 1

    
class MakeAttenuationRadiographsParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(MakeAttenuationRadiographsParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        
        self.ROI_group = QGroupBox("Apply Flux Correction")
        self.ROI_group.setCheckable(True)
        self.ROI_group.setChecked(False)
        ROI_layout = QGridLayout()
        rows_label = QLabel("Rows:")
        cols_label = QLabel("Cols:")
        to_label = QLabel("to")
        to_col_label = QLabel("to")
        self.row_lo_edit = QLineEdit()
        self.row_hi_edit = QLineEdit()
        self.col_lo_edit = QLineEdit()
        self.col_hi_edit = QLineEdit()
        ROI_layout.addWidget(rows_label, 0, 0)
        ROI_layout.addWidget(self.row_lo_edit, 0, 1)
        ROI_layout.addWidget(to_label, 0, 2)
        ROI_layout.addWidget(self.row_hi_edit, 0, 3)
        ROI_layout.addWidget(cols_label, 1, 0)
        ROI_layout.addWidget(self.col_lo_edit, 1, 1)
        ROI_layout.addWidget(to_col_label, 1, 2)
        ROI_layout.addWidget(self.col_hi_edit, 1, 3)
        self.ROI_group.setLayout(ROI_layout)
        
        show_stack_button = QPushButton("show stacked projection")
        show_stack_button.clicked.connect(self.show_stack_button_Clicked)
        
        overall_layout.addWidget(self.ROI_group)
        overall_layout.addWidget(show_stack_button)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
        
    def show_stack_button_Clicked(self):
        g_stack = self.lctserver.stacked_projection()
        if g_stack is not None:
            plt.imshow(g_stack, cmap='gray', interpolation='nearest')
            plt.show()
            
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/preprocessing_algorithms.html#leap_preprocessing_algorithms.makeAttenuationRadiographs')

    def preview_button_Clicked(self):
        if self.computeState == 0:
            self.previewAlgorithm()
        
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self, tryIndex=None):
        if len(self.row_lo_edit.text()) > 0 and len(self.row_hi_edit.text()) > 0 and len(self.col_lo_edit.text()) > 0 and len(self.col_hi_edit.text()) > 0:
            try:
                ROI = [int(self.row_lo_edit.text()), int(self.row_hi_edit.text()), int(self.col_lo_edit.text()), int(self.col_hi_edit.text())]
            except:
                ROI = None
        else:
            ROI = None
            
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
            
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing makeAttenuationRadiographs...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("makeAttenuationRadiographs...")
        if self.lctserver.makeAttenuationRadiographs(ROI, tryIndex):
            if tryIndex is None:
                self.completedSuccessfully()
        
        progressDialog.close()
        QApplication.restoreOverrideCursor()
        
class CropProjectionsParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(CropProjectionsParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        
        ROI_layout = QGridLayout()
        rows_label = QLabel("Rows:")
        cols_label = QLabel("Cols:")
        to_label = QLabel("to")
        to_col_label = QLabel("to")
        self.row_lo_edit = QLineEdit()
        self.row_hi_edit = QLineEdit()
        self.col_lo_edit = QLineEdit()
        self.col_hi_edit = QLineEdit()
        ROI_layout.addWidget(rows_label, 0, 0)
        ROI_layout.addWidget(self.row_lo_edit, 0, 1)
        ROI_layout.addWidget(to_label, 0, 2)
        ROI_layout.addWidget(self.row_hi_edit, 0, 3)
        ROI_layout.addWidget(cols_label, 1, 0)
        ROI_layout.addWidget(self.col_lo_edit, 1, 1)
        ROI_layout.addWidget(to_col_label, 1, 2)
        ROI_layout.addWidget(self.col_hi_edit, 1, 3)
        #self.ROI_group.setLayout(ROI_layout)
        
        show_stack_button = QPushButton("show stacked projection")
        show_stack_button.clicked.connect(self.show_stack_button_Clicked)
        
        overall_layout.addLayout(ROI_layout, 0, 0)
        overall_layout.addWidget(show_stack_button, 1, 0)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(False)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
        
    def show_stack_button_Clicked(self):
        g_stack = self.lctserver.stacked_projection()
        if g_stack is not None:
            plt.imshow(g_stack, cmap='gray', interpolation='nearest')
            plt.show()
            
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/projection_filters_and_transforms.html#leapctype.tomographicModels.crop_projections')

    def preview_button_Clicked(self):
        pass
        
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self):
        if len(self.row_lo_edit.text()) > 0 and len(self.row_hi_edit.text()) > 0:
            try:
                rowRange = [int(self.row_lo_edit.text()), int(self.row_hi_edit.text())]
            except:
                rowRange = None
        else:
            rowRange = None
            
        if len(self.col_lo_edit.text()) > 0 and len(self.col_hi_edit.text()) > 0:
            try:
                colRange = [int(self.col_lo_edit.text()), int(self.col_hi_edit.text())]
            except:
                colRange = None
        else:
            colRange = None
            
        if rowRange is None and colRange is None:
            return
            
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
            
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing crop_projections...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("crop_projections...")
        if self.lctserver.crop_projections(rowRange, colRange):
            self.completedSuccessfully()
        
        progressDialog.close()
        QApplication.restoreOverrideCursor()
        
class OutlierCorrectionParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(OutlierCorrectionParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        
        threshold_label = QLabel("threshold")
        self.threshold_edit = QLineEdit("0.03")
        windowSize_label = QLabel("window size")
        #self.windowSize_edit = QLineEdit()
        self.windowSize_combo = QComboBox()
        self.windowSize_combo.addItems(["3x3", "5x5", "7x7"])
        self.three_stage_filtering_check = QCheckBox("3-stage filtering")

        overall_layout.addWidget(threshold_label, 0, 0)
        overall_layout.addWidget(self.threshold_edit, 0, 1)
        overall_layout.addWidget(windowSize_label, 1, 0)
        overall_layout.addWidget(self.windowSize_combo, 1, 1)
        overall_layout.addWidget(self.three_stage_filtering_check, 2, 0)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
        
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/preprocessing_algorithms.html#leap_preprocessing_algorithms.outlierCorrection')
    
    def preview_button_Clicked(self):
        self.previewAlgorithm()
        
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self, tryIndex=None):
        if len(self.threshold_edit.text()) > 0:
            try:
                threshold = float(self.threshold_edit.text())
            except:
                threshold = 0.03
        else:
            threshold = 0.03
            
        if self.windowSize_combo.currentIndex() == 0:
            windowSize = 3
        elif self.windowSize_combo.currentIndex() == 1:
            windowSize = 5
        else:
            windowSize = 7
    
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing outlierCorrection...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        if self.three_stage_filtering_check.isChecked():
            print("outlierCorrection_highEnergy...")
            if self.lctserver.outlierCorrection_highEnergy(tryIndex):
                if tryIndex is None:
                    self.completedSuccessfully()
        else:
            print("outlierCorrection...")
            if self.lctserver.outlierCorrection(threshold, windowSize, tryIndex):
                if tryIndex is None:
                    self.completedSuccessfully()
                    
        progressDialog.close()
        QApplication.restoreOverrideCursor()
        

class FindCenterColParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(FindCenterColParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        
        row_index_label = QLabel("detector row index")
        self.row_index_edit = QLineEdit()

        overall_layout.addWidget(row_index_label, 0, 0)
        overall_layout.addWidget(self.row_index_edit, 0, 1)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(False)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
        
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/ctgeometries.html#leapctype.tomographicModels.find_centerCol')
    
    def preview_button_Clicked(self):
        pass
        
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self):
    
        if len(self.row_index_edit.text()) > 0:
            try:
                iRow = int(self.row_index_edit.text())
            except:
                iRow = None
        else:
            iRow = None
    
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing find_centerCol...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("find_centerCol...")
        if self.lctserver.find_centerCol(iRow):
            self.completedSuccessfully()
        
        progressDialog.close()
        QApplication.restoreOverrideCursor()
        

class EstimateDetectorTiltParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(EstimateDetectorTiltParametersPage, self).__init__(parent)
        
        self.parent = parent
        
        overall_layout = QGridLayout()
        
        tilt_label = QLabel("<div align='right'>tilt (degrees)</div>")
        self.tilt_edit = QLineEdit("0.0")
        centerCol_label = QLabel("<div align='right'>centerCol</div>")
        self.centerCol_edit = QLineEdit(str(self.leapct.get_centerCol()))
        conjugate_difference_button = QPushButton("display conjugate difference")
        self.tilt_edit.setMaximumWidth(50)
        conjugate_difference_button.setMaximumWidth(200)
        conjugate_difference_button.clicked.connect(self.conjugate_difference_button_clicked)
        auto_estimate_button = QPushButton("auto estimate")
        auto_estimate_button.clicked.connect(self.auto_estimate_button_clicked)
        overall_layout.addWidget(tilt_label, 0, 0)
        overall_layout.addWidget(self.tilt_edit, 0, 1)
        overall_layout.addWidget(centerCol_label, 0, 2)
        overall_layout.addWidget(self.centerCol_edit, 0, 3)
        overall_layout.addWidget(conjugate_difference_button, 1, 0, 1, 2)
        overall_layout.addWidget(auto_estimate_button, 1, 2, 1, 2)
        
        overall_layout.setRowStretch(overall_layout.rowCount(), 1)
        overall_layout.setColumnStretch(overall_layout.columnCount(), 1)
        #overall_layout.addStretch(2)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)
        #self.buttonBox.previewButton.setText("Auto Estimate")
        self.buttonBox.executeButton.setText("Done")

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
    
    def get_tilt(self):
        if len(self.tilt_edit.text()) > 0:
            try:
                return float(self.tilt_edit.text())
            except:
                return 0.0
        else:
            return 0.0
            
    def get_centerCol(self):
        if len(self.centerCol_edit.text()) > 0:
            try:
                return float(self.centerCol_edit.text())
            except:
                return self.leapct.get_centerCol()
        else:
            return self.leapct.get_centerCol()
    
    def conjugate_difference_button_clicked(self):
        self.lctserver.conjugate_difference(self.get_tilt(), centerCol=self.get_centerCol())
        if self.lctserver.lastImage is not None:
            plt.imshow(self.lctserver.lastImage, cmap='gray', interpolation='nearest')
            I = self.lctserver.lastImage
            #import scipy
            #I = scipy.ndimage.filters.gaussian_filter(I, 1.0)#, truncate=3.0)
            theError = 100.0*np.sum(I**2) / np.sum(I != 0.0)
            plt.title('Error: ' + str(theError))
            plt.show()
    
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/ctgeometries.html#leapctype.tomographicModels.estimate_tilt')
        
    def auto_estimate_button_clicked(self):
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing estimate_tilt...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("estimate_tilt...")        
        alpha = self.lctserver.estimate_tilt()
        self.tilt_edit.setText(str(f'{alpha:.4f}'))
        
        progressDialog.close()
        QApplication.restoreOverrideCursor()
    
    def preview_button_Clicked(self):
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
        
        if len(self.buttonBox.previewIndex.text()) > 0:
            try:
                ind = int(self.buttonBox.previewIndex.text())
            except:
                ind = None
        else:
            ind = None
        
        #QApplication.setOverrideCursor(Qt.WaitCursor)
        #progressDialog = ProgressDialog(self.parent, "processing parameter_sweep...")
        #progressDialog.setModal(True)
        #progressDialog.show()
        
        self.leapct.set_centerCol(self.get_centerCol())
        self.lctserver.parameter_sweep(np.array([self.get_tilt()]), param='tilt', iz=ind, algorithmName='FBP')
        
        #progressDialog.close()
        #QApplication.restoreOverrideCursor()
    
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self):
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return

        self.leapct.set_centerCol(self.get_centerCol())
        alpha = self.get_tilt()
        if alpha != 0.0:
            print("WARNING: converting to modular-beam data in order to model detector tilt")
            self.lctserver.leapct.convert_to_modularbeam()
            self.lctserver.leapct.rotate_detector(alpha)
                
        self.completedSuccessfully()

    
class RingRemovalParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(RingRemovalParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        
        #num iter, max change, delta
        numIter_label = QLabel("Number of Iterations")
        self.numIter_edit = QLineEdit("30")
        maxChange_label = QLabel("Max Change (%)")
        self.maxChange_edit = QLineEdit("0.05")
        delta_label = QLabel("delta")
        self.delta_edit = QLineEdit("0.01")
        
        overall_layout.addWidget(numIter_label, 0, 0)
        overall_layout.addWidget(self.numIter_edit, 0, 1)
        overall_layout.addWidget(maxChange_label, 1, 0)
        overall_layout.addWidget(self.maxChange_edit, 1, 1)
        overall_layout.addWidget(delta_label, 2, 0)
        overall_layout.addWidget(self.delta_edit, 2, 1)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
    
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/preprocessing_algorithms.html#leap_preprocessing_algorithms.ringRemoval_fast')
    
    def preview_button_Clicked(self):
        self.previewAlgorithm()
        
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self, tryIndex=None):
    
        if len(self.numIter_edit.text()) > 0:
            try:
                numIter = int(self.numIter_edit.text())
            except:
                numIter = 30
        else:
            numIter = 30
            
        if len(self.maxChange_edit.text()) > 0:
            try:
                maxChange = float(self.maxChange_edit.text())
            except:
                maxChange = 0.05
        else:
            maxChange = 0.05
            
        if len(self.delta_edit.text()) > 0:
            try:
                delta = float(self.delta_edit.text())
            except:
                delta = 0.01
        else:
            delta = 0.01
    
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing ringRemoval...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("ringRemoval_fast...")
        if self.lctserver.ringRemoval_fast(delta, numIter, maxChange, tryIndex):
            if tryIndex is None:
                self.completedSuccessfully()
        
        progressDialog.close()
        QApplication.restoreOverrideCursor()


class BeamHardeningCorrectionParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(BeamHardeningCorrectionParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        
        correction_type_group = QGroupBox("Method")
        correction_type_layout = QVBoxLayout()
        self.polynomial_radio = QRadioButton("polynomial")
        self.physics_radio = QRadioButton("physics-based")
        correction_type_layout.addWidget(self.physics_radio)
        correction_type_layout.addWidget(self.polynomial_radio)
        correction_type_group.setLayout(correction_type_layout)
        self.polynomial_radio.clicked.connect(self.polynomial_radio_Clicked)
        self.physics_radio.clicked.connect(self.physics_radio_Clicked)
        
        self.polynomial_group = QGroupBox()
        polynomial_layout = QHBoxLayout()
        self.coeff_one_edit = QLineEdit("1.0")
        x_label = QLabel("x +")
        self.coeff_two_edit = QLineEdit("0.0")
        x_2_label = QLabel("x^2 +")
        self.coeff_three_edit = QLineEdit("0.0")
        x_3_label = QLabel("x^3")
        self.coeff_one_edit.setMaximumWidth(40)
        self.coeff_two_edit.setMaximumWidth(40)
        self.coeff_three_edit.setMaximumWidth(40)
        polynomial_layout.addWidget(self.coeff_one_edit)
        polynomial_layout.addWidget(x_label)
        polynomial_layout.addWidget(self.coeff_two_edit)
        polynomial_layout.addWidget(x_2_label)
        polynomial_layout.addWidget(self.coeff_three_edit)
        polynomial_layout.addWidget(x_3_label)
        self.polynomial_group.setLayout(polynomial_layout)
        physics_button = QPushButton("Set Spectra and Object Model")
        if has_physics:
            physics_button.setEnabled(True)
        else:
            physics_button.setEnabled(False)
        
        overall_layout.addWidget(correction_type_group, 0, 0)
        overall_layout.addWidget(self.polynomial_group, 1, 0)
        overall_layout.addWidget(physics_button, 2, 0)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        if self.lctserver.source_spectra_defined():
            self.physics_radio.setChecked(True)
            self.physics_radio_Clicked()
        else:
            self.polynomial_radio.setChecked(True)
            self.polynomial_radio_Clicked()
        
        physics_button.clicked.connect(self.physics_button_Clicked)
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
    
    def polynomial_radio_Clicked(self):
        self.polynomial_group.setEnabled(True)
        
    def physics_radio_Clicked(self):
        self.polynomial_group.setEnabled(False)
    
    def help_button_Clicked(self):
        #webbrowser.open('')
        pass
    
    def physics_button_Clicked(self):
        self.parent.parent.workflowControls.workflowStackControl.fileNamesPage.physics_button_Clicked()
    
    def preview_button_Clicked(self):
        self.previewAlgorithm()
        
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self, tryIndex=None):
    
        if len(self.coeff_one_edit.text()) > 0:
            try:
                coeff_one = float(self.coeff_one_edit.text())
            except:
                coeff_one = 0.0
        else:
            coeff_one = 0.0
            
        if len(self.coeff_two_edit.text()) > 0:
            try:
                coeff_two = float(self.coeff_two_edit.text())
            except:
                coeff_two = 0.0
        else:
            coeff_two = 0.0
            
        if len(self.coeff_three_edit.text()) > 0:
            try:
                coeff_three = float(self.coeff_three_edit.text())
            except:
                coeff_three = 0.0
        else:
            coeff_three = 0.0
            
        if coeff_three != 0.0:
            coeffs = [coeff_one, coeff_two, coeff_three]
        else:
            coeffs = [coeff_one, coeff_two]
        coeffs = np.array(coeffs, dtype=np.float32)
    
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing BHC...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        if self.polynomial_radio.isChecked():
            print("polynomialBHC...")
            if self.lctserver.polynomialBHC(coeffs, tryIndex=tryIndex):
                if tryIndex is None:
                    self.completedSuccessfully()
        else:
            print("singleMaterialBHC...")
            if self.lctserver.singleMaterialBHC(tryIndex=tryIndex):
                if tryIndex is None:
                    self.completedSuccessfully()
        
        progressDialog.close()
        QApplication.restoreOverrideCursor()
        
        
class ParameterSweepParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(ParameterSweepParametersPage, self).__init__(parent)
        
        self.parent = parent
        
        overall_layout = QGridLayout()
        
        type_label = QLabel("<div align='right'>parameter:</div>")
        number_of_samples_label = QLabel("<div align='right'>number of samples:</div>")
        window_label = QLabel("<div align='right'>window radius</div>")
        self.type_combo = QComboBox()
        if self.leapct.get_geometry() == 'MODULAR':
            self.type_combo.addItems(["horizontal_shift", "vertical_shift", "tau", "tilt"])
        else:
            self.type_combo.addItems(["centerCol", "centerRow", "tau", "tilt"])
        self.number_of_samples_combo = QComboBox()
        self.number_of_samples_combo.addItems(["3", "5", "7", "9", "11", "13", "15"])
        self.window_edit = QLineEdit("1.0")
        self.window_edit.setMaximumWidth(60)
        algorithm_label = QLabel("<div align='right'>algorithm</div>")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["FBP", "inconsistency"])
        overall_layout.addWidget(type_label, 0, 0)
        overall_layout.addWidget(self.type_combo, 0, 1)
        overall_layout.addWidget(number_of_samples_label, 1, 0)
        overall_layout.addWidget(self.number_of_samples_combo, 1, 1)
        overall_layout.addWidget(window_label, 2, 0)
        overall_layout.addWidget(self.window_edit, 2, 1)
        overall_layout.addWidget(algorithm_label, 3, 0)
        overall_layout.addWidget(self.algorithm_combo, 3, 1)
        
        overall_layout.setRowStretch(overall_layout.rowCount(), 1)
        overall_layout.setColumnStretch(overall_layout.columnCount(), 1)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)
        self.buttonBox.previewButton.setText("Recon Sequence")
        self.buttonBox.executeButton.setText("Done")

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
        
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/preprocessing_algorithms.html#leap_preprocessing_algorithms.parameter_sweep')
        
    def preview_button_Clicked(self):

        geom_text = self.leapct.get_geometry()
        if geom_text == 'MODULAR':
            self.type_combo.setItemText(0, 'horizontal_shift')
            self.type_combo.setItemText(1, 'vertical_shift')
        else:
            self.type_combo.setItemText(0, 'centerCol')
            self.type_combo.setItemText(1, 'centerRow')
    
        
        type_text = self.type_combo.currentText()
        """
        geom_text = self.leapct.get_geometry()
        if geom_text == 'MODULAR':
            if type_text == 'centerCol':
                type_text = 'horizontal_shift'
            elif type_text == 'centerRow':
                type_text = 'vertical_shift'
        else:
            if type_text == 'horizontal_shift':
                type_text = 'centerCol'
            elif type_text == 'vertical_shift':
                type_text = 'centerRow'
        """
    
        if self.parent.runningPreviousAlgorithms == False:
            self.parent.runPreviousAlgorithms()

        if len(self.buttonBox.previewIndex.text()) > 0:
            try:
                ind = int(self.buttonBox.previewIndex.text())
            except:
                ind = None
        else:
            ind = None
            
        count = int(self.number_of_samples_combo.currentText())
        
        if len(self.window_edit.text()) > 0:
            try:
                window_radius = float(self.window_edit.text())
            except:
                window_radius = 0.5*(count-1)
        else:
            window_radius = 0.5*(count-1)
            
        values = (np.array(range(count))-0.5*(count-1)) * window_radius / (0.5*(count-1))
        if type_text == 'centerCol':
            values += self.leapct.get_centerCol()
        elif type_text == 'centerRow':
            values += self.leapct.get_centerRow()
        elif type_text == 'tau':
            values += self.leapct.get_tau()
        
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing parameter_sweep...")
        progressDialog.setModal(True)
        progressDialog.show()
        """
        
        self.lctserver.parameter_sweep(values, param=type_text, iz=ind, algorithmName=self.algorithm_combo.currentText())
        
        #progressDialog.close()
        #QApplication.restoreOverrideCursor()
    
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self):
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
        self.completedSuccessfully()


class SaveProjectionDataParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(SaveProjectionDataParametersPage, self).__init__(parent)
        
        self.parent = parent
        
        overall_layout = QGridLayout()
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)
        
        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(False)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
        
    def help_button_Clicked(self):
        pass
        
    def preview_button_Clicked(self):
        pass
    
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self):
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "saving projection data...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        if self.lctserver.save_projection_angles(update_params=True) is not None:
            self.lctserver.save_parameters()
            self.completedSuccessfully()
            
        progressDialog.close()
        QApplication.restoreOverrideCursor()


class FBPParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(FBPParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        self.do_clipping_check = QCheckBox("clipping")
        
        preview_slice_axis_label = QLabel("<div align='right'>preview slice axis</div>")
        self.preview_slice_axis_combo = QComboBox()
        self.preview_slice_axis_combo.addItems(['x','y','z'])
        self.preview_slice_axis_combo.setMaximumWidth(30)
        self.preview_slice_axis_combo.setCurrentIndex(2)
        overall_layout.addWidget(self.do_clipping_check, 0, 0)
        overall_layout.addWidget(preview_slice_axis_label, 1, 0)
        overall_layout.addWidget(self.preview_slice_axis_combo, 1, 1)
        
        overall_layout.setRowStretch(overall_layout.rowCount(), 1)
        overall_layout.setColumnStretch(overall_layout.columnCount(), 1)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
        
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/fbp.html#leapctype.tomographicModels.FBP')
        
    def preview_button_Clicked(self):
    
        if self.parent.runningPreviousAlgorithms == False:
            self.parent.runPreviousAlgorithms()
    
        if len(self.buttonBox.previewIndex.text()) > 0:
            try:
                ind = int(self.buttonBox.previewIndex.text())
            except:
                ind = None
        else:
            ind = None
        if self.preview_slice_axis_combo.currentIndex() == 0:
            axis_name = 'x'
        elif self.preview_slice_axis_combo.currentIndex() == 1:
            axis_name = 'y'
        else:
            axis_name = 'z'
        f_slice = self.lctserver.FBP_slice(islice=ind, coord=axis_name)
        if self.do_clipping_check.isChecked():
            f_slice[f_slice<0.0] = 0.0
        plt.imshow(np.squeeze(f_slice), cmap='gray', interpolation='nearest')
        plt.show()
    
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self):
    
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing FBP...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("FBP...")
        if self.lctserver.FBP(self.do_clipping_check.isChecked()):
            self.completedSuccessfully()
            
        progressDialog.close()
        QApplication.restoreOverrideCursor()
        
        if self.lctserver.f is not None:
            self.leapct.display(self.lctserver.f)
    

class MedianFilterParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(MedianFilterParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        curRow = 0
        
        num_dim_group = QGroupBox("Dimensions")
        num_dim_layout = QVBoxLayout()
        self.threeD_radio = QRadioButton("3D")
        self.twoD_radio = QRadioButton("2D")
        self.threeD_radio.setChecked(True)
        self.threeD_radio.clicked.connect(self.threeD_radio_Clicked)
        self.twoD_radio.clicked.connect(self.twoD_radio_Clicked)
        num_dim_layout.addWidget(self.threeD_radio)
        num_dim_layout.addWidget(self.twoD_radio)
        num_dim_group.setLayout(num_dim_layout)
        
        threshold_label = QLabel("threshold")
        self.threshold_edit = QLineEdit("0.0")
        windowSize_label = QLabel("window size")
        self.windowSize_combo = QComboBox()
        self.windowSize_combo.addItems(["3x3x3","3x5x5"])
        
        overall_layout.addWidget(num_dim_group, 0, 0, 2, 1)
        overall_layout.addWidget(threshold_label, 0, 1)
        overall_layout.addWidget(self.threshold_edit, 0, 2)
        overall_layout.addWidget(windowSize_label, 1, 1)
        overall_layout.addWidget(self.windowSize_combo, 1, 2)
        
        overall_layout.setRowStretch(overall_layout.rowCount(), 1)
        overall_layout.setColumnStretch(overall_layout.columnCount(), 1)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
    
    def threeD_radio_Clicked(self):
        self.windowSize_combo.setItemText(0, "3x3x3")
        self.windowSize_combo.setItemText(1, "3x5x5")
    
    def twoD_radio_Clicked(self):
        self.windowSize_combo.setItemText(0, "3x3")
        self.windowSize_combo.setItemText(1, "5x5")
    
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/filters.html#leapctype.tomographicModels.MedianFilter')
        
    def preview_button_Clicked(self):
        self.previewAlgorithm()
    
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self, tryIndex=None):
        if len(self.threshold_edit.text()) > 0:
            try:
                threshold = float(self.threshold_edit.text())
            except:
                threshold = 0.0
        else:
            threshold = 0.0
            
        if self.windowSize_combo.currentIndex() == 0:
            windowSize = 3
        elif self.windowSize_combo.currentIndex() == 1:
            windowSize = 5
    
        if self.parent.runningPreviousAlgorithms == False:
            if self.parent.runPreviousAlgorithms() == False:
                return
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing MedianFilter...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("medianFilter...")
        if self.threeD_radio.isChecked():
            if self.lctserver.MedianFilter(threshold, windowSize, tryIndex):
                if tryIndex is None:
                    self.completedSuccessfully()
        else:
            if self.lctserver.MedianFilter2D(threshold, windowSize, tryIndex):
                if tryIndex is None:
                    self.completedSuccessfully()
        
        progressDialog.close()
        QApplication.restoreOverrideCursor()
        
        if tryIndex is None and self.lctserver.f is not None:
            self.leapct.display(self.lctserver.f)
        

class TVdenoisingParametersPage(AlgorithmParameterPage):
    def __init__(self, parent = None):
        super(TVdenoisingParametersPage, self).__init__(parent)

        self.parent = parent
        
        overall_layout = QGridLayout()
        curRow = 0
        
        delta_label = QLabel("<div align='right'>delta</div>")
        beta_label = QLabel("<div align='right'>beta</div>")
        numIter_label = QLabel("<div align='right'>num iter</div>")
        p_label = QLabel("<div align='right'>p</div>")
        self.delta_edit = QLineEdit("0.001")
        self.beta_edit = QLineEdit("1.0e-1")
        self.numIter_edit = QLineEdit("20")
        self.p_edit = QLineEdit("1.2")
        overall_layout.addWidget(delta_label, 0, 0)
        overall_layout.addWidget(self.delta_edit, 0, 1)
        overall_layout.addWidget(beta_label, 1, 0)
        overall_layout.addWidget(self.beta_edit, 1, 1)
        overall_layout.addWidget(numIter_label, 2, 0)
        overall_layout.addWidget(self.numIter_edit, 2, 1)
        overall_layout.addWidget(p_label, 3, 0)
        overall_layout.addWidget(self.p_edit, 3, 1)
        
        overall_layout.setRowStretch(overall_layout.rowCount(), 1)
        overall_layout.setColumnStretch(overall_layout.columnCount(), 1)
        
        # Add the help/preview/execute button box in the lower right corner:
        exe_buttons_layout = QHBoxLayout()
        exe_buttons_layout.addWidget(self.buttonBox)
        exe_buttons_layout.addStretch(1)

        overall_vlayout = QVBoxLayout()
        overall_vlayout.addLayout(overall_layout)
        overall_vlayout.addLayout(exe_buttons_layout)
        overall_vlayout.addStretch(1)

        self.buttonBox.previewButton.setEnabled(True)
        self.setLayout(overall_vlayout)
        
        self.buttonBox.helpButton.clicked.connect(self.help_button_Clicked)
        self.buttonBox.previewButton.clicked.connect(self.preview_button_Clicked)
        self.buttonBox.executeButton.clicked.connect(self.execute_button_Clicked)
    
    def help_button_Clicked(self):
        webbrowser.open('https://leapct.readthedocs.io/en/latest/filters.html#leapctype.tomographicModels.TV_denoise')
        
    def preview_button_Clicked(self):
        self.previewAlgorithm()
    
    def execute_button_Clicked(self):
        if self.computeState == 0:
            self.execute_algorithm()
    
    def execute_algorithm(self, tryIndex=None):
    
        if len(self.delta_edit.text()) > 0:
            try:
                delta = float(self.delta_edit.text())
            except:
                delta = 0.02/20.0
        else:
            delta = 0.02/20.0
            
        if len(self.beta_edit.text()) > 0:
            try:
                beta = float(self.beta_edit.text())
            except:
                beta = 1.0e-1
        else:
            beta = 1.0e-1
            
        if len(self.numIter_edit.text()) > 0:
            try:
                numIter = int(self.numIter_edit.text())
            except:
                numIter = 20
        else:
            numIter = 20
            
        if len(self.p_edit.text()) > 0:
            try:
                p = float(self.p_edit.text())
            except:
                p = 1.2
        else:
            p = 1.2
    
        QApplication.setOverrideCursor(Qt.WaitCursor)
        progressDialog = ProgressDialog(self.parent, "processing TV denoising...")
        progressDialog.setModal(True)
        progressDialog.show()
        
        print("TVdenoising...")
        if self.lctserver.TVdenoising(delta, beta, numIter, p, tryIndex):
            if tryIndex is None:
                self.completedSuccessfully()
                
        progressDialog.close()
        QApplication.restoreOverrideCursor()

        if tryIndex is None and self.lctserver.f is not None:
            self.leapct.display(self.lctserver.f)
        