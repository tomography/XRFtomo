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
from scipy import signal, stats
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from skimage import measure

from xfluo.file_io.reader import *
# from widgets.file_widget import  FileTableWidget
# from widgets.image_process_widget import ImageProcessWidget
# from widgets.sinogram_widget import SinogramWidget
# from widgets.reconstruction_widget import ReconstructionWidget
import json
import os
import time

STR_CONFIG_THETA_STRS = 'theta_pv_strs'

class XfluoGui(QtGui.QMainWindow):
    def __init__(self, app, params):
        super(QtGui.QMainWindow, self).__init__()
        self.params = params
        self.param_list = {}
        self.app = app
        # self.get_values_from_params()
        self.initUI()

    def initUI(self):
        exitAction = QtGui.QAction('Exit', self)
        exitAction.triggered.connect(self.close)
        exitAction.setShortcut('Ctrl+Q')

        closeAction = QtGui.QAction('Quit', self)
        closeAction.triggered.connect(sys.exit)
        closeAction.setShortcut('Ctrl+X')

        openExchangeAction = QtGui.QAction('open exchange file', self)
        openExchangeAction.triggered.connect(self.openExchange)

        openTiffAction = QtGui.QAction('open tiff files', self)
        openTiffAction.triggered.connect(self.openTiffs)

        openThetaAction = QtGui.QAction('open thetas file', self)
        openThetaAction.triggered.connect(self.openThetas)

        #openTiffFolderAction = QtGui.QAction("Open Tiff Folder", self)
        #openTiffFolderAction.triggered.connect(self.openTiffFolder)

        saveProjectionAction = QtGui.QAction('Projections', self)
        saveProjectionAction.triggered.connect(self.saveProjections)

        # saveHotSpotPosAction = QtGui.QAction('save hotspot positions',self)
        # saveHotSpotPosAction.triggered.connect(self.save_hotspot_positions)

        saveSinogramAction = QtGui.QAction('Sinogram', self)
        saveSinogramAction.triggered.connect(self.saveSinogram)

        saveSinogram2Action = QtGui.QAction('Sinogram stack', self)
        saveSinogram2Action.triggered.connect(self.saveSinogram2)

        savephysicalPosition = QtGui.QAction('Angle and motor positions', self)
        # savephysicalPosition,triggered.connect(self.save_motor_position)

        saveReconstructionAction = QtGui.QAction('Reconstruction', self)
        saveReconstructionAction.triggered.connect(self.saveReconstruction)

        saveToHDFAction = QtGui.QAction('as HDF file', self)
        saveToHDFAction.triggered.connect(self.saveToHDF)

        saveThetasAction = QtGui.QAction('thetas to .txt', self)
        saveThetasAction.triggered.connect(self.saveThetas)

        saveToNumpyAction = QtGui.QAction("as Numpy file", self)
        saveToNumpyAction.triggered.connect(self.saveToNumpy)

        saveAlignemtInfoAction = QtGui.QAction("Alignment", self)
        saveAlignemtInfoAction.triggered.connect(self.saveAlignemnt)

        runTransRecAction = QtGui.QAction("Transmission Recon", self)
        #runTransRecAction.triggered.connect(self.runTransReconstruct)

        # selectImageTagAction = QtGui.QAction("Select Image Tag", self)
        #selectImageTagAction.triggered.connect(self.selectImageTag)

        undoAction = QtGui.QAction('Undo (Ctrl+Z)', self)
        undoAction.triggered.connect(self.undo)
        undoAction.setShortcut('Ctrl+Z')

        restoreAction = QtGui.QAction("Restore", self)
        restoreAction.triggered.connect(self.restore)

        keyMapAction = QtGui.QAction('key map settings', self)
        keyMapAction.triggered.connect(self.keyMapSettings)

        debugToolsAction = QtGui.QAction('enable debug tools', self)
        debugToolsAction.triggered.connect(self.debugMode)

        exitDebugToolsAction = QtGui.QAction('disable debug tools', self)
        exitDebugToolsAction.triggered.connect(self.exitDebugMode)

        # matcherAction = QtGui.QAction("match template", self)
        #matcherAction.triggered.connect(self.match_window)

        # saveHotSpotPosAction = QtGui.QAction("Save Hot Spot Pos", self)
        #saveHotSpotPosAction.triggered.connect(self.saveHotSpotPos)

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
        self.sinogramWidget = xfluo.SinogramWidget()
        self.reconstructionWidget = xfluo.ReconstructionWidget()
        self.writer = xfluo.SaveOptions()


        #refresh UI
        self.imageProcessWidget.refreshSig.connect(self.refreshUI)

        #sinogram changed
        self.sinogramWidget.sinoChangedSig.connect(self.update_sino)

        #slider change
        self.imageProcessWidget.sliderChangedSig.connect(self.imageProcessWidget.updateSliderSlot)

        #element dropdown change
        self.imageProcessWidget.elementChangedSig.connect(self.sinogramWidget.updateElementSlot)
        self.sinogramWidget.elementChangedSig.connect(self.reconstructionWidget.updateElementSlot)
        self.reconstructionWidget.elementChangedSig.connect(self.imageProcessWidget.updateElementSlot)

        # data update
        self.imageProcessWidget.dataChangedSig.connect(self.update_history)
        self.sinogramWidget.dataChangedSig.connect(self.update_history)

        # theta update
        self.imageProcessWidget.thetaChangedSig.connect(self.update_theta)

        #data dimensions changed
        self.imageProcessWidget.ySizeChanged.connect(self.sinogramWidget.yChanged)
        self.imageProcessWidget.ySizeChanged.connect(self.reconstructionWidget.ySizeChanged)
        #alignment changed
        self.imageProcessWidget.alignmentChangedSig.connect(self.update_alignment)
        self.sinogramWidget.alignmentChangedSig.connect(self.update_alignment)

        #fnames changed 
        self.imageProcessWidget.fnamesChanged.connect(self.update_filenames)

        #update_reconstructed_data
        self.reconstructionWidget.reconChangedSig.connect(self.update_recon)

        self.prevTab = 0
        self.TAB_FILE = 0
        self.TAB_IMAGE_PROC = 1
        self.TAB_SINOGRAM = 2
        self.TAB_RECONSTRUCTION = 3

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.fileTableWidget, 'Files')
        self.tab_widget.addTab(self.imageProcessWidget, "Pre Processing")
        self.tab_widget.addTab(self.sinogramWidget, "Alignment")
        self.tab_widget.addTab(self.reconstructionWidget, "Reconstruction")
        self.tab_widget.setTabEnabled(1,False)
        self.tab_widget.setTabEnabled(2,False)
        self.tab_widget.setTabEnabled(3,False)

        self.tab_widget.currentChanged.connect(self.onTabChanged)
        self.fileTableWidget.saveDataBtn.clicked.connect(self.updateImages)

        self.vl.addWidget(self.tab_widget)
        #self.vl.addWidget(self.createMessageWidget())

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        ## Top menu bar [file   Convert Option    Alignment   After saving in memory]
        menubar = self.menuBar()
        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(openExchangeAction)
        self.fileMenu.addAction(openTiffAction)
        self.fileMenu.addAction(openThetaAction)
        ##self.fileMenu.addAction(openFileAction)
        #self.fileMenu.addAction(openFolderAction)
        #self.fileMenu.addAction(openTiffFolderAction)
        self.fileMenu.addAction(exitAction)
        self.fileMenu.addAction(closeAction)

        self.editMenu = menubar.addMenu("Edit")
        self.editMenu.addAction(undoAction)
        # self.editMenu.addAction(matcherAction)
        # self.editMenu.addAction(saveHotSpotPosAction)
        # self.editMenu.addAction(alignHotSpotPosAction)
        # self.editMenu.addAction(externalImageRegAction)
        self.editMenu.addAction(restoreAction)
        self.editMenu.setDisabled(True)

        analysis = QtGui.QMenu('Analysis', self)
        corrElemAction = QtGui.QAction('Correlate Elements', self)
        analysis.addAction(corrElemAction)
        corrElemAction.triggered.connect(self.corrElem)

        self.toolsMenu = menubar.addMenu("Tools")
        self.toolsMenu.addMenu(analysis)
        self.toolsMenu.setDisabled(True)

        self.afterConversionMenu = menubar.addMenu('Save')
        self.afterConversionMenu.addAction(saveProjectionAction)
        # self.afterConversionMenu.addAction(saveHotSpotPosAction)
        self.afterConversionMenu.addAction(saveReconstructionAction)
        self.afterConversionMenu.addAction(saveAlignemtInfoAction)
        self.afterConversionMenu.addAction(saveSinogramAction)
        self.afterConversionMenu.addAction(saveSinogram2Action)
        self.afterConversionMenu.addAction(savephysicalPosition)
        self.afterConversionMenu.addAction(saveThetasAction)
        self.afterConversionMenu.addAction(saveToHDFAction)
        self.afterConversionMenu.addAction(saveToNumpyAction)

        self.helpMenu = menubar.addMenu('&Help')
        self.helpMenu.addAction(keyMapAction)
        self.helpMenu.addAction(debugToolsAction)
        self.helpMenu.addAction(exitDebugToolsAction)
        self.afterConversionMenu.setDisabled(True)

        add = 0
        if sys.platform == "win32":
            add = 50
        self.setGeometry(add, add, 1100 + add, 500 + add)
        self.setWindowTitle('xfluo')
        self.show()

    def debugMode(self):
        self.fileTableWidget.thetaLabel.setVisible(True)
        self.fileTableWidget.thetaLineEdit.setVisible(True)
        return
 
    def exitDebugMode(self):
        self.fileTableWidget.thetaLabel.setVisible(False)
        self.fileTableWidget.thetaLineEdit.setVisible(False)
        return      

    def openFolder(self):
        try:
            folderName = QtGui.QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())
        except IndexError:
            print("no folder has been selected")
        except OSError:
            print("no folder has been selected")
        return folderName

    def openExchange(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Open Folder", QtCore.QDir.currentPath())
        if fname[0] == '':
            return
        data, self.elements, thetas = xfluo.read_exchange_file(fname)

        sort_angle_index = np.argsort(thetas)
        self.thetas= thetas[sort_angle_index]
        self.data = data[:,sort_angle_index,:,:]
        self.fnames = ["projection {}".format(x) for x in self.thetas]
        self.updateImages(True)
        return

    def openTiffs(self):
        files = QtGui.QFileDialog.getOpenFileNames(self, "Open Tiffs", QtCore.QDir.currentPath())
        if files[0] == '' or files[0] == []:
            return

        dir_ending_index = files[0][0].split(".")[0][::-1].find("/")+1
        path = files[0][0].split(".")[0][:-dir_ending_index]
        ext = "*."+files[0][0].split(".")[2]
        self.fileTableWidget.dirLineEdit.setText(path)
        self.fileTableWidget.extLineEdit.setText(ext)
        self.fileTableWidget.onLoadDirectory()
        self.data = xfluo.read_tiffs(files[0])
        self.fnames = [files[0][i].split("/")[-1] for i in range(len(files[0]))]
        return

    def openThetas(self):
        file = QtGui.QFileDialog.getOpenFileName(self, "Open Theta.txt", QtCore.QDir.currentPath())
        if file[0] == '':
            return

        fnames, thetas = xfluo.load_thetas_file(file[0])

        if len(thetas)<self.data.shape[1] or len(thetas)>self.data.shape[1]:
            self.fileTableWidget.message.setText("nummber of angles different than number of loaded images. ")
            return

        if thetas == []:
            print("No angle information loaded")
            return

        if fnames == []:
            print("No filenames in .txt. Assuming Tiff order corresponds to loaded theta order")
            sorted_index = np.argsort(thetas)
            thetas = np.asarray(thetas)[sorted_index]
            self.fnames = np.asarray(self.fnames)[sorted_index]
            self.data = self.data[:,sorted_index]

        if set(fnames) == set(self.fnames): #if list of fnames from theta.txt have containst same fnames as from the tiffs..
            sorted_index = [self.fnames.index(i) for i in fnames]
            self.fnames = fnames
            self.data = self.data[:,sorted_index]

        if set(fnames) != set(self.fnames) and fnames != []: #fnames from tiffs and thetas.txt do not match
            print("fnames from tiffs and thetas.txt do not match. Assuming fnames from tiffs correspond to the same order as the loaded angles.")
            sorted_index = np.argsort(thetas)
            thetas = np.asarray(thetas)[sorted_index]
            self.fnames = np.asarray(self.fnames)[sorted_index]
            self.data = self.data[:,sorted_index]
            
        self.thetas = [float(list(thetas)[i]) for i in range(len(thetas))]
        self.fnames = [str(list(self.fnames)[i]) for i in range(len(self.fnames))]
        for i in range(len(self.thetas)):
            self.fileTableWidget.fileTableModel.arrayData[i].theta = self.thetas[i]
            self.fileTableWidget.fileTableModel.arrayData[i].filename = self.fnames[i]
        self.elements = ["Element_1"]
        self.thetas = np.asarray(self.thetas)
        self.updateImages(True)
        return

    def onTabChanged(self, index):
        if self.prevTab == self.TAB_FILE:
            self.loadImages()
        elif self.prevTab == self.TAB_IMAGE_PROC:
            pass
        elif self.prevTab == self.TAB_SINOGRAM:
            pass
        elif self.prevTab == self.TAB_RECONSTRUCTION:
            pass
        self.prevTab = index
 
    def saveAlignemnt(self):
        try:
            self.writer.save_alignemnt_information(self.fnames, self.x_shifts, self.y_shifts, self.centers)
        except AttributeError:
            print("Alignment data does not exist.")
        return

    def saveProjections(self):
        try:
            self.writer.save_projections(self.fnames, self.data, self.elements)
        except AttributeError:
            print("projection data do not exist")
        return

    def saveSinogram(self):
        try:
            self.writer.save_sinogram(self.sino)
        except AttributeError:
            print("sinogram data do not exist")
        return

    def saveSinogram2(self):
        try:
            self.writer.save_sinogram2(self.data, self.elements)
        except AttributeError:
            print("sinogram data do not exist")
        return

    def saveReconstruction(self, recon):
        try:
            self.writer.save_reconstruction(self.recon)
        except AttributeError:
            print("reconstructed data do not exist")
        return

    def saveToHDF(self):
        try:
            self.writer.save_dxhdf(self.fnames, self.data, self.elements)
        except AttributeError:
            print("projection data do not exist")
        return 

    def saveThetas(self):
        try:
            files = [i.filename for i in self.fileTableWidget.fileTableModel.arrayData]
            k = np.arange(len(files))
            thetas = [i.theta for i in self.fileTableWidget.fileTableModel.arrayData]
            files_bool = [i.use for i in self.fileTableWidget.fileTableModel.arrayData]
            self.fnames = [files[j] for j in k if files_bool[j]==True]
            self.thetas = np.asarray([thetas[j] for j in k if files_bool[j]==True])
            self.writer.save_thetas(self.fnames, self.thetas)
        except AttributeError:
            print("filename or angle information does not exist")
        return 

    def saveToNumpy(self):
        try:
            self.writer.save_numpy_array(self.data, self.thetas, self.elements)
        except AttributeError:
            print("data has not been imported first")
        return

    def loadImages(self):
        file_array = self.fileTableWidget.fileTableModel.arrayData
        self.element_array = self.fileTableWidget.elementTableModel.arrayData
        #for fidx in range(len(file_array)):

    # def reset_widgets(self):

    def updateImages(self, from_open=False):
        self.data_history = []
        self.x_shifts_history = []
        self.y_shifts_history = []
        self.theta_history = []
        self.fname_history = []
        # self.centers_history = []

        if not from_open:
            self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.data, self.elements, self.thetas, self.fnames = self.fileTableWidget.onSaveDataInMemory()
            self.app.restoreOverrideCursor()

            if len(self.data) == 0:
                return
            if len(self.elements) == 0:
                return
            if len(self.thetas) == 0:
                return
            if len(self.fnames) == 0:
                return

        self.centers = [100,100,self.data.shape[3]//2]
        self.x_shifts = zeros(self.data.shape[1], dtype=np.int)
        self.y_shifts = zeros(self.data.shape[1], dtype=np.int)
        self.original_data = self.data.copy()
        self.original_fnames = self.fnames.copy()
        self.original_thetas = self.thetas.copy()

        self.init_widgets()
        self.imageProcessWidget.showImgProcess()
        self.imageProcessWidget.imgAndHistoWidget.view.setAspectLocked(True)

        self.sinogramWidget.showSinogram()
        self.reconstructionWidget.showReconstruct()
        # self.reset_widgets()

        self.tab_widget.setTabEnabled(1,True)
        self.tab_widget.setTabEnabled(2,True)
        self.tab_widget.setTabEnabled(3,True)
        self.afterConversionMenu.setDisabled(False)
        self.editMenu.setDisabled(False)
        self.toolsMenu.setDisabled(False)
        # self.update_alignment(self.x_shifts, self.y_shifts, self.centers)
        self.update_history(self.data)
        self.update_alignment(self.x_shifts, self.y_shifts)
        self.refreshUI()

    def refreshUI(self):
        self.tab_widget.removeTab(1)
        self.tab_widget.removeTab(2)
        self.tab_widget.removeTab(3)
        self.tab_widget.insertTab(1, self.imageProcessWidget, "Pre Processing")
        self.tab_widget.insertTab(2, self.sinogramWidget, "Alignment")
        self.tab_widget.insertTab(3, self.reconstructionWidget, "Reconstruction")

    def init_widgets(self):
        self.imageProcessWidget.data = self.data
        self.imageProcessWidget.elements = self.elements
        self.imageProcessWidget.thetas = self.thetas
        self.imageProcessWidget.fnames = self.fnames
        self.imageProcessWidget.x_shifts = self.x_shifts
        self.imageProcessWidget.y_shifts = self.y_shifts
        self.imageProcessWidget.centers = self.centers
        self.imageProcessWidget.ViewControl.combo1.setCurrentIndex(0)
        self.imageProcessWidget.imgAndHistoWidget.sld.setValue(0)

        self.sinogramWidget.data = self.data 
        self.sinogramWidget.elements = self.elements 
        self.sinogramWidget.thetas = self.thetas 
        self.sinogramWidget.fnames = self.fnames 
        self.sinogramWidget.x_shifts = self.x_shifts 
        self.sinogramWidget.y_shifts = self.y_shifts 
        self.sinogramWidget.centers = self.centers 
        self.sinogramWidget.ViewControl.combo1.setCurrentIndex(0)
        self.sinogramWidget.sld.setValue(0)

        self.reconstructionWidget.data = self.data 
        self.reconstructionWidget.elements = self.elements 
        self.reconstructionWidget.thetas = self.thetas 
        self.reconstructionWidget.fnames = self.fnames
        self.reconstructionWidget.x_shifts = self.x_shifts
        self.reconstructionWidget.y_shifts = self.y_shifts
        self.reconstructionWidget.centers = self.centers
        self.reconstructionWidget.ViewControl.combo1.setCurrentIndex(0)

        self.imageProcessWidget.imgAndHistoWidget.sld.setValue(0)
        self.reconstructionWidget.imgAndHistoWidget.sld.setValue(0)
        self.imageProcessWidget.imgAndHistoWidget.lcd.display(str(self.thetas[0]))
        self.reconstructionWidget.recon = []
        self.sinogramWidget.sld.setValue(1)

    def update_history(self, data):
        index = self.imageProcessWidget.imgAndHistoWidget.sld.value()
        self.update_data(data)
        self.update_theta(self.thetas)
        self.update_filenames(self.fnames, index)
        self.update_alignment(self.x_shifts, self.y_shifts)

        print('history save event')
        self.data_history.append(data.copy())
        self.theta_history.append(self.thetas.copy())
        self.x_shifts_history.append(self.x_shifts.copy())
        self.y_shifts_history.append(self.y_shifts.copy())
        # self.centers_history.append(self.centers.copy())
        self.fname_history.append(self.fnames.copy())

        print(len(self.data_history))
        if len(self.data_history) > 10:
            del self.data_history[0]
            del self.theta_history[0]
            del self.x_shifts_history[0]
            del self.y_shifts_history[0]
            # del self.centers[0]
            del self.fname_history[0]
        return

    def update_recon(self, recon):
        self.recon = recon.copy()
        return

    def update_sino(self, sino):
        self.sino = sino.copy()
        return

    def update_data(self, data):
        self.data = data 
        self.imageProcessWidget.data = self.data
        self.imageProcessWidget.imageChanged()
        self.sinogramWidget.data = self.data
        self.sinogramWidget.imageChanged()
        self.reconstructionWidget.data = self.data
        return

    def update_theta(self, thetas):
        self.thetas = thetas
        self.imageProcessWidget.thetas = self.thetas
        self.sinogramWidget.thetas = self.thetas
        return

    def update_alignment(self, x_shifts, y_shifts):
        self.x_shifts = x_shifts
        self.y_shifts = y_shifts
        # self.centers = centers 
        self.imageProcessWidget.x_shifts = self.x_shifts
        self.imageProcessWidget.y_shifts = self.y_shifts
        self.sinogramWidget.x_shifts = self.x_shifts
        self.sinogramWidget.y_shifts = self.y_shifts
        self.sinogramWidget.actions.x_shifts = self.x_shifts
        self.sinogramWidget.actions.y_shifts = self.y_shifts
        # self.sinogramWidget.actions.centers = self.centers
        return
        
    def update_filenames(self, fnames, index):
        self.fnames = fnames 
        self.imageProcessWidget.fnames = fnames
        self.imageProcessWidget.updateFileDisplay(fnames, index)
        return

    def update_slider_range(self, thetas):
        index = self.imageProcessWidget.imgAndHistoWidget.sld.value()
        self.imageProcessWidget.updateSldRange(index, thetas)
        return

    def clear_all(self):
        self.data_history = []
        self.x_shifts_history = []
        self.y_shifts_history = []
        self.fname_history = []
        self.update_alignment([],[])

        # self.update_recon([])
        # self.update_sino([])

        return

    def undo(self):
        try:
            if len(self.data_history) <=1:
                print("maximum history stplt.imshow(self.data_history[1][0])ate reached, cannot undo further")
            else:
                del self.data_history[-1]
                del self.x_shifts_history[-1]
                del self.y_shifts_history[-1]
                del self.theta_history[-1]
                del self.fname_history[-1]
                # del self.centers_history[-1]
                self.data = self.data_history[-1].copy()
                self.x_shifts = self.x_shifts_history[-1].copy()
                self.y_shifts = self.y_shifts_history[-1].copy()
                self.thetas = self.theta_history[-1].copy()
                self.fnames = self.fname_history[-1].copy()
                # self.centers = self.centers_history[-1]

                self.update_alignment(self.x_shifts, self.y_shifts)
                self.update_slider_range(self.thetas)
                index = self.imageProcessWidget.imgAndHistoWidget.sld.value()
                self.update_theta(self.thetas)
                self.update_filenames(self.fnames, index)
                self.update_data(self.data)

        except AttributeError:
            print("Load dataset first")
            return
        print(len(self.data_history))
        return

    def restore(self):
        try:
            num_projections = self.original_data.shape[1]
            self.data = self.original_data
            self.thetas = self.original_thetas
            self.fnames = self.original_thetas
            self.x_shifts = zeros(self.data.shape[1], dtype=np.int)
            self.y_shifts = zeros(self.data.shape[1], dtype=np.int)
            self.centers = [100,100,self.data.shape[3]//2]
            self.update_history(self.data)
            self.update_slider_range(self.thetas)

        except AttributeError:
            print("Load dataset first")
            return

    # def corrElem2(self):
    #     self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
    #     data = self.data
    #     corrMat = np.zeros((data.shape[0],data.shape[0]))
    #     for i in range(data.shape[0]):
    #         for j in range(data.shape[0]):
    #             elemA = data[i]
    #             elemB = data[j]
    #             corr = np.mean(signal.correlate(elemA, elemB, method='direct', mode='same') / (data.shape[1]*data.shape[2]*data.shape[3]))
    #             corrMat[i,j] = corr

    #     sns.set(style="white")

    #     # Generate a mask for the upper triangle
    #     mask = np.zeros_like(corrMat, dtype=np.bool)
    #     mask[np.triu_indices_from(mask,1)] = True

    #     # Set up the matplotlib figure
    #     f, ax = plt.subplots(figsize=(11, 9))

    #     # Generate a custom diverging colormap
    #     cmap = sns.diverging_palette(220, 10, as_cmap=True)

    #     # Draw the heatmap with the mask and correct aspect ratio
    #     d = pd.DataFrame(data=corrMat, columns=self.elements, index=self.elements)
    #     sns.heatmap(d, mask=mask, cmap=cmap, vmax=corrMat.max(), center=0,
    #                 square=True, linewidths=.5, cbar_kws={"shrink": .5})
    #     f.show()
    #     self.app.restoreOverrideCursor()
    #     return corrMat


    def corrElem(self):
        self.app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        
        data = self.data
        #normalize data
        # nom_data = self.normData(data)
        # errMat = np.zeros((data.shape[0],data.shape[0]))
        # simMat = np.zeros((data.shape[0],data.shape[0]))
        rMat = np.zeros((data.shape[0],data.shape[0]))
        for i in range(data.shape[0]):      #elemA
            for j in range(data.shape[0]):  #elemB
                elemA = data[i]
                elemB = data[j]
                # corr = np.mean(signal.correlate(elemA, elemB, method='direct', mode='same') / (data.shape[1]*data.shape[2]*data.shape[3]))
                rval = self.compare(elemA, elemB)
                # errMat[i,j]= err
                # simMat[i,j]= sim
                rMat[i,j]= rval

        sns.set(style="white")

        # Generate a mask for the upper triangle
        mask = np.zeros_like(rMat, dtype=np.bool)
        mask[np.triu_indices_from(mask,1)] = True

        # Set up the matplotlib figure
        f, ax = plt.subplots(figsize=(11, 9))

        # Generate a custom diverging colormap
        cmap = sns.diverging_palette(220, 10, as_cmap=True)

        # Draw the heatmap with the mask and correct aspect ratio
        d = pd.DataFrame(data=rMat, columns=self.elements, index=self.elements)
        sns.heatmap(d, mask=mask, annot=True, cmap=cmap, vmax=rMat.max(), center=0,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5})
        f.show()

        self.app.restoreOverrideCursor()
        return rMat

    # def normData(self,data):
    #     norm = np.zeros_like(data)
    #     for i in range(data.shape[0]):
    #         data_mean = np.mean(data[i])
    #         data_std = np.std(data[i])
    #         data_med = np.median(data[i])
    #         data_max = np.max(data[i])
    #         new_max = data_mean+10*data_std
    #         current_elem = data[i]
    #         current_elem[data[i] >= new_max] = new_max
    #         data[i] = current_elem

    #     return data 

    def compare(self, imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;

        d = len(imageA)
        # d2 = len(imageB)
        # errMat = np.zeros(imageA.shape[0])
        # simMat = np.zeros(imageA.shape[0])
        rMat = np.zeros(imageA.shape[0])


        if d > 2:
            for i in range(imageA.shape[0]):
                # err = np.sum((imageA[i].astype("float") - imageB[i].astype("float")) ** 2)
                # err /= float(imageA[i].shape[0] * imageA[i].shape[1])
                # sim = measure.compare_ssim(imageA[i], imageB[i])
                r, p = stats.pearsonr(imageA[i].flatten(), imageB[i].flatten())

                # errMat[i] = err
                # simMat[i] = sim
                rMat[i] = r
                # errVal = np.sum(errMat)/len(errMat)
                # simVal = np.sum(simMat)/len(simMat)
            rVal = np.sum(rMat)/len(rMat)
        else:
            # err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
            # err /= float(imageA.shape[0] * imageA.shape[1])
            # sim  = measure.compare_ssim(imageA, imageB)
            # errVal = err
            # simVal = sim
            r, p = stats.pearsonr(imageA.flatten(), imageB.flatten())

            rVal = r





        # return the MSE, the lower the error, the more "similar"
        return rVal


    def keyMapSettings(self):
        self.msg = QtWidgets.QWidget()
        self.msg.resize(600,400)
        self.msg.setWindowTitle('key map')
        text = QtWidgets.QLabel("Undo: \t\t Ctr+Z \t\t previous image: \t A \n\n" 
                    "shift image up: \t up \t\t next image: \t D \n\n" 
                    "shift image down: \t down  \t\t skip (hotspot): \t S \n\n"
                    "shift image left: \t left \t\t next (hotspot): \t N \n\n"
                    "shift image right: \t right  \n\n"
                    "shift stack up: \t Shift + up \n\n"
                    "shift stack down: \t Shift + down \n\n"
                    "shift stack left: \t Shift + left \n\n"
                    "shift stack right: \t Shift + right \n\n"
                    "exclude image: \t Delete \n\n"
                    "copy background: \t Ctrl + C \n\npaste background:  Ctrl + V" 


                    )



        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(text)

        self.msg.setLayout(vbox)
        self.msg.show()


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
