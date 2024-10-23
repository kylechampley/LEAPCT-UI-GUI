import os
import time
import numpy as np
import matplotlib.pyplot as plt
from leapctserver import leapctserver

# Set the path and create an leapctserver object
path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_data')
lctserver = leapctserver(None, path)

# If sample data cannot be found, generate it
if os.path.isfile(os.path.join(path, 'air.tif')) == False:
    exec(open("full_simulation.py").read())


###############################################################################
# Set input file names, CT geometry, and spectra model
###############################################################################
# If the dark current file is not given, assumes the dark current has already been subtracted from the data
# If the air scan file is not given, assumes the data has already been divided by the air scan (is transmission data)
lctserver.set_raw_data_files('raw.tif', 'air.tif', 'dark.tif')
lctserver.geometry_file = 'geometry.txt'
lctserver.load_geometry_file()
lctserver.set_source_spectra(160.0)
lctserver.set_detector_response('GOS', None, 0.1)
lctserver.reference_energy = 63.9544
lctserver.set_object_model('water')
lctserver.save_parameters()
#quit()

###############################################################################
# Run preprocessing algorithms
###############################################################################
startTime = time.time()

# First we convert the raw data to attenuation data (line integrals)
# This includes subtracting off the dark current, dividing by the air scan, and taking the negative log
# The ROI argument is optional.  It specifies a region in every projection [first row, last row, first column, last column]
# where the object does not cast a shadow on the detector.  An average value is calculated in this region to track the source
# flux variations and normalize them out
lctserver.makeAttenuationRadiographs(ROI=[1, 31, 1, 10])

# Next we apply the outlier correction which removes bad pixels and outlier measurements (sometimes called "zingers")
lctserver.outlierCorrection()

# Now we run the ring removal algorithm which corrects for pixel-to-pixel gain variations which may cause
# ring artifacts in the reconstruction.  Note that this is a preprocessing algorithm meaning it modifies the projection data
#lctserver.ringRemoval_median(windowSize=7)
#lctserver.ringRemoval_fast()
lctserver.ringRemoval()

# Finally we perform single material beam hardening correction (BHC).  This is optional and requires a spectral model.
# LEAP also has multi-material BHC algorithms.
lctserver.singleMaterialBHC()
#lctserver.leapct.display(lctserver.g)

###############################################################################
# Perform Geometric Calibration
###############################################################################
# 1) Run the automated find_centerCol routine
# 2) Perform a series of reconstructions with values of centerCol around the estimated value to allow the user to estimate the best value
lctserver.leapct.find_centerCol(lctserver.g)
elapsedTime = time.time() - startTime
lctserver.leapct.display(lctserver.parameter_sweep(np.array(range(9))-4.0+lctserver.leapct.get_centerCol()))
centerCol = input("Enter the estimate for centerCol: ")
lctserver.leapct.set_centerCol(float(centerCol))


# Reconstruct
startTime = time.time()
lctserver.FBP()
print('Total processing time: ' + str(time.time()-startTime+elapsedTime))
lctserver.f[lctserver.f<0.0] = 0.0


# Display result
plt.imshow(np.squeeze(lctserver.f[lctserver.f.shape[0]//2,:,:]), cmap='gray')
plt.show()
#lctserver.leapct.display(lctserver.f)
