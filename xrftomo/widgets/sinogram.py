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

import xrftomo
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
import pyqtgraph
import numpy as np
import scipy.ndimage

class SinogramWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')
    alignmentChangedSig = pyqtSignal(np.ndarray, np.ndarray, name="alignmentChangedSig")
    sinoChangedSig = pyqtSignal(np.ndarray, name="sinoChangedSig")
    restoreSig = pyqtSignal(name="restoreSig")

    def __init__(self):
        super(SinogramWidget, self).__init__()
        self.initUI()

    def initUI(self):
        button1size = 250       #long button (1 column)
        button2size = 123     #mid button (2 column)
        button33size = 78.3
        button3size = 73.3      #small button (almost third)
        button4size = 59     #textbox size (less than a third)
        self.ViewControl = xrftomo.SinogramControlsWidget()
        self.sinoView = xrftomo.SinogramView()
        self.imageView = xrftomo.ImageView()
        # self.diffView = xrftomo.differenceView()
        self.actions = xrftomo.SinogramActions()
        self.x_padding_hist = [0]
        self.y_padding_hist = [0]
        self.sub_pixel_shift = 1
        self.fnames = None

        self.view_options = QtWidgets.QComboBox()
        self.view_options.setFixedWidth(button2size)
        for j in ["sinogram view", "projection view"]:
            self.view_options.addItem(j)

        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)    #sino slider
        self.sld2 = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)   #image slider
        self.sld3 = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)   #image slider
        self.sld.setValue(1)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.lcd2 = QtWidgets.QLCDNumber(self)
        self.lcd3 = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        self.hist.setImageItem(self.sinoView.projView)
        self.hist.setImageItem(self.imageView.projView)
        # self.hist.setImageItem(self.diffView.projView)
        self.data = np.ndarray(shape=(1, 10, 10, 10), dtype=float)
        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
        self.data = None
        self.sinogramData = None

        self.ViewControl.btn1.clicked.connect(self.ViewControl.com_options.show)
        self.ViewControl.run_com.clicked.connect(self.centerOfMass_params)
        self.ViewControl.xcorsino.clicked.connect(self.xcorsino_params)
        self.ViewControl.opflow.clicked.connect(self.opFlow_params)
        self.ViewControl.fitPeaks.clicked.connect(self.fitPeaks_params)
        self.ViewControl.btn2.clicked.connect(self.crossCorrelate_params)
        self.ViewControl.xcorry.clicked.connect(self.xcorry_params)
        self.ViewControl.xcorrdy.clicked.connect(self.xcorrdy_params)
        self.ViewControl.btn3.clicked.connect(self.phaseCorrelate_params)
        self.ViewControl.btn6.clicked.connect(self.ViewControl.iter_parameters.show)
        self.ViewControl.run_iter_align.clicked.connect(self.iter_align_params)
        self.ViewControl.btn7.clicked.connect(self.alignFromText2_params)
        self.ViewControl.btn5.clicked.connect(self.ViewControl.move2edge.show)
        self.ViewControl.run_move2edge.clicked.connect(self.move2edge_params)
        self.ViewControl.btn9.clicked.connect(self.ViewControl.sino_manip.show)
        self.ViewControl.run_sino_adjust.clicked.connect(self.adjust_sino_params)
        self.ViewControl.move2center.clicked.connect(self.move2center_params)
        self.ViewControl.find_center_1.clicked.connect(self.center_tomopy_params)
        self.ViewControl.find_center_2.clicked.connect(self.center_Vacek_params)
        self.ViewControl.center.clicked.connect(self.ViewControl.center_parameters.show)
        self.ViewControl.center.clicked.connect(self.updateCenterFindParameters)
        self.ViewControl.rot_axis.clicked.connect(self.rot_axis_params)
        self.ViewControl.freq_sld.sliderReleased.connect(self.sinoCurvesldChanged)
        self.ViewControl.amp_sld.sliderReleased.connect(self.sinoCurvesldChanged)
        self.ViewControl.phase_sld.sliderReleased.connect(self.sinoCurvesldChanged)
        self.ViewControl.offst_sld.sliderReleased.connect(self.sinoCurvesldChanged)
        self.sld.valueChanged.connect(self.sinoSliderChanged)
        self.sld2.valueChanged.connect(self.imageSliderChanged)
        self.sld3.valueChanged.connect(self.diffSliderChanged)
        self.sinoView.keyPressSig.connect(self.shiftEvent_params)
        self.imageView.mousePressSig.connect(self.hotspot_event)
        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.view_options.currentIndexChanged.connect(self.display)

        self.ViewControl.amp.returnPressed.connect(self.updateSinoPlot)
        self.ViewControl.freq.returnPressed.connect(self.updateSinoPlot)
        self.ViewControl.phase.returnPressed.connect(self.updateSinoPlot)
        self.ViewControl.offst.returnPressed.connect(self.updateSinoPlot)

        self.ViewControl.amp.returnPressed.connect(self.updateSinoPlot)
        self.ViewControl.freq.returnPressed.connect(self.updateSinoPlot)
        self.ViewControl.phase.returnPressed.connect(self.updateSinoPlot)
        self.ViewControl.offst.returnPressed.connect(self.updateSinoPlot)

        self.ViewControl.set2line.clicked.connect(self.fit_curve)

        self.ViewControl.fit_line.clicked.connect(self.fitLine_params)
        self.ViewControl.fit_sine.clicked.connect(self.fitSine_params)
        self.ViewControl.fit_y.clicked.connect(self.fitY_params)
        self.ViewControl.clear_data.clicked.connect(self.clrHotspot_params)

        # self.diffView.keyPressSig.connect(self.keyProcess)
        self.imageView.keyPressSig.connect(self.keyProcess)

        self.ViewControl.fit_line.setEnabled(False)
        self.ViewControl.fit_sine.setEnabled(False)
        self.ViewControl.fit_y.setEnabled(False)
        self.ViewControl.clear_data.setEnabled(False)

        self.stack1 = QtWidgets.QWidget()
        self.stack2 = QtWidgets.QWidget()
        self.stack3 = QtWidgets.QWidget()

        self.stack1UI()
        self.stack2UI()
        self.stack3UI()

        self.Stack = QtWidgets.QStackedWidget (self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        self.Stack.addWidget(self.stack3)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addWidget(self.view_options)
        vb1.addWidget(self.Stack)
        vb1.maximumSize()

        sinoBox = QtWidgets.QHBoxLayout()
        sinoBox.addWidget(self.ViewControl)
        sinoBox.addLayout(vb1)
        sinoBox.addWidget(self.hist,10)

        self.setLayout(sinoBox)

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

        self.updateSinoPlot()

    def stack1UI(self):
        lbl = QtWidgets.QLabel('Row y')
        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(lbl)
        hb0.addWidget(self.lcd)
        hb0.addWidget(self.sld)

        vb = QtWidgets.QVBoxLayout()
        vb.addWidget(self.sinoView)
        vb.addLayout(hb0)

        self.stack1.setLayout(vb)

    def stack2UI(self):
        lbl = QtWidgets.QLabel('Angle')
        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(lbl)
        hb0.addWidget(self.lcd2)
        hb0.addWidget(self.sld2)

        vb = QtWidgets.QVBoxLayout()
        vb.addWidget(self.imageView)
        vb.addLayout(hb0)

        self.stack2.setLayout(vb)


    def stack3UI(self):

        lbl = QtWidgets.QLabel('Angle')
        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(lbl)
        hb0.addWidget(self.lcd3)
        hb0.addWidget(self.sld3)

        vb = QtWidgets.QVBoxLayout()
        # vb.addWidget(self.diffView)
        vb.addLayout(hb0)

        self.stack3.setLayout(vb)

    def display(self,i):
        self.Stack.setCurrentIndex(i)

        # if i == 1:

        #     self.ViewControl.hotspot_mode_chbx.setVisible(True)
        #     self.ViewControl.hotspot_lbl.setVisible(True)
        #     self.ViewControl.combo3.setVisible(True)
        #     self.ViewControl.fit_line.setVisible(True)
        #     self.ViewControl.fit_y.setVisible(True)
        #     self.ViewControl.clear_data.setVisible(True)
        # else:
        self.ViewControl.hotspot_mode_chbx.setVisible(False)
        self.ViewControl.hotspot_lbl.setVisible(False)
        self.ViewControl.combo3.setVisible(False)
        self.ViewControl.fit_line.setVisible(False)
        self.ViewControl.fit_y.setVisible(False)
        self.ViewControl.clear_data.setVisible(False)
        #change slider range and label here depending on i

    def keyProcess(self, command):
        index = self.sld3.value()
        data = self.data
        sps = self.sub_pixel_shift
        if command == 'left':
            self.x_shifts[index] -= sps
            data = self.actions.shiftProjection(self.data, -sps, 0, index)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            return
        if command == 'right':
            self.x_shifts[index] +=sps
            data = self.actions.shiftProjection(self.data, sps, 0, index)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            return
        if command == 'up':
            self.y_shifts[index] +=sps
            data = self.actions.shiftProjection(self.data, 0, -sps, index)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            return
        if command == 'down':
            self.y_shifts[index] -=sps
            data = self.actions.shiftProjection(self.data, 0, sps, index)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        if command == 'shiftLeft':
            self.x_shifts -=sps
            data = self.actions.shiftStack(self.data, -sps, 0)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            return
        if command == 'shiftRight':
            self.x_shifts +=sps
            data = self.actions.shiftStack(self.data, sps, 0)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            return
        if command == 'shiftUp':
            self.y_shifts +=sps
            data = self.actions.shiftStack(self.data, 0, -sps)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            return
        if command == 'shiftDown':
            self.y_shifts -=sps
            data = self.actions.shiftStack(self.data, 0, sps)
            self.dataChangedSig.emit(data)
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
            return
        if command == "Next":
            self.hotspot_event(1)
            return


    def showImgProcess(self):
        self.posMat = np.zeros((5,int(self.data.shape[1]),2))
        self.imageView.hotSpotNumb = 0
        num_projections  = self.data.shape[1]
        self.sld2.setRange(0, num_projections - 1)

    def showSinoCurve(self):
        self.ViewControl.freq_sld.setRange(0, 200)
        self.ViewControl.amp_sld.setRange(0, 200)
        self.ViewControl.phase_sld.setRange(0, 200)
        self.ViewControl.offst_sld.setRange(0,200)

    def showDiffProcess(self):
        num_projections  = self.data.shape[1]
        self.sld3.setRange(0, num_projections - 1)

    def imageSliderChanged(self):
        index = self.sld2.value()
        self.updateSliderSlot(index)

    def sinoCurvesldChanged(self):
        #sld current index
        freq_idx = self.ViewControl.freq_sld.value()
        amp_idx = self.ViewControl.amp_sld.value()
        phase_idx = self.ViewControl.phase_sld.value()
        offst_idx = self.ViewControl.offst_sld.value()

        #array values
        #TODO: create array of values for each slider, set each QlineEdit to the indexed value.
        freq_arr = np.linspace(0, 2, 201)
        amp_arr = np.linspace(0, self.data.shape[3], self.data.shape[3]+1)
        self.ViewControl.amp_sld.setRange(0, self.data.shape[3]+1)

        phase_arr = np.linspace(-np.pi, np.pi, 201)
        offst_arr = np.linspace(-self.data.shape[3], self.data.shape[3], 201)

        #TODO: set Qlineedit to value[index]
        self.ViewControl.freq.setText(str(round(freq_arr[freq_idx],3)))
        self.ViewControl.amp.setText(str(round(amp_arr[amp_idx],3)))
        self.ViewControl.phase.setText(str(round(phase_arr[phase_idx],3)))
        self.ViewControl.offst.setText(str(round(offst_arr[offst_idx],3)))
        self.updateSinoPlot()
        return

    def sinoCurveParamsChanged(self):
        #sld current index
        freq_idx = self.ViewControl.freq_sld.value()
        amp_idx = self.ViewControl.amp_sld.value()
        phase_idx = self.ViewControl.phase_sld.value()
        offst_idx = self.ViewControl.offst_sld.value()

        # array values
        # TODO: create array of values for each slider, set each QlineEdit to the indexed value.
        freq_arr = np.linspace(0, 2, 201)
        amp_arr = np.linspace(0, self.data.shape[3], self.data.shape[3] + 1)
        self.ViewControl.amp_sld.setRange(0, self.data.shape[3] + 1)

        phase_arr = np.linspace(-np.pi, np.pi, 201)
        offst_arr = np.linspace(-self.data.shape[3], self.data.shape[3], 201)

        # TODO: set Qlineedit to value[index]
        self.ViewControl.freq.setText(str(round(freq_arr[freq_idx], 3)))
        self.ViewControl.amp.setText(str(round(amp_arr[amp_idx], 3)))
        self.ViewControl.phase.setText(str(round(phase_arr[phase_idx], 3)))
        self.ViewControl.offst.setText(str(round(offst_arr[offst_idx], 3)))
        self.updateSinoPlot()
        return

    def diffSliderChanged(self):
        index = self.sld3.value()
        self.updateDiffSliderSlot(index)

    def update_filenames(self, fnames):
        self.fnames = fnames

    def updateDiffSliderSlot(self, index):
        if len(self.thetas) == 0:
            return
        angle = round(self.thetas[index],3)
        self.lcd3.display(angle)
        self.sld3.setValue(index)
        # self.updateDiffImage(index)


    def updateSinoPlot(self, thetas= None):

        try:
            thetas = self.thetas
        except:
            thetas = np.linspace(-np.pi, np.pi, 10)
            middl = 0
        else:
            thetas = self.thetas
            middl = self.sinogramData.shape[1] // 2

        try:
            amp = eval(self.ViewControl.amp.text())
            phase = eval(self.ViewControl.phase.text())
            freq = eval(self.ViewControl.freq.text())
            offst = eval(self.ViewControl.offst.text())
        except:
            print("eval enter int or float")


        self.curve = amp*np.sin((freq*np.array(thetas) * np.pi / 180) - phase ) + middl + offst
        self.sinoView.p1.clearPlots()
        self.sinoView.p1.plot(thetas,self.curve, pen=pyqtgraph.mkPen(color='c'))

        
    def fit_curve(self):
        try:
            data = self.data.copy()
            thetas = self.thetas
            curve = self.curve
            middl = self.sinogramData.shape[1] // 2
            shifts = middl - curve
            x_shifts, y_shifts = self.actions.validate_alignment(data, shifts, self.y_shifts)

            for i in range(data.shape[0]):
                for j in range(len(x_shifts)):
                    data[i,j] = scipy.ndimage.shift(data[i,j], (0,x_shifts[j]), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)
            self.alignmentChangedSig.emit(self.x_shifts + shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
            return
        except:
            return
        pass


    def updateDiffImage(self, index):
        element = self.ViewControl.combo1.currentIndex()
        x_index = int(self.data.shape[3] * 0.1)
        y_index = int(self.data.shape[2]* 0.1)

        position = [0.0, 0.25, 0.4, 0.6, 0.75, 1.0]
        colors = [[64, 0, 0, 255], [255, 0, 0, 255], [255, 255, 255, 255], [255, 255, 255, 255], [0, 0, 255, 255], [0, 0, 64, 255]]
        bi_polar_color_map = pyqtgraph.ColorMap(position, colors)
        lookup_table = bi_polar_color_map.getLookupTable(0.0, 1.0, 256)


        # if index < self.data.shape[1]-1:
        #     img = self.data[element, index] - self.data[element, index+1]
        #     img = img[y_index:-y_index, x_index:-x_index]
        # else:
        #     img = self.data[element, index] - self.data[element, 0]
        #     img = img[x_index:-x_index, y_index:-y_index]

        if index < self.data.shape[1]-1:
            img = self.data[element, index]/2 + self.data[element, index+1]/2
            img = img[y_index:-y_index, x_index:-x_index]
        else:
            img = self.data[element, index]/2 + self.data[element, 0]/2
            img = img[x_index:-x_index, y_index:-y_index]

        # self.diffView.projView.setImage(img, border='w')
        # self.diffView.projView.setLookupTable(lookup_table)


    def updateSliderSlot(self, index):
        if len(self.thetas) == 0:
            return
        angle = round(self.thetas[index],3)
        element = self.ViewControl.combo1.currentIndex()
        self.lcd2.display(angle)
        self.sld2.setValue(index)
        # self.imageView.projView.setImage(self.data[element, index, :, :], border='w')
        self.imageView.projView.setImage(self.data[element, index, ::-1, :], border='w')

    def updateImgSldRange(self, index, thetas):
        element = self.ViewControl.combo1.currentIndex()
        self.sld2.setRange(0, len(self.thetas) -1)
        self.lcd2.display(thetas[index])
        self.sld2.setValue(index)
        self.imageChanged()
        self.posMat = np.zeros((5,int(self.data.shape[1]), 2))

    def updateDiffSldRange(self, index, thetas):
        element = self.ViewControl.combo1.currentIndex()
        self.sld3.setRange(0, len(self.thetas) -1)
        self.lcd3.display(thetas[index])
        self.sld3.setValue(index)
        self.imageChanged()

    def showSinogram(self):
        '''
        loads sinogram tabS
        '''

        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers

        self.ViewControl.combo1.clear()
        for j in self.elements:
            self.ViewControl.combo1.addItem(j)

        self.actions = xrftomo.SinogramActions()
        self.elementChanged()
        self.sld.setRange(1, self.data.shape[2])
        self.lcd.display(1)





    def sinoSliderChanged(self):
        index = self.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.lcd.display(index)
        self.sld.setValue(index)
        self.sinogram(element)
        self.show()

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = 0
        self.updateElementSlot(element)
        self.updateImgElementSlot(element,self.sld2.value())
        self.elementChangedSig.emit(element, projection)

    def imageChanged(self):
        index = self.sld2.value()
        index3 = self.sld3.value()
        element = self.ViewControl.combo1.currentIndex()
        self.sinogram(element)
        # self.imageView.projView.setImage(self.data[element, index, :, :], border='w')
        self.imageView.projView.setImage(self.data[element, index, ::-1, :], border='w')
        # self.updateDiffImage(index3)

    def ySizeChanged(self, ySize):
        self.sld.setRange(1, ySize)
        self.sld.setValue(1)
        self.lcd.display(1)

    def updateElementSlot(self, element):
        self.sinogram(element)
        self.ViewControl.combo1.setCurrentIndex(element)

    def updateImgElementSlot(self, element, projection = None):
        try:
            if projection == None:
                projection =  self.sld.value()
            # self.imageView.projView.setImage(self.data[element, projection, :, :], border='w')
            #TODO: line below errors out when loading another dataset, somethin is not getting cleared and reinitialized properly.
            self.imageView.projView.setImage(self.data[element, projection, ::-1, :], border='w')
        except TypeError:
            return

    def hotSpotSetChanged(self):
        self.imageView.hotSpotSetNumb = self.ViewControl.combo3.currentIndex()
        # self.actions.saveHotSpotPos()

    def fitLine_params(self):
        element, x_size, y_size, hs_group, posMat, data = self.get_params_imgView()
        data, x_shifts, y_shifts = self.actions.hotspot2line(element, x_size, y_size, hs_group, posMat, data)
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts - y_shifts)
        self.ViewControl.clear_data.setEnabled(True)
        return

    def fitSine_params(self):
        element, x_size, y_size, hs_group, posMat, data = self.get_params_imgView()
        thetas = self.thetas
        data, x_shifts, y_shifts = self.actions.hotspot2sine(element, x_size, y_size, hs_group, posMat, data, thetas)
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts +y_shifts)
        self.ViewControl.clear_data.setEnabled(True)
        return

    def fitY_params(self):
        element, x_size, y_size, hs_group, posMat, data = self.get_params_imgView()
        data, y_shifts = self.actions.setY(element, x_size, y_size, hs_group, posMat, data)
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts + y_shifts)
        self.ViewControl.clear_data.setEnabled(True)
        return

    def hotspot_event(self, mouse_button):
        if not self.ViewControl.hotspot_mode_chbx.isChecked():
            return
        else:
            pass

        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.sld2.value()
        x_pos = self.imageView.x_pos
        y_pos = self.imageView.y_pos

        if mouse_button == 1:
            self.posMat[int(hs_group), int(hs_number)-1] = [x_pos, y_pos]
            if hs_number < self.posMat.shape[1]:
                print("Total projections", self.posMat.shape[1], "current position", hs_number+1, "group number", hs_group + 1)
                hs_number += 1
                if hs_number < self.posMat.shape[1]:
                    self.sld2.setValue(self.sld2.value() + 1)
                    self.imageSliderChanged()
                else:
                    self.sld2.setValue(self.data.shape[1])
                    self.imageSliderChanged()
                    print("This is the last projection")
        self.ViewControl.clear_data.setEnabled(True)
        self.ViewControl.fit_y.setEnabled(True)
        self.ViewControl.fit_sine.setEnabled(True)
        self.ViewControl.fit_line.setEnabled(True)
        if mouse_button == 2:
            self.posMat[int(hs_group), int(hs_number)-1] = [0, 0]
            if hs_number < self.posMat.shape[1]:
                hs_number += 1
                self.sld2.setValue(self.sld2.value() + 1)
                self.imageSliderChanged()

    def clrHotspot_params(self):
        self.posMat = self.actions.clrHotspot(self.posMat)
        self.ViewControl.clear_data.setEnabled(False)
        self.ViewControl.fit_y.setEnabled(False)
        self.ViewControl.fit_sine.setEnabled(False)
        self.ViewControl.fit_line.setEnabled(False)

    def rot_axis_params(self):
        data = self.data
        num_projections = data.shape[1]
        thetas = self.thetas
        rAxis_pos = self.imageView.cross_pos_x
        center = data.shape[3]//2
        theta_pos = self.lcd2.value()
        shift_arr = self.actions.move_rot_axis(thetas, center, rAxis_pos, theta_pos)
        shift_arr = np.round(shift_arr)

        for i in range(num_projections):
            data[:,i] = np.roll(data[:,i],int(shift_arr[i]),axis=2)
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + shift_arr, self.y_shifts)
        return

    def center_tomopy_params(self):        
        valid = self.ViewControl.validate_move2center_parameters()
        if not valid:
            return
        element, row, data, thetas = self.get_params()

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
        self.ViewControl.rot_axis.setDisabled(False)

    def center_Vacek_params(self):
        element, row, data, thetas = self.get_params()
        data = self.data
        thetasum = np.sum(self.data[element], axis=1)
        
        valid = self.ViewControl.validate_move2center_parameters()
        if not valid:
            return

        limit = self.ViewControl.limit_textbox.text()
        center_offset = self.actions.rot_center3(thetasum, ave_mode = 'Median', limit = None, return_all = False)
        center = self.data.shape[3]//2 - center_offset
        center_int = np.round(center_offset)
        self.ViewControl.center_1.setText("center: {}".format(center))
        self.ViewControl.center_2.setText("center: {}".format(center))
        self.ViewControl.rot_axis.setDisabled(False)

    def move2center_params(self):
        data = self.data
        rot_center = int(np.round(float(self.ViewControl.center_1.text().split()[1])))
        x_shifts = data.shape[3]//2 - rot_center

        if x_shifts !=0:
            data = self.actions.shiftStack(data, x_shifts, 0)
            self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts)
            self.dataChangedSig.emit(data)
        return

    def updateCenterFindParameters(self):
        if self.ViewControl.init_textbox.text() == "-1":
            self.ViewControl.init_textbox.setText(str(self.data.shape[3]//2))
        if self.ViewControl.slice_textbox.text() == "-1":
            self.ViewControl.slice_textbox.setText(str(self.data.shape[2]//2))
        if self.ViewControl.limit_textbox.text() == "-1":
            self.ViewControl.limit_textbox.setText("1")
            
    def sinogram(self, element):
        '''
        load variables and image for sinogram window

        Variables
        -----------
        self.thickness: number
              thickness of y of each projections
        self.sino.combo.currentIndexsinogram((): number
              indicates the index of the element
        self.data: ndarray
              4d tomographic data [element, projections, y,x]
        '''

        if element == -1: # escape if element == -1.
            return

        try: #TODO: fails when loading new dataset, be sure to clear absolutely everything or raise exception
            sinodata = self.data[element, :, :, :]
        except TypeError:
            return
        self.sinogramData = np.zeros([sinodata.shape[0] * 10, sinodata.shape[2]], dtype=np.float32)
        num_projections = self.data.shape[1]

        try: #TODO: fails when cropping
            for i in range(num_projections):
                self.sinogramData[i * 10:(i + 1) * 10, :] = sinodata[i, self.sld.value()-1, :]
        except IndexError:
            return
        self.sinogramData[np.isinf(self.sinogramData)] = 0.001
        self.sinoView.projView.setImage(self.sinogramData, border='w')
        if len(self.thetas) > 0:
            self.sinoView.projView.setRect(QtCore.QRect(round(self.thetas[0]), 0, round(self.thetas[-1])- round(self.thetas[0]), self.sinogramData.shape[1]))
        self.sinoChangedSig.emit(self.sinogramData)
        return

    def centerOfMass_params(self):
        #TODO: if roi checked, get partial data and get shifts based on partial data, then adjust full data based on shifts
        #TODO: alignment methods should just output shifts, and nother function to apply shifts should be separate
        element, row, data, thetas = self.get_params()
        wcom = self.ViewControl.weighted_com_checkbox.isChecked()
        shiftXY = self.ViewControl.shiftXY_checkbox.isChecked()
        if self.ViewControl.roi.isChecked():
            roi_data = self.get_roi_data(data)
            roi_data , x_shifts, y_shifts = self.actions.runCenterOfMass(element, roi_data, thetas, wcom, shiftXY)
            data = self.actions.shift_all(data,x_shifts,y_shifts)
        else:
            data, x_shifts, y_shifts = self.actions.runCenterOfMass(element, data, thetas, wcom, shiftXY)

        x_shifts = self.actions.discontinuity_check(data,x_shifts,40)
        x_shifts, y_shifts = self.actions.validate_alignment(data, x_shifts, y_shifts)

        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts + y_shifts)
        return

    def get_roi_data(self, data):
        x_pos = self.imageView.x_pos
        y_pos = self.imageView.y_pos
        x_size = self.imageView.xSize
        y_size = self.imageView.ySize
        frame_height = data.shape[2]
        y_end = int(round(frame_height - y_pos))
        y_start = int(round(frame_height-y_pos-y_size))
        x_start = int(round(x_pos))
        x_end = int(round(x_pos) + x_size)
        img = np.copy(data)
        img = img[:, :, y_start:y_end, x_start: x_end]
        return img
    def opFlow_params(self):
        element, row, data, thetas = self.get_params()
        data = self.actions.runOpFlow(element, data)
        self.dataChangedSig.emit(data)
        return

    def fitPeaks_params(self):
        #TODO: if roi checked
        element, row, data, thetas = self.get_params()

        if self.ViewControl.roi.isChecked():
            roi_data = self.get_roi_data(data)
            roi_data , x_shifts, y_shifts = self.actions.runFitPeaks(element, roi_data)
            data = self.actions.shift_all(data,x_shifts,y_shifts)
        else:
            data, x_shifts, y_shifts = self.actions.runFitPeaks(element, data)

        #TODO: add a function to check discontinuities in aligment values spcifically for xcor.
        x_shifts = self.actions.discontinuity_check(data,x_shifts,data.shape[3]//2)
        #TODO: add a post-alignment function to validate shifts based on image size
        x_shifts, y_shifts = self.actions.validate_alignment(data, x_shifts, y_shifts)

        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts + y_shifts)
        pass


    def shiftEvent_params(self, shift_dir, col_number):
        sinoData = self.sinogramData
        data = self.data
        thetas = self.thetas

        data, self.sinogramData = self.actions.shift(sinoData, data, shift_dir, col_number)
        self.x_shifts[col_number] += shift_dir
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts)
        return

    def crossCorrelate_params(self):
        #TODO: if roi checked
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        if self.ViewControl.roi.isChecked():
            roi_data = self.get_roi_data(data)
            roi_data , x_shifts, y_shifts = self.actions.crossCorrelate2(element, roi_data)
            data = self.actions.shift_all(data,x_shifts,y_shifts)
        else:
            data, x_shifts, y_shifts = self.actions.crossCorrelate2(element, data)

        #TODO: add a function to check discontinuities in aligment values spcifically for xcor.
        x_shifts = self.actions.discontinuity_check(data,x_shifts,40)
        #TODO: add a post-alignment function to validate shifts based on image size
        x_shifts, y_shifts = self.actions.validate_alignment(data, x_shifts, y_shifts)

        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts + y_shifts)
        return

    def xcorrdy_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        if self.ViewControl.roi.isChecked():
            roi_data = self.get_roi_data(data)
            roi_data, x_shifts, y_shifts = self.actions.xcor_dysum(element, roi_data)
            data = self.actions.shift_all(data,x_shifts,y_shifts)
        else:
            data, x_shifts, y_shifts = self.actions.xcor_dysum(element, data)

        data, x_shifts, y_shifts = self.actions.xcor_dysum(element, data)
        x_shifts = self.actions.discontinuity_check(data,x_shifts,data.shape[3]//2)
        x_shifts, y_shifts = self.actions.validate_alignment(data, x_shifts, y_shifts)

        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts + y_shifts)
        return

    def xcorry_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()

        if self.ViewControl.roi.isChecked():
            roi_data = self.get_roi_data(data)
            roi_data , x_shifts, y_shifts = self.actions.xcor_ysum(element, roi_data)
            data = self.actions.shift_all(data,x_shifts,y_shifts)
        else:
            data, x_shifts, y_shifts = self.actions.xcor_ysum(element, data)

        x_shifts = self.actions.discontinuity_check(data,x_shifts,data.shape[3]//2)
        x_shifts, y_shifts = self.actions.validate_alignment(data, x_shifts, y_shifts)

        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts + y_shifts)
        return

    def xcorsino_params(self):
        layer = self.sld.value()-1
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        if self.ViewControl.roi.isChecked():
            roi_data = self.get_roi_data(data)
            roi_data , x_shifts = self.actions.xcor_sino(element, layer, roi_data)
            data = self.actions.shift_all(data,x_shifts)
        else:
            data, x_shifts = self.actions.xcor_sino(element, layer, data)

        x_shifts = self.actions.validate_alignment(data, x_shifts)
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts)
        pass

    def phaseCorrelate_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        data, x_shifts, y_shifts = self.actions.phaseCorrelate(element, data)
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts+x_shifts, self.y_shifts+y_shifts)
        return

    def sine_fitting_params(self):
        #TODO: sine fitting function
        "https://stackoverflow.com/questions/16716302/how-do-i-fit-a-sine-curve-to-my-data-with-pylab-and-numpy"
        pass
    def move2edge_params(self):
        #TODO: if roi checked

        data = self.data
        element = self.ViewControl.combo1.currentIndex()

        valid = self.ViewControl.validate_parameters()
        if not valid:
            return

        if self.ViewControl.bottom_checkbox.isChecked():
            loc=0
        else: 
            loc=1

        threshold = int(self.ViewControl.threshold_textbox.text())

        if self.ViewControl.roi.isChecked():
            roi_data = self.get_roi_data(data)
            y_shifts, roi_data = self.actions.align2edge(element, roi_data, loc, threshold)
            data = self.actions.shift_all(data,np.zeros_like(y_shifts),y_shifts)

        else:
            y_shifts, data = self.actions.align2edge(element, data, loc, threshold)

        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts+y_shifts)
        return

        
    def adjust_sino_params(self):
        sinogramData = self.sinogramData
        data = self.data
        element = self.ViewControl.combo1.currentIndex()

        valid = self.ViewControl.validate_parameters()
        if not valid:
            return
        shift = int(self.ViewControl.shift_textbox.text())
        slope = int(self.ViewControl.slope_adjust_textbox.text())
            
        x_shifts, data, self.sinogramData = self.actions.slope_adjust(sinogramData, data, shift, slope)
        x_shifts, dummy = self.actions.validate_alignment(data,x_shifts,self.y_shifts)
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts+x_shifts, self.y_shifts)
        return

    # def matchTermplate_params(self):
    #     self.actions.matchTemmplate()
    #     pass

    def iter_align_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        #TODO: Thetas must be in radians
        thetas = self.thetas
        valid = self.ViewControl.validate_parameters()
        if not valid:
            return
            
        if self.ViewControl.center_textbox.text() == "":
            center = None
        else:
            center = int(self.ViewControl.center_textbox.text())
            if center >0 and center < data.shape[3]:
                pass
            else:
                self.ViewControl.center_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                return
        iters = int(self.ViewControl.iter_textbox.text())
        blur_bool = self.ViewControl.blur_checkbox.isChecked()
        save_bool = self.ViewControl.save_checkbox.isChecked()
        debug_bool = self.ViewControl.debug_checkbox.isChecked()
        padX = int(self.ViewControl.paddingX_textbox.text())
        padY = int(self.ViewControl.paddingY_textbox.text())
        pad = (padX,padY)
        algorithm = self.ViewControl.algorithm.currentText()
        upsample_factor = int(self.ViewControl.upsample_factor_textbox.text())
        
        if self.ViewControl.blur_checkbox.isChecked():
            rin = float(self.ViewControl.inner_radius_textbox.text())
            rout = float(self.ViewControl.outer_radius_textbox.text())
        else:
            rin = None
            rout = None

        x_shifts, y_shifts, data = self.actions.iterative_align(element, data, thetas, pad, blur_bool, rin, rout, center, algorithm, upsample_factor, save_bool, debug_bool, iters)
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts+x_shifts, self.y_shifts+y_shifts)
        return

        #save parameters 
        #run iterative alignment
        ##maybe put this entire function within 'iter_align_params'

        pass

    def alignFromText2_params(self):
        ##### for future reference "All File (*);;CSV (*.csv *.CSV)"
        fileName = QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath(), "TXT (*.txt) ;; NPY (*.npy)")

        if fileName[0] == "":
            return
        data = self.data.copy()
        data_fnames = self.fnames
        x_padding = self.x_padding_hist[-1]
        try:
            data, x_shifts, y_shifts = self.actions.alignFromText2(fileName, data, data_fnames, x_padding)
            self.restoreSig.emit()
                
        except TypeError:
            return
        self.dataChangedSig.emit(data)
        self.alignmentChangedSig.emit(self.x_shifts + x_shifts, self.y_shifts + y_shifts)
        return

    # def alignfromHotspotxt_params(self):
    #     self.actions.alignfromHotspotxt()
    #     pass

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        row = self.sld.value()
        return element, row, self.data, self.thetas

    def get_params_imgView(self):
        element = self.ViewControl.combo1.currentIndex()
        x_size = self.imageView.xSize
        y_size = self.imageView.ySize
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        posMat = self.posMat

        return element, x_size, y_size, hs_group, posMat, data