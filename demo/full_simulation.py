import sys
import os
import imageio
import time
import numpy as np
import matplotlib.pyplot as plt
from leapctype import *
leapct = tomographicModels()
try:
    from xrayphysics import *
    physics = xrayPhysics()
except:
    print('This demo script requires the XrayPhysics package found here:')
    print('https://github.com/kylechampley/XrayPhysics')
    quit()

dataPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_data')
raw_file = os.path.join(dataPath, 'raw.tif')
air_file = os.path.join(dataPath, 'air.tif')
dark_file = os.path.join(dataPath, 'dark.tif')

# Set the scanner geometry
numCols = 512
numAngles = 2*2*int(360*numCols/1024)
pixelSize = 0.65*512/numCols
numRows = 64
leapct.set_conebeam(numAngles, numRows, numCols, pixelSize, pixelSize, 0.5*(numRows-1), 0.5*(numCols-1)+10, leapct.setAngleArray(numAngles, 360.0), 1100, 1400)

# Set the volume parameters
leapct.set_default_volume()
leapct.set_numZ(numRows+8)

# "Simulate" projection data
g = leapct.allocate_projections()
f = leapct.allocate_volume()
leapct.set_FORBILD(f,True)
leapct.project(g,f)

# Simulate the spectra
kV = 160.0
takeOffAngle = 11.0
Es, s = physics.simulateSpectra(kV,takeOffAngle)
detResp = physics.detectorResponse('GOS', None, 0.1, Es)
s_total = s#*detResp #*filtResp

# Apply Beam Hardening
BH_LUT, T_lut = physics.setBHlookupTable(s_total, Es, 'water', 63.9544)
leapct.applyTransferFunction(g, BH_LUT, T_lut)


# Simulate gain variations to add ring artifacts
detectorGain = np.random.uniform(1.0-0.02,1.0+0.02,(numRows,numCols))
g[:] = g[:] - np.log(detectorGain[None,:,:])

# Make some of the detector pixels have zero value to emulate bad measurements
ind = np.abs(np.random.normal(0,1,g.shape)) > 3.0
g[ind] = 0.0

# Simulate air scan, dark current image, and flux variation
air_scan = 50000.0*np.ones((numRows, numCols), dtype=np.float32)
dark_scan = np.random.normal(50.0, 2.0, (numRows,numCols))
dark_scan[dark_scan<0.0] = 0.0
dark_scan = np.ascontiguousarray(dark_scan, dtype=np.float32)
flux = np.random.normal(1.0, 0.01, (numAngles))

print(np.max(flux))
print(np.min(flux))

#t = (raw-dark)/(air-dark)
t = leapct.expNeg(g)
t *= air_scan
t *= flux[:,None,None]
t += dark_scan
air_scan += dark_scan

leapct.set_default_volume()
leapct.save_parameters(os.path.join(dataPath, 'geometry.txt'))
leapct.save_projections(raw_file, t)
imageio.imwrite(air_file, air_scan)
imageio.imwrite(dark_file, dark_scan)
