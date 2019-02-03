# #########################################################################
# Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2018. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################


from PyQt5 import QtGui, QtWidgets, QtCore
import sys
import xfluo

# from widgets.file_widget import  FileTableWidget
# from widgets.image_process_widget import ImageProcessWidget
# from widgets.hotspot_widget import HotspotWidget
# from widgets.sinogram_widget import SinogramWidget
# from widgets.reconstruction_widget import ReconstructionWidget
import json
import os

STR_CONFIG_THETA_STRS = 'theta_pv_strs'


class XfluoGui(QtGui.QMainWindow):
    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        with open('xfluo_config.json') as json_file:
            self.config = json.load(json_file)
        self.initUI()

    def initUI(self):
        exitAction = QtGui.QAction('Exit', self)
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut('Ctrl+Q')

        closeAction = QtGui.QAction('Quit', self)
        closeAction.triggered.connect(sys.exit)
        closeAction.setShortcut('Ctrl+X')

        #openFileAction = QtGui.QAction('Open File', self)
        #openFileAction.triggered.connect(self.openfile)

        #openFolderAction = QtGui.QAction('Open Folder', self)
        #openFolderAction.triggered.connect(self.openFolder)

        #openTiffFolderAction = QtGui.QAction("Open Tiff Folder", self)
        #openTiffFolderAction.triggered.connect(self.openTiffFolder)

        sinogramAction = QtGui.QAction('Sinogram', self)
        #sinogramAction.triggered.connect(self.sinogram)

        saveImageAction = QtGui.QAction('Save Projections', self)
        #saveImageAction.triggered.connect(self.saveImage)

        #selectElementAction = QtGui.QAction('Select Element', self)
        #selectElementAction.triggered.connect(self.selectElement)

        #selectFilesAction = QtGui.QAction('Select Files', self)
        #selectFilesAction.triggered.connect(self.selectFilesShow)

        #saveThetaTxtAction = QtGui.QAction("Save Theta Postion as txt", self)
        #saveThetaTxtAction.triggered.connect(self.saveThetaTxt)

        #convertAction = QtGui.QAction('Save data in memory', self)
        #convertAction.triggered.connect(self.convert)

        saveSinogramAction = QtGui.QAction('Save Sinogram', self)
        #saveSinogramAction.triggered.connect(self.saveSinogram)

        runReconstructAction = QtGui.QAction("Reconstruction", self)
        #runReconstructAction.triggered.connect(self.runReconstruct)

        selectImageTagAction = QtGui.QAction("Select Image Tag", self)
        #selectImageTagAction.triggered.connect(self.selectImageTag)

        xCorAction = QtGui.QAction("Cross Correlation", self)
        #xCorAction.triggered.connect(self.CrossCorrelation_test)

        phaseXCorAction = QtGui.QAction("Phase Correlation", self)
        #phaseXCorAction.triggered.connect(self.CrossCorrelation_test)

        alignFromTextAction = QtGui.QAction("Alignment from Text", self)
        #alignFromTextAction.triggered.connect(self.alignFromText)

        alignFromText2Action = QtGui.QAction("Alignment from Text2", self)
        #alignFromText2Action.triggered.connect(self.alignFromText2)

        saveAlignToTextAction = QtGui.QAction("Save Alignment information to text", self)
        #saveAlignToTextAction.triggered.connect(self.saveAlignToText)

        restoreAction = QtGui.QAction("Restore", self)
        #restoreAction.triggered.connect(self.restore)

        readConfigAction = QtGui.QAction("Read configuration file", self)
        #readConfigAction.triggered.connect(self.readConfigFile)

        runCenterOfMassAction = QtGui.QAction("run center of mass action", self)
        #runCenterOfMassAction.triggered.connect(self.centerOfMassWindow)

        alignCenterOfMassAction = QtGui.QAction("Align by fitting center of mass position into sine curve", self)
        #alignCenterOfMassAction.triggered.connect(self.alignCenterOfMass)

        matcherAction = QtGui.QAction("match template", self)
        #matcherAction.triggered.connect(self.match_window)

        configurationAction = QtGui.QAction("Configuration Window", self)
        #configurationAction.triggered.connect(self.configurationWindow)

        exportDataAction = QtGui.QAction("export data", self)
        #exportDataAction.triggered.connect(self.export_data)

        runTransRecAction = QtGui.QAction("Transmission Recon", self)
        #runTransRecAction.triggered.connect(self.runTransReconstruct)

        saveHotSpotPosAction = QtGui.QAction("Save Hot Spot Pos", self)
        #saveHotSpotPosAction.triggered.connect(self.saveHotSpotPos)

        alignHotSpotPosAction = QtGui.QAction("Align Hot Spot pos", self)
        #alignHotSpotPosAction.triggered.connect(self.alignHotSpotPos1)

        reorderAction = QtGui.QAction("Reorder", self)
        #reorderAction.triggered.connect(self.reorder_matrix)

        wienerAction = QtGui.QAction("Wiener", self)
        #wienerAction.triggered.connect(self.ipWiener)

        reorderAction = QtGui.QAction("Reorder", self)
        #reorderAction.triggered.connect(self.reorder_matrix)

        externalImageRegAction = QtGui.QAction("External Image Registaration", self)
        #externalImageRegAction.triggered.connect(self.externalImageReg)

        ###
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()

        theta_auto_completes = self.config.get(STR_CONFIG_THETA_STRS)
        if theta_auto_completes is None:
            theta_auto_completes = []
        self.fileTableWidget = xfluo.FileTableWidget(theta_auto_completes)
        self.imageProcessWidget = xfluo.ImageProcessWidget()
        self.hotspotWidget = xfluo.HotspotWidget()
        self.sinogramWidget = xfluo.SinogramWidget()
        self.reconstructionWidget = xfluo.ReconstructionWidget()

        self.prevTab = 0
        self.TAB_FILE = 0
        self.TAB_IMAGE_PROC = 1
        self.TAB_HOTSPOT = 2
        self.TAB_SINOGRAM = 3
        self.TAB_RECONSTRUCTION = 4

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.fileTableWidget, 'Files')
        self.tab_widget.addTab(self.imageProcessWidget, "Image Process")
        self.tab_widget.addTab(self.hotspotWidget, "Hotspot")
        self.tab_widget.addTab(self.sinogramWidget, "Sinogram")
        self.tab_widget.addTab(self.reconstructionWidget, "Reconstruction")
        self.tab_widget.currentChanged.connect(self.onTabChanged)

        self.fileTableWidget.saveDataBtn.clicked.connect(self.updateImages)

        self.vl.addWidget(self.tab_widget)
        #self.vl.addWidget(self.createMessageWidget())

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        ## Top menu bar [file   Convert Option    Alignment   After saving in memory]
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(configurationAction) #to replace readconfiguration Action
        self.fileMenu.addAction(readConfigAction)
        ##self.fileMenu.addAction(openFileAction)
        #self.fileMenu.addAction(openFolderAction)
        #self.fileMenu.addAction(openTiffFolderAction)
        self.fileMenu.addAction(exitAction)
        self.fileMenu.addAction(closeAction)

        self.optionMenu = menubar.addMenu('Convert Option')
        #self.optionMenu.addAction(selectFilesAction)
        self.optionMenu.addAction(selectImageTagAction)
        #self.optionMenu.addAction(selectElementAction)
        #self.optionMenu.addAction(convertAction)
        #self.optionMenu.setDisabled(True)

        self.alignmentMenu = menubar.addMenu("Alignment")
        self.alignmentMenu.addAction(saveAlignToTextAction)
        self.alignmentMenu.addAction(runCenterOfMassAction)
        self.alignmentMenu.addAction(alignCenterOfMassAction)
        self.alignmentMenu.addAction(xCorAction)
        self.alignmentMenu.addAction(phaseXCorAction)
        self.alignmentMenu.addAction(matcherAction)
        self.alignmentMenu.addAction(alignFromTextAction)
        self.alignmentMenu.addAction(alignFromText2Action)
        self.alignmentMenu.addAction(saveHotSpotPosAction)
        self.alignmentMenu.addAction(alignHotSpotPosAction)
        self.alignmentMenu.addAction(externalImageRegAction)
        self.alignmentMenu.addAction(restoreAction)
        #self.alignmentMenu.setDisabled(True)

        self.afterConversionMenu = menubar.addMenu('After saving data in memory')
        self.afterConversionMenu.addAction(saveImageAction)
        #self.afterConversionMenu.addAction(saveThetaTxtAction)
        # self.afterConversionMenu.addAction(selectElementAction)
        self.afterConversionMenu.addAction(saveSinogramAction)
        # self.afterConversionMenu.addAction(runReconstructAction)
        self.afterConversionMenu.addAction(reorderAction)
        #self.afterConversionMenu.setDisabled(True)

        add = 0
        if sys.platform == "win32":
            add = 50
        self.setGeometry(add, add, 1100 + add, 500 + add)
        self.setWindowTitle('xfluo')
        self.show()


    def openFolder(self):
        try:
            folderName = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
        except IndexError:
            print("no folder has been selected")
        except OSError:
            print("no folder has been selected")
        return folderName

    def onTabChanged(self, index):
        if self.prevTab == self.TAB_FILE:
            self.loadImages()
        elif self.prevTab == self.TAB_IMAGE_PROC:
            pass
        elif self.prevTab == self.TAB_HOTSPOT:
            pass
        elif self.prevTab == self.TAB_SINOGRAM:
            pass
        elif self.prevTab == self.TAB_RECONSTRUCTION:
            pass
        self.prevTab = index

    def loadImages(self):
        file_array = self.fileTableWidget.fileTableModel.arrayData
        element_array = self.fileTableWidget.elementTableModel.arrayData
        #for fidx in range(len(file_array)):

    def updateImages(self):
        self.fileTableWidget.onSaveDataInMemory()

        self.imageProcessWidget.showImgProcess(self.fileTableWidget.data, self.fileTableWidget.use_elements)
        self.imageProcessWidget.show()

        self.hotspotWidget.showHotSpot(self.fileTableWidget.data, self.fileTableWidget.use_elements)

        self.sinogramWidget.showSinogram(self.fileTableWidget.data, self.fileTableWidget.use_elements)
        self.sinogramWidget.sinogram()
        self.sinogramWidget.show()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWindow = XfluoGui()
    sys.exit(app.exec_())