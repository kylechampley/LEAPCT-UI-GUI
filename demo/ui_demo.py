import os
import numpy as np
from leapctserver import leapctserver

path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_data')
lctserver = leapctserver(None, path)

# Set input file names, CT geometry, and spectra model
lctserver.set_raw_data_files('raw.tif', 'air.tif', 'dark.tif')
lctserver.geometry_file = 'geometry.txt'
lctserver.load_geometry_file()
lctserver.set_source_spectra(160.0)

# Run preprocessing algorithms
lctserver.makeAttenuationRadiographs(ROI=[1, 31, 1, 10])
lctserver.outlierCorrection()
lctserver.ringRemoval_median(windowSize=7)
lctserver.singleMaterialBHC('water')
#lctserver.leapct.display(lctserver.g)

# Perform Geometric Calibration
# 1) Run the automated find_centerCol routine
# 2) Perform a series of reconstructions with values of centerCol around the estimated value to allow the user to estimate the best value
lctserver.leapct.find_centerCol(lctserver.g)
lctserver.leapct.display(lctserver.parameter_sweep(np.array(range(9))-4.0+lctserver.leapct.get_centerCol()))
centerCol = input("Enter the estimate for centerCol: ")
lctserver.leapct.set_centerCol(float(centerCol))

# Reconstruct and display result
lctserver.FBP()
lctserver.f[lctserver.f<0.0] = 0.0
lctserver.leapct.display(lctserver.f)
