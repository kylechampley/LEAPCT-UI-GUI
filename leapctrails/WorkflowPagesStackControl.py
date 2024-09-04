from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from file_names_page import *
from ct_geometry_page import *
from ct_volume_page import *
from ct_algorithm_controls_page import *

class WorkflowPagesStackControl(QStackedWidget):

    def __init__(self, parent = None):
        super(WorkflowPagesStackControl, self).__init__(parent)

        self.parent = parent

        self.lastIndex = -1

        self.fileNamesPage     = FileNamesPage(self.parent)
        self.lastIndex = self.lastIndex + 1
        self.geometryPage        = CTgeometryPage(self.parent)
        self.lastIndex = self.lastIndex + 1
        
        self.volumePage = CTvolumePage(self.parent)
        self.lastIndex = self.lastIndex + 1
        
        self.algorithmsPage = CTalgorithmControlsPage(self.parent)
        self.lastIndex = self.lastIndex + 1

        self.addWidget(self.fileNamesPage)
        self.addWidget(self.geometryPage)
        self.addWidget(self.volumePage)
        self.addWidget(self.algorithmsPage)

        self.setCurrentIndex(0)

    def nextPage(self):
        
        currentIndex = self.currentIndex()
        if currentIndex < self.lastIndex:
            self.setCurrentIndex(currentIndex + 1)
            self.fileNamesPage.refresh()
            self.geometryPage.refresh()
            self.volumePage.refresh()
            self.algorithmsPage.refresh()

    def previousPage(self):
        
        currentIndex = self.currentIndex()
        if currentIndex > 0:
            self.setCurrentIndex(currentIndex - 1)
            self.fileNamesPage.refresh()
            self.geometryPage.refresh()
            self.volumePage.refresh()
            self.algorithmsPage.refresh()

    def getLastIndex(self):
        return self.lastIndex
