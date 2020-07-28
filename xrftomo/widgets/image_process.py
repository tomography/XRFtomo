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
import pyqtgraph
import numpy as np
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb


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
    padSig = pyqtSignal(int, int, name="padSig")

    def __init__(self):
        super(ImageProcessWidget, self).__init__()
        self.thetas = []
        self.initUI()

    def initUI(self):
        self.ViewControl = xrftomo.ImageProcessControlsWidget()
        # self.imageView = xrftomo.ImageView(self)
        self.imageView = xrftomo.ImageView()
        self.actions = xrftomo.ImageProcessActions()
        self.sub_pixel_shift = 1

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
        self.ViewControl.reshapeBtn.clicked.connect(self.ViewControl.reshape_options.show)
        self.ViewControl.run_reshape.clicked.connect(self.reshape_params)
        self.ViewControl.padBtn.clicked.connect(self.ViewControl.padding_options.show)
        self.ViewControl.run_padding.clicked.connect(self.pad_params)
        self.ViewControl.cropBtn.clicked.connect(self.cut_params)
        # self.ViewControl.gaussian33Btn.clicked.connect(self.actions.gauss33)
        # self.ViewControl.gaussian55Btn.clicked.connect(self.actions.gauss55)
        self.ViewControl.captureBackground.clicked.connect(self.copyBG_params)
        self.ViewControl.setBackground.clicked.connect(self.pasteBG_params)
        self.ViewControl.deleteProjection.clicked.connect(self.exclude_params)
        # self.ViewControl.hist_equalize.clicked.connect(self.equalize_params)
        self.ViewControl.rm_hotspot.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.Equalize.clicked.connect(self.histo_params)
        self.ViewControl.invert.clicked.connect(self.invert_params)
        # self.ViewControl.histogramButton.clicked.connect(self.histogram)

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
        if x >= self.data.shape[3] or x < 0 or y >= self.data.shape[2] or y < 0:
            self.lbl2.setText("")
            self.lbl4.setText("")
            self.lbl7.setText("")
        else:
            self.lbl2.setText(str(x))
            self.lbl4.setText(str(y))
            try:
                pixel_val = round(self.imageView.projView.image[abs(y)-1,x],4)
                self.lbl7.setText(str(pixel_val))
            except:
                self.lbl7.setText("")
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
        for k in range(num_projections):
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
        # self.imageView.projView.setImage(self.data[element, index, :, :], border='w')
        self.imageView.projView.setImage(self.data[element, index, ::-1, :], border='w')

    def updateElementSlot(self, element, projection = None):
        if projection == None:
           projection =  self.sld.value()
        # self.imageView.projView.setImage(self.data[element, projection, :, :], border='w')
        self.imageView.projView.setImage(self.data[element, projection, ::-1, :], border='w')

        self.ViewControl.combo1.setCurrentIndex(element)
        self.ViewControl.combo2.setCurrentIndex(projection)

    def updateFileDisplay(self, fnames, index):
        self.fnames = fnames
        self.file_name_title.setText(str(self.fnames[index]))

    def imageChanged(self):
        index = self.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        # self.imageView.projView.setImage(self.data[element, index, :, :], border='w')
        self.imageView.projView.setImage(self.data[element, index, ::-1, :], border='w')

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
        sps = self.sub_pixel_shift
        # hs_group = self.ViewControl.combo3.currentIndex()
        # hs_number = self.sld.value()
        if command == 'A': #previous projection
            self.sld.setValue(self.sld.value() - 1)
            self.imageSliderChanged()
        if command == 'D':  #next projection
            self.sld.setValue(self.sld.value() + 1)
            self.imageSliderChanged()
        if command == 'left':
            self.x_shifts[index] -=sps
            data = self.actions.shiftProjection(self.data, -sps, 0, index)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'right':
            self.x_shifts[index] +=sps
            data = self.actions.shiftProjection(self.data, sps, 0, index)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'up':
            self.y_shifts[index] +=sps
            data = self.actions.shiftProjection(self.data, 0, -sps, index)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'down':
            self.y_shifts[index] -=sps
            data = self.actions.shiftProjection(self.data, 0, sps, index) #image axis flipped
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftLeft':
            self.x_shifts -=sps
            data = self.actions.shiftStack(self.data, -sps, 0)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftRight':
            self.x_shifts +=sps
            data = self.actions.shiftStack(self.data, sps, 0)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftUp':
            self.y_shifts +=sps
            data = self.actions.shiftStack(self.data, 0, -sps)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'shiftDown':
            self.y_shifts -=sps
            data = self.actions.shiftStack(self.data, 0, sps)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        if command == 'Delete':
            self.exclude_params()
        if command == 'Copy':
            self.copyBG_params(img)
        if command == 'Paste':
            data = self.pasteBG_params()

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.sld.value()
        x_pos = self.imageView.x_pos
        y_pos = self.imageView.y_pos
        x_size = self.imageView.xSize
        y_size = self.imageView.ySize
        frame_height = self.data.shape[2]
        y_end = int(round(frame_height - y_pos))
        y_start = int(round(frame_height-y_pos-y_size))
        x_start = int(round(x_pos))
        x_end = int(round(x_pos) + x_size)

        img = self.data[element, projection, y_start:y_end, x_start: x_end]
        return element, projection, x_pos, y_pos, x_size, y_size, img[::-1]

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

    def invert_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        data = self.actions.invert(data, element)
        self.dataChangedSig.emit(data)

    def cut_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.actions.cut(self.data, x_pos, y_pos, x_size, y_size)
        self.ySizeChangedSig.emit(y_size)
        self.dataChangedSig.emit(data)
        #TODO: move crosshairs an ROI to crop region after crop
        self.imageView.p1.items[3].setValue(0)
        self.imageView.p1.items[4].setValue(0)
        self.imageView.ROI.setPos([0, 0], finish=False)
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
        self.ySizeChangedSig.emit(new_ySize)
        # self.xSizeChangedSig.emit(new_xSize)
        self.dataChangedSig.emit(data)
        self.refreshSig.emit()
        pass

    def pad_params(self):
        data = self.data
        padding_x = int(eval(self.ViewControl.pad_x.text()))
        padding_y = int(eval(self.ViewControl.pad_y.text()))
        clip_x = int(eval(self.ViewControl.clip_x.text()))
        x_shifts = self.x_shifts
        y_shifts = self.y_shifts
        x_dimension = data.shape[3]
        y_dimension = data.shape[2]
        valid = self.ViewControl.validate_padding_parameters()

        if valid:
            data = self.actions.padData(self.data, padding_x, padding_y, x_shifts, y_shifts, clip_x)
            for i in range(len(self.x_shifts)):
                #TODO: if xy_shift exceeds xy dimension, then apply 2xy_padding_xy, else, dont.
                if x_shifts[i] > x_dimension:
                    x_shifts[i] = x_shifts[i] - x_dimension
                if y_shifts[i] > y_dimension:
                    y_shifts[i] = y_shifts[i] - y_dimension
                data = self.actions.shiftProjection(data, x_shifts[i], y_shifts[i], i)

        # self.padSig.emit(x,y)
        self.dataChangedSig.emit(data)
        return data

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

