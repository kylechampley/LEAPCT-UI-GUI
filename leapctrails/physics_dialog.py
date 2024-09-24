
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ctypes
import os
import sys
import matplotlib.pyplot as plt
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

class TableView(QTableWidget):
    def __init__(self, data1, data2, *args):
        QTableWidget.__init__(self, *args)
        self.setWindowTitle("LEAP Material Library")
        self.data1 = data1
        self.data2 = data2
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.resize(750,600)
 
    def setData(self): 
        horHeaders = []
        """
        for n, key in enumerate(sorted(self.data.keys())):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(item)
                self.setItem(m, n, newitem)
        """
        horHeaders.append('material name')
        horHeaders.append('density (g/cm^3)')
        horHeaders.append('chemical formula')
        for n, key in enumerate(self.data1.keys()):
            #horHeaders.append(key)
            #item = self.data1[key]
            #newitem = QTableWidgetItem(item)
            self.setItem(n, 0, QTableWidgetItem(key))
            self.setItem(n, 1, QTableWidgetItem(str(self.data2[key])))
            self.setItem(n, 2, QTableWidgetItem(self.data1[key]))
        self.setHorizontalHeaderLabels(horHeaders)

class PhysicsDialogControls(QWidget):
    def __init__(self, parent = None):
        super(PhysicsDialogControls, self).__init__(parent)

        self.parent = parent
        self.lctserver = self.parent.lctserver
        self.leapct = self.lctserver.leapct
        
        overallgrid = QGridLayout()
        curRow = 0
        
        source_model_type_group = QGroupBox("Method")
        source_model_type_layout = QVBoxLayout()
        self.source_model_type_analytic_radio = QRadioButton("analytic")
        self.source_model_type_file_radio = QRadioButton("file")
        self.source_model_type_analytic_radio.clicked.connect(self.push_analytic_source_model)
        self.source_model_type_file_radio.clicked.connect(self.push_file_source_model)
        source_model_type_layout.addWidget(self.source_model_type_analytic_radio)
        source_model_type_layout.addWidget(self.source_model_type_file_radio)
        source_model_type_group.setLayout(source_model_type_layout)
        overallgrid.addWidget(source_model_type_group, curRow, 0, 2, 1)
        
        self.source_modeling_group = QGroupBox("Source Spectrum Model")
        source_modeling_layout = QGridLayout()
        kV_label = QLabel("kV")
        self.kV_edit = QLineEdit()
        self.kV_edit.editingFinished.connect(self.push_kV)
        takeoff_angle_label = QLabel("takeoff angle (degrees)")
        self.takeoff_angle_edit = QLineEdit()
        self.takeoff_angle_edit.setText("11")
        self.takeoff_angle_edit.editingFinished.connect(self.push_takeoff_angle)
        anode_material_group = QGroupBox("Anode Material")
        anode_material_layout = QGridLayout()
        self.W_anode_radio = QRadioButton("Tungsten (W)")
        self.Mo_anode_radio = QRadioButton("Molybdenum (Mo)")
        self.Au_anode_radio = QRadioButton("Gold (Au)")
        self.Cu_anode_radio = QRadioButton("Copper (Cu)")
        self.W_anode_radio.clicked.connect(self.push_W_anode_radio)
        self.Mo_anode_radio.clicked.connect(self.push_Mo_anode_radio)
        self.Au_anode_radio.clicked.connect(self.push_Au_anode_radio)
        self.Cu_anode_radio.clicked.connect(self.push_Cu_anode_radio)
        self.W_anode_radio.setChecked(True)
        anode_material_layout.addWidget(self.W_anode_radio, 0, 0)
        anode_material_layout.addWidget(self.Mo_anode_radio, 0, 1)
        anode_material_layout.addWidget(self.Au_anode_radio, 1, 0)
        anode_material_layout.addWidget(self.Cu_anode_radio, 1, 1)
        anode_material_group.setLayout(anode_material_layout)
        source_modeling_layout.addWidget(kV_label, 0, 0)
        source_modeling_layout.addWidget(self.kV_edit, 0, 1)
        source_modeling_layout.addWidget(takeoff_angle_label, 1, 0)
        source_modeling_layout.addWidget(self.takeoff_angle_edit, 1, 1)
        source_modeling_layout.addWidget(anode_material_group, 0, 2, 2, 1)
        self.source_modeling_group.setLayout(source_modeling_layout)
        overallgrid.addWidget(self.source_modeling_group, curRow, 1)
        curRow += 1
        
        source_spectra_file_layout = QHBoxLayout()
        self.source_spectra_file_button = QPushButton("Source Spectra File")
        self.source_spectra_file_edit = QLineEdit()
        source_spectra_file_layout.addWidget(self.source_spectra_file_button)
        source_spectra_file_layout.addWidget(self.source_spectra_file_edit)
        self.source_spectra_file_button.clicked.connect(self.source_spectra_file_button_Clicked)
        self.source_spectra_file_edit.editingFinished.connect(self.push_source_spectra_file)
        overallgrid.addLayout(source_spectra_file_layout, curRow, 1)
        curRow += 1
        
        # X-RAY FILTERS
        filters_group = QGroupBox("X-Ray Filters")
        filters_layout = QGridLayout()
        filter_material_label = QLabel("material")
        self.filter_material_edit = QLineEdit()
        filter_density_label = QLabel("density (g/cm^3)")
        self.filter_density_edit = QLineEdit()
        filter_thickness_label = QLabel("thickness (mm)")
        self.filter_thickness_edit = QLineEdit()
        filter_add_button = QPushButton("add filter")
        filter_add_button.setMaximumWidth(55)
        filter_clear_button = QPushButton("clear filters")
        self.filter_text_label = QLabel()
        filters_layout.addWidget(filter_material_label, 0, 0)
        filters_layout.addWidget(self.filter_material_edit, 0, 1)
        filters_layout.addWidget(filter_density_label, 0, 2)
        filters_layout.addWidget(self.filter_density_edit, 0, 3)
        filters_layout.addWidget(filter_thickness_label, 0, 4)
        filters_layout.addWidget(self.filter_thickness_edit, 0, 5)
        filters_layout.addWidget(filter_add_button, 1, 0)
        filters_layout.addWidget(self.filter_text_label, 1, 1, 1, 4)
        filters_layout.addWidget(filter_clear_button, 1, 5)
        filters_group.setLayout(filters_layout)
        self.filter_material_edit.editingFinished.connect(self.autofill_filter_density)
        filter_add_button.clicked.connect(self.filter_add_button_Clicked)
        filter_clear_button.clicked.connect(self.filter_clear_button_Clicked)
        
        overallgrid.addWidget(filters_group, curRow, 0, 1, 2)
        curRow += 1
        
        # DETECTOR RESPONSE
        detector_response_group = QGroupBox("Detector Response")
        detector_response_layout = QHBoxLayout()
        detector_material_label = QLabel("material")
        self.detector_material_edit = QLineEdit()
        detector_density_label = QLabel("density (g/cm^3)")
        self.detector_density_edit = QLineEdit()
        detector_thickness_label = QLabel("thickness (mm)")
        self.detector_thickness_edit = QLineEdit()
        detector_response_layout.addWidget(detector_material_label)
        detector_response_layout.addWidget(self.detector_material_edit)
        detector_response_layout.addWidget(detector_density_label)
        detector_response_layout.addWidget(self.detector_density_edit)
        detector_response_layout.addWidget(detector_thickness_label)
        detector_response_layout.addWidget(self.detector_thickness_edit)
        detector_response_group.setLayout(detector_response_layout)
        self.detector_material_edit.editingFinished.connect(self.push_detector_response)
        self.detector_density_edit.editingFinished.connect(self.push_detector_response)
        self.detector_thickness_edit.editingFinished.connect(self.push_detector_response)
        overallgrid.addWidget(detector_response_group, curRow, 0, 1, 2)
        curRow += 1
        
        # OBJECT MODEL
        object_model_group = QGroupBox("Object Model")
        object_model_layout = QHBoxLayout()
        object_material_label = QLabel("material")
        self.object_material_edit = QLineEdit()
        object_density_label = QLabel("density (g/cm^3)")
        self.object_density_edit = QLineEdit()
        object_model_layout.addWidget(object_material_label)
        object_model_layout.addWidget(self.object_material_edit)
        object_model_layout.addWidget(object_density_label)
        object_model_layout.addWidget(self.object_density_edit)
        object_model_group.setLayout(object_model_layout)
        self.object_material_edit.editingFinished.connect(self.push_object_model)
        self.object_density_edit.editingFinished.connect(self.push_object_model)
        overallgrid.addWidget(object_model_group, curRow, 0, 1, 2)
        curRow += 1
        
        # ENERGY SAMPLES
        energy_samples_group = QGroupBox("Energy Samples (optional)")
        energy_samples_layout = QHBoxLayout()
        lowest_energy_label = QLabel("Minimum Energy (keV)")
        self.lowest_energy_edit = QLineEdit()
        energy_bin_width_label = QLabel("Energy Bin Width (keV)")
        self.energy_bin_width_edit = QLineEdit()
        reference_energy_label = QLabel("Reference Energy (keV)")
        self.reference_energy_edit = QLineEdit()
        self.lowest_energy_edit.editingFinished.connect(self.push_lowest_energy)
        self.energy_bin_width_edit.editingFinished.connect(self.push_energy_bin_width)
        self.reference_energy_edit.editingFinished.connect(self.push_reference_energy)
        energy_samples_layout.addWidget(reference_energy_label)
        energy_samples_layout.addWidget(self.reference_energy_edit)
        energy_samples_layout.addWidget(lowest_energy_label)
        energy_samples_layout.addWidget(self.lowest_energy_edit)
        energy_samples_layout.addWidget(energy_bin_width_label)
        energy_samples_layout.addWidget(self.energy_bin_width_edit)
        energy_samples_group.setLayout(energy_samples_layout)
        overallgrid.addWidget(energy_samples_group, curRow, 0, 1, 2)
        curRow += 1
        
        plot_spectra_button = QPushButton("Plot Spectra")
        material_library_button = QPushButton("Material Library")
        material_library_button.setMaximumWidth(100)
        plot_spectra_button.clicked.connect(self.plot_spectra_button_Clicked)
        overallgrid.addWidget(plot_spectra_button, curRow, 0)
        material_library_button.clicked.connect(self.material_library_button_Clicked)
        overallgrid.addWidget(material_library_button, curRow, 1)
        curRow += 1
        
        if self.lctserver.source_spectra_file is not None and len(self.lctserver.source_spectra_file) > 0:
            self.source_model_type_file_radio.setChecked(True)
            self.push_file_source_model()
        else:
            self.source_model_type_analytic_radio.setChecked(True)
            self.push_analytic_source_model()
        
        self.setLayout(overallgrid)
        self.refresh()

    def refresh(self):
        if self.lctserver.anode_material == 74:
            self.W_anode_radio.setChecked(True)
        elif self.lctserver.anode_material == 42:
            self.Mo_anode_radio.setChecked(True)
        elif self.lctserver.anode_material == 79:
            self.Au_anode_radio.setChecked(True)
        elif self.lctserver.anode_material == 29:
            self.Cu_anode_radio.setChecked(True)
        
        if self.lctserver.kV is not None and self.lctserver.kV > 0.0:
            self.kV_edit.setText(str(self.lctserver.kV))
        else:
            self.kV_edit.setText("")
        
        if self.lctserver.takeoff_angle is not None and self.lctserver.takeoff_angle > 0.0:
            self.takeoff_angle_edit.setText(str(self.lctserver.takeoff_angle))
        else:
            self.takeoff_angle_edit.setText("")
        
        self.refresh_filters()
        
        if self.lctserver.detector_response_model is None:
            self.detector_material_edit.setText("")
            self.detector_density_edit.setText("")
            self.detector_thickness_edit.setText("")
        else:
            self.detector_material_edit.setText(str(self.lctserver.detector_response_model[0]))
            self.detector_density_edit.setText(str(f'{1.0e3*self.lctserver.detector_response_model[1]:.4f}'))
            self.detector_thickness_edit.setText(str(self.lctserver.detector_response_model[2]))
        
        if self.lctserver.object_model is None:
            self.object_material_edit.setText("")
            self.object_density_edit.setText("")
        else:
            self.object_material_edit.setText(self.lctserver.object_model[0])
            self.object_density_edit.setText(f'{1.0e3*self.lctserver.object_model[1]:.4f}')
        
        if self.lctserver.lowest_energy is not None and self.lctserver.lowest_energy > 0:
            self.lowest_energy_edit.setText(str(self.lctserver.lowest_energy))
        else:
            self.lowest_energy_edit.setText("")
            
        if self.lctserver.energy_bin_width is not None and self.lctserver.energy_bin_width > 0:
            self.energy_bin_width_edit.setText(str(self.lctserver.energy_bin_width))
        else:
            self.energy_bin_width_edit.setText("")
        
        if self.lctserver.reference_energy is not None and self.lctserver.reference_energy > 0:
            self.reference_energy_edit.setText(str(f'{self.lctserver.reference_energy:.4f}'))
        else:
            self.reference_energy_edit.setText("")
    
    def refresh_filters(self):
        if self.lctserver.xray_filters is None:
            self.filter_text_label.setText("")
        else:
            text = ""
            for n in range(len(self.lctserver.xray_filters)):
                text = text + '[' + str(self.lctserver.xray_filters[n][0]) + ', ' + str(f'{1.0e3*self.lctserver.xray_filters[n][1]:.4f}') + ', ' + str(self.lctserver.xray_filters[n][2]) + '] '
            self.filter_text_label.setText(text)
            
    def autofill_filter_density(self):
        material = self.filter_material_edit.text()
        if len(material) == 0:
            return
        if len(self.filter_density_edit.text()) == 0:
            density = self.lctserver.physics.massDensity(material)
            self.filter_density_edit.setText(str(f'{1.0e3*density:.4f}'))
    
    def filter_add_button_Clicked(self):
        material = self.filter_material_edit.text()
        if len(material) == 0:
            return
    
        if len(self.filter_density_edit.text()) > 0:
            try:
                density = float(self.filter_density_edit.text())*1.0e-3
            except:
                density = 0.0
        else:
            density = 0.0
            
        if len(self.filter_thickness_edit.text()) > 0:
            try:
                thickness = float(self.filter_thickness_edit.text())
            except:
                thickness = 0.0
        else:
            thickness = 0.0
        
        if density == 0.0:
            density = self.lctserver.physics.massDensity(material)
            self.filter_density_edit.setText(str(f'{1.0e3*density:.4f}'))
        
        if density > 0.0 and thickness > 0.0 and len(material) > 0:
            self.lctserver.add_filter(material, density, thickness)
            self.refresh_filters()
            self.filter_material_edit.setText("")
            self.filter_density_edit.setText("")
            self.filter_thickness_edit.setText("")

    def filter_clear_button_Clicked(self):
        self.lctserver.xray_filters = None
        self.filter_text_label.setText("")
    
    def push_object_model(self):
        material = self.object_material_edit.text()
        if len(material) == 0:
            self.lctserver.clear_object_model()
            return

        if len(self.object_density_edit.text()) > 0:
            try:
                density = float(self.object_density_edit.text())*1.0e-3
            except:
                density = 0.0
        else:
            density = 0.0
            
        if density == 0.0:
            density = self.lctserver.physics.massDensity(material)
            self.object_density_edit.setText(str(f'{1.0e3*density:.4f}'))
        
        if len(material) > 0:
            self.lctserver.set_object_model(material, density)
        else:
            self.lctserver.clear_object_model()
    
    def push_detector_response(self):
        material = self.detector_material_edit.text()
        if len(material) == 0:
            self.lctserver.clear_detector_response()
            return
    
        if len(self.detector_density_edit.text()) > 0:
            try:
                density = float(self.detector_density_edit.text())*1.0e-3
            except:
                density = 0.0
        else:
            density = 0.0
            
        if len(self.detector_thickness_edit.text()) > 0:
            try:
                thickness = float(self.detector_thickness_edit.text())
            except:
                thickness = 0.0
        else:
            thickness = 0.0
        
        if density == 0.0:
            density = self.lctserver.physics.massDensity(material)
            self.detector_density_edit.setText(str(density*1.0e3))
        
        if density > 0.0 and thickness > 0.0 and len(material) > 0:
            self.lctserver.set_detector_response(material, density, thickness)
        else:
            self.lctserver.clear_detector_response()
    
    def plot_spectra_button_Clicked(self):
        if self.lctserver.source_spectra_defined():
            Es, s_total = self.lctserver.totalSystemSpectralResponse(True)
            meanEnergy = self.lctserver.physics.meanEnergy(s_total, Es)
            plt.plot(Es, s_total, 'k-')
            plt.title('Total System Spectral Response (mean energy ' + str(f'{meanEnergy:.2f}') + ' keV)')
            plt.xlabel('x-ray energy (keV)')
            plt.ylabel('normalized response (unitless)')
            plt.show()
    
    def material_library_button_Clicked(self):
        try:
            materialFormulas, materialDensities = self.lctserver.physics.get_material_library()
            self.table = TableView(materialFormulas, materialDensities, len(materialFormulas), 3)
            self.table.show()
        except:
            print('please update the XrayPhysics library to access this feature')
        
    def openDataFile(self):
        
        loadFileDialog = QFileDialog()
        loadFileDialog.setFileMode(QFileDialog.AnyFile)
        loadFileDialog.setNameFilters(["Image Files (*.txt *.npy)"])
        if loadFileDialog.exec_():
            imageFile = loadFileDialog.selectedFiles()
            inputArg = os.path.abspath(str(imageFile[0]))
            return inputArg
        else:
            return []
    
    def source_spectra_file_button_Clicked(self):
        inputArg = self.openDataFile()
        if len(inputArg) > 0:
            self.source_spectra_file_edit.setText(inputArg)
            self.push_source_spectra_file()
            
    def push_source_spectra_file(self):
        self.lctserver.source_spectra_file = self.source_spectra_file_edit.text()
    
    def push_analytic_source_model(self):
        self.source_spectra_file_edit.setEnabled(False)
        self.source_spectra_file_button.setEnabled(False)
        self.source_modeling_group.setEnabled(True)
        
    def push_file_source_model(self):
        self.source_spectra_file_edit.setEnabled(True)
        self.source_spectra_file_button.setEnabled(True)
        self.source_modeling_group.setEnabled(False)
    
    def push_lowest_energy(self):
        val = 0.0
        try:
            val = float(self.lowest_energy_edit.text())
        except:
            val = 0.0
        if val > 0.0:
            self.lctserver.lowest_energy = val
        
    def push_energy_bin_width(self):
        val = 0.0
        try:
            val = float(self.energy_bin_width_edit.text())
        except:
            val = 0.0
        if val > 0.0:
            self.lctserver.energy_bin_width = val
        
    def push_reference_energy(self):
        val = 0.0
        try:
            val = float(self.reference_energy_edit.text())
        except:
            val = 0.0
        if val > 0.0:
            self.lctserver.reference_energy = val
    
    def push_W_anode_radio(self):
        self.lctserver.anode_material = 74
        
    def push_Mo_anode_radio(self):
        self.lctserver.anode_material = 42
        
    def push_Au_anode_radio(self):
        self.lctserver.anode_material = 79
        
    def push_Cu_anode_radio(self):
        self.lctserver.anode_material = 29
    
    def push_takeoff_angle(self):
        val = 0.0
        try:
            val = float(self.takeoff_angle_edit.text())
        except:
            val = 0.0
        if val > 0.0:
            self.lctserver.takeoff_angle = val
            
    def push_kV(self):
        val = 0.0
        try:
            val = float(self.kV_edit.text())
        except:
            val = 0.0
        if val > 0.0:
            self.lctserver.kV = val
    
class PhysicsDialog(QDialog):
    def __init__(self, title, parent = None):
        super(PhysicsDialog, self).__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle(title)

        self.parent = parent
        self.lctserver = self.parent.lctserver
        self.leapct = self.lctserver.leapct

        # Instantiate the volume controls widget, passing this class as the parent:
        self.controls = PhysicsDialogControls(self)
        overallGrid = QGridLayout()
        overallGrid.addWidget(self.controls, 0, 0)
        self.setLayout(overallGrid)
        self.resize(400,400) # column, row
        