from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets  import *

class GeneralWarningDialog(QDialog):

    def __init__(self, parent = None, warningMessage = None):
        super(GeneralWarningDialog, self).__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.optionAccepted = False
        self.setWindowTitle("Proceed?")

        # Instantiate a label to warn the user:
        if warningMessage == None:
            label = QLabel("Proceeeding with this operation will overwrite current settings and delete any data in memory associated with this data set. Continue?")
        else:
            label = QLabel(str(warningMessage))

        # Instantiate an OK/Cancel button box:
        buttonBox = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Instantiate a vertical box layout to house the drop-down list and the button box:
        self.overallVerticalLayout = QVBoxLayout()
        self.overallVerticalLayout.addWidget(label)
        self.overallVerticalLayout.addWidget(buttonBox)

        # Assign the overall layout:
        self.setLayout(self.overallVerticalLayout)

        # Position the dialog relative to its parent (the processing queue dock page):
        parentRect = QRect(parent.mapToGlobal(parent.pos()), parent.size())
        self.move(int(parentRect.left() + parentRect.width() * 0.25), int(parentRect.top() + parentRect.height() * 0.25))

    def cancelButton_pressed(self):
        self.optionAccepted = False
        self.close()

    def OKbutton_pressed(self):
        self.optionAccepted = True
        self.close()
