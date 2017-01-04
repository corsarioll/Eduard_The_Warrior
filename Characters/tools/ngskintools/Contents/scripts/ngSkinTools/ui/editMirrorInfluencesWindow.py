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
from ngSkinTools import selectionState
from ngSkinTools.doclink import SkinToolsDocs
from ngSkinTools.influenceMapping import InfluenceMapping
from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.ui.basetab import CommandLayout
from ngSkinTools.ui.basetoolwindow import BaseToolWindow
from ngSkinTools.ui.components import uiGroup
from ngSkinTools.ui.components.influencesManualMapping import InfluencesManualMapping
from ngSkinTools.ui.components.influencesMappingPreview import InfluencesMappingPreview


class EditMirrorInfluencesWindow(BaseToolWindow):
    def __init__(self, windowName):
        BaseToolWindow.__init__(self, windowName)
        self.useUserPrefSize = False
        self.windowTitle = 'Edit Mirror Influences'
        self.sizeable = True
        self.defaultHeight = 400
        self.defaultWidth = 450

        self.influenceMappingPreview = InfluencesMappingPreview()
        self.influencesManualMapping = InfluencesManualMapping()

        self.buildMapper = None


        self.mapper = InfluenceMapping()

    @staticmethod
    def getInstance():
        return BaseToolWindow.getWindowInstance('EditMirrorInfluencesWindow', EditMirrorInfluencesWindow)

    def setMapperBuilder(self,buildMapper):
        self.buildMapper = buildMapper
        self.previewInfluenceMapping()


    def createWindow(self):
        BaseToolWindow.createWindow(self)

        buttons = [
            ('Close', self.closeWindow, '')
        ]

        self.cmdLayout = CommandLayout(SkinToolsDocs.MIRRORWEIGHTS_INTERFACE, buttons)

        contentRoot = self.cmdLayout.innerLayout

        self.influenceMappingPreview.mirrorMode = True
        self.influenceMappingPreview.createUI(contentRoot)
        self.influenceMappingPreview.onDelete.addHandler(self.influencesManualMapping.removeSelectedManualMappings, contentRoot)

        manualGroup = uiGroup.create(contentRoot, 'Manual influence mapping')
        self.influencesManualMapping.mirrorMode = True
        self.influencesManualMapping.createUI(manualGroup)
        self.influencesManualMapping.getSelectedInfluences = lambda: self.influenceMappingPreview.currentInfluencesSelection

        def onManualOverridesChanged():
            mll = MllInterface()
            mll.setManualMirrorInfluences(self.influencesManualMapping.manualOverrides)
            self.previewInfluenceMapping()
        self.influencesManualMapping.manualOverridesChanged.addHandler(onManualOverridesChanged, contentRoot)


        def updateForSelectionInfoChange():
            layersAvailable = selectionState.getLayersAvailable()
            cmds.layout(contentRoot,e=True,enable=layersAvailable)
            if not layersAvailable:
                return


            self.influencesManualMapping.manualOverrides = selectionState.mll.getManualMirrorInfluences()
            self.previewInfluenceMapping()

        selectionState.selectionInfo.changed.addHandler(updateForSelectionInfoChange,contentRoot)
        selectionState.mirrorInfo.changed.addHandler(self.previewInfluenceMapping,contentRoot)
        updateForSelectionInfoChange()

    def previewInfluenceMapping(self):
        if self.buildMapper is None:
            return
        self.mapper.sourceInfluences = selectionState.mll.listInfluenceInfo()
        self.mapper = self.buildMapper()

        self.mapper.manualOverrides = self.influencesManualMapping.manualOverrides
        self.mapper.calculate()

        self.influenceMappingPreview.mapper = self.mapper
        self.influenceMappingPreview.constructInfluenceList()
