#
#    ngSkinTools
#    Copyright (c) 2009-2016 Viktoras Makauskas. 
#    All rights reserved.
#    
#    Get more information at 
#        http://www.ngskintools.com
#    
#    --------------------------------------------------------------------------
#
#    The coded instructions, statements, computer programs, and/or related
#    material (collectively the "Data") in these files are subject to the terms 
#    and conditions defined by EULA.
#         
#    A copy of EULA can be found in file 'LICENSE.txt', which is part 
#    of this source code package.
#    

#
#    ngSkinTools
#    Copyright (c) 2009-2016 Viktoras Makauskas. 
#    All rights reserved.
#    
#    Get more information at 
#        http://www.ngskintools.com
#    
#    --------------------------------------------------------------------------
#
#    The coded instructions, statements, computer programs, and/or related
#    material (collectively the "Data") in these files are subject to the terms 
#    and conditions defined by EULA.
#         
#    A copy of EULA can be found in file 'LICENSE.txt', which is part 
#    of this source code package.
#    

from maya import cmds
from ngSkinTools import utils
from ngSkinTools.ui.basetoolwindow import BaseQtToolWindow
import qtCompatibility as qt
import os.path
from ngSkinTools import license
from ngSkinTools.utils import Utils

class layout:
    layoutStack = []
    def __init__(self,layoutClass,*args,**kwargs):
        self.layout = layoutClass(*args, **kwargs)
        if len(layout.layoutStack)>0:
            layout.layoutStack[-1].addLayout(self.layout)
        
    def __enter__(self):
        layout.layoutStack.append(self.layout)
        return self.layout
    def __exit__(self, type, value, traceback):
        layout.layoutStack.pop()
        pass



class Model(object):
    def __init__(self):
        self.ui = None
        self.licenseLocation = None
    
    def doNext(self):
        if self.ui.currentPage == self.ui.activationChoicePage:
            self.licenseKey = self.ui.activationChoicePage.licenseKeyEdit.text().strip()
            if self.licenseKey=="":
                utils.displayError("Enter license key to proceed")
                return
            self.ui.setVisiblePage(self.ui.settingsPage)
            return
        
        if self.ui.currentPage == self.ui.settingsPage:
            self.licenseLocation = self.ui.settingsPage.licensePath.text()
            if not os.path.isdir(self.licenseLocation):
                utils.displayError("Please select an existing directory")
                return
            
            nextPage = self.ui.onlineActivationPage
            if self.ui.activationChoicePage.selectEmailActivation.isChecked():
                nextPage = self.ui.emailActivationPage
                nextPage.emailText.setText(self.buildActivationEmailText())
            else:
                try:
                    license.downloadLicenseFile(self.licenseKey)
                    nextPage.activationFailedRow.setVisible(False)
                except Exception, err:
                    nextPage.activationSuccessRow.setVisible(False)
                    nextPage.activationErrorLabel.setText(str(err))
                
            

            self.ui.setVisiblePage(nextPage)
            
            self.ui.buttonNext.setVisible(False)
            self.ui.buttonClose.setText("Finish")
            return
        
            
    def buildActivationEmailText(self):
        return """
                <p>To: support@ngskintools.com</p>
                <p><b>License file request</b></p>
                
                <p>Please issue a license file for:</p>
                <ul>
                <li>License key: {licenseKey}</li>
                <li>Host id: {hostId}</li>
                </ul>
                """.format(licenseKey=self.licenseKey,hostId=license.getHostId())
        
        
        
    
class SettingsPage(qt.widgets.QFrame):
    def __init__(self):
        qt.widgets.QFrame.__init__(self)
        
        def browseHandler():
            result = cmds.fileDialog2(fileMode=3, dialogStyle=1,startingDirectory=self.licensePath.text())
            if result is None:
                return
            
            result = os.path.normpath(result[0])
            license.setLicensePath(result)
            self.licensePath.setText(license.getLicensePath())
        
        column = qt.widgets.QVBoxLayout()
        self.setLayout(column)

        row = qt.widgets.QHBoxLayout()
        label = qt.widgets.QLabel("In order to activate a license, ngSkinTools needs to store or locate it's license file ngskintools.lic. When using online activation, this file will be created automatically; if you're using offline activation, please locate a folder where you have placed the license file.")
        label.setWordWrap(True);
        row.addWidget(label)
        column.addLayout(row)
        
        column.addSpacing(10)
        row = qt.widgets.QHBoxLayout()
        row.addWidget(qt.widgets.QLabel("Folder to save license file into:"))
        column.addLayout(row)
        
        licensePath = license.getLicensePath()
        
        self.licensePath = qt.widgets.QLineEdit(text=licensePath)
        row = qt.widgets.QHBoxLayout()
        row.addWidget(self.licensePath,stretch=1)
        row.addWidget(qt.widgets.QPushButton("Browse...",clicked=browseHandler))
        column.addLayout(row)
        
        column.addStretch(1)

class ActivationChoicePage(qt.widgets.QFrame):
    def __init__(self):
        qt.widgets.QFrame.__init__(self)

        self.licenseKeyEdit = qt.widgets.QLineEdit(text="")
        
        with layout(qt.widgets.QVBoxLayout) as column:
            self.setLayout(column)
            
            description = "If you've purchased ngSkinTools already, you should have received email with your license key (give it up to 12 hours to arrive). " + \
                "License key will be bound to this computer when used."
            
            with layout(qt.widgets.QVBoxLayout) as row:
                row.addWidget(qt.widgets.QLabel(description,wordWrap=True))
                row.addSpacing(5)
                row.addWidget(qt.widgets.QLabel("License key:"))
                row.addWidget(self.licenseKeyEdit)
                
            column.addSpacing(10)
            with layout(qt.widgets.QHBoxLayout) as row:
                row.addWidget(qt.widgets.QLabel("Choose your activation method:",wordWrap=True))
    
            column.addSpacing(10)
            with layout(qt.widgets.QGridLayout) as row:
                self.selectOnlineActivation = qt.widgets.QRadioButton(checked=True)
                row.addWidget(self.selectOnlineActivation,0,0)
                row.addWidget(qt.widgets.QLabel("Online activation"),0,1)
                row.addWidget(qt.widgets.QLabel("Choose this option if you have internet connectivity. A license file, matching this host ID, will be downloaded for you automatically.",wordWrap=True),1,1)
                row.setColumnStretch(1,1)
            
            column.addSpacing(10)
            with layout(qt.widgets.QGridLayout) as row:
                self.selectEmailActivation = qt.widgets.QRadioButton() 
                row.addWidget(self.selectEmailActivation,0,0)
                row.addWidget(qt.widgets.QLabel("Email activation"),0,1)
                row.addWidget(qt.widgets.QLabel("Request license file to be delivered via email.",wordWrap=True),1,1)
                row.setColumnStretch(1,1)
                    
            
            column.addStretch(1)

class EmailActivationPage(qt.widgets.QFrame):
    def __init__(self):
        qt.widgets.QFrame.__init__(self)
        with layout(qt.widgets.QVBoxLayout) as column:
            self.setLayout(column)

            with layout(qt.widgets.QHBoxLayout) as row:
                row.addWidget(qt.widgets.QLabel("Send the below text to support@ngskintools.com. You'll receive further instructions with your license file.",wordWrap=True))
            
            column.addSpacing(10)
            with layout(qt.widgets.QHBoxLayout) as row:
                self.emailText = qt.widgets.QTextEdit("""
                <p>To: support@ngskintools.com</p>
                <p><b>License file request</b></p>
                
                <p>Please issue a license file for:</p>
                <ul>
                <li>License key: 123-123-123</li>
                <li>Host id: 123</li>
                </ul>
                """,readOnly=True)
                row.addWidget(self.emailText)
            
            
            def copyToClipboard():
                self.emailText.selectAll()
                self.emailText.copy()

            with layout(qt.widgets.QHBoxLayout) as row:
                row.addStretch(1)
                row.addWidget(qt.widgets.QPushButton("Copy to clipboard",clicked=copyToClipboard))
            column.addStretch(1)
        


class OnlineActivationPage(qt.widgets.QFrame):
    def __init__(self):
        qt.widgets.QFrame.__init__(self)
        with layout(qt.widgets.QVBoxLayout) as column:
            self.setLayout(column)
            
            def createContainerAndLayout():
                container = qt.widgets.QFrame()
                column.addWidget(container)
                row = qt.widgets.QVBoxLayout()
                container.setLayout(row)
                return container,row
            
            self.activationSuccessRow, row = createContainerAndLayout()
            row.addWidget(qt.widgets.QLabel("Success!",wordWrap=True))
            row.addWidget(qt.widgets.QLabel("Your license file was downloaded.",wordWrap=True))

            self.activationFailedRow, row = createContainerAndLayout()
            self.activationErrorLabel = qt.widgets.QLabel("Error text here",wordWrap=True)
            self.activationErrorLabel.setTextInteractionFlags(qt.QtCore.Qt.TextSelectableByKeyboard | qt.QtCore.Qt.TextSelectableByMouse)
            row.addWidget(qt.widgets.QLabel("Failure",wordWrap=True))
            row.addWidget(self.activationErrorLabel)
                
            column.addStretch(1)


    
class ActivationDialog(BaseQtToolWindow):
    def __init__(self):
        BaseQtToolWindow.__init__(self,"activationDialog")
        self.setWindowTitle("ngSkinTools license activation")
        self.resize(500,300)

        self.model = Model()
        self.model.ui = self

        
        
        self.settingsPage = SettingsPage()
        self.activationChoicePage = ActivationChoicePage()
        self.emailActivationPage = EmailActivationPage()
        self.onlineActivationPage = OnlineActivationPage()
        
        self.createUI()

        self.setVisiblePage(self.activationChoicePage)


    def createUI(self):
        box = qt.widgets.QGridLayout()

        self.pageContents = qt.widgets.QStackedLayout()
        for page in (self.settingsPage,self.activationChoicePage,self.emailActivationPage,self.onlineActivationPage):
            self.pageContents.addWidget(page)
            
            
        box.addLayout(self.pageContents,0,0)
        box.setRowStretch(0,1)
        
        buttonsRow = qt.widgets.QHBoxLayout()
        buttonsRow.addStretch(1)
        self.buttonNext = qt.widgets.QPushButton("&Next",maximumWidth=100,clicked=self.model.doNext,minimumHeight=26)
        self.buttonClose = qt.widgets.QPushButton("&Close",maximumWidth=100,clicked=self.close,minimumHeight=26)
        buttonsRow.addWidget(self.buttonNext, stretch=1)
        buttonsRow.addWidget(self.buttonClose, stretch=1)
        box.addLayout(buttonsRow,1,0)
        
        self.setLayout(box) 
        
    def setVisiblePage(self,page):
        self.currentPage = page
        self.pageContents.setCurrentWidget(page)
               
    def closeEvent(self, event):
        BaseQtToolWindow.closeEvent(self, event)
        self.deleteLater() 
