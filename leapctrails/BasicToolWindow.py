
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ToolWindow(QDockWidget):

    def __init__(self, title, parent=None):
        super(ToolWindow, self).__init__(title, parent)

        # Setup the default background color:
        basicToolWindowPalette = QPalette()
        basicToolWindowPalette.setColor(QPalette.Background, QColor(240,240,240))

        # Set the default parameters:
        self.setAutoFillBackground(True)
        self.setPalette(basicToolWindowPalette)
        #self.setAllowedAreas(Qt.LeftDockWidgetArea)
        #self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

