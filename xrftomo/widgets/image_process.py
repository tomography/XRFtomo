# #########################################################################
# Copyright © 2020, UChicago Argonne, LLC. All Rights Reserved.           #
#                                                                         #
#                       Software Name: XRFtomo                            #
#                                                                         #
#                   By: Argonne National Laboratory                       #
#                                                                         #
#                       OPEN SOURCE LICENSE                               #
#                                                                         #
# Redistribution and use in source and binary forms, with or without      #
# modification, are permitted provided that the following conditions      #
# are met:                                                                #
#                                                                         #
# 1. Redistributions of source code must retain the above copyright       #
#    notice, this list of conditions and the following disclaimer.        #
#                                                                         #
# 2. Redistributions in binary form must reproduce the above copyright    #
#    notice, this list of conditions and the following disclaimer in      #
#    the documentation and/or other materials provided with the           #
#    distribution.                                                        #
#                                                                         #
# 3. Neither the name of the copyright holder nor the names of its        #
#    contributors may be used to endorse or promote products derived      #
#    from this software without specific prior written permission.        #
#                                                                         #
#                               DISCLAIMER                                #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR   #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT    #
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT        #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY   #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT     #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE   #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.    #
###########################################################################

import numpy as np
import pyqtgraph
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
import sys
import xrftomo

#TODO: use separate button for background subtraction instead of remove hotspot.
#TODO: make an interactive masking option for alignment reasons. bring back equalize function.

# class Stream(QtCore.QObject):
#     newText = QtCore.pyqtSignal(str)
#     def write(self, text):
#         self.newText.emit(str(text))
class ImageProcessWidget(QtWidgets.QWidget):

    sliderChangedSig = pyqtSignal(int, name='sliderChangedSig')
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')
    thetaChangedSig = pyqtSignal(int, np.ndarray, name='thetaChangedSig')
    fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")
    alignmentChangedSig = pyqtSignal(np.ndarray, np.ndarray, name="alignmentChangedSig")
    ySizeChangedSig = pyqtSignal(int, name='ySizeChangedSig')
    xSizeChangedSig = pyqtSignal(int, name='xSizeChangedSig')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    refreshSig = pyqtSignal(name='refreshSig')
    padSig = pyqtSignal(int, int, name="padSig")



    def __init__(self, parent):
        super(ImageProcessWidget, self).__init__()
        self.parent = parent
        self.thetas = []
        self.initUI()
        sys.stdout = xrftomo.gui.Stream(newText=self.parent.onUpdateText)


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

        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.cropBtn.clicked.connect(self.cut_params)
        self.ViewControl.mask.clicked.connect(self.mask_params)
        self.ViewControl.padBtn.clicked.connect(self.ViewControl.padding_options.show)
        self.ViewControl.run_padding.clicked.connect(self.pad_params)
        self.ViewControl.deleteProjection.clicked.connect(self.exclude_params)
        self.ViewControl.rm_hotspot.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.normalize.clicked.connect(self.normalize_params)
        self.ViewControl.downsample.clicked.connect(self.downsample_params)
        self.ViewControl.invert.clicked.connect(self.invert_params)

        self.imageView.keyPressSig.connect(self.keyProcess)
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
        self.updatePlot(self.data[element, index, ::-1, :], self.data[element])
        self.imageView.projView.setImage(self.data[element, index, ::-1, :], border='w')

    def updatePlot(self,img,stack):
        yrange = img.shape[0]
        xrange = img.shape[1]

        ploth = np.sum(img, axis=0)*xrange*0.2/(np.sum(stack,axis=1).max())
        plotv = np.sum(img, axis=1)*yrange*0.2/(np.sum(stack,axis=2).max())
        dy = 0.1
        plot_dx = np.gradient(ploth, dy)
        ploty_dx = plot_dx*yrange*0.1/plot_dx.max()

        dx = 0.1
        plot_dy = np.gradient(plotv, dx)**2
        plot_dy = self.relax_edge(plot_dy,3)

        try: 
            ploty_dy = plot_dy*xrange*0.1/plot_dy.max()
        except:
            ploty_dy = plot_dy*xrange*0.1


        self.imageView.p1.clearPlots()
        self.imageView.p1.plot(ploth, pen=pyqtgraph.mkPen(color='b'))
        self.imageView.p1.plot(ploty_dx, pen=pyqtgraph.mkPen(color='c'))

        self.imageView.p1.plot(plotv, np.arange(len(plotv)), pen=pyqtgraph.mkPen(color='r'))
        self.imageView.p1.plot(ploty_dy, np.arange(len(plot_dy)), pen=pyqtgraph.mkPen(color='y'))

        self.imageView.p1.setXRange(int(-xrange*0.1), xrange, padding=0)
        self.imageView.p1.setYRange(int(-yrange*0.1), yrange, padding=0)

    def relax_edge(self, arr, N):
        # tail_head = int(len(arr)*0.1)
        # new_arr = arr[tail_head:-tail_head]

        if len(arr.shape) >=2:
            new_arr = np.zeros_like(arr)
            for i in range(new_arr.shape[0]):
                for j in range(N):
                    new_arr[i] = self.trim_edge(arr[i])
                new_arr[i][-1]=0
                new_arr[i][0]=0

            return new_arr
        else:
            #TODO: check array size, if tail_head exceeds bounds, raise exception.
            for i in range(N):
                new_arr = self.trim_edge(arr)
            return new_arr

    def trim_edge(self, arr):
        arr_max = abs(arr.max())
        arr_length = arr.shape[0]
        for i in range(1, arr_length):
            l_diff = abs(arr[i]-arr[i-1])
            r_diff = abs(arr[-i-1] - arr[-i])
            arr[-1] = 0
            arr[0] = 0
            if l_diff > arr_max*0.50:
                arr[i] = 0
                break
            if r_diff >= arr_max*0.50:
                arr[-i-1] = 0
                break
        return arr

    def updateElementSlot(self, element, projection = None):
        if projection == None:
           projection =  self.sld.value()
        # self.imageView.projView.setImage(self.data[element, projection, :, :], border='w')
        self.updatePlot(self.data[element, projection, ::-1, :], self.data[element])
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
        self.updatePlot(self.data[element, index, ::-1, :], self.data[element])
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
        # hs_group = self.ViewControl.hs_group.currentIndex()
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

    def filcen_params(self):
        element = self.ViewControl.combo1.currentIndex()
        data = self.data
        data[element] = self.actions.filter(data[element], bpfilter=3)
        self.dataChangedSig.emit(data)
        pass

    def mask_params(self):
        data = self.data
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        threshold = self.ViewControl.mask_lndt.text()
        try:
            threshold = eval(threshold)
            if threshold <0 or threshold>100:
                print("threshold outside range: 0-100")
                return
            data[element] = self.actions.mask_data(data, element, threshold)
            self.dataChangedSig.emit(data)

        except Exception as error:
            print("mask_params error: ", error)
        return

    def downsample_params(self):
        data = self.data[:,:,::2,::2]
        self.dataChangedSig.emit(data)
        return

    def background_value_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.background_value(img)

    def invert_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        data = self.actions.invert(data, element)
        self.dataChangedSig.emit(data)

    def cut_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.actions.cut(self.data, x_pos, y_pos, x_size, y_size)
        self.ySizeChangedSig.emit(y_size)
        self.xSizeChangedSig.emit(x_size)
        self.dataChangedSig.emit(data)
        #TODO: move crosshairs an ROI to crop region after crop
        self.imageView.p1.items[2].setValue(0)
        self.imageView.p1.items[3].setValue(0)
        self.imageView.ROI.setPos([0, 0], finish=False)
        self.parent.prevTab = 1
        self.refreshSig.emit()

    def analysis_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.noise_analysis(img)

    def bounding_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        img = data[element, projection, :,:]
        self.actions.bounding_analysis(img)
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

        self.padSig.emit(padding_x,padding_y)
        self.dataChangedSig.emit(data)
        self.ySizeChangedSig.emit(self.data.shape[2])
        self.xSizeChangedSig.emit(self.data.shape[3])
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

    def normalize_params(self):
        data = self.data
        sino = self.parent.sinogramWidget.sinogramData[::10]
        data = self.actions.normalize(data, sino)
        self.dataChangedSig.emit(data)
        return