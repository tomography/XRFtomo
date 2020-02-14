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

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
import xrftomo
from pylab import *
import pyqtgraph
import xrftomo.widgets.image_process_actions as actions
import numpy as np



class ImageProcessWidget(QtWidgets.QWidget):

    sliderChangedSig = pyqtSignal(int, name='sliderChangedSig')
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')
    thetaChangedSig = pyqtSignal(int, np.ndarray, name='thetaChangedSig')
    fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")
    alignmentChangedSig = pyqtSignal(np.ndarray, np.ndarray, name="alignmentChangedSig")
    ySizeChangedSig = pyqtSignal(int, name='ySizeChangedSig')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    refreshSig = pyqtSignal(name='refreshSig')

    def __init__(self):
        super(ImageProcessWidget, self).__init__()
        self.thetas = []
        self.initUI()

    def initUI(self):
        self.ViewControl = xrftomo.ImageProcessControlsWidget()
        # self.imageView = xrftomo.ImageView(self)
        self.imageView = xrftomo.ImageView()
        self.actions = xrftomo.ImageProcessActions()

        self.file_name_title = QtWidgets.QLabel("_")
        lbl1 = QtWidgets.QLabel("x pos:")
        self.lbl2 = QtWidgets.QLabel("")
        lbl3 = QtWidgets.QLabel("y pos:")
        self.lbl4 = QtWidgets.QLabel("")
        self.lbl5 = QtWidgets.QLabel("Angle")
        lbl6 = QtWidgets.QLabel("pixel value:")
        self.lbl7 = QtWidgets.QLabel("")

        self.imageView.mouseMoveSig.connect(self.updatePanel)
        #get pixel value from Histogram widget's projview 

        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        self.hist.setImageItem(self.imageView.projView)





        # self.imgAndHistoWidget.setSizePolicy(QtWidgets.QSizePolicy.setHeightForWidth(True))

        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(True)
        # sizePolicy.setWidthForHeight(True)
        # self.imgAndHistoWidget.setSizePolicy(sizePolicy)

        # self.imgAndHistoWidget.resize(1000, 700)


        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        # self.ViewControl.combo2.currentIndexChanged.connect(self.elementChanged)
        # self.ViewControl.x_sld.valueChanged.connect(self.imgProcessBoxSizeChange)
        # self.ViewControl.xSizeTxt.editingFinished.connect(self.imgProcessBoxSizeChange)
        # self.ViewControl.y_sld.valueChanged.connect(self.imgProcessBoxSizeChange)
        # self.ViewControl.ySizeTxt.editingFinished.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.reshapeBtn.clicked.connect(self.ViewControl.reshape_options.show)
        self.ViewControl.run_reshape.clicked.connect(self.reshape_params)
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

        self.imageView.keyPressSig.connect(self.keyProcess)
        # self.actions.dataSig.connect(self.send_data)
        # self.actions.thetaSig.connect(self.send_thetas)
        self.sld.valueChanged.connect(self.imageSliderChanged)

        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
        self.data = None
        self.meanNoise = 0
        self.stdNoise = 0

        palette = self.lcd.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(85, 85, 255))
        # background color
        palette.setColor(palette.Background, QtGui.QColor(0, 170, 255))
        # "light" border
        palette.setColor(palette.Light, QtGui.QColor(255, 255, 0))
        # "dark" border
        palette.setColor(palette.Dark, QtGui.QColor(0, 0, 0))
        # set the palette
        self.lcd.setPalette(palette)
        self.imageView.projView.setScaledMode()
        
        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(lbl1)
        hb0.addWidget(self.lbl2)
        hb0.addWidget(lbl3)
        hb0.addWidget(self.lbl4)
        hb0.addWidget(lbl6)
        hb0.addWidget(self.lbl7)

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(self.lbl5)
        hb1.addWidget(self.lcd)
        hb1.addWidget(self.sld)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addWidget(self.file_name_title)
        vb1.addLayout(hb0)
        vb1.addWidget(self.imageView)
        vb1.addLayout(hb1)

        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.ViewControl)
        hb2.addLayout(vb1)
        hb2.addWidget(self.hist, 10)

        self.setLayout(hb2)
    def updatePanel(self,x,y):
        self.lbl2.setText(str(x))
        self.lbl4.setText(str(y))
        try:
            pixel_val = round(self.imageView.projView.image[abs(y)-1,x],4)
            self.lbl7.setText(str(pixel_val))
        except:
            self.lbl7.setText("")

    def lockAspect(self):
        if self.ViewControl.aspectChkbx.isChecked():
            self.imageView.setRange(lockAspect=True)
            # self.imageView.setAspectLocked(True)
        else:
            # self.imageView.setAspectLocked(False)
            self.imageView.setRange(lockAspect=False)

            #destroy and redraw
            #or disable locked aspect and set size policy to expanding
            # self.imageView.redraw(True)
        return

    def showImgProcess(self):
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.posMat = np.zeros((5,int(self.data.shape[1]),2))
        self.imageView.hotSpotNumb = 0
        # self.ViewControl.x_sld.setRange(1, self.data.shape[3])
        # self.ViewControl.y_sld.setRange(1, self.data.shape[2])

        self.ViewControl.combo1.clear()
        self.ViewControl.combo2.clear()
        for j in self.elements:
            self.ViewControl.combo1.addItem(j)
        num_projections  = self.data.shape[1]
        for k in arange(num_projections):
            self.ViewControl.combo2.addItem(str(k+1))

        self.elementChanged()
        self.sld.setRange(0, num_projections - 1)
        self.ViewControl.combo2.setVisible(False)
        self.file_name_title.setText(str(self.fnames[0]))

    def imageSliderChanged(self):
        index = self.sld.value()
        self.updateFileDisplay(self.fnames, index)
        # self.filename_event
        self.updateSliderSlot(index)
        self.sliderChangedSig.emit(index)

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.sld.value()
        self.updateElementSlot(element, projection)
        self.elementChangedSig.emit(element, projection)

    def filename_event(self):
        index = self.sld.value()
        self.file_name_title.setText(self.fnames[index])

    def updateSliderSlot(self, index):
        if len(self.thetas) == 0:
            return
        angle = round(self.thetas[index])
        element = self.ViewControl.combo1.currentIndex()
        self.lcd.display(angle)
        self.sld.setValue(index)
        self.imageView.projView.setImage(self.data[element, index, :, :], border='w')

    def updateElementSlot(self, element, projection = None):
        if projection == None:
           projection =  self.sld.value()
        self.imageView.projView.setImage(self.data[element, projection, :, :], border='w')
        self.ViewControl.combo1.setCurrentIndex(element)
        self.ViewControl.combo2.setCurrentIndex(projection)

    def updateFileDisplay(self, fnames, index):
        self.fnames = fnames
        self.file_name_title.setText(str(self.fnames[index]))

    # def imgProcessBoxSizeChange(self):
    #     xSize = self.ViewControl.xSize
    #     ySize = self.ViewControl.ySize
    #     if xSize > self.data.shape[3]:
    #         xSize = self.data.shape[3]
    #         self.ViewControl.xSize = xSize
    #     if ySize > self.data.shape[2]:
    #         ySize = self.data.shape[2]
    #         self.ViewControl.ySize = ySize

    #     self.imageView.xSize = xSize
    #     self.imageView.ySize = ySize
    #     self.imageView.ROI.setSize([xSize, ySize])
    #     x_pos = int(round(self.imageView.x_pos))
    #     y_pos = int(round(self.imageView.y_pos))
    #     frame_height = self.data.shape[2]
    #     frame_width = self.data.shape[3]
    #     x_pos, y_pos, cross_pos_x, cross_pos_y  = self.imageView.update_roi(x_pos, y_pos, xSize, ySize, frame_height, frame_width)

    #     self.imageView.ROI.setPos([x_pos-xSize/2, y_pos-ySize/2])

    def imageChanged(self):
        index = self.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.imageView.projView.setImage(self.data[element, index, :, :], border='w')

    # def ySizeChanged(self, ySize):
    #     self.ViewControl.y_sld.setRange(2, ySize)

    def updateSldRange(self, index, thetas):
        element = self.ViewControl.combo1.currentIndex()
        self.sld.setRange(0, len(thetas) -1)
        self.lcd.display(thetas[index])
        self.sld.setValue(index)
        self.imageChanged()
        self.posMat = np.zeros((5,int(self.data.shape[1]), 2))

    def keyProcess(self, command):
        index = self.sld.value()
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data

        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.sld.value()
        if command == 'A': #previous projection
            self.sld.setValue(self.sld.value() - 1)
            self.imageSliderChanged()
        if command == 'D':  #next projection
            self.sld.setValue(self.sld.value() + 1)
            self.imageSliderChanged()
        if command == 'left':
            self.x_shifts[index] -=1
            data = self.actions.shiftProjectionX(self.data, index, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'right':
            self.x_shifts[index] +=1
            data = self.actions.shiftProjectionX(self.data, index, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'up':
            self.y_shifts[index] +=1
            data = self.actions.shiftProjectionY(self.data, index, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'down':
            self.y_shifts[index] -=1
            data = self.actions.shiftProjectionY(self.data, index, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftLeft':
            self.x_shifts -=1
            data = self.actions.shiftDataX(self.data, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftRight':
            self.x_shifts +=1
            data = self.actions.shiftDataX(self.data, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftUp':
            self.y_shifts +=1
            data = self.actions.shiftDataY(self.data, -1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftDown':
            self.y_shifts -=1
            data = self.actions.shiftDataY(self.data, 1)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'Delete':
            self.exclude_params()
        if command == 'Copy':
            self.copyBG_params(img)
        if command == 'Paste':
            data = self.pasteBG_params()
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
        self.imageView.hotSpotSetNumb = self.ViewControl.combo3.currentIndex()
        # self.actions.saveHotSpotPos()

    def hotspot2line_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.sld.value()
        posMat = self.posMat
        data, x_shifts, y_shifts = self.actions.hotspot2line(element, x_size, y_size, hs_group, posMat, data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts + y_shifts)
        self.dataChangedSig.emit(data)
        self.ViewControl.btn4.setEnabled(True)

    def hotspot2sine_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.sld.value()
        posMat = self.posMat
        thetas = self.thetas
        data, x_shifts, y_shifts = self.actions.hotspot2sine(element, x_size, y_size, hs_group, posMat, data, thetas)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts +y_shifts)
        self.dataChangedSig.emit(data)
        self.ViewControl.btn4.setEnabled(True)

    def setY_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.sld.value()
        posMat = self.posMat
        data, y_shifts = self.actions.setY(element, x_size, y_size, hs_group, posMat, data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts + y_shifts)
        self.dataChangedSig.emit(data)
        self.ViewControl.btn4.setEnabled(True)

    def clrHotspot_params(self):
        self.posMat = self.actions.clrHotspot(self.posMat)
        self.ViewControl.btn4.setEnabled(False)
        self.ViewControl.btn3.setEnabled(False)
        self.ViewControl.btn2.setEnabled(False)
        self.ViewControl.btn1.setEnabled(False)

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.sld.value()
        x_pos = self.imageView.x_pos
        y_pos = self.imageView.y_pos
        x_size = self.imageView.xSize
        y_size = self.imageView.ySize
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
        self.dataChangedSig.emit(data)

    def equalize_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        data = self.actions.equalize(data, element)
        self.dataChangedSig.emit(data)

    def cut_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.actions.cut(self.data, x_pos, y_pos, x_size, y_size)
        # self.ySizeChangedSig.emit(y_size)
        self.dataChangedSig.emit(data)
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
        data = self.actions.paste_background(data, element, projection, x_pos, y_pos, x_size, y_size, img, meanNoise, stdNoise)
        self.dataChangedSig.emit(data)

    def analysis_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.noise_analysis(img)

    def bounding_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        img = data[element, projection, :,:]
        self.actions.bounding_analysis(img)

    def reshape_params(self):

        valid = self.ViewControl.validate_reshape_parameters()
        if not valid:
            return
        y_multiplier = int(self.ViewControl.yUpsample_text.text())
        x_multiplier = int(self.ViewControl.xUpsample_text.text())
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        datasize_x = self.data.shape[3]
        datasize_y = self.data.shape[2]
        data = self.actions.reshape_data(self.data, x_multiplier, y_multiplier)
        new_ySize = int(datasize_y*y_multiplier)
        # self.ySizeChangedSig.emit(new_ySize)
        # self.xSizeChangedSig.emit(new_xSize)
        self.dataChangedSig.emit(data)
        self.refreshSig.emit()

        pass


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
        index, data, self.thetas, self.fnames, self.x_shifts, self.y_shifts = self.actions.exclude_projection(index, data, thetas, fnames, x_shifts, y_shifts)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        self.updateSldRange(index, self.thetas)
        self.imageSliderChanged()
        # self.sldRangeChanged.emit(index, self.data, self.thetas)
        self.thetaChangedSig.emit(index, self.thetas)
        self.dataChangedSig.emit(data)

    def rm_hotspot_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        data = self.actions.remove_hotspots(data, element)
        self.dataChangedSig.emit(data)



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

    def rot_axis_params(self):
        data = self.data
        num_projections = data.shape[1]
        thetas = self.thetas
        rAxis_pos = self.imageView.cross_pos_x
        center = data.shape[3]//2
        theta_pos = self.lcd.value()
        shift_arr = self.actions.move_rot_axis(thetas, center, rAxis_pos, theta_pos)
        shift_arr = np.round(shift_arr)

        for i in range(num_projections):
            data[:,i] = np.roll(data[:,i],int(shift_arr[i]),axis=2)
        self.alignmentChangedSig.emit(self.x_shifts + shift_arr, self.y_shifts)
        self.dataChangedSig.emit(data)
        return

    def histo_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        for i in range(data.shape[1]):
            mask = self.actions.create_mask(data[element,i])
            data[element, i], m = self.actions.equalize_hist_ev(data[element,i], 2**16, mask)
        self.dataChangedSig.emit(data)




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

