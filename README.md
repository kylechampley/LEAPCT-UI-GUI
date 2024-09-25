# LEAPCT-UI-GUI
Beta version 0.3 has been released!

The purpose of this repo is to provide a high level UI and GUI for the [LEAP-CT](https://github.com/LLNL/LEAP/) and [XrayPhysics](https://github.com/kylechampley/XrayPhysics) libraries.

The UI part (leapctserver.py) is meant to help with
1) File I/O
2) If a LEAP algorithm requires more CPU memory than the user has access to, then it will utilize the hard drive to process the data in small enough chunks to fit in the CPU memory.
3) Provide a higher level of automation for the LEAP algorithms which will limit their flexibility, but make them easier to use.

The GUI, which we call LEAP-CT Rails, is built upon leapctserver.py using PyQt5 to assist in reconstructing real CT datasets.  I promised this GUI several months ago and I wanted to make good on this statement, but please be patient with this version.  There may be several bugs and things may not go as smoothly as you'd like.  Also note that this GUI currently only supports a small subset of the LEAP-CT features.

<p align="center">
  <img src=https://github.com/kylechampley/LEAPCT-UI-GUI/blob/main/screenshot.png>
</p>

This GUI is similar to the LTT GUI and future releases will add more features that are similar to the LTT GUI.  Some LTT GUI videos were posted to YouTube several years ago, so if you want to get a glimpse of where we are going with this GUI, see [here](https://www.youtube.com/watch?v=oVcFYh8oB4I).  You can also see [this](https://www.youtube.com/watch?v=VHt2kL85Ews) video for a demo of the XrayPhysics part of the GUI.


## Requirements
1) [LEAP-CT v1.21](https://github.com/LLNL/LEAP) or newer
2) Python 3.10 or newer
3) PyQt5

Although not required, we also recommend installing the [XrayPhysics](https://github.com/kylechampley/XrayPhysics) package.


## Installation and Usage
To install the LEAP-CT GUI, do the following

```
git clone https://github.com/kylechampley/LEAPCT-UI-GUI.git
cd LEAPCT-UI-GUI
pip install .
```

One should now find a clickable file to launch the GUI on their desktop.  For Windows this is a batch file and for Linux this is a shell script.  This file can be moved anywhere one wishes and it will still work.

## Future Releases

For the next releases, we are working on the following:
1) Data chunking for all pre- and post-processing algorithms, so there are no CPU RAM limitations.
2) Add more preprocessing algorithms
3) Add more postprocessing algorihms
4) Add iterative reconstruction algorithms
5) Add integrated image/ volume viewing capabilities
6) Ability to generate more physics plots


## Author
Kyle Champley (champley@gmail.com)


## License
LEAP-CT Rails is distributed under the terms of the MIT license. All new contributions must be made under this license. See LICENSE in this directory for the terms of the license.
See [LICENSE](LICENSE) for more details.  
SPDX-License-Identifier: MIT  

Please cite our work by referencing this github page and citing our [article](https://arxiv.org/abs/2307.05801):

Hyojin Kim and Kyle Champley, "Differentiable Forward Projector for X-ray Computed Tomography”, ICML, 2023
