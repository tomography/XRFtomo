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

import xfluo
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal

# from widgets.sinogram_view import SinogramView
# from widgets.sinogram_controls_widget import SinogramControlsWidget
import pyqtgraph
from pylab import *
import numpy as np

class SinogramWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')
    alignmentChangedSig = pyqtSignal(np.ndarray, np.ndarray, list, name="alignmentChangedSig")
    sinoChangedSig = pyqtSignal(np.ndarray, name="sinoChangedSig")

    def __init__(self):
        super(SinogramWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.SinogramControlsWidget()
        self.sinoView = xfluo.SinogramView()
        self.actions = xfluo.SinogramActions()

        self.lbl = QtWidgets.QLabel('Row y')
        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setValue(1)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        self.hist.setImageItem(self.sinoView.projView)
        self.data = np.ndarray(shape=(1, 10, 10, 10), dtype=float)
        self.x_shifts = None
        self.y_shifts = None
        self.centers = None

        self.ViewControl.btn1.clicked.connect(self.centerOfMass_params)
        # self.ViewControl.btn1.clicked.connect(self.centerOfMass2_params)
        self.ViewControl.btn2.clicked.connect(self.crossCorrelate_params)
        self.ViewControl.btn3.clicked.connect(self.phaseCorrelate_params)
        self.ViewControl.btn4.clicked.connect(self.crossCorrelate2_params)
        self.ViewControl.btn5.clicked.connect(self.align_y_top_params)
        self.ViewControl.btn6.clicked.connect(self.iter_align_params)
        self.ViewControl.btn7.clicked.connect(self.alignFromText2_params)
        self.ViewControl.btn8.clicked.connect(self.align_y_bottom_params)
        self.ViewControl.btn9.clicked.connect(self.adjust_sino_params)
        self.sld.valueChanged.connect(self.imageSliderChanged)
        self.sinoView.keyPressSig.connect(self.shiftEvent_params)
        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)

        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(self.lbl)
        hb0.addWidget(self.lcd)
        hb0.addWidget(self.sld)
        vb1 = QtWidgets.QVBoxLayout()
        vb1.addWidget(self.sinoView)
        vb1.addLayout(hb0)
        vb1.maximumSize()

        sinoBox = QtWidgets.QHBoxLayout()
        sinoBox.addWidget(self.ViewControl)
        sinoBox.addLayout(vb1)
        sinoBox.addWidget(self.hist)

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

    def showSinogram(self, data, element_names, thetas, fnames, x_shifts, y_shifts, centers):
        '''
        loads sinogram tabS
        '''

        self.x_shifts = x_shifts
        self.y_shifts = y_shifts
        self.centers = centers
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.fnames = fnames
        self.thetas = thetas
        self.data = data
        self.ViewControl.combo1.clear()
        for j in element_names:
            self.ViewControl.combo1.addItem(j)

        self.actions = xfluo.SinogramActions()
        self.elementChanged()
        self.sld.setRange(1, self.data.shape[2])
        self.lcd.display(1)

    def imageSliderChanged(self):
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
        self.elementChangedSig.emit(element, projection)

    def imageChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        self.sinogram(element)

    def yChanged(self, ySize):
        self.sld.setRange(1, ySize)
        self.sld.setValue(1)
        self.lcd.display(1)

    def updateElementSlot(self, element):
        self.sinogram(element)
        self.ViewControl.combo1.setCurrentIndex(element)

    def sinogram(self, element):
        '''
        load variables and image for sinogram window

        Variables
        -----------
        self.thickness: number
              thickness of y of each projections
        self.sino.combo.currentIndex(): number
              indicates the index of the element
        self.data: ndarray
              4d tomographic data [element, projections, y,x]
        '''
        # if self.data == None:
        #     print('TODO: initialize data for sinogramwidget')

        # else:
        sinodata = self.data[element, :, :, :]

        self.sinogramData = zeros([sinodata.shape[0] * 10, sinodata.shape[2]], dtype=float32)
        num_projections = self.data.shape[1]
        for i in arange(num_projections):
            self.sinogramData[i * 10:(i + 1) * 10, :] = sinodata[i, self.sld.value()-1, :]

        self.sinogramData[isinf(self.sinogramData)] = 0.001
        self.sinoView.projView.setImage(self.sinogramData, border='w')
        if len(self.thetas) > 0:
            self.sinoView.projView.setRect(QtCore.QRect(round(self.thetas[0]), 0, round(self.thetas[-1])- round(self.thetas[0]), self.sinogramData.shape[1]))
        else:
            print("Warning: Could not set Rect for sinogram. TODO: Look into why this happens")
        self.sinoChangedSig.emit(self.sinogramData)
        return

    def centerOfMass_params(self):
        element, row, data, thetas = self.get_params()
        data = self.data
        thetas = self.thetas
        self.data, self.x_shifts = self.actions.runCenterOfMass(element, row, data, thetas)
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return
        
    # def centerOfMass2_params(self):
    #     element, row, data, thetas = self.get_params()
    #     self.data, self.x_shifts, self.centers = self.actions.runCenterOfMass2(element, row, data, thetas)
    #     self.dataChangedSig.emit(self.data)
    #     self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
    #     return

    def shiftEvent_params(self, shift_dir, col_number):
        sinoData = self.sinogramData
        data = self.data
        thetas = self.thetas

        self.data, self.sinogramData = self.actions.shift(sinoData, data, shift_dir, col_number)
        self.x_shifts[col_number] += shift_dir
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    def crossCorrelate_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        self.data, self.x_shifts, self.y_shifts = self.actions.crossCorrelate(element, data)
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    def crossCorrelate2_params(self):
        data = self.data
        self.data, self.x_shifts, self.y_shifts = self.actions.crossCorrelate2(data)
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    def phaseCorrelate_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        self.data, self.x_shifts, self.y_shifts = self.actions.phaseCorrelate(element, data)
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    def align_y_top_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        # thetas= self.thetas
        self.y_shifts, self.data = self.actions.align_y_top(element, data) 
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    def align_y_bottom_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        # thetas= self.thetas
        self.y_shifts, self.data = self.actions.align_y_bottom(element, data) 
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return
        
    def adjust_sino_params(self):
        sinogramData = self.sinogramData
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        delta = int(self.ViewControl.slopeText.text())
        x_shifts, self. data, self.sinogramData = self.actions.slope_adjust(sinogramData, data, element, delta)
        self.x_shifts += x_shifts
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    # def matchTermplate_params(self):
    #     self.actions.matchTemmplate()
    #     pass

    def iter_align_params(self):
        data = self.data
        element = self.ViewControl.combo1.currentIndex()
        thetas = self.thetas
        # sx =  self.actions.iterative_align(element, data, thetas, 2)
        self.x_shifts, self.y_shifts, self.data = self.actions.iterative_align(element, data, thetas, 3)
        self.dataChangedSig.emit(self.data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    def alignFromText2_params(self):
        data = self.data
        self.data, self.x_shifts, self.y_shifts = self.actions.alignFromText2(data)
        self.dataChangedSig.emit(self.data)
        # self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        return

    # def alignfromHotspotxt_params(self):
    #     self.actions.alignfromHotspotxt()
    #     pass

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        row = self.sld.value()
        return element, row, self.data, self.thetas
