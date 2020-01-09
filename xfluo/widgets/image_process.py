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

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
import xfluo
from pylab import *
import pyqtgraph
import xfluo.widgets.image_process_actions as actions
import numpy as np



class ImageProcessWidget(QtWidgets.QWidget):

    sliderChangedSig = pyqtSignal(int, name='sliderChangedSig')
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')
    thetaChangedSig = pyqtSignal(np.ndarray, name='thetaChangedSig')
    fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")
    alignmentChangedSig = pyqtSignal(np.ndarray, np.ndarray, name="alignmentChangedSig")
    ySizeChanged = pyqtSignal(int, name='ySizeChanged')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    refreshSig = pyqtSignal(name='refreshSig')

    def __init__(self):
        super(ImageProcessWidget, self).__init__()
        self.thetas = []
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.ImageProcessControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget(self)
        # self.imgAndHistoWidget.setSizePolicy(QtWidgets.QSizePolicy.setHeightForWidth(True))

        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(True)
        # sizePolicy.setWidthForHeight(True)
        # self.imgAndHistoWidget.setSizePolicy(sizePolicy)

        # self.imgAndHistoWidget.resize(1000, 700)

        self.actions = xfluo.ImageProcessActions()

        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.combo2.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.x_sld.valueChanged.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.xSizeTxt.editingFinished.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.y_sld.valueChanged.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.ySizeTxt.editingFinished.connect(self.imgProcessBoxSizeChange)
        # self.ViewControl.normalizeBtn.clicked.connect(self.normalize_params)
        self.ViewControl.cropBtn.clicked.connect(self.cut_params)
        self.ViewControl.aspectChkbx.clicked.connect(self.lockAspect)
        # self.ViewControl.gaussian33Btn.clicked.connect(self.actions.gauss33)
        # self.ViewControl.gaussian55Btn.clicked.connect(self.actions.gauss55)
        self.ViewControl.captureBackground.clicked.connect(self.copyBG_params)
        self.ViewControl.setBackground.clicked.connect(self.pasteBG_params)
        self.ViewControl.deleteProjection.clicked.connect(self.exclude_params)
        # self.ViewControl.hist_equalize.clicked.connect(self.equalize_params)
        self.ViewControl.rm_hotspot.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.Equalize.clicked.connect(self.histo_params)
        self.ViewControl.center.clicked.connect(self.ViewControl.center_parameters.show)
        self.ViewControl.center.clicked.connect(self.updateCenterFindParameters)
        self.ViewControl.find_center_1.clicked.connect(self.center_tomopy_params)
        self.ViewControl.find_center_2.clicked.connect(self.center_Everett_params)
        self.ViewControl.move2center.clicked.connect(self.move2center_params)
        self.ViewControl.rot_axis.clicked.connect(self.rot_axis_params)
        # self.ViewControl.histogramButton.clicked.connect(self.histogram)

        # x_pos, y_pos, x_size, y_size, frame_height, frame_width

        # self.ViewControl.x_sld.valueChanged.connect(self.xSldChange)
        # self.ViewControl.y_sld.valueChanged.connect(self.xSldChange)
        self.ViewControl.btn1.clicked.connect(self.hotspot2line_params)
        self.ViewControl.btn2.clicked.connect(self.hotspot2sine_params)
        self.ViewControl.btn3.clicked.connect(self.setY_params)
        self.ViewControl.btn4.clicked.connect(self.clrHotspot_params)
        self.ViewControl.btn4.setEnabled(False)
        self.ViewControl.btn3.setEnabled(False)
        self.ViewControl.btn2.setEnabled(False)
        self.ViewControl.btn1.setEnabled(False)

        self.imgAndHistoWidget.view.keyPressSig.connect(self.keyProcess)
        self.actions.dataSig.connect(self.send_data)
        # self.actions.thetaSig.connect(self.send_thetas)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.imageSliderChanged)

        mainHBox = QtWidgets.QHBoxLayout()
        mainHBox.addWidget(self.ViewControl)
        mainHBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(mainHBox)
        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
        self.data = None
        self.meanNoise = 0
        self.stdNoise = 0

        palette = self.imgAndHistoWidget.lcd.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(85, 85, 255))
        # background color
        palette.setColor(palette.Background, QtGui.QColor(0, 170, 255))
        # "light" border
        palette.setColor(palette.Light, QtGui.QColor(255, 255, 0))
        # "dark" border
        palette.setColor(palette.Dark, QtGui.QColor(0, 0, 0))
        # set the palette
        self.imgAndHistoWidget.lcd.setPalette(palette)
        self.imgAndHistoWidget.view.projView.setScaledMode()

    def lockAspect(self):
        if self.ViewControl.aspectChkbx.isChecked():
            self.imgAndHistoWidget.view.setRange(lockAspect=True)
            # self.imgAndHistoWidget.view.setAspectLocked(True)
        else:
            # self.imgAndHistoWidget.view.setAspectLocked(False)
            self.imgAndHistoWidget.view.setRange(lockAspect=False)

            #destroy and redraw
            #or disable locked aspect and set size policy to expanding
            # self.imgAndHistoWidget.view.redraw(True)
        return

    def showImgProcess(self):
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.posMat = np.zeros((5,int(self.data.shape[1]),2))
        self.imgAndHistoWidget.view.hotSpotNumb = 0
        self.ViewControl.x_sld.setRange(1, self.data.shape[3])
        self.ViewControl.y_sld.setRange(1, self.data.shape[2])

        self.ViewControl.combo1.clear()
        self.ViewControl.combo2.clear()
        for j in self.elements:
            self.ViewControl.combo1.addItem(j)
        num_projections  = self.data.shape[1]
        for k in arange(num_projections):
            self.ViewControl.combo2.addItem(str(k+1))

        self.elementChanged()
        self.imgAndHistoWidget.sld.setRange(0, num_projections - 1)
        self.ViewControl.combo2.setVisible(False)
        self.imgAndHistoWidget.file_name_title.setText(str(self.fnames[0]))

    def imageSliderChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        self.updateFileDisplay(self.fnames, index)
        # self.filename_event
        self.updateSliderSlot(index)
        self.sliderChangedSig.emit(index)

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.imgAndHistoWidget.sld.value()
        self.updateElementSlot(element, projection)
        self.elementChangedSig.emit(element, projection)

    def filename_event(self):
        index = self.imgAndHistoWidget.sld.value()
        self.imgAndHistoWidget.file_name_title.setText(self.fnames[index])

    def updateSliderSlot(self, index):
        if len(self.thetas) == 0:
            return
        angle = round(self.thetas[index])
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.lcd.display(angle)
        self.imgAndHistoWidget.sld.setValue(index)
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :], border='w')

    def updateElementSlot(self, element, projection = None):
        if projection == None:
           projection =  self.imgAndHistoWidget.sld.value()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, projection, :, :], border='w')
        self.ViewControl.combo1.setCurrentIndex(element)
        self.ViewControl.combo2.setCurrentIndex(projection)

    def updateFileDisplay(self, fnames, index):
        self.fnames = fnames
        self.imgAndHistoWidget.file_name_title.setText(str(self.fnames[index]))

    def updateCenterFindParameters(self):
        if self.ViewControl.init_textbox.text() == "-1":
            self.ViewControl.init_textbox.setText(str(self.data.shape[3]//2))
        if self.ViewControl.slice_textbox.text() == "-1":
            self.ViewControl.slice_textbox.setText(str(self.data.shape[2]//2))
        if self.ViewControl.limit_textbox.text() == "-1":
            self.ViewControl.limit_textbox.setText("1")

    def imgProcessBoxSizeChange(self):
        xSize = self.ViewControl.xSize
        ySize = self.ViewControl.ySize
        if xSize > self.data.shape[3]:
            xSize = self.data.shape[3]
            self.ViewControl.xSize = xSize
        if ySize > self.data.shape[2]:
            ySize = self.data.shape[2]
            self.ViewControl.ySize = ySize

        self.imgAndHistoWidget.view.xSize = xSize
        self.imgAndHistoWidget.view.ySize = ySize
        self.imgAndHistoWidget.view.ROI.setSize([xSize, ySize])
        x_pos = int(round(self.imgAndHistoWidget.view.x_pos))
        y_pos = int(round(self.imgAndHistoWidget.view.y_pos))
        frame_height = self.data.shape[2]
        frame_width = self.data.shape[3]
        x_pos, y_pos, cross_pos_x, cross_pos_y  = self.imgAndHistoWidget.view.update_roi(x_pos, y_pos, xSize, ySize, frame_height, frame_width)

        self.imgAndHistoWidget.view.ROI.setPos([x_pos-xSize/2, y_pos-ySize/2])

    def imageChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :], border='w')

    def updateSldRange(self, index, thetas):
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.sld.setRange(0, len(thetas) -1)
        self.imgAndHistoWidget.lcd.display(thetas[index])
        self.imgAndHistoWidget.sld.setValue(index)
        self.imageChanged()
        self.posMat = np.zeros((5,int(self.data.shape[1]), 2))
        # self.imgAndHistoWidget.view.projView.setImage(data[element, projection])

    def keyProcess(self, command):
        index = self.imgAndHistoWidget.sld.value()
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data

        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        if command == 'A': #previous projection
            self.imgAndHistoWidget.sld.setValue(self.imgAndHistoWidget.sld.value() - 1)
            self.imageSliderChanged()
        if command == 'D':  #next projection
            self.imgAndHistoWidget.sld.setValue(self.imgAndHistoWidget.sld.value() + 1)
            self.imageSliderChanged()
        if command == 'left':
            self.x_shifts[index] -=1
            self.actions.shiftProjectionX(self.data, index, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'right':
            self.x_shifts[index] +=1
            self.actions.shiftProjectionX(self.data, index, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'up':
            self.y_shifts[index] +=1
            self.actions.shiftProjectionY(self.data, index, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'down':
            self.y_shifts[index] -=1
            self.actions.shiftProjectionY(self.data, index, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'shiftLeft':
            self.x_shifts -=1
            self.actions.shiftDataX(self.data, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'shiftRight':
            self.x_shifts +=1
            self.actions.shiftDataX(self.data, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'shiftUp':
            self.y_shifts +=1
            self.actions.shiftDataY(self.data, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'shiftDown':
            self.y_shifts -=1
            self.actions.shiftDataY(self.data, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'Delete':
            self.exclude_params()
            # self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'Copy':
            self.copyBG_params(img)
        if command == 'Paste':
            self.pasteBG_params()
        if command == 'Next':
            self.posMat[int(hs_group), int(hs_number)-1] = [x_pos, y_pos]
            if hs_number < self.posMat.shape[1]:
                print("Total projections", self.posMat.shape[1], "current position", hs_number+1, "group number", hs_group + 1)
                hs_number += 1
                if hs_number < self.posMat.shape[1]:
                    self.sliderChangedSig.emit(hs_number)
                else:
                    self.sliderChangedSig.emit(hs_number-1)
                    print("This is the last projection")
            self.ViewControl.btn3.setEnabled(True)
            self.ViewControl.btn2.setEnabled(True)
            self.ViewControl.btn1.setEnabled(True)
            self.ViewControl.btn4.setEnabled(True)
        if command == 'Skip':
            self.posMat[int(hs_group), int(hs_number)-1] = [0, 0]
            if hs_number < self.posMat.shape[1]:
                hs_number += 1
                self.sliderChangedSig.emit(hs_number)

    def hotSpotSetChanged(self):
        self.imgAndHistoWidget.view.hotSpotSetNumb = self.ViewControl.combo3.currentIndex()
        # self.actions.saveHotSpotPos()

    def hotspot2line_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        posMat = self.posMat
        self.x_shifts, self.y_shifts, self.centers = self.actions.hotspot2line(element, x_size, y_size, hs_group, posMat, data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        self.ViewControl.btn4.setEnabled(True)

    def hotspot2sine_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        posMat = self.posMat
        thetas = self.thetas
        self.x_shifts, self.y_shifts, self.centers = self.actions.hotspot2sine(element, x_size, y_size, hs_group, posMat, data, thetas)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        self.ViewControl.btn4.setEnabled(True)

    def setY_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        posMat = self.posMat
        self.y_shifts, self.centers = self.actions.setY(element, x_size, y_size, hs_group, posMat, data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        self.ViewControl.btn4.setEnabled(True)

    def clrHotspot_params(self):
        self.posMat = self.actions.clrHotspot(self.posMat)
        self.ViewControl.btn4.setEnabled(False)
        self.ViewControl.btn3.setEnabled(False)
        self.ViewControl.btn2.setEnabled(False)
        self.ViewControl.btn1.setEnabled(False)

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.imgAndHistoWidget.sld.value()
        x_pos = self.imgAndHistoWidget.view.x_pos
        y_pos = self.imgAndHistoWidget.view.y_pos
        x_size = self.ViewControl.xSize
        y_size = self.ViewControl.ySize
        img = self.data[element, projection,
            int(round(abs(y_pos)) - y_size/2): int(round(abs(y_pos)) + y_size/2),
            int(round(x_pos) - x_size/2): int(round(x_pos) + x_size/2)]
        return element, projection, x_pos, y_pos, x_size, y_size, img

    def background_value_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.background_value(img)

    def normalize_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        self.actions.normalize(data, element)

    def equalize_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        data = self.actions.equalize(data, element)

    def cut_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.cut(self.data, x_pos, y_pos, x_size, y_size)
        self.ySizeChanged.emit(y_size)
        self.refreshSig.emit()

    def copyBG_params(self,*img):
        if type(img[0]) == bool:
            element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()

        self.meanNoise, self.stdNoise = self.actions.copy_background(img)
        return

    def pasteBG_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        meanNoise = self.meanNoise
        stdNoise= self.stdNoise
        data = self.data
        self.actions.paste_background(data, element, projection, x_pos, y_pos, x_size, y_size, img, meanNoise, stdNoise)

    def analysis_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.noise_analysis(img)

    def bounding_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        img = data[element, projection, :,:]
        self.actions.bounding_analysis(img)

    def save_analysis(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        thetas = self.thetas
        img = data[element, projection, :,:]
        self.actions.save_bound_anlysis(data, element, thetas)

    def exclude_params(self):
        element, index, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        thetas = self.thetas
        fnames = self.fnames
        num_files = len(self.fnames)
        x_shifts = self.x_shifts
        y_shifts = self.y_shifts
        #new = function(old)
        index, self.data, self.thetas, self.fnames, self.x_shifts, self.y_shifts = self.actions.exclude_projection(index, data, thetas, fnames, x_shifts, y_shifts)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        self.updateSldRange(index, self.thetas)
        self.imageSliderChanged()

        # self.sldRangeChanged.emit(index, self.data, self.thetas)
        self.thetaChangedSig.emit(self.thetas)
        self.dataChangedSig.emit(self.data)

    def rm_hotspot_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        self.actions.remove_hotspots(data, element)



    # debugging and statistic gathering function, leave commented plz.
    # def histo_signal(self):
    #     data = self.data
    #     element_names = self.element_names
    #     num_elements = data.shape[0]
    #     num_projections = data.shape[1]
    #     histo_arr = np.ndarray(shape=(num_elements,num_projections), dtype=float)
    #     histo_mean = np.ndarray(shape=(num_elements), dtype=float)
    #
    #     for i in range(num_elements):
    #         for j in range(num_projections):
    #             histo_arr[i,j] = np.sum(data[i,j])
    #         histo_mean[i] = np.mean(histo_arr[i])
    #
    #     fig = plt.figure(figsize=(5,7))
    #     #ax1, ax2, ax3 = top right, middle
    #     ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
    #     ax2 = plt.subplot2grid((3, 3), (1, 0), colspan=3)
    #     ax3 = plt.subplot2grid((3, 3), (2, 0), colspan=3)
    #
    #     ax1.hist(histo_arr[0], num_projections)
    #     ax2.hist(histo_arr[1], num_projections)
    #     ax3.hist(histo_arr[2], num_projections)
    #
    #     ax1.set_title(element_names[0])
    #     ax2.set_title(element_names[1])
    #     ax3.set_title(element_names[2])
    #
    #     for i in range(num_elements):
    #         print(element_names[i],": ",np.round(histo_mean[i]))
    #
    #     print("Fe to Ti: ",np.round(histo_mean[1]/histo_mean[0]))
    #     print("Ti to Se: ",np.round(histo_mean[0]/histo_mean[2]))
    #     print("Fe to Se: ",np.round(histo_mean[1]/histo_mean[2]))
    #     # plt.show()
    #
    #     return
    #

    def send_data(self, data):
        '''
        This sends a signal one level up indicating that the data array has changed
        '''

        self.dataChangedSig.emit(data)

    def send_thetas(self, thetas):
        '''
        This sends a signal one level up indicating that the theta array has changed
        '''

        self.thetaChangedSig.emit(thetas)

    # def send_fnames(self, fnames):
    #     '''
    #     This sends a signal one level up indicating that the fnames array has changed
    #     '''
    #     self.fnmaesChangedSig.emit(fnames)

    # def send_alignment(self, x_shifts, y_shifts):
    #     '''
    #     This sends a signal one level up indicating that the alignment information has changed.
    #     '''
    #     self.alignemntChangedSig.emit(x_shifts, y_shifts)

    def rot_axis_params(self):
        data = self.data
        num_projections = data.shape[1]
        thetas = self.thetas
        rAxis_pos = self.imgAndHistoWidget.view.cross_pos_x
        center = data.shape[3]//2
        theta_pos = self.imgAndHistoWidget.lcd.value()
        shift_arr = self.actions.move_rot_axis(thetas, center, rAxis_pos, theta_pos)
        shift_arr = np.round(shift_arr)

        for i in range(num_projections):
            data[:,i] = np.roll(data[:,i],int(shift_arr[i]),axis=2)
        self.send_data(data)
        self.alignmentChangedSig.emit(self.x_shifts + shift_arr, self.y_shifts)
        return

    def move2center_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        rot_center = int(np.round(float(self.ViewControl.center_1.text().split()[1])))
        shift = self.data.shape[3]//2 - rot_center
        self.x_shifts += shift

        if shift<0:
            self.actions.shiftDataX(self.data, shift)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            
        if shift>0:
            self.actions.shiftDataX(data, shift)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)

    def histo_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        for i in range(data.shape[1]):
            mask = self.actions.create_mask(data[element,i])
            data[element, i], m = self.actions.equalize_hist_ev(data[element,i], 2**16, mask)
        self.send_data(data)

    def center_tomopy_params(self):        
        valid = self.ViewControl.validate_parameters()
        if not valid:
            return
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()

        data = self.data
        thetas = self.thetas
        tomo = data[element]
        slice_index = int(self.ViewControl.slice_textbox.text())
        init_center = int(self.ViewControl.init_textbox.text())
        tol = float(self.ViewControl.tol_textbox.text())
        mask_bool = self.ViewControl.mask_checkbox.isChecked()
        ratio = float(self.ViewControl.ratio_textbox.text())

        center = self.actions.find_center(tomo, thetas, slice_index, init_center, tol, mask_bool, ratio)
        self.ViewControl.center_1.setText("center: {}".format(center))
        self.ViewControl.center_2.setText("center: {}".format(center))

    def center_Everett_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        thetasum = np.sum(self.data[element], axis=1)
        
        valid = self.ViewControl.validate_parameters()
        if not valid:
            return

        limit = self.ViewControl.limit_textbox.text()
        center_offset = self.actions.rot_center3(thetasum, ave_mode = 'Median', limit = None, return_all = False)
        center = self.data.shape[3]//2 - center_offset
        center_int = np.round(center_offset)
        self.ViewControl.center_1.setText("center: {}".format(center))
        self.ViewControl.center_2.setText("center: {}".format(center))


    def equalize_colocalization(self, elements, mask = None, nbins = 2**16, eq_hsv = False,
                                global_shift = True, shift_funct = np.median):
        '''
        elements: each element dataset to use for colocalization (up to 3).
        mask: bool or binary masks used to select roi.
        nbins: number of bins used for histogram equalization.
        eq_hsv: equalize the lumination of the colocalization.
        global_shift: global shift each element to match
                (i.e. have the mean of element 1 match the mean of element 2 after colocalization)
        shift_funct: function used for global_shift.
        '''
        rgb = np.zeros((elements[0].shape[0], elements[0].shape[1], 3))
        for i, element in enumerate(elements):
            # Remove inf and nan.
            element[~np.isfinite(element)] = 0
            # Add to RGB image and normalize components.
            rgb[:,:,i] = element/element.max()
            # Equalize the R, G, and B components individually.
            rgb[:,:,i], m = self.equalize_hist_ev(rgb[:,:,i], mask = mask, nbins = nbins,
                                             shift_funct = np.median)
            # Set shift value to zero.
            if global_shift:
                rgb[:,:,i] -= m

        # shift all values to > 0.
        if global_shift:
            rgb[:,:,0:len(elements)] -= rgb[:,:,0:len(elements)].min()
        if eq_hsv:
            # Convert RGB to HSV and equalize the value. Convert back to RGB.
            hsv = rgb_to_hsv(rgb)
            # Equalize value component of the hsv image
            #hsv[:,:,2] = equalize_hist(hsv[:,:,2], mask = mask, nbins = nbins)
            # OR use CLASqualize value component of the hsv image
            hsv[:,:,2] = exposure.equalize_adapthist(hsv[:,:,2], nbins = nbins, clip_limit = .001)
            rgb = hsv_to_rgb(hsv)
        return rgb

    # # Rotation Center Finding

