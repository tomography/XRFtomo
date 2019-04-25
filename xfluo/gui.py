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
import xfluo.config as config
from pylab import *

# from widgets.file_widget import  FileTableWidget
# from widgets.image_process_widget import ImageProcessWidget
# from widgets.hotspot_widget import HotspotWidget
# from widgets.sinogram_widget import SinogramWidget
# from widgets.reconstruction_widget import ReconstructionWidget
import json
import os

STR_CONFIG_THETA_STRS = 'theta_pv_strs'

class XfluoGui(QtGui.QMainWindow):
    def __init__(self, app, params):
        super(QtGui.QMainWindow, self).__init__()
        self.params = params
        self.param_list = {}
        self.app = app
        self.get_values_from_params()
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

        saveImageAction = QtGui.QAction('Save Projections', self)
        saveImageAction.triggered.connect(self.saveProjections)

        # saveHotSpotPosAction = QtGui.QAction('save hotspot positions',self)
        # saveHotSpotPosAction.triggered.connect(self.save_hotspot_positions)

        saveSinogramAction = QtGui.QAction('Save Sinogram', self)
        #saveSinogramAction.triggered.connect(self.saveSinogram)

        savephysicalPosition = QtGui.QAction('Save angle and motor positions', self)
        # savephysicalPosition,triggered.connect(self.save_motor_position)

        saveToHDF = QtGui.QAction('Save to h5 file', self)
        # export_h5.triggered.connect(self.export_h5)

        saveAlignemtInfoAction = QtGui.QAction("save alignment", self)
        saveAlignemtInfoAction.triggered.connect(self.saveAlignemnt)

        #selectElementAction = QtGui.QAction('Select Element', self)
        #selectElementAction.triggered.connect(self.selectElement)

        #selectFilesAction = QtGui.QAction('Select Files', self)
        #selectFilesAction.triggered.connect(self.selectFilesShow)

        #saveThetaTxtAction = QtGui.QAction("Save Theta Postion as txt", self)
        #saveThetaTxtAction.triggered.connect(self.saveThetaTxt)

        #convertAction = QtGui.QAction('Save data in memory', self)
        #convertAction.triggered.connect(self.convert)

        runReconstructAction = QtGui.QAction("Reconstruction", self)
        #runReconstructAction.triggered.connect(self.runReconstruct)

        # selectImageTagAction = QtGui.QAction("Select Image Tag", self)
        #selectImageTagAction.triggered.connect(self.selectImageTag)

        # xCorAction = QtGui.QAction("Cross Correlation", self)
        #xCorAction.triggered.connect(self.CrossCorrelation_test)

        # phaseXCorAction = QtGui.QAction("Phase Correlation", self)
        #phaseXCorAction.triggered.connect(self.CrossCorrelation_test)

        # alignFromTextAction = QtGui.QAction("Alignment from Text", self)
        #alignFromTextAction.triggered.connect(self.alignFromText)

        # alignFromText2Action = QtGui.QAction("Alignment from Text2", self)
        #alignFromText2Action.triggered.connect(self.alignFromText2)

        # saveAlignToTextAction = QtGui.QAction("Save Alignment information to text", self)
        #saveAlignToTextAction.triggered.connect(self.saveAlignToText)



        undoAction = QtGui.QAction('Undo (Ctrl+Z)', self)
        undoAction.triggered.connect(self.undo)
        undoAction.setShortcut('Ctrl+Z')

        restoreAction = QtGui.QAction("Restore", self)
        restoreAction.triggered.connect(self.restore)

        # readConfigAction = QtGui.QAction("Read configuration file", self)
        #readConfigAction.triggered.connect(self.readConfigFile)

        runCenterOfMassAction = QtGui.QAction("run center of mass action", self)
        #runCenterOfMassAction.triggered.connect(self.centerOfMassWindow)

        # alignCenterOfMassAction = QtGui.QAction("Align by fitting center of mass position into sine curve", self)
        #alignCenterOfMassAction.triggered.connect(self.alignCenterOfMass)

        # matcherAction = QtGui.QAction("match template", self)
        #matcherAction.triggered.connect(self.match_window)

        # configurationAction = QtGui.QAction("Configuration Window", self)
        #configurationAction.triggered.connect(self.configurationWindow)

        # exportDataAction = QtGui.QAction("export data", self)
        #exportDataAction.triggered.connect(self.export_data)

        runTransRecAction = QtGui.QAction("Transmission Recon", self)
        #runTransRecAction.triggered.connect(self.runTransReconstruct)

        # saveHotSpotPosAction = QtGui.QAction("Save Hot Spot Pos", self)
        #saveHotSpotPosAction.triggered.connect(self.saveHotSpotPos)

        # alignHotSpotPosAction = QtGui.QAction("Align Hot Spot pos", self)
        #alignHotSpotPosAction.triggered.connect(self.alignHotSpotPos1)

        wienerAction = QtGui.QAction("Wiener", self)
        #wienerAction.triggered.connect(self.ipWiener)

        # externalImageRegAction = QtGui.QAction("External Image Registaration", self)
        #externalImageRegAction.triggered.connect(self.externalImageReg)

        ###
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()

        # theta_auto_completes = seshowImgProcesslf.config.get(STR_CONFIG_THETA_STRS)
        # theta_auto_completes = self.params.theta_pv
        # if theta_auto_completes is None:
        #     theta_auto_completes = []
        self.fileTableWidget = xfluo.FileTableWidget(self)
        self.imageProcessWidget = xfluo.ImageProcessWidget()
        self.hotspotWidget = xfluo.HotspotWidget()
        self.sinogramWidget = xfluo.SinogramWidget()
        self.reconstructionWidget = xfluo.ReconstructionWidget()
        self.writer = xfluo.SaveOptions()

        self.prevTab = 0
        self.TAB_FILE = 0
        self.TAB_IMAGE_PROC = 1
        self.TAB_HOTSPOT = 2
        self.TAB_SINOGRAM = 3
        self.TAB_RECONSTRUCTION = 4

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.fileTableWidget, 'Files')
        self.tab_widget.addTab(self.imageProcessWidget, "Pre Processing")
        self.tab_widget.addTab(self.hotspotWidget, "Hotspot")
        self.tab_widget.addTab(self.sinogramWidget, "Alignment")
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
        # self.fileMenu.addAction(configurationAction) #to replace readconfiguration Action
        # self.fileMenu.addAction(readConfigAction)
        ##self.fileMenu.addAction(openFileAction)
        #self.fileMenu.addAction(openFolderAction)
        #self.fileMenu.addAction(openTiffFolderAction)
        self.fileMenu.addAction(exitAction)
        self.fileMenu.addAction(closeAction)

        # self.optionMenu = menubar.addMenu('Convert Option')
        #self.optionMenu.addAction(selectFilesAction)
        # self.optionMenu.addAction(selectImageTagAction)
        #self.optionMenu.addAction(selectElementAction)
        #self.optionMenu.addAction(convertAction)
        #self.optionMenu.setDisabled(True)

        self.editMenu = menubar.addMenu("Edit")
        self.editMenu.addAction(undoAction)
        # self.editMenu.addAction(saveAlignToTextAction)
        # self.editMenu.addAction(runCenterOfMassAction)
        # self.editMenu.addAction(alignCenterOfMassAction)
        # self.editMenu.addAction(xCorAction)
        # self.editMenu.addAction(phaseXCorAction)
        # self.editMenu.addAction(matcherAction)
        # self.editMenu.addAction(alignFromTextAction)
        # self.editMenu.addAction(alignFromText2Action)
        # self.editMenu.addAction(saveHotSpotPosAction)
        # self.editMenu.addAction(alignHotSpotPosAction)
        # self.editMenu.addAction(externalImageRegAction)
        self.editMenu.addAction(restoreAction)
        #self.editMenu.setDisabled(True)

        self.afterConversionMenu = menubar.addMenu('Save items')
        self.afterConversionMenu.addAction(saveImageAction)
        # self.afterConversionMenu.addAction(saveHotSpotPosAction)
        self.afterConversionMenu.addAction(saveAlignemtInfoAction)
        self.afterConversionMenu.addAction(saveSinogramAction)
        self.afterConversionMenu.addAction(savephysicalPosition)
        self.afterConversionMenu.addAction(saveToHDF)

        #self.afterConversionMenu.addAction(saveThetaTxtAction)
        # self.afterConversionMenu.addAction(selectElementAction)
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
 
    def saveAlignemnt(self):
        self.writer.save_alignemnt_information(self.fnames, self.x_shifts, self.y_shifts, self.centers)
        return

    def saveProjections(self):
        self.writer.save_projections(self.fnames, self.data, self.element_array)
        return

    def saveSinogram(self):
        self.sinodata = "get sinodata somehow "
        return

    def saveH5(self):
        #get bunch of data,
        #save bunh of data in such a way that can be easely imported
        pass

    def loadImages(self):
        file_array = self.fileTableWidget.fileTableModel.arrayData
        self.element_array = self.fileTableWidget.elementTableModel.arrayData
        #for fidx in range(len(file_array)):

    def updateImages(self):
        self.data_history = []
        self.x_shifts_history = []
        self.y_shifts_history = []   
        # self.centers_history = []
        self.from_undo = False
        self.data, elements, self.thetas, self.fnames = self.fileTableWidget.onSaveDataInMemory()
        self.centers = [100,100,self.data.shape[3]//2]
        self.x_shifts = zeros(self.data.shape[1], dtype=np.int)
        self.y_shifts = zeros(self.data.shape[1], dtype=np.int)
        self.data_history.append(self.data.copy())
        self.original_data = self.data.copy()

        self.imageProcessWidget.showImgProcess(self.data, elements, self.thetas, self.fnames, self.x_shifts, self.y_shifts, self.centers)
        self.hotspotWidget.showHotSpot(self.data, elements, self.thetas, self.fnames, self.x_shifts, self.y_shifts, self.centers)
        self.sinogramWidget.showSinogram(self.data, elements, self.thetas, self.fnames, self.x_shifts, self.y_shifts, self.centers)
        self.reconstructionWidget.showReconstruct(self.data, elements, self.fnames, self.thetas, self.x_shifts, self.y_shifts, self.centers)

        self.tab_widget.removeTab(1)
        self.tab_widget.removeTab(2)
        self.tab_widget.removeTab(3)
        self.tab_widget.removeTab(4)
        self.tab_widget.insertTab(1, self.imageProcessWidget, "Pre Processing")
        self.tab_widget.insertTab(2, self.hotspotWidget, "Hotspot")
        self.tab_widget.insertTab(3, self.sinogramWidget, "Alignment")
        self.tab_widget.insertTab(4, self.reconstructionWidget, "Reconstruction")

        #slider change
        self.imageProcessWidget.sliderChangedSig.connect(self.hotspotWidget.updateSliderSlot)
        self.hotspotWidget.sliderChangedSig.connect(self.imageProcessWidget.updateSliderSlot)
       
        #element dropdown change
        self.imageProcessWidget.elementChangedSig.connect(self.hotspotWidget.updateElementSlot)
        self.hotspotWidget.elementChangedSig.connect(self.sinogramWidget.updateElementSlot)
        self.sinogramWidget.elementChangedSig.connect(self.reconstructionWidget.updateElementSlot)
        self.reconstructionWidget.elementChangedSig.connect(self.imageProcessWidget.updateElementSlot)

        # data update
        self.imageProcessWidget.dataChangedSig.connect(self.update_data)
        self.sinogramWidget.dataChangedSig.connect(self.update_data)

        #data dimensions changed
        self.imageProcessWidget.ySizeChanged.connect(self.sinogramWidget.yChanged)
        # self.actions = xfluo.ImageProcessActions(self)

        #slider range change
        self.imageProcessWidget.sldRangeChanged.connect(self.hotspotWidget.updateSldRange)
        self.hotspotWidget.sldRangeChanged.connect(self.imageProcessWidget.updateSldRange)

        #filenames changed
        self.imageProcessWidget.fnamesChanged.connect(self.hotspotWidget.updateFileDisplay)

        #alignment changed 
        self.imageProcessWidget.alignmentChangedSig.connect(self.update_alignment)
        self.hotspotWidget.alignmentChangedSig.connect(self.update_alignment)
        self.sinogramWidget.alignmentChangedSig.connect(self.update_alignment)

        #update_reconstructed_data
        self.reconstructionWidget.reconChangedSig.connect(self.update_recon_data)

        # self.update_alignment(self.x_shifts, self.y_shifts, self.centers)
        self.update_alignment(self.x_shifts, self.y_shifts)

    def update_recon_data(self, recon):
        self.recon = recon.copy()
        return

    def update_data(self, data):
        self.data = data 
        self.imageProcessWidget.data = self.data
        self.imageProcessWidget.imageChanged()
        self.hotspotWidget.data = self.data
        self.hotspotWidget.imageChanged()
        self.sinogramWidget.data = self.data
        self.sinogramWidget.imageChanged()

        if self.from_undo:
            return
        else:
            self.data_history.append(self.data.copy())
            if len(self.data_history) > 10:
                del self.data_history[0]
        return

    def undo(self):
        if len(self.data_history) <= 1:
            print("maximum history state reached, cannot undo further")
        else:
            del self.data_history[-1]
            del self.x_shifts_history[-1]
            del self.y_shifts_history[-1]
            # del self.centers_history[-1]
            self.data = self.data_history[-1]
            self.x_shifts = self.x_shifts_history[-1]
            self.y_shifts = self.y_shifts_history[-1]
            # self.centers = self.centers_history[-1]

            self.from_undo = True
            self.update_data(self.data)
            # self.update_alignment(self.x_shifts, self.y_shifts, self.centers)
            self.update_alignment(self.x_shifts, self.y_shifts)
        self.from_undo = False
        print(len(self.data_history))

    def restore(self):
        num_projections = self.original_data.shape[1]
        self.data = zeros(self.original_data.shape)
        self.data[...] = self.original_data[...]

        self.centers = [100,100,self.data.shape[3]//2]
        self.x_shifts = zeros(self.data.shape[1], dtype=np.int)
        self.y_shifts = zeros(self.data.shape[1], dtype=np.int)

        self.update_data(self.data)
        # self.update_alignment(self.x_shifts, self.y_shifts, self.centers)
        self.update_alignment(self.x_shifts, self.y_shifts)

    def update_alignment(self, x_shifts, y_shifts):
        self.x_shifts = x_shifts
        self.y_shifts = y_shifts
        # self.centers = centers 
        self.imageProcessWidget.x_shifts = self.x_shifts
        self.imageProcessWidget.y_shifts = self.y_shifts
        # self.imageProcessWidget.centers = self.centers
        self.imageProcessWidget.actions.x_shifts = self.x_shifts
        self.imageProcessWidget.actions.y_shifts = self.y_shifts
        # self.imageProcessWidget.actions.centers = self.centers

        self.hotspotWidget.x_shifts = self.x_shifts
        self.hotspotWidget.y_shifts = self.y_shifts
        # self.hotspotWidget.centers = self.centers
        self.hotspotWidget.actions.x_shifts = self.x_shifts
        self.hotspotWidget.actions.y_shifts = self.y_shifts
        # self.hotspotWidget.actions.centers = self.centers

        self.sinogramWidget.x_shifts = self.x_shifts
        self.sinogramWidget.y_shifts = self.y_shifts
        # self.sinogramWidget.centers = self.centers
        self.sinogramWidget.actions.x_shifts = self.x_shifts
        self.sinogramWidget.actions.y_shifts = self.y_shifts
        # self.sinogramWidget.actions.centers = self.centers

        if self.from_undo:
            return
        else:
            self.x_shifts_history.append(self.x_shifts.copy())
            self.y_shifts_history.append(self.y_shifts.copy())
            # self.centers_history.append(self.centers.copy())
            if len(self.x_shifts_history) > 10:
                del self.x_shifts_history[0]
                del self.y_shifts_history[0]
                # del self.centers[0]
        return

    def get_values_from_params(self):
        # self.param_list[0] = self.params.theta_pv
        # self.param_list[1] = self.params.input_path
        # self.param_list[2] = self.params.image_tag
        # self.param_list[3] = self.params.data_tag
        # self.param_list[4] = self.params.element_tag
        # self.param_list[5] = self.params.sorted_angles
        # self.param_list[6] = self.params.selected_elements
        pass
        
    def closeEvent(self, event):
        try:
            sections = config.TOMO_PARAMS + ('gui', 'file-io')
            config.write('xfluo.conf', args=self.params, sections=sections)
        except IOError as e:
            self.gui_warn(str(e))
            self.on_save_as()

def main(params):
    app = QtGui.QApplication(sys.argv)
    mainWindow = XfluoGui(app, params)
    sys.exit(app.exec_())
