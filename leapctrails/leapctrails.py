import sys
from sys import platform as _platform
import os
import inspect

from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

from file_names_page import *
from ct_geometry_page import *
from ct_volume_page import *
from ct_algorithm_controls_page import *
from WorkflowWindow import *

from leapctserver import leapctserver

class leapctrails(QMainWindow):
     
    def __init__(self, lctserver=None, parent = None):
        super(leapctrails, self).__init__(parent)

        self.versionNumber = "0.2"
        print ("LEAP-CT Rails v" + str(self.versionNumber))
        if lctserver is None:
            self.lctserver = leapctserver()
            self.leapct = self.lctserver.leapct
        else:
            if type(lctserver) is leapctserver:
                self.lctserver = lctserver
                self.leapct = self.lctserver.leapct
            elif type(lctserver) is tomographicModels:
                self.leapct = lctserver
                self.lctserver = leapctserver(self.leapct)
            else:
                print("Error: incorrect initialization!")
                return
        
        self.verify_version()
        
        self.mainWindowBaseTitle = "LEAP-CT Rails v" + str(self.versionNumber) + " (LEAP-CT v" + str(self.lctserver.leapct.version())  + ")"
        self.mainWindowSecondaryTitle = ""
        self.setWindowTitle(self.mainWindowBaseTitle)
        
        # Set some initial parameters for the MainWindow:
        #self.setWindowState(Qt.WindowMaximized)
        #self.setAutoFillBackground(True)

        # Instantiate the MainWindow background color palette and assign it:
        #MainWindowPalette = QPalette()
        #MainWindowPalette.setColor(QPalette.Background, QColor(41,57,85))
        #self.setPalette(MainWindowPalette)
        
        overall_grid = QGridLayout()
        self.workflowWindow = WorkflowWindow(self.lctserver, "Workflow", self)
        overall_grid.addWidget(self.workflowWindow, 0, 0)
        
        wid = QWidget(self)
        self.setCentralWidget(wid)
        layout = QVBoxLayout()
        wid.setLayout(overall_grid)
        
    def refresh(self):
        self.workflowWindow.refreshAllPages()
        
    def verify_version(self):
        versionText_min = "1.22"
        versionNumberHash_min = 1*10000 + 22*100 + 0
    
        versionText = self.leapct.version()
        if versionText == "unknown":
            print("LEAP-CT Rails requires LEAP-CT " + versionText_min + " or newer!")
            exit()
        else:
            majorVersionNumber = 0
            minorVersionNumber = 0
            fixVersionNumber = 0
            if versionText.count(".") == 0:
                majorVersionNumber = int(versionText)
            elif versionText.count(".") == 1:
                [majorVersionNumber, minorVersionNumber] = versionText.split(".")
                majorVersionNumber = int(majorVersionNumber)
                minorVersionNumber = int(minorVersionNumber)
            else:
                [majorVersionNumber, minorVersionNumber, fixVersionNumber] = versionText.split(".")
                majorVersionNumber = int(majorVersionNumber)
                minorVersionNumber = int(minorVersionNumber)
                fixVersionNumber = ''.join(i for i in fixVersionNumber if i.isdigit())
                fixVersionNumber = int(fixVersionNumber)

        versionNumberHash = majorVersionNumber*10000 + minorVersionNumber*100 + fixVersionNumber
        if versionNumberHash < versionNumberHash_min:
            print("LEAP-CT Rails requires LEAP-CT " + versionText_min + " or newer!")
            exit()
        