################################################################################
# Copyright 2024 Kyle Champley
# SPDX-License-Identifier: MIT
#
# LivermorE AI Projector for Computed Tomography (LEAP)
# leapctserver class
# This class manages file I/O, memory, and spectra parameters for LEAP
# It is useful for running algorithms that require more CPU RAM
# than what is available by processing the data in smaller chunks and saving
# intermediate results to file.
################################################################################
import os
import sys
import uuid
import numpy as np
import matplotlib.pyplot as plt
from leapctype import *
import leap_preprocessing_algorithms

try:
    from xrayphysics import *
    has_physics = True
except:
    has_physics = False

root_path = os.path.dirname(os.path.realpath(__file__))

class leapctserver:

    def __init__(self, leapct=None, path=None, outputDir=None):
        if leapct is None:
            self.leapct = tomographicModels()
        else:
            self.leapct = leapct
        
        if has_physics:
            self.physics = xrayPhysics()
        else:
            self.physics = None
        self.physics.use_mm()
        
        self.leapct_backup = tomographicModels()
            
        self.reset(path, outputDir)
        
    def reset(self, path=None, outputDir=None):
    
        ### Section I: file names
        # Path to folder where inputs are stored and outputs may be written
        if path is None:
            self.path = os.getcwd()
        else:
            self.path = path
            
        # Output directory (must be a subfolder of path)
        if outputDir is None:
            self.outputDir = str('leapct_') + str(uuid.uuid4().hex)
        else:
            self.outputDir = outputDir

        # File name for air scan data
        self.air_scan_file = None
        
        # File name for dark scan data
        self.dark_scan_file = None
        
        # File name for raw data projections
        self.raw_scan_file = None
        
        # File name for transmission or attenuation projections
        self.projection_file = None
        
        # File name for reconstructed slices
        self.reconstruction_file = None
        
        # File name where CT geometry and CT volume parameters are stored
        self.geometry_file = None
        
        # File name where all spectra parameters are stored
        self.spectra_model_file = None # not sure what this is for, not currently being used
        
        # File name where source spectra is stored
        self.source_spectra_file = None
        
        # File name where detector response is stored
        self.detector_response_file = None

        # Tags for the projection data type
        [self.UNSPECIFIED, self.RAW, self.RAW_DARK_SUBTRACTED, self.TRANSMISSION, self.ATTENUATION] = [0, 1, 2, 3, 4]
        self.data_type = self.UNSPECIFIED

        
        ### Section II: data
        # Projection data (numpy array or torch tensor)
        self.g = None
        
        # Reconstruction volume data (numpy array or torch tensor)
        self.f = None
        
        # The maximum amount of memory that leapctserver is allowed to use
        # Users are encouraged to change this!
        physicalMemory = self.total_RAM()
        if physicalMemory > 0.0:
            if physicalMemory < 0.8:
                self.max_CPU_memory_usage = physicalMemory
            elif physicalMemory < 8.0:
                self.max_CPU_memory_usage = 5.0/6.0*physicalMemory - 2.0/3.0 # 1 GB if have 2 GB of memory, 6 GB if 8 GB of memory
            elif physicalMemory < 32.0:
                self.max_CPU_memory_usage = 11.0/12.0*physicalMemory - 4.0/3.0 # 6 GB if 8 GB of memory, 28 GB if 32 GB of memory
            else:
                self.max_CPU_memory_usage = min(physicalMemory - 4.0, 0.95*physicalMemory) # reserve 4 GB of memory; this is likely too much
        else:
            self.max_CPU_memory_usage = 128.0
        if self.max_CPU_memory_usage > 1.0:
            self.max_CPU_memory_usage = np.floor(self.max_CPU_memory_usage)
            
        # Section III: data chunking
        [self.PROJECTION, self.DETECTOR_ROW, self.Z_SLICE] = [0, 1, 2]
        self.chunking_type = self.PROJECTION
        self.num_proj = 0
        self.num_vol = 0
        self.scratch_space = 0.125 # extra memory reserved
        self.chunk_size = 0
        
        ### Section IV: spectra parameters
        self.reference_energy = -1.0
        self.lowest_energy = -1.0
        self.energy_bin_width = -1.0
        self.kV = None
        self.takeoff_angle = 11.0
        self.anode_material = 74
        self.xray_filters = None
        self.detector_response_model = None
        self.object_model = None
        
        self.init_angle = 0.0
        self.angular_range = 0.0
        self.angular_step = 0.0
        self.num_angles = 0.0
        
        ### Other
        #self.leapct.reset() # use clearAll
        self.lastImage = None
        
        self.restore_defaults()
        
    def clearAll(self):
        self.reset()
        self.leapct.reset()
        
    def save_defaults(self):
        defaults_file = os.path.join(root_path, "leapctserver_defaults.txt")
        f = open(defaults_file, "w")
        
        #if self.path is not None and len(self.path) > 0:
        #    f.write('path = ' + self.path + '\n')
        
        f.close()
        
    def restore_defaults(self):
        defaults_file = os.path.join(root_path, "leapctserver_defaults.txt")
        if os.path.isfile(defaults_file):
            self.load_parameters(defaults_file)
        
    def is_number(self, s):
        if s is None:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def print_parameters(self):
        print('\n======== File I/O ========')
        if self.path is not None:
            print('path = ', self.path)
        if self.air_scan_file is not None:
            print('air_scan_file = ', self.air_scan_file)
        if self.dark_scan_file is not None:
            print('dark_scan_file = ', self.dark_scan_file)
        if self.raw_scan_file is not None:
            print('raw_scan_file = ', self.raw_scan_file)
        if self.reconstruction_file is not None:
            print('reconstruction_file = ', self.reconstruction_file)
        print('')
        
        print('======== Physics ========')
        if self.source_spectra_file is not None and len(self.source_spectra_file) > 0:
            print('source_spectra_file = ', self.source_spectra_file)
        elif self.kV > 0.0:
            print('kV = ', self.kV)
            print('anode_material = ', self.anode_material)
            print('takeoff_angle = ', self.takeoff_angle)
        if self.xray_filters is not None:
            print('xray_filters = ', self.xray_filters)
        if self.detector_response_model is not None:
            print('detector_response_model = ', self.detector_response_model)
        if self.object_model is not None:
            print('object_model = ', self.object_model)
        if self.reference_energy > 0.0:
            print('reference_energy = ', self.reference_energy)
        
        self.leapct.print_parameters()
        """
        self.dark_scan_file = None
        self.raw_scan_file = None
        self.projection_file = None
        self.reconstruction_file = None
        """
    
    ###################################################################################################################
    ###################################################################################################################
    # FILE I/O
    ###################################################################################################################
    ###################################################################################################################
    def set_path(self, path):
        if os.path.exists(fullPath):
            self.path = path
        else:
            print('Error: specified path does not exist')
        
    def clear_path(self):
        self.path = None
        
    def create_outputDir(self):
        fullPath = os.path.join(self.path, self.outputDir)
        if not os.path.exists(fullPath):
            os.makedirs(fullPath)
        
    def save_image_file(self, fileName, x, use_outputDir=True):
        """Save 2D data to file (tif sequence, nrrd, or npy)"""
        if x is None:
            return False
        if len(x.shape) != 2:
            return False
        if use_outputDir:
            fullPath = os.path.join(self.path, self.outputDir, fileName)
            self.create_outputDir()
        else:
            fullPath = os.path.join(self.path, fileName)
        volFilePath, dontCare = os.path.split(fullPath)
        if os.path.isdir(volFilePath) == False or os.access(volFilePath, os.W_OK) == False:
            print('Folder to save data either does not exist or not accessible!')
            return False
            
        if has_torch == True and type(x) is torch.Tensor:
            x = x.cpu().detach().numpy()
            
        if fullPath.endswith('.npy'):
            np.save(fullPath, x)
            return True
        elif fullPath.endswith('.nrrd'):
            try:
                import nrrd
                
                # https://pynrrd.readthedocs.io/en/latest/examples.html
                #header = {'units': ['mm', 'mm', 'mm'], 'spacings': [T, T, T], 'axismins': [offset_0, offset_1, offset_2], 'thicknesses': [T, T, T],}
                #nrrd.write(fileName, x, header)
                nrrd.write(fullPath, x)
                return True
            except:
                print('Error: Failed to load nrrd library!')
                print('To install this package do: pip install pynrrd')
                return False
        elif fullPath.endswith('.tif') or fullPath.endswith('.tiff'):
            try:
                #from PIL import Image
                import imageio
                
                imageio.imwrite(fullPath, x)
                return True
                
            except:
                #print('Error: Failed to load PIL library!')
                #print('To install this package do: pip install Pillow')
                print('Error: Failed to load imageio library!')
                print('To install PIL do: pip install imageio')
                return False
        else:
            print('Error: must be a tif, npy, or nrrd file!')
            return False
        
    def read_1D(self, fileName):
        if fileName is None:
            return None
        fullPath = os.path.join(self.path, fileName)
        if fullPath.endswith('.npy'):
            if os.path.isfile(fullPath) == False:
                print('file does not exist')
                return None
            else:
                x = np.array(np.load(fullPath), dtype=np.float32)
                return x
        elif fullPath.endswith('.txt'):
            data = []
            try:
                with open(fullPath, 'r') as file:
                    for line in file:
                        if line[0] != '#':
                            data.append(float(line))
                x = np.array(data, dtype=np.float32)
                return x
            except FileNotFoundError:
                print('Error: failed to open the file ', fullPath)
                return None
            except Exception as e:
                print('Error occured while loading the data', str(e))
                return None
        else:
            print('Error: read_1D currently only works for npy and txt files')
            return None
        
    def read_image_file(self, fileName, rowRange=None, colRange=None, shape=None, dtype=np.float32):
        if fileName is None:
            return None
        if isinstance(fileName, int) or isinstance(fileName, float):
            return float(fileName)
        fullPath = os.path.join(self.path, fileName)
        if rowRange is not None:
            if len(rowRange) != 2 or rowRange[0] > rowRange[1] or rowRange[0] < 0 or rowRange[1] < 0:
                print('Error: rowRange must be a list of two positive numbers')
                return None
        if colRange is not None:
            if len(colRange) != 2 or colRange[0] > colRange[1] or colRange[0] < 0 or colRange[1] < 0:
                print('Error: colRange must be a list of two positive numbers')
                return None
        
        if fullPath.endswith('.npy'):
            if os.path.isfile(fullPath) == False:
                print('file does not exist')
                return None
            else:
                x = np.load(fullPath)
        elif fullPath.endswith('.nrrd'):
            if os.path.isfile(fullPath) == False:
                print('file does not exist')
                return None
            try:
                import nrrd
                x, header = nrrd.read(fullPath)
            except:
                print('Error: Failed to load nrrd library!')
                print('To install this package do: pip install pynrrd')
                return None
        elif fullPath.endswith('.tif') or fullPath.endswith('.tiff'):
            
            try:
                #from PIL import Image
                import imageio
                hasPIL = True
            except:
                #print('Error: Failed to load PIL or glob library!')
                #print('To install PIL do: pip install Pillow')
                print('Error: Failed to load imageio or glob library!')
                print('To install PIL do: pip install imageio')
                return None
            if hasPIL == True:
                if os.path.isfile(fullPath) == False:
                    print('file does not exist')
                    return None
                else:
                    x = np.array(imageio.imread(fullPath), dtype=np.float32)
        elif fullPath.endswith('.raw') or fullPath.endswith('.sdt'):
            if shape is None or dtype is None:
                print('Error: must specify shape and dtype for raw file types')
                return None
            else:
                x = self.read_raw_file(fullPath, shape, dtype, rowRange, colRange)
        else:
            try:
                x = float(fileName)
                return x
            except:
                print('Error: must be a tif, tiff, std, raw, npy, or nrrd file!')
                return None
            
        return self.crop_image(x, rowRange, colRange)
        
    def read_raw_file(self, fileName, shape=None, dtype=np.float32, rowRange=None, colRange=None):
        x = np.fromfile(fileName, dtype)
        if shape is not None and len(shape) == 2:
            x = x.reshape((shape[0], shape[1]))
            x = self.crop_image(x, rowRange, colRange)
        return x
        
    def crop_image(self, x, rowRange=None, colRange=None):
        if x is None:
            return None
        if len(x.shape) != 2:
            x = np.ascontiguousarray(x, dtype=np.float32)
        else:
            if rowRange is not None and len(rowRange) == 2 and rowRange[1] < x.shape[0]:
                x = x[rowRange[0]:rowRange[1]+1,:]
            if colRange is not None and len(colRange) == 2 and colRange[1] < x.shape[1]:
                x = x[:,colRange[0]:colRange[1]+1]
            x = np.ascontiguousarray(x, dtype=np.float32)
        return x
        
    def set_raw_data_files(self, raw, air, dark=None):
        if raw is not None and air is None:
            print('Error: air scan file name must be specified, when raw data file name is specified')
            return
        self.dark_scan_file = dark
        self.air_scan_file = air
        self.raw_scan_file = raw
        if raw is None:
            self.data_type = self.UNSPECIFIED
        elif self.dark_scan_file is None:
            self.data_type = self.RAW_DARK_SUBTRACTED
        else:
            self.data_type = self.RAW
            
    def set_transmission_data_files(self, trans):
        if trans is None:
            self.data_type = self.UNSPECIFIED
        else:
            self.data_type = self.TRANSMISSION
        self.projection_file = trans
    
    def set_attenuation_data_files(self, atten):
        if atten is None:
            self.data_type = self.UNSPECIFIED
        else:
            self.data_type = self.ATTENUATION
        self.projection_file = atten
        
    def set_reconstruction_data_file(self, zslices):
        #if zslices is None:
        #    print('Error: reconstruction data file names must be specified')
        #    return
        self.reconstruction_file = zslices
    
    def save_geometry_file(self):
        self.create_outputDir()
        if self.geometry_file is None or len(self.geometry_file) == 0:
            self.geometry_file = os.path.join(self.outputDir, 'geometry.txt')
        elif self.geometry_file.startswith(self.outputDir) == False:
            self.geometry_file = os.path.join(self.outputDir, self.geometry_file)
        fullPath = os.path.join(self.path, self.geometry_file)
        return self.leapct.save_parameters(fullPath)
    
    def load_geometry_file(self, inputFile=None):
        if inputFile is not None:
            self.geometry_file = inputFile
        if self.geometry_file is not None and len(self.geometry_file) > 0:
            if self.geometry_file.startswith(self.path):
                fullPath = self.geometry_file
            else:
                fullPath = os.path.join(self.path, self.geometry_file)
            return self.leapct.load_parameters(fullPath)
        else:
            return False
    
    def save_spectra_model(self):
        if has_physics:
            if self.source_spectra_defined():
                Es, s = self.source_spectra()
                self.physics.save_spectra(self.source_spectra_file, s, Es)
                if self.detector_response_defined():
                    Es, d = self.detector_response(Es)
                    self.physics.save_spectra(self.detector_response_file, d, Es)
        
    def save_parameters(self, fileName=None):
        """Saves CT geometry, CT volume, and all spectra parameters to file"""
        self.create_outputDir()
        if fileName is None or len(fileName) == 0:
            fileName = os.path.join(self.path, self.outputDir, 'leapct_params.txt')
        elif fileName.startswith(self.path) == False and os.path.isabs(fileName) == False:
            fileName = os.path.join(self.path, self.outputDir, fileName)
        self.save_geometry_file()
        
        """
        self.path
        self.air_scan_file
        self.dark_scan_file
        self.raw_scan_file
        self.projection_file
        self.reconstruction_file
        self.geometry_file
        """
        f = open(fileName, "w")
        if self.path is not None and len(self.path) > 0:
            f.write('path = ' + self.path + '\n')
        if self.air_scan_file is not None and len(self.air_scan_file) > 0:
            f.write('air_scan_file = ' + self.air_scan_file + '\n')
        if self.dark_scan_file is not None and len(self.dark_scan_file) > 0:
            f.write('dark_scan_file = ' + self.dark_scan_file + '\n')
        if self.raw_scan_file is not None and len(self.raw_scan_file) > 0:
            f.write('raw_scan_file = ' + self.raw_scan_file + '\n')
        if self.projection_file is not None and len(self.projection_file) > 0:
            f.write('projection_file = ' + self.projection_file + '\n')
        if self.reconstruction_file is not None and len(self.reconstruction_file) > 0:
            f.write('reconstruction_file = ' + self.reconstruction_file + '\n')
        if self.geometry_file is not None and len(self.geometry_file) > 0:
            f.write('geometry_file = ' + self.geometry_file + '\n')
        
        if self.data_type == self.RAW:
            f.write('data_type = RAW\n')
        elif self.data_type == self.RAW_DARK_SUBTRACTED:
            f.write('data_type = RAW_DARK_SUBTRACTED\n')
        elif self.data_type == self.TRANSMISSION:
            f.write('data_type = TRANSMISSION\n')
        elif self.data_type == self.ATTENUATION:
            f.write('data_type = ATTENUATION\n')
            
        #"""
        if self.source_spectra_file is not None and len(self.source_spectra_file) > 0:
            f.write('source_spectra_file = ' + self.source_spectra_file + '\n')
        elif self.kV > 0.0:
            f.write('kV = ' + str(self.kV) + '\n')
            f.write('anode_material = ' + str(self.anode_material) + '\n')
            f.write('takeoff_angle = ' + str(self.takeoff_angle) + '\n')
        if self.xray_filters is not None:
            f.write('xray_filters = ' + str(self.xray_filters) + '\n')
        if self.detector_response_model is not None:
            f.write('detector_response_model = ' + str(self.detector_response_model) + '\n')
        if self.object_model is not None:
            f.write('object_model = ' + str(self.object_model) + '\n')
        if self.reference_energy > 0.0:
            f.write('reference_energy = ' + str(self.reference_energy) + '\n')
        #"""
        
        f.close()
        #self.save_spectra_model()
    
    def load_projections_into_memory(self):
        if self.data_type == self.TRANSMISSION or self.data_type == self.ATTENUATION:
            if self.projection_file is not None and len(self.projection_file) > 0:
                self.g = self.load_projections(self.projection_file)
        else:
            if self.raw_scan_file is not None and len(self.raw_scan_file) > 0:
                self.g = self.load_projections(self.raw_scan_file)

    def load_dark_scan_into_memory(self):
        if self.dark_scan_file is not None and len(self.dark_scan_file) > 0:
            return self.read_image_file(self.dark_scan_file)
        else:
            return None
            
    def load_air_scan_into_memory(self):
        if self.air_scan_file is not None and len(self.air_scan_file) > 0:
            return self.read_image_file(self.air_scan_file)
        else:
            return None
        
    def load_volume_into_memory(self):
        if self.reconstruction_file is not None and len(self.reconstruction_file) > 0:
            self.f = self.load_volume(self.reconstruction_file)
    
    def load_projections(self, fileName=None):
        return self.load_projection_angles(fileName)
    
    def load_projection_angles(self, fileName=None, inds=None):
        """load selected angles of projections
        
        Args:
            fileName (string): full path
            inds (list of two integers): specifies the range of projections to load
            
        Returns:
            3D numpy of the projections loaded from file
        """
        if fileName is None:
            if self.data_type == self.RAW or self.data_type == self.RAW_DARK_SUBTRACTED:
                if self.raw_scan_file is None:
                    print('Error: data_type is raw, but raw_scan_file is not specified!')
                    return None
                fileName = self.raw_scan_file
            else:
                if self.projection_file is None:
                    print('Error: projection_file is not specified!')
                    return None
                fileName = self.projection_file
        fullPath = os.path.join(self.path, fileName)
        #if os.path.isfile(fullPath) == False:
        #    print('Error: ' + str(fullPath) + ' does not exist!')
        #    return None
        dataFolder, baseFileName = os.path.split(fullPath)
        if "sino" in baseFileName:
            if inds is not None:
                g = np.zeros((inds[1]-inds[0]+1, self.leapct.get_numRows(), self.leapct.get_numCols()),dtype=np.float32)
            else:
                g = np.zeros((self.leapct.get_numAngles(), self.leapct.get_numRows(), self.leapct.get_numCols()),dtype=np.float32)
            g = np.swapaxes(g, 0, 1)
            g = self.leapct.load_data(fullPath, x=g, fileRange=None, rowRange=inds, colRange=None)
            g = np.swapaxes(g, 0, 1)
            g = np.ascontiguousarray(g, dtype=np.float32)
            """
            elif baseFileName.find('*') != -1:
                import imageio
                files = glob.glob(fullPath)
                if inds is None:
                    inds = [0, len(files)-1]
                else:
                    inds[0] = max(0, inds[0])
                    inds[1] = min(len(files)-1, inds[1])
                for n in range(inds[0], inds[1]+1):
                    file = files[n]
                    anImage = np.array(imageio.imread(files[n]))
                    if n == inds[0]:
                        g = np.zeros((len(files), anImage.shape[0], anImage.shape[1]), dtype=np.float32)
                    g[n,:,:] = anImage[:,:]
            """
        else:
            g = self.leapct.load_data(fullPath, x=None, fileRange=inds, rowRange=None, colRange=None)
        #self.g = g # ?
        return g
        
    def load_projection_rows(self, fileName=None, inds=None):
        """load selected rows of projections
        
        Args:
            fileName (string): full path
            inds (list of two integers): specifies the range of detector rows to load
            
        Returns:
            3D numpy of the sinograms loaded from file
        """
        if fileName is None:
            if self.data_type == self.RAW or self.data_type == self.RAW_DARK_SUBTRACTED:
                if self.raw_scan_file is None:
                    print('Error: data_type is raw, but raw_scan_file is not specified!')
                    return None
                fileName = self.raw_scan_file
            else:
                if self.projection_file is None:
                    print('Error: projection_file is not specified!')
                    return None
                fileName = self.projection_file
        fullPath = os.path.join(self.path, fileName)
        if os.path.isfile(fullPath) == False:
            print('Error: ' + str(fullPath) + ' does not exist!')
            return None
        dataFolder, baseFileName = os.path.split(fullPath)
        if "sino" in baseFileName:
            if inds is not None:
                g = np.zeros((self.leapct.get_numAngles(), inds[1]-inds[0]+1, self.leapct.get_numCols()),dtype=np.float32)
            else:
                g = np.zeros((self.leapct.get_numAngles(), self.leapct.get_numRows(), self.leapct.get_numCols()),dtype=np.float32)
            g = np.swapaxes(g, 0, 1)
            g = self.leapct.load_data(fullPath, x=g, fileRange=inds, rowRange=None, colRange=None)
            g = np.swapaxes(g, 0, 1)
            g = np.ascontiguousarray(g, dtype=np.float32)
        else:
            g = self.leapct.load_data(fullPath, x=None, fileRange=None, rowRange=inds, colRange=None)
        #self.g = g # ?
        return g
    
    def save_projection_angles(self, g=None, seq_offset=0, update_params=False):
        """Saves the projection data in a sequence of tif files, one file for each projection angle
        
        Args:
            g (C contiguous float32 numpy array or torch tensor): projection data
            seq_offset (int): the file sequence number for the first file
            
        Returns:
            The base file name of the saved data, if failed to write to file returns None
        """
        if g is None:
            g = self.g
        if g is None:
            print('Error: no projection data exists to save')
            return None
        self.create_outputDir()
        #if self.data_type == self.RAW or self.data_type == self.RAW_DARK_SUBTRACTED:
        #    fileName = self.raw_scan_file
        #else:
        #    fileName = self.projection_file
        if self.data_type == self.RAW:
            fileName = 'raw.tif'
        elif self.data_type == self.RAW_DARK_SUBTRACTED:
            fileName = 'rawDarkSub.tif'
        elif self.data_type == self.TRANSMISSION:
            fileName = 'transRad.tif'
        elif self.data_type == self.ATTENUATION:
            fileName = 'attenRad.tif'
        else:
            fileName = 'image.tif'
        if self.outputDir in fileName:
            newFileName = fileName
        else:
            newFileName = os.path.join(self.outputDir, fileName)
        fullPath = os.path.join(self.path, newFileName)
        
        if self.leapct.save_projections(fullPath, g, seq_offset) == True:
            if update_params:
                if self.data_type == self.TRANSMISSION or self.data_type == self.ATTENUATION:
                    self.projection_file = newFileName
                else:
                    self.raw_scan_file = newFileName
            return newFileName
        else:
            return None
            
    def load_volume(fileName, inds):
        if fileName is None:
            fileName = self.reconstruction_file
        fullPath = os.path.join(self.path, fileName)
        if os.path.isfile(fullPath) == False:
            print('Error: ' + str(fullPath) + ' does not exist!')
            return None
        f = self.leapct.load_data(fullPath, x=None, fileRange=inds, rowRange=None, colRange=None)
        #self.f = f # ?
        return f
        
    def save_projection_rows(self, g, seq_offset=0):
        """Saves the projection data in a sequence of tif files, one file for each detector row
        
        Args:
            g (C contiguous float32 numpy array or torch tensor): projection data
            seq_offset (int): the file sequence number for the first file
            
        Returns:
            The base file name of the saved data, if failed to write to file returns None
        """
        self.create_outputDir()
        if self.data_type == self.RAW:
            fileName = 'sino_raw.tif'
        elif self.data_type == self.RAW_DARK_SUBTRACTED:
            fileName = 'sino_rawDarkSub.tif'
        elif self.data_type == self.TRANSMISSION:
            fileName = 'sino_trans.tif'
        elif self.data_type == self.ATTENUATION:
            fileName = 'sino.tif'
        else:
            fileName = 'sino.tif'
            
        if self.outputDir in fileName:
            newFileName = fileName
        else:
            newFileName = os.path.join(self.outputDir, fileName)
        fullPath = os.path.join(self.path, fileName)
        
        g = np.swapaxes(g, 0, 1)
        isSuccessful = self.leapct.save_projections(fullPath, g, seq_offset)
        g = np.swapaxes(g, 0, 1)
        g = np.ascontiguousarray(g, dtype=np.float32)
        if isSuccessful:
            return newFileName
        else:
            return None
    
    def get_zslice(self, iz, thickness=1):
        # TODO: read from file if not loaded in memory
        if self.f is None:
            return None
        elif self.leapct.ct_volume_defined() == False:
            return None
        else:
            return self.get_2Dsubset(self.f, iz, 0, thickness)
            
    def get_yslice(self, iy, thickness=1):
        # TODO: read from file if not loaded in memory
        if self.f is None:
            return None
        elif self.leapct.ct_volume_defined() == False:
            return None
        else:
            return self.get_2Dsubset(self.f, iy, 1, thickness)
            
    def get_xslice(self, ix, thickness=1):
        # TODO: read from file if not loaded in memory
        if self.f is None:
            return None
        elif self.leapct.ct_volume_defined() == False:
            return None
        else:
            return self.get_2Dsubset(self.f, ix, 2, thickness)
            
    def get_projection(self, iphi, thickness=1):
        # TODO: read from file if not loaded in memory
        if self.g is None:
            return None
        elif self.leapct.ct_geometry_defined() == False:
            return None
        else:
            return self.get_2Dsubset(self.g, iphi, 0, thickness)
            
    def get_sinogram(self, irow, thickness=1):
        # TODO: read from file if not loaded in memory
        if self.g is None:
            return None
        elif self.leapct.ct_geometry_defined() == False:
            return None
        else:
            return self.get_2Dsubset(self.g, irow, 1, thickness)
            
    def get_2Dsubset(self, x, ind, axis, thickness=1):
        if x is None:
            return None
        elif axis < 0 or axis > 3:
            return None
        elif ind < 0 or ind >= x.shape[axis]:
            return None
        else:
            thickness = min(max(1,thickness), ind+1, x.shape[axis]-ind)
            if axis == 0:
                slice = np.empty((x.shape[1], x.shape[2]), dtype=np.float32)
            elif axis == 1:
                slice = np.empty((x.shape[0], x.shape[2]), dtype=np.float32)
            else:
                slice = np.empty((x.shape[0], x.shape[1]), dtype=np.float32)
            if thickness == 1:
                if axis == 0:
                    slice[:,:] = x[ind,:,:]
                elif axis == 1:
                    slice[:,:] = x[:,ind,:]
                else:
                    slice[:,:] = x[:,:,ind]
            else:
                ind_min = ind - thickness//2
                ind_max = ind + thickness//2
                if thickness % 2 == 0:
                    w = np.ones(thickness+1, dtype=np.float32)
                    w[0] = 0.5
                    w[-1] = 0.5
                    w = w / float(thickness)
                    if axis == 0:
                        #slice[:,:] = np.tensordot(x[ind_min:ind_max+1,:,:], w, axes=axis)
                        slice[:,:] = np.sum(x[ind_min:ind_max+1,:,:] * w[:,None,None], axis=axis)
                    elif axis == 1:
                        slice[:,:] = np.sum(x[:,ind_min:ind_max+1,:] * w[None,:,None], axis=axis)
                    else:
                        slice[:,:] = np.sum(x[:,:,ind_min:ind_max+1] * w[None,None,:], axis=axis)
                else:
                    if axis == 0:
                        slice[:,:] = np.sum(x[ind_min:ind_max+1,:,:], axes=axis) / float(thickness)
                    elif axis == 1:
                        slice[:,:] = np.sum(x[:,ind_min:ind_max+1,:], axes=axis) / float(thickness)
                    else:
                        slice[:,:] = np.sum(x[:,:,ind_min:ind_max+1], axes=axis) / float(thickness)
            return slice
    
    def basic_stats(self, x):
        if x is None:
            return None, None, None, None, None
        else:
            #numpy.histogram(a, bins=10, range=None, density=None, weights=None)
            mu = np.mean(x)
            sigma = np.std(x)
            return np.min(x), np.max(x), mu, sigma, mu/sigma
    
    ###################################################################################################################
    ###################################################################################################################
    # DATA MANAGEMENT
    ###################################################################################################################
    ###################################################################################################################
    def set_projection_data(self, g):
        self.g = g
        
    def clear_projection_data(self):
        del self.g
        self.g = None
        
    def set_volume_data(self, f):
        self.f = f
        
    def clear_volume_data(self):
        del self.f
        self.f = None
        
    def available_RAM(self):
        """Returns the amount of available CPU RAM in GB"""
        try:
            import psutil
            return psutil.virtual_memory()[1]/2**30
        except:
            print('Error: cannot load psutil module which is used to calculate the amount of available CPU RAM!')
            return 0.0
            
    def total_RAM(self):
        """Returns the total amount of CPU RAM in GB"""
        try:
            import psutil
            return psutil.virtual_memory().total/2**30
        except:
            print('Error: cannot load psutil module which is used to calculate the total amount of CPU RAM!')
            return 0.0
    
    def memory_used_by_array(self, x):
        if x is None:
            return 0.0
        else:
            return float(x.nbytes) / 2.0**30
        
    def memory_usage(self):
        return self.memory_used_by_array(self.g) + self.memory_used_by_array(self.f)
        
        
    def projection_memory(self):
        if self.leapct.ct_geometry_defined():
            N_phis = self.leapct.get_numAngles()
            N_rows = self.leapct.get_numRows()
            N_cols = self.leapct.get_numCols()
            return 4.0 * float(N_phis) * float(N_rows) * float(N_cols) / 2.0**30
        else:
            return 0.0
            
    def volume_memory(self):
        if self.leapct.ct_volume_defined():
            numX = self.leapct.get_numX()
            numY = self.leapct.get_numY()
            numZ = self.leapct.get_numZ()
            return 4.0 * float(numX) * float(numY) * float(numZ) / 2.0**30
        else:
            return 0.0
        
    """
    [self.PROJECTION, self.DETECTOR_ROW, self.Z_SLICE] = [0, 1, 2]
    self.chunking_type = self.PROJECTION
    self.num_proj = 0
    self.num_vol = 0
    self.scratch_space = 0.0 # extra memory reserved
    self.chunk_size = 0
    """
    
    def set_chunk_size(self):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        
        self.num_proj = max(1, self.num_proj)
        
        if self.chunking_type == self.PROJECTION:
        
            if self.num_proj * self.projection_memory() < self.max_CPU_memory_usage - self.scratch_space:
                self.chunk_size = self.leapct.get_numAngles()
            else:
                numAngles = self.get_numAngles()
                #chunk_size * self.num_proj * self.projection_memory() / float(numAngles) = self.max_CPU_memory_usage - self.scratch_space
                self.chunk_size = int(np.float((self.max_CPU_memory_usage - self.scratch_space) * float(numAngles) / (self.num_proj * self.projection_memory())))
        
        elif self.chunking_type == self.DETECTOR_ROW:
        
            if self.num_proj * self.projection_memory() < self.max_CPU_memory_usage - self.scratch_space:
                self.chunk_size = self.leapct.get_numRows()
            else:
                numRows = self.get_numRows()
                self.chunk_size = int(np.float((self.max_CPU_memory_usage - self.scratch_space) * float(numRows) / (self.num_proj * self.projection_memory())))
        
        elif self.chunking_type == self.Z_SLICE:
            self.chunk_size = 1
            self.num_vol = max(1, self.num_vol)
            if self.leapct.ct_volume_defined() == False:
                print('Error: CT volume not defined!')
                return False

            memory_remaining = self.max_CPU_memory_usage - self.scratch_space - self.memory_usage()
            if memory_remaining <= 0.0:
                return False
            
            numZ = float(self.leapct.get_numZ())
            numRows = float(self.leapct.get_numRows())
            while self.chunk_size < numZ:
                numRows_needed = float(self.leapct.numRowsRequiredForBackprojectingSlab(self.chunk_size))
                mem_needed = self.num_vol*self.volume_memory()*self.chunk_size/numZ + self.num_proj*self.projection_memory()*numRows_needed/numRows
                if mem_needed > memory_remaining:
                    self.chunk_size = self.chunk_size-1
                    break
                self.chunk_size = self.chunk_size + 1
            self.chunk_size = min(self.chunk_size, numZ)
            numChunks = int(np.ceil(float(numZ)/float(self.chunk_size)))
            self.chunk_size = int(np.ceil(float(numZ)/float(numChunks)))
            return True
                
        else:
            print('Error: chunking_type value is invalid')
            self.chunk_size = 0
            
        if self.chunk_size > 0:
            return True
    
    ###################################################################################################################
    ###################################################################################################################
    # SPECTRA
    ###################################################################################################################
    ###################################################################################################################
    def source_spectra_defined(self):
        if self.kV is not None and self.kV >= 1.0:
            return True
        elif self.is_number(self.source_spectra_file):
            return True
        elif self.source_spectra_file is not None and os.path.isfile(self.source_spectra_file):
            return True
        else:
            return False
    
    def detector_response_defined(self):
        if self.detector_response_file is not None and os.path.isfile(self.detector_response_file):
            return True
        elif self.detector_response_model is not None:
            return True
        else:
            return False
    
    def set_source_spectra(self, kV, takeOffAngle=11.0, Z=74):
        self.kV = kV
        self.takeoff_angle = takeOffAngle
        self.anode_material = Z
    
    def add_filter(self, material, mass_density, thickness):
        if mass_density is None:
            mass_density = self.physics.massDensity(material)
        if self.xray_filters is None:
            self.xray_filters = [(material, mass_density, thickness)]
        else:
            self.xray_filters.append((material, mass_density, thickness))
    
    def clear_filters(self):
        self.xray_filters = None
        
    def set_detector_response(self, material, mass_density, thickness):
        if mass_density is None:
            mass_density = self.physics.massDensity(material)
        self.detector_response_model = [material, mass_density, thickness]
        
    def clear_detector_response(self):
        self.detector_response_model = None
        
    def set_object_model(self, material, mass_density=None):
        if mass_density is None or mass_density == 0.0:
            mass_density = self.physics.massDensity(material)
        self.object_model = [material, mass_density]
        
    def clear_object_model(self):
        self.object_model = None
    
    def source_spectra(self, do_normalize=False):
        if has_physics == False:
            print('Error: XrayPhysics library not found!')
            return None, None
        elif self.source_spectra_defined() == False:
            print('Error: spectra not defined!')
            return None, None
        else:
            # Set source spectra
            if self.is_number(self.source_spectra_file):
                Es = np.array([float(self.source_spectra_file)], dtype=np.float32)
                s = Es.copy()
                s[:] = 1.0
            elif self.source_spectra_file is not None and os.path.isfile(self.source_spectra_file):
                Es, s = self.physics.load_spectra(self.source_spectra_file)
                if Es is None or s is None:
                    return None, None
            else:
                Es, s = self.physics.simulateSpectra(self.kV, self.takeoff_angle, self.anode_material)
                
                if self.lowest_energy >= 1.0 or self.energy_bin_width >= 1.0:
                    if self.lowest_energy >= 1.0:
                        lowest_energy  = self.lowest_energy
                    else:
                        lowest_energy  = Es[0]
                    if self.energy_bin_width >= 1.0:
                        energy_bin_width  = self.energy_bin_width
                    else:
                        energy_bin_width  = Es[1]-Es[0]
                    N_E = int(np.ceil((Es[-1]-lowest_energy) / energy_bin_width))
                    Es = np.array(range(N_E), dtype=np.float32)*energy_bin_width + lowest_energy
                    Es, s = self.physics.simulateSpectra(self.kV, self.takeoff_angle, self.anode_material, Es)
                    
            
            # Set filter response
            if self.xray_filters is not None:
                #print(len(self.xray_filters))
                #print(self.xray_filters)
                for n in range(len(self.xray_filters)):
                    s *= self.physics.filterResponse(self.xray_filters[n][0], self.xray_filters[n][1], self.xray_filters[n][2], Es)
            if do_normalize:
                self.physics.normalizeSpectrum(s, Es)
            return Es, s
            
    def detector_response(self, Es):
        if has_physics == False:
            print('Error: XrayPhysics library not found!')
            return None, None
        elif self.detector_response_file is not None and os.path.isfile(self.detector_response_file):
            Es_new, s = self.physics.load_spectra(self.detector_response_file)
            return Es_new, s
        elif Es is None:
            print('Error: energy bins not defined!')
            return None, None
        elif self.detector_response_model is not None:
            s = self.physics.detectorResponse(self.detector_response_model[0], self.detector_response_model[1], self.detector_response_model[2], Es)
            return Es, s
        else:
            s = Es.copy()
            s[:] = 1.0
            return Es, s
    
    def totalSystemSpectralResponse(self, do_normalize=False):
        if has_physics == False:
            print('Error: XrayPhysics library not found!')
            return None, None
        elif self.source_spectra_defined() == False:
            print('Error: spectra not defined!')
            return None, None
        else:
            Es, s = self.source_spectra()
            if Es is None or s is None:
                return None, None

            dont_care, d = self.detector_response(Es)
            if d is not None:
                s *= d
            
            if do_normalize:
                self.physics.normalizeSpectrum(s, Es)
            return Es, s
            
            
    ###################################################################################################################
    ###################################################################################################################
    # PREPROCESSING ALGORITHMS
    ###################################################################################################################
    ###################################################################################################################
    def grab_single_projection(self, iProj):
        iProj = max(0, min(self.leapct.get_numAngles()-1, iProj))
        if self.g is None:
            aProj = self.load_projection_angles(inds=[iProj, iProj])
            if aProj is None:
                print('Error: failed to load data')
                return None
        else:
            aProj = np.zeros((1, self.g.shape[1], self.g.shape[2]), dtype=np.float32)
            aProj[0,:,:] = self.g[iProj, :, :]
        return aProj
        
    def grab_necessary_sinograms_for_reconstruction(self, iz):
        if self.leapct.ct_geometry_defined() == False or self.leapct.ct_volume_defined() == False:
            return None, None
        if iz < 0 or iz >= self.leapct.get_numZ():
            iz = self.leapct.get_numZ()//2
        rowRange = self.leapct.rowRangeNeededForBackprojection(iz)
        #print(rowRange)
        if rowRange is None:
            return None, None
        
        if self.g is None:
            g_ROI = self.load_projection_rows(inds=rowRange)
        else:
            g_ROI = np.zeros((self.g.shape[0], rowRange[1]-rowRange[0]+1, self.g.shape[2]), dtype=np.float32)
            g_ROI[:,:,:] = self.g[:,rowRange[0]:rowRange[1]+1,:]
        return g_ROI, rowRange
    
    def grab_slices(self, sliceRange):
        if self.f is None:
            f_ROI = self.load_volume(inds=sliceRange)
        else:
            f_ROI = np.zeros((sliceRange[1]-sliceRange[0]+1, self.f.shape[1], self.f.shape[2]), dtype=np.float32)
            f_ROI[:,:,:] = self.f[sliceRange[0]:sliceRange[1]+1,:,:]
        return f_ROI
    
    def stacked_projection(self):
        if self.data_type == self.UNSPECIFIED:
            print('Error: must specify data_type')
            return None
        elif self.g is None:
            self.g = self.load_projections()
        if self.g is None:
            print('Error: failed to load data')
            return None
        else:
            if self.data_type == self.ATTENUATION:
                if has_torch == True and type(self.g) is torch.Tensor:
                    g_stack = torch.max(self.g,axis=0)
                else:
                    g_stack = np.max(self.g,axis=0)
            else:
                if has_torch == True and type(self.g) is torch.Tensor:
                    g_stack = torch.min(self.g,axis=0)
                else:
                    g_stack = np.min(self.g,axis=0)
            return g_stack
            
    
    def gain_correction(self, calibration_scans=None, ROI=None, badPixelFile=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
            
        if ROI is not None:
            if ROI[0] < 0 or ROI[2] < 0 or ROI[1] < ROI[0] or ROI[3] < ROI[2] or ROI[1] >= self.leapct.get_numRows() or ROI[3] >= self.leapct.get_numCols():
                print('Error: invalid ROI')
                return False
            
        air_scan = None
        dark_scan = None
        
        # FIXME: load bad pixel map from file
        badPixelMap = self.read_image_file(badPixelFile)
        
        #Read in air and dark scan images if necessary
        if self.data_type <= self.UNSPECIFIED or self.data_type > self.ATTENUATION:
            print('Error: must specify data_type')
            return False
        
        if self.data_type == self.RAW:
            dark_scan = self.read_image_file(self.dark_scan_file)
            if dark_scan is None:
                print('Error: failed to load dark scan file')
                return False
        else:
            print('Nothing to do; this function is only for processing raw data')
            return True
            
        if self.data_type == self.RAW or self.data_type == self.RAW_DARK_SUBTRACTED:
            air_scan = self.read_image_file(self.air_scan_file)
            if air_scan is None:
                print('Error: failed to load air scan file')
                return False
            
        if self.g is None:
            self.g = self.load_projections()
            if self.g is None:
                print('Error: failed to load data')
                return False
        
        if self.data_type == self.ATTENUATION:
            self.g = self.leapct.expNeg(self.g)
        
        func = lambda g: leap_preprocessing_algorithms.gain_correction(self.leapct, g, air_scan, dark_scan, calibration_scans, ROI, badPixelMap)
        if func(self.g) == True:
            self.data_type = self.RAW_DARK_SUBTRACTED

            # need to save air scan file
            baseFileName, fileExtension = os.path.splitext(os.path.basename(self.air_scan_file))
            self.air_scan_file = baseFileName + '_gain' + fileExtension
            self.save_image_file(self.air_scan_file, air_scan, use_outputDir=False)
            
            return True
        else:
            return False
    
    def makeAttenuationRadiographs(self, ROI=None, tryIndex=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
            
        if ROI is not None:
            if ROI[0] < 0 or ROI[2] < 0 or ROI[1] < ROI[0] or ROI[3] < ROI[2] or ROI[1] >= self.leapct.get_numRows() or ROI[3] >= self.leapct.get_numCols():
                print('Error: invalid ROI')
                return False
            
        air_scan = None
        dark_scan = None
            
        #Read in air and dark scan images if necessary
        if self.data_type <= self.UNSPECIFIED or self.data_type > self.ATTENUATION:
            print('Error: must specify data_type')
            return False
        
        if self.data_type == self.RAW:
            dark_scan = self.read_image_file(self.dark_scan_file)
            if dark_scan is None:
                print('Error: failed to load dark scan file')
                return False
            
        if self.data_type == self.RAW or self.data_type == self.RAW_DARK_SUBTRACTED:
            air_scan = self.read_image_file(self.air_scan_file)
            if air_scan is None:
                print('Error: failed to load air scan file')
                return False
            
        func = lambda g: leap_preprocessing_algorithms.makeAttenuationRadiographs(self.leapct, g, air_scan, dark_scan, ROI)
        
        if tryIndex is None:
        
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
        
            if self.data_type == self.ATTENUATION:
                self.leapct.expNeg(self.g)
            
            if func(self.g) == True:
                self.data_type = self.ATTENUATION
                return True
            else:
                return False
        else:
            aProj = self.grab_single_projection(tryIndex)
            if aProj is None:
                return False
                
            if self.data_type == self.ATTENUATION:
                self.leapct.expNeg(aProj)
            
            if func(aProj) == True:
                self.lastImage = np.squeeze(aProj)
                return True
            else:
                self.lastImage = None
                return False
                
    def crop_projections(self, rowRange=None, colRange=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
            if rowRange is not None or colRange is not None:
                self.g = self.leapct.crop_projections(rowRange, colRange, self.g)
            return True
        else:
            print('Error: crop projections current only implemented for attenuation data')
            return False
        
    def badPixelCorrection(self, badPixelFile=None, windowSize=5):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
            
        # FIXME: load bad pixel map from file
        badPixelMap = self.read_image_file(badPixelFile)
        
        air_scan = None
        dark_scan = None
            
        #Read in air and dark scan images if necessary
        if self.data_type <= self.UNSPECIFIED or self.data_type > self.ATTENUATION:
            print('Error: must specify data_type')
            return False
        
        if self.data_type == self.RAW:
            dark_scan = self.read_image_file(self.dark_scan_file)
            if dark_scan is None:
                print('Error: failed to load dark scan file')
                return False
            
        if self.data_type == self.RAW or self.data_type == self.RAW_DARK_SUBTRACTED:
            air_scan = self.read_image_file(self.air_scan_file)
            if air_scan is None:
                print('Error: failed to load air scan file')
                return False
        
        if self.g is None:
            self.g = self.load_projections()
            if self.g is None:
                print('Error: failed to load data')
                return False
        
        if leap_preprocessing_algorithms.badPixelCorrection(self.leapct, self.g, air_scan, dark_scan, badPixelMap, windowSize, self.data_type == self.ATTENUATION) == True:
            if air_scan is not None:
                # need to save air scan file
                baseFileName, fileExtension = os.path.splitext(os.path.basename(self.air_scan_file))
                self.air_scan_file = baseFileName + '_badpix' + fileExtension
                self.save_image_file(self.air_scan_file, air_scan, use_outputDir=False)
                #plt.imshow(air_scan)
                #plt.show()
            if dark_scan is not None:
                # need to save dark scan file
                baseFileName, fileExtension = os.path.splitext(os.path.basename(self.dark_scan_file))
                self.dark_scan_file = baseFileName + '_badpix' + fileExtension
                self.save_image_file(self.dark_scan_file, dark_scan, use_outputDir=False)
                #plt.imshow(dark_scan)
                #plt.show()

            return True
        else:
            return False
        
    def outlierCorrection(self, threshold=0.03, windowSize=3, tryIndex=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if tryIndex is None:
                if self.g is None:
                    self.g = self.load_projections()
                    if self.g is None:
                        print('Error: failed to load data')
                        return False
                return leap_preprocessing_algorithms.outlierCorrection(self.leapct, self.g, threshold, windowSize, isAttenuationData=True)
            else:
                aProj = self.grab_single_projection(tryIndex)
                if aProj is None:
                    return False
                    
                if leap_preprocessing_algorithms.outlierCorrection(self.leapct, aProj, threshold, windowSize, isAttenuationData=True) == True:
                    self.lastImage = np.squeeze(aProj)
                    return True
                else:
                    self.lastImage = None
                    return False
        else:
            print('Error: outlier correction current only implemented for attenuation data')
            return False
        
    def outlierCorrection_highEnergy(self, tryIndex=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if tryIndex is None:
                if self.g is None:
                    self.g = self.load_projections()
                    if self.g is None:
                        print('Error: failed to load data')
                        return False
                return leap_preprocessing_algorithms.outlierCorrection_highEnergy(self.leapct, self.g, isAttenuationData=True)
            else:
                aProj = self.grab_single_projection(tryIndex)
                if aProj is None:
                    return False
                    
                if leap_preprocessing_algorithms.outlierCorrection_highEnergy(self.leapct, aProj, isAttenuationData=True) == True:
                    self.lastImage = np.squeeze(aProj)
                    return True
                else:
                    self.lastImage = None
                    return False
        else:
            print('Error: outlier correction current only implemented for attenuation data')
            return False
        
    def detectorDeblur_FourierDeconv(self, H, WienerParam=0.0):
        #leap_preprocessing_algorithms.detectorDeblur_FourierDeconv(self.leapct, ...)
        pass
        
    def detectorDeblur_RichardsonLucy(self, H, numIter=10):
        #leap_preprocessing_algorithms.detectorDeblur_RichardsonLucy(self.leapct, ...)
        pass
        
    def find_centerCol(self, iRow=-1):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
            self.leapct.find_centerCol(self.g, iRow)
            return True
        else:
            print('Error: find_centerCol current only implemented for attenuation data')
            return False
            
    def conjugate_difference(self, alpha=0.0, centerCol=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
            self.lastImage = self.leapct.conjugate_difference(self.g, alpha, centerCol)
            return True
        else:
            print('Error: conjugate_difference current only implemented for attenuation data')
            return False
    
    def estimate_tilt(self):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return 0.0
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return 0.0
            return self.leapct.estimate_tilt(self.g)
        else:
            print('Error: estimate_tilt current only implemented for attenuation data')
            return 0.0
    
    def ringRemoval_fast(self, delta=0.01, numIter=30, maxChange=0.05, tryIndex=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if tryIndex is None:
                if self.g is None:
                    self.g = self.load_projections()
                    if self.g is None:
                        print('Error: failed to load data')
                        return False
                return leap_preprocessing_algorithms.ringRemoval_fast(self.leapct, self.g, delta, numIter, maxChange)
            else:
                iz = tryIndex
                if iz < 0 or iz >= self.leapct.get_numZ():
                    iz = self.leapct.get_numZ()//2
                g_ROI, rowRange = self.grab_necessary_sinograms_for_reconstruction(iz)
                if g_ROI is None:
                    print('Error: failed to load data')
                    return False
                
                leap_preprocessing_algorithms.ringRemoval_fast(self.leapct, g_ROI, delta, numIter, maxChange)
                self.leapct_backup.copy_parameters(self.leapct)
                self.leapct_backup.crop_projections(rowRange)
                f_slice = self.leapct_backup.FBP_slice(g_ROI, iz)
                del g_ROI
                self.lastImage = np.squeeze(f_slice)
                
                return True
        else:
            print('Error: ring removal current only implemented for attenuation data')
            return False
        
    def ringRemoval_median(self, threshold=0.0, windowSize=5, numIter=1):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
            return leap_preprocessing_algorithms.ringRemoval_median(self.leapct, self.g, threshold, windowSize, numIter)
        else:
            print('Error: ring removal current only implemented for attenuation data')
            return False
        
    def ringRemoval(self, delta=0.01, beta=1.0e1, numIter=30):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
            return leap_preprocessing_algorithms.ringRemoval(self.leapct, self.g, delta, beta, numIter)
        else:
            print('Error: ring removal current only implemented for attenuation data')
            return False
        
    def parameter_sweep(self, values, param='centerCol', iz=None, algorithmName='FBP'):
        if self.leapct.all_defined() == False:
            print('Error: CT geometry and CT volume must be defined before running this algorithm!')
            return False
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
            f_stack = leap_preprocessing_algorithms.parameter_sweep(self.leapct, self.g, values, param, iz, algorithmName)
            if f_stack is None:
                return False
            else:
                if f_stack.shape[0] == 1 or len(f_stack.shape) == 2:
                    plt.imshow(np.squeeze(f_stack), cmap='gray', interpolation='nearest')
                    plt.show()
                else:
                    self.leapct.display(f_stack)
                return True
        else:
            print('Error: parameter_sweep current only implemented for attenuation data')
            return False
    
    def polynomialBHC(self, coeffs, tryIndex=None):
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if coeffs is None:
            print('Error: must define the polynomial coefficients for BHC')
            
        if self.data_type == self.ATTENUATION:
            if self.g is None:
                self.g = self.load_projections()
                if self.g is None:
                    print('Error: failed to load data')
                    return False
        else:
            print('Error: polynomialBHC current only implemented for attenuation data')
            return False

        if tryIndex is not None:
            iz = tryIndex
            if iz < 0 or iz >= self.leapct.get_numZ():
                iz = self.leapct.get_numZ()//2
            g_ROI, rowRange = self.grab_necessary_sinograms_for_reconstruction(iz)
            if g_ROI is None:
                print('Error: failed to load data')
                return False
            
            self.apply_polynomial(g_ROI, coeffs)
            self.leapct_backup.copy_parameters(self.leapct)
            self.leapct_backup.crop_projections(rowRange)
            f_slice = self.leapct_backup.FBP_slice(g_ROI, iz)
            del g_ROI
            self.lastImage = np.squeeze(f_slice)

        else:
            self.apply_polynomial(self.g, coeffs)
        
        return True
    
    def apply_polynomial(self, g, coeffs):
    
        if coeffs.size == 1:
            if coeffs[0] != 1.0:
                g[:] = coeffs[0]*g[:]
        elif coeffs.size == 2:
            if coeffs[0] != 1.0 or coeffs[1] != 0.0:
                g[:] = coeffs[0]*g[:] + coeffs[1]*g[:]**2
        elif coeffs.size == 3:
            if coeffs[0] != 1.0 or coeffs[1] != 0.0 or coeffs[2] != 0.0:
                g[:] = coeffs[0]*g[:] + coeffs[1]*g[:]**2 + coeffs[2]*g[:]**3
        elif coeffs.size == 4:
            if coeffs[0] != 1.0 or coeffs[1] != 0.0 or coeffs[2] != 0.0 or coeffs[3] != 0.0:
                g[:] = coeffs[0]*g[:] + coeffs[1]*g[:]**2 + coeffs[2]*g[:]**3 + coeffs[3]*g[:]**4
        else:
            if coeffs[0] != 1.0 or coeffs[1] != 0.0 or coeffs[2] != 0.0 or coeffs[3] != 0.0 or coeffs[4] != 0.0:
                g[:] = coeffs[0]*g[:] + coeffs[1]*g[:]**2 + coeffs[2]*g[:]**3 + coeffs[3]*g[:]**4 + coeffs[4]*g[:]**5
    
    def singleMaterialBHC(self, material=None, tryIndex=None):
        if has_physics == False:
            print('Error: BHC requires the XrayPhysics package!')
            return False
        if self.leapct.ct_geometry_defined() == False:
            print('Error: CT geometry not defined!')
            return False
        if self.source_spectra_defined() == False:
            print('Error: spectra not defined!')
        if material is None:
            if self.object_model is not None:
                material = self.object_model[0]
            else:
                print('Error: must define material for BHC')
                return False
            
        if self.data_type == self.ATTENUATION:
        
            Es, s_total = self.totalSystemSpectralResponse()
            if self.reference_energy is None or self.reference_energy < Es[0] or self.reference_energy > Es[-1]:
                self.reference_energy = self.physics.meanEnergy(s_total, Es)
            BHC_LUT, T_lut = self.physics.setBHClookupTable(s_total, Es, material, self.reference_energy)
            if BHC_LUT is None:
                return False
            
            if tryIndex is not None:
                iz = tryIndex
                if iz < 0 or iz >= self.leapct.get_numZ():
                    iz = self.leapct.get_numZ()//2
                g_ROI, rowRange = self.grab_necessary_sinograms_for_reconstruction(iz)
                if g_ROI is None:
                    print('Error: failed to load data')
                    return False
                
                self.leapct.applyTransferFunction(g_ROI, BHC_LUT, T_lut)
                self.leapct_backup.copy_parameters(self.leapct)
                self.leapct_backup.crop_projections(rowRange)
                f_slice = self.leapct_backup.FBP_slice(g_ROI, iz)
                del g_ROI
                self.lastImage = np.squeeze(f_slice)
                
                return True
                
            else:
                if self.g is None:
                    self.g = self.load_projections()
                    if self.g is None:
                        print('Error: failed to load data')
                        return False

                self.leapct.applyTransferFunction(self.g, BHC_LUT, T_lut)
                return True
            
        else:
            print('Error: singleMaterialBHC current only implemented for attenuation data')
            return False
            
    def projection_processing(self, func, g):
        func(g)
        
    def sinogram_processing(self):
        pass
        
    def reconstruction_slab_processing(self):
        pass
    
    ###################################################################################################################
    ###################################################################################################################
    # RECONSTRUCTION ALGORITHMS
    ###################################################################################################################
    ###################################################################################################################
    def project(self):
        if self.leapct.all_defined() == False:
            print('Error: CT geometry and CT volume must be defined before running this algorithm!')
            return False
        if self.data_type != self.ATTENUATION:
            print('Error: data_type must be ATTENUATION for projection')
            return False
        if self.f is None:
            self.f = self.load_volume(self.reconstruction_file)
            if self.f is None:
                print('Error: failed to load volume data')
                return False
        if self.leapct.project(self.g, self.f) is not None:
            return True
        else:
            return False
        
    def backproject(self):
        if self.leapct.all_defined() == False:
            print('Error: CT geometry and CT volume must be defined before running this algorithm!')
            return False
        if self.data_type != self.ATTENUATION:
            print('Error: data_type must be ATTENUATION for reconstruction')
            return False
        if self.g is None:
            self.g = self.load_projections()
            if self.g is None:
                print('Error: failed to load data')
                return False
        if self.leapct.backproject(self.g, self.f) is not None:
            return True
        else:
            return False
        
    def FBP(self, doClipping=False):
        if self.leapct.all_defined() == False:
            print('Error: CT geometry and CT volume must be defined before running this algorithm!')
            return False
        if self.data_type != self.ATTENUATION:
            print('Error: data_type must be ATTENUATION for reconstruction')
            return False
        
        if self.projection_memory() >= self.max_CPU_memory_usage:
            print('Error: insufficient memory!')
            return False
        
        if self.g is None:
            self.g = self.load_projections()
            if self.g is None:
                print('Error: failed to load data')
                return False

        if self.f is not None:
            del self.f
        if self.projection_memory() + self.volume_memory() < self.max_CPU_memory_usage:
            self.f = self.leapct.allocate_volume()
            if self.leapct.FBP(self.g, self.f) is not None:
                if doClipping:
                    self.f[self.f<0.0] = 0.0
                return True
            else:
                return False
        else:
            # chunking!
            output_file = os.path.join(self.outputDir, 'zslice.tif')
            output_full_path = os.path.join(self.path, output_file)
            self.create_outputDir()
            self.chunking_type = self.Z_SLICE
            self.num_vol = 1
            self.num_proj = 1
            self.set_chunk_size()
            if self.chunk_size < 1:
                print('Error: insufficient memory!')
                return False
                
            numChunks = int(np.ceil(float(self.leapct.get_numZ())/float(self.chunk_size)))
            z = self.leapct.z_samples()
            
            print('Performing FBP in ' + str(numChunks) + ' chunks of ' + str(self.chunk_size) + ' slices...')
            
            for n in range(numChunks):
                print('processing chunk ' + str(n+1) + ' of ' + str(numChunks))
                self.leapct_backup.copy_parameters(self.leapct)
                
                sliceStart = n*self.chunk_size
                sliceEnd = min(z.size-1, sliceStart + self.chunk_size - 1)
                numZ = sliceEnd - sliceStart + 1
                
                self.leapct_backup.set_numZ(numZ)
                self.leapct_backup.set_offsetZ(self.leapct_backup.get_offsetZ() + z[sliceStart]-self.leapct_backup.get_z0())
                rowRange = self.leapct_backup.rowRangeNeededForBackprojection()

                g_chunk = self.leapct_backup.cropProjections(rowRange, None, self.g)
                
                f_chunk = self.leapct_backup.FBP(g_chunk)
                del g_chunk
                
                if doClipping:
                    f_chunk[f_chunk<0.0] = 0.0
                
                self.leapct_backup.save_volume(output_full_path, f_chunk, sliceStart)
                del f_chunk
            self.reconstruction_file = output_file
            return True
            
    def FBP_slice(self, islice=None, coord='z'):
        if self.leapct.all_defined() == False:
            print('Error: CT geometry and CT volume must be defined before running this algorithm!')
            return None
        if self.data_type != self.ATTENUATION:
            print('Error: data_type must be ATTENUATION for reconstruction')
            return None
        if self.g is None:
            self.g = self.load_projections()
            if self.g is None:
                print('Error: failed to load data')
                return None
        f_slice = self.leapct.FBP_slice(self.g, islice, coord)
        return f_slice
        
    def inconsistencyReconstruction(self):
        if self.leapct.all_defined() == False:
            print('Error: CT geometry and CT volume must be defined before running this algorithm!')
            return False
        if self.data_type != self.ATTENUATION:
            print('Error: data_type must be ATTENUATION for reconstruction')
            return False
        if self.g is None:
            self.g = self.load_projections()
            if self.g is None:
                print('Error: failed to load data')
                return False
        if self.leapct.inconsistencyReconstruction(self.g, self.f) is not None:
            return True
        else:
            return False
        
    def SIRT(self, numIter, mask=None):
        #self.leapct.SIRT(g, f, numIter, mask)
        pass
        
    def SART(self, numIter, numSubsets=1, mask=None):
        #self.leapct.SART(g, f, numIter, numSubsets, mask)
        pass
        
    def ASDPOCS(self, numIter, numSubsets, numTV, filters=None, mask=None):
        #self.leapct.ASDPOCS(g, f, numIter, numSubsets, numTV, filters, mask)
        pass
        
    def LS(self, numIter, preconditioner=None, nonnegativityConstraint=True):
        #self.leapct.LS(g, f, numIter, preconditioner, nonnegativityConstraint)
        pass
        
    def WLS(self, numIter, W=None, preconditioner=None, nonnegativityConstraint=True):
        #self.leapct.WLS(g, f, numIter, W, preconditioner, nonnegativityConstraint)
        pass
        
    def RLS(self, numIter, filters=None, preconditioner=None, nonnegativityConstraint=True):
        #self.leapct.RLS(g, f, numIter, filters, preconditioner, nonnegativityConstraint)
        pass
        
    def RWLS(self, numIter, filters=None, W=None, preconditioner=None, nonnegativityConstraint=True):
        #self.leapct.RWLS(g, f, numIter, filters, W, preconditioner, nonnegativityConstraint)
        pass
        
    def DLS(self, numIter, preconditionerFWHM=1.0, nonnegativityConstraint=False, dimDeriv=2):
        #self.leapct.DLS(g, f, numIter, preconditionerFWHM, nonnegativityConstraint, dimDeriv)
        pass
        
    def RDLS(self, numIter, filters=None, preconditionerFWHM=1.0, nonnegativityConstraint=False, dimDeriv=1):
        #self.leapct.RDLS(g, f, numIter, filters, preconditionerFWHM, nonnegativityConstraint, dimDeriv)
        pass
        
    def MLTR(self, numIter, numSubsets=1, filters=None, mask=None):
        #self.leapct.MLTR(g, f, numIter, numSubsets, filters, mask)
        pass

    
    ###################################################################################################################
    ###################################################################################################################
    # VOLUME DENOISING
    ###################################################################################################################
    ###################################################################################################################
    def MedianFilter(self, threshold=0.0, windowSize=3, tryIndex=None):
        if self.leapct.ct_volume_defined() == False:
            print('Error: CT volume must be defined before running this algorithm!')
            return False
        if tryIndex is None:
            if self.f is None:
                
                if self.memory_usage() + self.volume_memory() >= self.max_CPU_memory_usage:
                    print('Error: not enough CPU RAM to run this algorithm!')
                    return False
                
                self.f = self.load_volume(self.reconstruction_file)
                if self.f is None:
                    print('Error: failed to load data')
                    return False
            if self.leapct.MedianFilter(self.f, threshold, windowSize) is not None:
                return True
            else:
                return False
        else:
            iz = tryIndex
            numZ = self.leapct.get_numZ()
            if iz < 0 or iz >= numZ:
                iz = numZ//2
            sliceRange = [max(0, min(iz-1, numZ-1)), max(0, min(iz+1, numZ-1))]
            f_ROI = self.grab_slices(sliceRange)
            if f_ROI is None:
                print('Error: failed to load data')
                return False
            else:
                self.leapct.MedianFilter(f_ROI, threshold, windowSize)
                self.lastImage = np.squeeze(f_ROI[f_ROI.shape[0]//2,:,:])
                del f_ROI
                return True
        
    def MedianFilter2D(self, threshold=0.0, windowSize=3, tryIndex=None):
        if self.leapct.ct_volume_defined() == False:
            print('Error: CT volume must be defined before running this algorithm!')
            return False
        if tryIndex is None:
            if self.f is None:
            
                if self.memory_usage() + self.volume_memory() >= self.max_CPU_memory_usage:
                    print('Error: not enough CPU RAM to run this algorithm!')
                    return False
            
                self.f = self.load_volume(self.reconstruction_file)
                if self.f is None:
                    print('Error: failed to load data')
                    return False
            if self.leapct.MedianFilter2D(self.f, threshold, windowSize) is not None:
                return True
            else:
                return False
        else:
            iz = tryIndex
            numZ = self.leapct.get_numZ()
            if iz < 0 or iz >= numZ:
                iz = numZ//2
            sliceRange = [iz, iz]
            f_ROI = self.grab_slices(sliceRange)
            if f_ROI is None:
                print('Error: failed to load data')
                return False
            else:
                self.leapct.MedianFilter2D(f_ROI, threshold, windowSize)
                self.lastImage = np.squeeze(f_ROI[f_ROI.shape[0]//2,:,:])
                del f_ROI
                return True
        
    def TVdenoising(self, delta=0.001, beta=1.0e1, numIter=20, p=1.2, tryIndex=None):
        if self.leapct.ct_volume_defined() == False:
            print('Error: CT volume must be defined before running this algorithm!')
            return False
        if tryIndex is None:
            if self.f is None:
                
                if self.memory_usage() + self.volume_memory() >= self.max_CPU_memory_usage:
                    print('Error: not enough CPU RAM to run this algorithm!')
                    return False
            
                self.f = self.load_volume(self.reconstruction_file)
                if self.f is None:
                    print('Error: failed to load data')
                    return False
            if self.leapct.TV_denoise(self.f, delta, beta, numIter, p) is not None:
                return True
            else:
                return False
        else:
            iz = tryIndex
            numZ = self.leapct.get_numZ()
            if iz < 0 or iz >= numZ:
                iz = numZ//2
            sliceRange = [max(0, min(iz-4, numZ-1)), max(0, min(iz+4, numZ-1))]
            f_ROI = self.grab_slices(sliceRange)
            if f_ROI is None:
                print('Error: failed to load data')
                return False
            else:
                self.leapct.TV_denoise(f_ROI, delta, beta, numIter, p)
                self.lastImage = np.squeeze(f_ROI[f_ROI.shape[0]//2,:,:])
                del f_ROI
                return True
    
    ###################################################################################################################
    ###################################################################################################################
    # GUI UTILITY FUNCTIONS
    ###################################################################################################################
    ###################################################################################################################
    def run(self, text, optional=None):
        return self.cmd(text)
    
    def cmd(self, text, optional=None):
        if "=" in text:
            return self.set_cmd(text)
        elif text.startswith("clear"):
            return self.clear_cmd(text)
        elif text == "trackHistory":
            return False
        else:
            print("Error cmd (" + str(text) + ") failed!")
            return False
            
    def clear_cmd(self, text):
        key = text.split(' ')[1].strip()
        #print("Error: clear command not yet implemented")
        match key:
            case "archdir" | "path":
                self.path = ""
            case "outputdir":
                self.outputDir = ""
            case "dataType":
                #[self.UNSPECIFIED, self.RAW, self.RAW_DARK_SUBTRACTED, self.TRANSMISSION, self.ATTENUATION]
                self.dataType = self.UNSPECIFIED
            case "backgroundFile":
                self.air_scan_file = ""
            case "darkCurrentFile":
                self.dark_scan_file = ""
            case "sfile":
                self.raw_scan_file = ""
            case "pfile":
                self.projection_file = ""
            case "rfile":
                self.reconstruction_file = ""
            case "systemGeometryFile":
                self.geometry_file = ""
            case "lengthUnits":
                pass
            case "bgeometry":
                self.leapct.set_geometry(0)
            case "geometry":
                self.leapct.set_geometry(0)
            case "sod":
                self.leapct.set_sod(0.0)
            case "sdd":
                self.leapct.set_sdd(0.0)
            case "odd":
                pass
            case "helicalpitch":
                self.leapct.set_helicalPitch(0.0)
            case "nangles":
                self.num_angles = 0
                self.leapct.set_numAngles(0)
            case "initangle":
                self.init_angle = 0.0
                phis = self.leapct.get_angles()
                if phis is not None:
                    phis -= phi[0]
                    self.leapct.set_angles(phis)
            case "arange":
                self.angular_range = 0.0
                self.angular_step = 0.0
                self.leapct.set_numAngles(0)
            case "rotationDirection":
                phis = self.leapct.get_angles()
                if phis is not None and phis.size > 1:
                    if phis[1] < phis[0]:
                        phis *= -1.0
                        self.leapct.set_angles(phis)
            case "rotationdirection":
                phis = self.leapct.get_angles()
                if phis is not None and phis.size > 1:
                    if phis[1] < phis[0]:
                        phis *= -1.0
                        self.leapct.set_angles(phis)
            case "nrays":
                self.leapct.set_numCols(0)
            case "nslices":
                self.leapct.set_numRows(0)
            case "pxcenter":
                self.leapct.set_centerCol(0.0)
            case "pzcenter":
                self.leapct.set_centerRow(0.0)
            case "pxmidoff":
                leapct.set_tau(0.0)
            case "pxsize":
                self.leapct.set_pixelWidth(0.0)
            case "pzsize":
                self.leapct.set_pixelHeight(0.0)
            case "detectorShape":
                self.leapct.set_flatDetector()
            case "detectorResponseFile":
                self.detector_response_file = ""
            case "kV":
                self.kV = -1.0
            case "takeOffAngle":
                self.takeoff_angle = 11.0
            case "anodeMaterial":
                self.anode_material = 74
            case "filterMaterials":
                self.xray_filters = None
            case "spectraFile":
                #self.spectra_model_file = ""
                self.source_spectra_file = ""
            case "referenceEnergy":
                self.reference_energy = -1.0
            case "rfilter":
                self.leapct.set_rampFilter(2)
            case "rampFWHM":
                self.leapct.set_FBPlowpass(1.0)
            case "rxsize":
                self.leapct.set_voxelWidth(0.0)
            case "rysize":
                self.leapct.set_voxelWidth(0.0)
            case "rzsize":
                self.leapct.set_voxelHeigh(0.0)
            case "rxref":
                self.leapct.set_offsetX(0.0)
            case "ryref":
                self.leapct.set_offsetY(0.0)
            case "rzref":
                self.leapct.set_offsetZ(0.0)
            case "rxoffset":
                pass
            case "ryoffset":
                pass
            case "rzoffset":
                pass
            case "rxelements":
                self.leapct.set_numX(0)
            case "ryelements":
                self.leapct.set_numY(0)
            case "rzelements":
                self.leapct.set_numZ(0)
            case "axisOfSymmetry":
                self.leapct.clear_axisOfSymmetry()
            case "halfscan":
                self.leapct.set_offsetScan(False)
            case _:
                print("Error: cmd keyword " + str(key) + " not yet implemented!")
                return False
        return True
    
    def set_cmd(self, text, printError=True):
        key = text.split('=')[0].strip()
        value = text.split('=')[1].strip()
        self.set_key_value_pairs(key, value, printError)
        
    def set_key_value_pairs(self, key, value, printError=True):
        match key:
            case "archdir" | "path":
                self.path = value
            case "outputdir":
                self.outputDir = value
            case "dataType" | "data_type":
                #[self.UNSPECIFIED, self.RAW, self.RAW_DARK_SUBTRACTED, self.TRANSMISSION, self.ATTENUATION]
                if value.upper() == "RAW_UNCALIB" or value.upper() == "RAW":
                    self.data_type = self.RAW
                elif value.upper() == "RAW_CALIB" or value.upper() == "RAW_DARKSUB" or value.upper() == "RAW_DARK_SUBTRACTED":
                    self.data_type = self.RAW_DARK_SUBTRACTED
                elif value.upper() == "TRANS_RAD" or value.upper() == "TRANSMISSION":
                    self.data_type = self.TRANSMISSION
                elif value.upper() == "ATTEN_RAD" or value.upper() == "ATTENUATION" or value.upper() == "SINOGRAM":
                    self.data_type = self.ATTENUATION
                elif value.upper() == "RECXY":
                    self.data_type = self.UNSPECIFIED
            case "backgroundFile" | "air_scan_file":
                self.air_scan_file = value
            case "darkCurrentFile" | "dark_scan_file":
                self.dark_scan_file = value
            case "sfile" | "scan_file" | "raw_scan_file":
                self.raw_scan_file = value
            case "Filename Prefix":
                self.raw_scan_file = value + str("*[0-9].tif")
            case "pfile" | "projection_file":
                self.projection_file = value
            case "rfile":
                self.reconstruction_file = value
            case "systemGeometryFile" | "system_geometry_file" | "geometry_file":
                self.geometry_file = value
            case "lengthUnits":
                pass
            case "bgeometry" | "geometry":
                self.leapct.set_geometry(value)
            case "geometry":
                self.leapct.set_geometry(value)
            case "sod" | "Object to Source (mm)":
                self.leapct.set_sod(float(value))
            case "sdd" | "Camera to Source (mm)":
                self.leapct.set_sdd(float(value))
            case "odd":
                pass
            case "helicalpitch" | "helicalPitch" | "helical_pitch":
                self.leapct.set_helicalPitch(float(value))
            case "nangles" | "numAngles" | "Number of Files":
                self.num_angles = int(value)
                if key == "Number of Files":
                    self.num_angles = self.num_angles - 1
                self.leapct.set_numAngles(int(value))
                if self.num_angles > 0 and self.angular_range != 0.0:
                    phis = self.init_angle + self.leapct.setAngleArray(self.num_angles, self.angular_range)
                    self.leapct.set_angles(phis)
                elif self.num_angles > 0 and self.angular_step != 0.0:
                    phis = self.init_angle + self.leapct.setAngleArray(self.num_angles, self.angular_step*self.num_angles)
                    self.leapct.set_angles(phis)
            case "initangle" | "init_angle":
                self.init_angle = float(value)
                if self.num_angles > 0 and self.angular_range != 0.0:
                    phis = self.init_angle + self.leapct.setAngleArray(self.num_angles, self.angular_range)
                    self.leapct.set_angles(phis)
                elif self.num_angles > 0 and self.angular_step != 0.0:
                    phis = self.init_angle + self.leapct.setAngleArray(self.num_angles, self.angular_step*self.num_angles)
                    self.leapct.set_angles(phis)
            case "arange" | "angularRange" | "angular_range":
                self.angular_range = float(value)
                if self.num_angles > 0 and self.angular_range != 0.0:
                    phis = self.init_angle + self.leapct.setAngleArray(self.num_angles, self.angular_range)
                    self.leapct.set_angles(phis)
            case "Rotation Step (deg)":
                self.angular_step = float(value)
                if self.num_angles > 0 and self.angular_step != 0.0:
                    phis = self.init_angle + self.leapct.setAngleArray(self.num_angles, self.angular_step*self.num_angles)
                    self.leapct.set_angles(phis)
            case "rotationDirection":
                print("Set rotationDirection not yet implemented!")
            case "nrays" | "numCols" | "Number of Columns":
                self.leapct.set_numCols(int(value))
            case "nslices" | "numRows" | "Number of Rows":
                self.leapct.set_numRows(int(value))
            case "pxcenter" | "centerCol":
                self.leapct.set_centerCol(float(value))
            case "pzcenter" | "centerRow" | "Optical Axis (line)":
                self.leapct.set_centerRow(float(value))
            case "pxmidoff":
                #print("Set pxmidoff not yet implemented!")
                self.leapct.set_tau(float(value))
            case "tau":
                self.leapct.set_tau(float(value))
            case "pxsize" | "pixelWidth":
                self.leapct.set_pixelWidth(float(value))
            case "pzsize" | "pixelHeight":
                self.leapct.set_pixelHeight(float(value))
            case "detectorShape" | "detector_shape" | "detectorType" | "detector_type":
                if value == "FLAT":
                    self.leapct.set_flatDetector()
                else:
                    self.leapct.set_curvedDetector()
            case "detectorResponseFile" | "detector_response_file":
                self.detector_response_file = value
            case "kV" | "Source Voltage (kV)":
                self.kV = float(value)
            case "takeOffAngle":
                self.takeoff_angle = float(value)
            case "anodeMaterial":
                self.anode_material = int(value)
            case "filterMaterials" | "xray_filters":
                if value[0] == '[':
                    self.xray_filters = eval(value)
                else:
                    self.xray_filters = value
            case "object_model":
                if value[0] == '[':
                    self.object_model = eval(value)
                else:
                    self.object_model = value
            case "detector_response_model":
                if value[0] == '[':
                    self.detector_response_model = eval(value)
                else:
                    self.detector_response_model = value
            case "spectraFile" | "source_spectra_file":
                #self.spectra_model_file = value
                self.source_spectra_file = value
            case "referenceEnergy" | "reference_energy":
                self.reference_energy = float(value)
            case "rfilter":
                self.leapct.set_rampFilter(int(value))
            case "rampID" | "rampFilter":
                self.leapct.set_rampFilter(int(value))
            case "rampFWHM" | "FBPlowpass":
                self.leapct.set_FBPlowpass(float(value))
            case "rxsize" | "voxelWidth":
                self.leapct.set_voxelWidth(float(value))
            case "rysize" | "voxelWidth":
                self.leapct.set_voxelWidth(float(value))
            case "rzsize" | "voxelHeight":
                self.leapct.set_voxelHeight(float(value))
            case "rxref":
                #rxref = 0.5*(self.leapct.get_numX()-1) - self.leapct.get_offsetX()/self.leapct.get_voxelWidth()
                rref = float(value)
                offsetX = 0.5*(self.leapct.get_numX()-1)*self.leapct.get_voxelWidth() - rref*self.leapct.get_voxelWidth()
                self.leapct.set_offsetX(offsetX)
            case "ryref":
                rref = float(value)
                offsetY = 0.5*(self.leapct.get_numY()-1)*self.leapct.get_voxelWidth() - rref*self.leapct.get_voxelWidth()
                self.leapct.set_offsetY(offsetY)
            case "rzref":
                rref = float(value)
                offsetZ = 0.5*(self.leapct.get_numZ()-1)*self.leapct.get_voxelHeight() - rref*self.leapct.get_voxelHeight()
                self.leapct.set_offsetZ(offsetZ)
            case "offsetX":
                self.leapct.set_offsetX(float(value))
            case "offsetY":
                self.leapct.set_offsetY(float(value))
            case "offsetZ":
                self.leapct.set_offsetZ(float(value))
            case "rxoffset":
                pass
            case "ryoffset":
                pass
            case "rzoffset":
                pass
            case "rxelements" | "numX":
                self.leapct.set_numX(int(value))
            case "ryelements" | "numY":
                self.leapct.set_numY(int(value))
            case "rzelements" | "numZ":
                self.leapct.set_numZ(int(value))
            case "halfscan" | "offsetScan":
                if value.lower() == "true":
                    self.leapct.set_offsetScan(True)
                elif value.lower() == "false":
                    self.leapct.set_offsetScan(False)
                else:
                    print("Error setting offsetScan")
            case "truncatedScan":
                if value.lower() == "true":
                    self.leapct.set_truncatedScan(True)
                elif value.lower() == "false":
                    self.leapct.set_truncatedScan(False)
                else:
                    print("Error setting truncatedScan")
            case "trackHistory":
                pass
            case "Camera Pixel Size (um)":
                self.leapct.set_pixelWidth(float(value)/1000.0)
                self.leapct.set_pixelHeight(float(value)/1000.0)
            case _:
                if printError:
                    print("Error: cmd keyword " + str(key) + " not yet implemented!")
                return False
        return True
        
    def getParam(self, text):
        match text:
            case "archdir":
                return self.path
            case "outputdir":
                return self.outputDir
            case "dataType":
                #[self.UNSPECIFIED, self.RAW, self.RAW_DARK_SUBTRACTED, self.TRANSMISSION, self.ATTENUATION]
                if self.data_type == 0:
                    return "UNKNOWN"
                elif self.data_type == 1:
                    return "RAW_UNCALIB"
                elif self.data_type == 2:
                    return "RAW_DARKSUB"
                elif self.data_type == 3:
                    return "TRANS_RAD"
                else: #if self.data_type == 4:
                    return "ATTEN_RAD"
            case "datatype":
                if self.data_type == 0:
                    return "UNKNOWN"
                elif self.data_type == 1:
                    return "RAW_UNCALIB"
                elif self.data_type == 2:
                    return "RAW_DARKSUB"
                elif self.data_type == 3:
                    return "TRANS_RAD"
                else: #if self.data_type == 4:
                    return "ATTEN_RAD"
            case "backgroundFile":
                return self.air_scan_file
            case "backgroundfile":
                return self.air_scan_file
            case "darkCurrentFile":
                return self.dark_scan_file
            case "darkcurrentfile":
                return self.dark_scan_file
            case "sfile":
                return self.raw_scan_file
            case "pfile":
                return self.projection_file
            case "rfile":
                return self.reconstruction_file
            case "systemGeometryFile":
                return self.geometry_file
            case "lengthUnits":
                return "mm"
            case "bgeometry":
                return self.leapct.get_geometry()
            case "geometry":
                return self.leapct.get_geometry()
            case "sod":
                return str(self.leapct.get_sod())
            case "sdd":
                return str(self.leapct.get_sdd())
            case "odd":
                return str(self.leapct.get_sdd() - self.leapct.get_sod())
            case "helicalpitch" | "helicalPitch":
                return str(self.leapct.get_helicalPitch())
            case "normalizedHelicalPitch":
                return str(self.leapct.get_normalizedHelicalPitch())
            case "axisOfSymmetry":
                axisOfSymmetry = self.leapct.get_axisOfSymmetry()
                if np.abs(self.leapct.get_axisOfSymmetry()) <= 30.0:
                    return str(axisOfSymmetry)
                else:
                    return ""
            case "nangles":
                return str(self.leapct.get_numAngles())
            case "initangle":
                phis = self.leapct.get_angles()
                if phis is None or len(phis) == 0:
                    return str(0.0)
                else:
                    return str(phis[0])
            case "initAngle":
                phis = self.leapct.get_angles()
                if phis is None or len(phis) == 0:
                    return str(0.0)
                else:
                    return str(phis[0])
            case "arange":
                return str(self.leapct.get_angularRange())
            case "rotationDirection":
                if self.leapct.get_angularRange() >= 0.0:
                    return "COUNTERCLOCKWISE"
                else:
                    return "CLOCKWISE"
            case "rotationdirection":
                if self.leapct.get_angularRange() >= 0.0:
                    return "COUNTERCLOCKWISE"
                else:
                    return "CLOCKWISE"
            case "nrays":
                return str(self.leapct.get_numCols())
            case "nslices":
                return str(self.leapct.get_numRows())
            case "pxcenter":
                return str(self.leapct.get_centerCol())
            case "pzcenter":
                return str(self.leapct.get_centerRow())
            case "pxmidoff":
                #print("Error: getParams pxmidoff not yet implemented!")
                #return str(0.0)
                return str(self.leapct.get_tau())
            case "tau":
                return str(self.leapct.get_tau())
            case "pxsize":
                return str(self.leapct.get_pixelWidth())
            case "pzsize":
                return str(self.leapct.get_pixelHeight())
            case "detectorShape":
                return self.leapct.get_detectorType()
            case "detectorResponseFile":
                return self.detector_response_file
            case "kV":
                return str(self.kV)
            case "takeOffAngle":
                return str(self.takeoff_angle)
            case "anodeMaterial":
                return str(self.anode_material)
            case "filterMaterials":
                return str(self.xray_filters)
            case "spectraFile":
                #return self.spectra_model_file
                return self.source_spectra_file
            case "referenceEnergy":
                return str(self.reference_energy)
            case "rfilter":
                return str(self.leapct.get_rampFilter())
            case "rampID":
                return str(self.leapct.get_rampFilter())
            case "rampFWHM":
                return str(self.leapct.get_FBPlowpass())
            case "rxsize":
                return str(self.leapct.get_voxelWidth())
            case "rysize":
                return str(self.leapct.get_voxelWidth())
            case "rzsize":
                return str(self.leapct.get_voxelHeight())
            case "rxref":
                if self.leapct.get_voxelWidth() <= 0.0:
                    return str(0.0)
                else:
                    return str(0.5*(self.leapct.get_numX()-1) - self.leapct.get_offsetX()/self.leapct.get_voxelWidth())
            case "ryref":
                if self.leapct.get_voxelWidth() <= 0.0:
                    return str(0.0)
                else:
                    return str(0.5*(self.leapct.get_numY()-1) - self.leapct.get_offsetY()/self.leapct.get_voxelWidth())
            case "rzref":
                if self.leapct.get_voxelHeight() <= 0.0:
                    return str(0.0)
                else:
                    return str(0.5*(self.leapct.get_numZ()-1) - self.leapct.get_offsetZ()/self.leapct.get_voxelHeight())
            case "rxoffset":
                return str(0)
            case "ryoffset":
                return str(0)
            case "rzoffset":
                return str(0)
            case "rxelements":
                return str(self.leapct.get_numX())
            case "ryelements":
                return str(self.leapct.get_numY())
            case "rzelements":
                return str(self.leapct.get_numZ())
            case "halfscan":
                return str(self.leapct.get_offsetScan())
            case "ImageJpath":
                return ""
            case "LTTcmd":
                return ""
            case "wmin":
                return ""
            case "wmax":
                return ""
            case "compressFile":
                return "False"
            case "LTTwCmd":
                return ""
            case "trackHistory":
                return "False"
            case "fileType":
                return "tif"
            case "untruncatedProjection":
                return "0"
            case _:
                print("Error: getParam keyword " + str(text) +  " not yet implemented!")
                return ""
        
    def unknown(self, text):
        match text:
            case "archdir":
                if len(self.path) >  0:
                    return False
                else:
                    return True
            case "outputdir":
                if len(self.outputDir) >  0:
                    return False
                else:
                    return True
            case "dataType":
                if self.data_type == self.UNSPECIFIED:
                    return True
                else:
                    return False
            case "datatype":
                if self.data_type == self.UNSPECIFIED:
                    return True
                else:
                    return False
            case "backgroundFile":
                if len(self.air_scan_file) >  0:
                    return False
                else:
                    return True
            case "backgroundfile":
                if len(self.air_scan_file) >  0:
                    return False
                else:
                    return True
                return self.air_scan_file
            case "darkCurrentFile":
                if len(self.dark_scan_file) >  0:
                    return False
                else:
                    return True
            case "darkcurrentfile":
                if len(self.dark_scan_file) >  0:
                    return False
                else:
                    return True
            case "sfile":
                if len(self.raw_scan_file) >  0:
                    return False
                else:
                    return True
            case "pfile":
                if len(self.projection_file) >  0:
                    return False
                else:
                    return True
            case "rfile":
                if len(self.reconstruction_file) >  0:
                    return False
                else:
                    return True
            case "systemGeometryFile":
                if len(self.geometry_file) >  0:
                    return False
                else:
                    return True
            case "lengthUnits":
                return False
            case "bgeometry":
                return False
            case "geometry":
                return False
            case "sod":
                if self.leapct.get_sod() > 0.0:
                    return False
                else:
                    return True
            case "sdd":
                if self.leapct.get_sdd() > 0.0:
                    return False
                else:
                    return True
            case "odd":
                if self.leapct.get_sod() > 0.0 and self.leapct.get_sdd() > 0.0:
                    return False
                else:
                    return True
            case "helicalpitch":
                return False
            case "helicalPitch":
                return False
            case "normalizedHelicalPitch":
                return False
            case "axisOfSymmetry":
                axisOfSymmetry = self.leapct.get_axisOfSymmetry()
                if np.abs(self.leapct.get_axisOfSymmetry()) <= 30.0:
                    return False
                else:
                    return True
            case "nangles":
                if self.leapct.get_numAngles() > 0:
                    return False
                else:
                    return True
            case "initangle":
                phis = self.leapct.get_angles()
                if phis is None or len(phis) == 0:
                    return True
                else:
                    return False
            case "initAngle":
                phis = self.leapct.get_angles()
                if phis is None or len(phis) == 0:
                    return True
                else:
                    return False
            case "arange":
                if self.leapct.get_angularRange() == 0.0:
                    return True
                else:
                    return False
            case "rotationDirection":
                if self.leapct.get_angularRange() == 0.0:
                    return True
                else:
                    return False
            case "rotationdirection":
                if self.leapct.get_angularRange() == 0.0:
                    return True
                else:
                    return False
            case "nrays":
                if self.leapct.get_numCols() > 0:
                    return False
                else:
                    return True
            case "nslices":
                if self.leapct.get_numRows() > 0:
                    return False
                else:
                    return True
            case "pxcenter":
                return False
            case "pzcenter":
                return False
            case "pxmidoff":
                return False
            case "pxsize":
                if self.leapct.get_pixelWidth() > 0.0:
                    return False
                else:
                    return True
            case "pzsize":
                if self.leapct.get_pixelHeight() > 0.0:
                    return False
                else:
                    return True
            case "detectorShape":
                return False
            case "detectorResponseFile":
                if len(self.detector_response_file) == 0:
                    return True
                else:
                    return False
            case "kV":
                if self.kV > 0.0:
                    return False
                else:
                    return True
            case "takeOffAngle":
                if self.takeoff_angle > 0.0:
                    return False
                else:
                    return True
            case "anodeMaterial":
                return False
            case "filterMaterials":
                if xray_filters is None:
                    return True
                else:
                    return False
            case "spectraFile":
                #if len(self.spectra_model_file) > 0:
                if len(self.source_spectra_file) > 0:
                    return False
                else:
                    return True
            case "referenceEnergy":
                if self.reference_energy > 0.0:
                    return False
                else:
                    return True
            case "rfilter":
                return False
            case "rxsize":
                if self.leapct.get_voxelWidth() > 0.0:
                    return False
                else:
                    return True
            case "rysize":
                if self.leapct.get_voxelWidth() > 0.0:
                    return False
                else:
                    return True
            case "rzsize":
                if self.leapct.get_voxelHeight() > 0.0:
                    return False
                else:
                    return True
            case "rxref":
                if self.leapct.get_voxelWidth() <= 0.0:
                    return True
                else:
                    return False
            case "ryref":
                if self.leapct.get_voxelWidth() <= 0.0:
                    return True
                else:
                    return False
            case "rzref":
                if self.leapct.get_voxelHeight() <= 0.0:
                    return True
                else:
                    return False
            case "rxoffset":
                return False
            case "ryoffset":
                return False
            case "rzoffset":
                return False
            case "rxelements":
                if self.leapct.get_numX() > 0:
                    return False
                else:
                    return True
            case "ryelements":
                if self.leapct.get_numY() > 0:
                    return False
                else:
                    return True
            case "rzelements":
                if self.leapct.get_numZ() > 0:
                    return False
                else:
                    return True
            case "halfscan":
                return False
            case "ImageJpath":
                return True
            case "LTTcmd":
                return True
            case "wmin":
                return True
            case "wmax":
                return True
            case "compressFile":
                return True
            case "LTTwCmd":
                return True
            case "trackHistory":
                return True
            case "fileType":
                return False
            case _:
                print("Error: getParam keyword " + str(text) +  " not yet implemented!")
                return ""

    def loadsct(self, fileName):
        if fileName.endswith('.sct'):
            fdes = open(fileName, 'r')
            Lines = fdes.readlines()
            for line in Lines:
                if line[0] == '-':
                    line = line[1:].strip()
                    x = line.split(' ', 1)
                    if len(x) == 2:
                        self.set_key_value_pairs(x[0], x[1])
        else:
            print('This is not an sct file')
            
    def load_skyscan(self, fileName):
        if fileName.endswith('.log'):
            fdes = open(fileName, 'r')
            Lines = fdes.readlines()
            for line in Lines:
                if "=" in line:
                    self.set_cmd(line, False)
            self.path = os.path.split(fileName)[0]
            self.leapct.set_geometry("CONE")
            self.leapct.set_flatDetector()
            self.air_scan_file = "57363.766"
            self.data_type = self.RAW_DARK_SUBTRACTED
            self.leapct.set_centerCol((self.leapct.get_numCols()-1)/2.0)
            #self.leapct.set_centerRow((self.leapct.get_numRows()-1)/2.0)
            self.takeoff_angle = 38.0
            self.set_detector_response('Gd2O2S', 7.32e-3, 0.02)
        else:
            print('This is not a Skyscan/ Bruker log file')
    
    def load_parameters(self, fileName):
        self.load_key_equal_value(fileName)
        self.load_geometry_file()
        self.geometry_file = None
    
    def load_key_equal_value(self, fileName):
        fdes = open(fileName, 'r')
        Lines = fdes.readlines()
        for line in Lines:
            if "=" in line:
                #print(line)
                self.set_cmd(line, False)
        if self.path is None or len(self.path) == 0:
            self.path = os.path.split(fileName)[0]
        
        
    def getHelpText(self, text, length=0):
        return "---"
        
    def get_nangles(self):
        return self.leapct.get_numAngles()
        
    def get_nrays(self):
        return self.leapct.get_numCols()
        
    def get_rxoffset(self):
        return 0
        
    def get_ryoffset(self):
        return 0
        
    def get_rzoffset(self):
        return 0
        
    def get_rxelements(self):
        return self.leapct.get_numX()
        
    def get_ryelements(self):
        return self.leapct.get_numY()
        
    def get_rzelements(self):
        return self.leapct.get_numZ()
        
    def projectionsAllocated(self):
        if self.g is None:
            return False
        else:
            return True
            
    def volumeAllocated(self):
        if self.f is None:
            return False
        else:
            return True
            
    def projectionDataExists(self):
        # FIXME: need to check for file
        return self.projectionsAllocated()
    
    def reconstructionDataExists(self):
        # FIXME: need to check for file
        return self.volumeAllocated()
        
    def getLengthUnits(self):
        return "mm"
    
"""
match text:
case "archdir":
case "dataType":
case "backgroundFile":
case "darkCurrentFile":
case "sfile":
case "pfile":
case "rfile":
case "systemGeometryFile":
case "lengthUnits":
case "bgeometry":
case "geometry":
case "sod":
case "sdd":
case "odd":
case "helicalpitch":
case "nangles":
case "initangle":
case "arange":
case "rotationDirection":
case "nrays":
case "nslices":
case "pxcenter":
case "pzcenter":
case "pxmidoff":
case "pxsize":
case "pzsize":
case "detectorShape":
case "detectorResponseFile":
case "kV":
case "TakeOffAngle":
case "AnodeMaterial":
case "filterMaterials":
case "spectraFile":
case "referenceEnergy":
case "rfilter":
case "rxsize":
case "rysize":
case "rzsize":
case "rxref":
case "ryref":
case "rzref":
case "rxoffset":
case "ryoffset":
case "rzoffset":
case "rxelements":
case "ryelements":
case "rzelements":
case "halfscan":
case _:
    """
     
""" TESTING
lctserver=leapctserver()
lctserver.set_source_spectra(100)
lctserver.physics.use_mm()
lctserver.add_filter('Al',None,2.0)
lctserver.set_detector_response('GOS',None,0.1)
Es,s=lctserver.totalSystemSpectralResponse()

import matplotlib.pyplot as plt
plt.plot(Es,s)
plt.show()
#"""
     