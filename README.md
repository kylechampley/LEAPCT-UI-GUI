# LEAPCT-UI-GUI
This repo is currently under development and not yet ready for use, but if you want to go ahead and try it out go ahead and let me know how it goes!

The purpose of this repo is to provide a high level UI and GUI for the [LEAP-CT](https://github.com/LLNL/LEAP/) and [XrayPhysics](https://github.com/kylechampley/XrayPhysics) libraries.

The UI part (leapctserver.py) is meant to help with
1) File I/O
2) If a LEAP algorithm requires more CPU memory than the user has access to, then it will utilize the hard drive to process the data in small enough chunks to fit in the CPU memory.
3) Provide a higher level of automation for the LEAP algorithms which will limit their flexibility, but make them easier to use.

The GUI part will be built upon leapctserver.py and will provide a PyQt GUI to assist in reconstructing real CT datasets.  This GUI will be an adaptation of the LTT GUI.
Some LTT GUI videos were posted to YouTube several years ago, so if you want to get a glimpse of what this GUI will look like, see [here](https://www.youtube.com/watch?v=oVcFYh8oB4I).

You can also see [this](https://www.youtube.com/watch?v=VHt2kL85Ews) video for a demo of the XrayPhysics part of the GUI.

