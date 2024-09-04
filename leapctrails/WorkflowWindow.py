from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from BasicToolWindow           import *
from WorkflowPagesStackControl import *



class WorkflowControls(QWidget):

    def __init__(self, parent = None):
        super(WorkflowControls, self).__init__(parent)

        self.parent = parent

        # Instantiate the stack control that displays the various sequential pages of a workflow:
        self.workflowStackControl = WorkflowPagesStackControl(self.parent)

        # Instantiate the "Previous / Next" controls:
        navigationGroupBox      = QGroupBox()
        navigationOverallLayout = QHBoxLayout()
        navigationSubLayout     = QHBoxLayout()
        self.previousButton     = QPushButton("Previous")
        self.nextButton         = QPushButton("Next")
        pageLabel = QLabel("page (1-4)")
        self.pageNumberEdit = QLineEdit()
        self.pageNumberEdit.setText("1")
        self.pageNumberEdit.setFixedWidth(24)
        self.previousButton.clicked.connect(self.previousButton_Clicked)
        self.nextButton.clicked.connect(self.nextButton_Clicked)
        navigationSubLayout.addWidget(self.previousButton)
        navigationSubLayout.addWidget(self.nextButton)
        navigationSubLayout.addWidget(pageLabel)
        navigationSubLayout.addWidget(self.pageNumberEdit)
        navigationGroupBox.setLayout(navigationSubLayout)
        navigationOverallLayout.addStretch(1)
        navigationOverallLayout.addWidget(navigationGroupBox)
        navigationOverallLayout.addStretch(1)

        self.nextButton.setFocus(True)

        # Instantiate the overall vertical layout and add the controls:
        overallVerticalLayout = QVBoxLayout()
        overallVerticalLayout.addWidget(self.workflowStackControl)
        overallVerticalLayout.addLayout(navigationOverallLayout)
        overallVerticalLayout.addStretch(1)
        self.setLayout(overallVerticalLayout)

        # Disable the previous button by default since the control starts up at the first page:
        self.previousButton.setEnabled(False)

        self.setNextButtonToolTip()
        self.setPreviousButtonToolTip()
        self.setWindowTitle(0)

        #self.pageNumberEdit.editingFinished.connect(self.push_pageNumber)
        self.pageNumberEdit.keyPressEvent = self.pageNumber_KeyPressed

        #self.pageNumberEdit.setText("3")
        #self.push_pageNumber()

        '''
        page 0: file I/O
        page 1: CT geometry
        page 2: CT volume
        page 3: algorithms
        '''

    def pageNumber_KeyPressed(self, event):
        # Check which key was pressed:
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return or event.key() == Qt.Key_Tab:
            self.push_pageNumber()
        else:
            # Call base class key press event to allow entering of text other than that being handled above:
            QLineEdit.keyPressEvent(self.pageNumberEdit, event)

    def push_pageNumber(self):
        if len(self.pageNumberEdit.text()) == 0:
            return
        pageNumberRequest = int(self.pageNumberEdit.text())
        if pageNumberRequest == self.workflowStackControl.currentIndex() + 1:
            return
        maximumPageNumber = 4
        if pageNumberRequest < 1:
            pageNumberRequest = 1
        elif pageNumberRequest > maximumPageNumber:
            pageNumberRequest = maximumPageNumber

        currentPageNumber = self.workflowStackControl.currentIndex() + 1

        if pageNumberRequest < currentPageNumber:
            for i in range(currentPageNumber-pageNumberRequest):
                self.previousButton_Clicked()
        elif pageNumberRequest > currentPageNumber:
            for i in range(pageNumberRequest-currentPageNumber):
                self.nextButton_Clicked()

    def nextButton_Clicked(self):

        # Push all parameters for the current page:
        currentPage = self.workflowStackControl.widget(self.workflowStackControl.currentIndex())
        currentPage.pushAllParameters()

        # Instruct the stack control to go to the next page:
        self.workflowStackControl.nextPage()

        currentIndex = self.workflowStackControl.currentIndex()

        # In case the button is currently disabled:
        self.previousButton.setEnabled(True)
        self.nextButton.setEnabled(True)
        
        if currentIndex == self.workflowStackControl.getLastIndex():
            self.nextButton.setEnabled(False)
        
        self.setNextButtonToolTip()
        self.setPreviousButtonToolTip()
        self.setWindowTitle(currentIndex)
        self.pageNumberEdit.setText(str(currentIndex + 1))

    def previousButton_Clicked(self):
        
        # Instruct the stack control to go to the next page:
        self.workflowStackControl.previousPage()

        # Check the stack control's current index and if equal zero disable/enable the navigation buttons:
        currentIndex = self.workflowStackControl.currentIndex()

        # In case the button is currently disabled:
        self.nextButton.setEnabled(True)
        
        if currentIndex == 0:
            self.previousButton.setEnabled(False)

        self.setNextButtonToolTip()
        self.setPreviousButtonToolTip()
        self.setWindowTitle(currentIndex)
        self.pageNumberEdit.setText(str(currentIndex + 1))

    def setWindowTitle(self,currentIndex):
        if currentIndex == 0:
            self.parent.setWindowTitle("File I/o")
        elif currentIndex == 1:
            self.parent.setWindowTitle("Scanner Geometry")
        elif currentIndex == 2:
            self.parent.setWindowTitle("Reconstruction Volume")
        elif currentIndex == 3:
            self.parent.setWindowTitle("Algorithms")

    def setNextButtonToolTip(self):
        currentIndex = self.workflowStackControl.currentIndex()
        if currentIndex == 0:
            self.nextButton.setToolTip("scanner geometry")
        elif currentIndex == 1:
            if self.nextButton.isEnabled() == False:
                self.nextButton.setToolTip("please specify all parameters in red before continuing")
            else:
                self.nextButton.setToolTip("reconstruction volume")
        elif currentIndex == 2:
            if self.nextButton.isEnabled() == False:
                self.nextButton.setToolTip("please specify all scanner parameters in red before continuing")
            else:
                self.nextButton.setToolTip("algorithms")
        elif currentIndex == 3:
            self.nextButton.setToolTip("none")

    def setPreviousButtonToolTip(self):
        currentIndex = self.workflowStackControl.currentIndex()
        if currentIndex == 0:
            self.previousButton.setToolTip("none")
        elif currentIndex == 1:
            self.previousButton.setToolTip("file I/O")
        elif currentIndex == 2:
            self.previousButton.setToolTip("scanner geometry")
        elif currentIndex == 3:
            self.previousButton.setToolTip("reconstruction volume")


class WorkflowWindow(ToolWindow):
    """description of class"""

    def __init__(self, lctserver, title, parent = None):
        super(WorkflowWindow, self).__init__(title, parent)

        self.parent = parent
        self.lctserver = lctserver
        self.leapct = self.lctserver.leapct

        # Instantiate the workflow controls and set it as the central widget:
        self.workflowControls = WorkflowControls(self)
        self.setWidget(self.workflowControls)

    def refreshAllPages(self):
        self.refreshFileNamesParameters()
        self.refreshGeometryParameters()
        self.refreshVolumeParameters()

    def refreshFileNamesParameters(self):
        self.workflowControls.workflowStackControl.fileNamesPage.refresh()

    def refreshGeometryParameters(self):
        self.workflowControls.workflowStackControl.geometryPage.refresh()

    def refreshVolumeParameters(self):
        self.workflowControls.workflowStackControl.volumePage.refresh()

