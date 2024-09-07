
import os
import inspect
import sys
from sys import platform as _platform
from leapctserver import leapctserver
lctserver = leapctserver()

from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

import leapctrails as mw

application = QApplication(sys.argv)
#application.setStyleSheet("QLabel{font-size: 18pt;}")
mainWindow = mw.leapctrails(lctserver)
#mainWindow.placeHolderWindow.resize(1000,1000)

#run(max_loop_level=2)

""" Set Icon
icon = QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "LEAPicon.png"))
application.setWindowIcon(icon)
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)
#"""

from PyQt5.QtCore import pyqtRemoveInputHook
pyqtRemoveInputHook()

if _platform == "linux" or _platform == "linux2":
    mainWindow.setStyleSheet("QGroupBox {background-color: rgb(230,230,230);}")
mainWindow.show()

if len(sys.argv) > 1 and len(sys.argv[1]) >= 4:
    inputArg = sys.argv[1]
    if inputArg.endswith('.sct'):
        Succeeded = lctserver.loadsct(inputArg)
    elif inputArg.endswith('.log'):
        Succeeded = lctserver.load_skyscan(inputArg)
    elif inputArg.endswith('.txt'):
        Succeeded = lctserver.load_parameters(inputArg)
    else:
        Succeeded = False
    mainWindow.refresh()

application.exec_()
