from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

class ProgressDialog(QDialog):

    def __init__(self, parent = None, txt="Processing..."):
        super(ProgressDialog, self).__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.parent = parent
        self.resize(350,75)

        self.operationSuccessful = False

        self.setWindowTitle(txt)

        # Instantiate a label to warn the user:
        self.messageLabel = QLabel("running LEAP-CT command, GUI disabled until processing is completed")

        # Instantiate a vertical box layout to house the drop-down list and the button box:
        overallVerticalLayout = QVBoxLayout()
        overallVerticalLayout.addWidget(self.messageLabel)

        # Assign the overall layout:
        self.setLayout(overallVerticalLayout)

        # Position the dialog relative to its parent (the processing queue dock page):
        parentRect = QRect(parent.mapToGlobal(parent.pos()), parent.size())
        self.move(int(parentRect.left() + parentRect.width() * 0.25), int(parentRect.top() + parentRect.height() * 0.25))

    def doing(self):

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.messageLabel.setText("doing stuff...")
        QApplication.processEvents()
        self.operationSuccessful = self.parent.lttServer.getReconstructionSliceX(sliceNumber)
        QApplication.restoreOverrideCursor()

