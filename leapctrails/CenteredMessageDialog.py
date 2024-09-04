from PyQt5.QtCore import *
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import *

class CenteredMessageDialog(QDialog):

    def __init__(self, Title, MessageBody, parent = None):
        super(CenteredMessageDialog, self).__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)

        self.setWindowTitle(Title)

        # Instantiate a label to warn the user:
        label = QLabel(MessageBody)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse);

        # Instantiate an OK/Cancel button box:
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        #self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
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


