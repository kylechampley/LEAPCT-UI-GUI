from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

class HelpPreviewExecuteButtonBox(QWidget):

    def __init__(self, parent = None):
        super(HelpPreviewExecuteButtonBox, self).__init__(parent)

        self.parent = parent

        # Instantiate a horizontal layout for the three buttons and populate:
        horizontalSubLayout1 = QHBoxLayout()

        self.helpButton = QPushButton("Help")
        self.helpButton.setToolTip("display algorithm help pages")
        horizontalSubLayout1.addWidget(self.helpButton)

        blankSpaceA = QLabel(" ")
        horizontalSubLayout1.addWidget(blankSpaceA)

        self.previewButton = QPushButton("Preview")
        self.previewButton.setToolTip("apply algorithm to a 2D subset of the data to preview its effect")
        horizontalSubLayout1.addWidget(self.previewButton)

        self.previewIndex = QLineEdit()
        self.previewIndex.setMaximumWidth(50)
        self.previewIndex.setToolTip("enter index of 2D subset for preview; default value given if none is specified")
        horizontalSubLayout1.addWidget(self.previewIndex)

        blankSpaceB = QLabel(" ")
        horizontalSubLayout1.addWidget(blankSpaceB)

        self.executeButton = QPushButton("Execute")
        self.executeButton.setToolTip("execute algorithm")
        horizontalSubLayout1.addWidget(self.executeButton)

        self.setLayout(horizontalSubLayout1)

    def get_previewIndex(self):
        txt = self.previewIndex.text()
        if txt is None:
            return None
        elif len(txt) == 0:
            return None
        else:
            try:
                x = int(txt)
                return x
            except:
                return None
