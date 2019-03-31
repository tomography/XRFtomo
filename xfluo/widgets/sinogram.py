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
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal

# from widgets.sinogram_view import SinogramView
# from widgets.sinogram_controls_widget import SinogramControlsWidget
import pyqtgraph
from pylab import *
import numpy as np

class SinogramWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')

    def __init__(self):
        super(SinogramWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.SinogramControlsWidget()
        self.sinoView = xfluo.SinogramView()
        self.lbl = QtWidgets.QLabel('Row y')
        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setValue(1)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        self.hist.setImageItem(self.sinoView.projView)

        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(self.lbl)
        hb0.addWidget(self.lcd)
        hb0.addWidget(self.sld)
        vb1 = QtWidgets.QVBoxLayout()
        vb1.addWidget(self.sinoView)
        vb1.addLayout(hb0)

        sinoBox = QtWidgets.QHBoxLayout()
        sinoBox.addWidget(self.ViewControl)
        sinoBox.addLayout(vb1)
        sinoBox.addWidget(self.hist, 10)

        self.setLayout(sinoBox)

    def showSinogram(self, data, element_names, thetas):
        '''
        loads sinogram tabS
        '''
        self.thetas = thetas
        self.data = data
        self.ViewControl.combo1.clear()
        for j in element_names:
            self.ViewControl.combo1.addItem(j)

        self.actions = xfluo.SinogramActions()
        self.elementChanged()
        self.ViewControl.btn.clicked.connect(self.centerOfMass_params)
        self.ViewControl.btn2.setVisible(False)
        self.sld.setRange(1, self.data.shape[2])
        self.lcd.display(1)
        self.sld.valueChanged.connect(self.imageSliderChanged)
        self.sinoView.keyPressSig.connect(self.shiftEvent_params)
        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)

    def imageSliderChanged(self):
        index = self.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.lcd.display(index)
        print(index)
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
        sinodata = self.data[element, :, :, :]

        self.sinogramData = zeros([sinodata.shape[0] * 10, sinodata.shape[2]], dtype=float32)
        num_projections = self.data.shape[1]
        for i in arange(num_projections):
            self.sinogramData[i * 10:(i + 1) * 10, :] = sinodata[i, self.sld.value()-1, :]

        self.sinogramData[isinf(self.sinogramData)] = 0.001
        self.sinoView.projView.setImage(self.sinogramData)
        # self.view.projView.setRect(QtCore.QRect(round(self.theta[0]), 0, round(self.theta[-1])- round(self.theta[0]), self.sinogramData.shape[1]))
        # self.sinoView.projData = self.sinogramData
        return

    def centerOfMass_params(self):
        element, row, data, thetas = self.get_params()
        self.data = self.actions.runCenterOfMass2(element, row, data, thetas)
        self.dataChangedSig.emit(self.data)

    def shiftEvent_params(self, shift_number, column_number):
        sinoData = self.sinogramData
        data = self.data
        self.data, self.sinogramData = self.actions.shift(sinoData, data, shift_number, column_number)
        self.dataChangedSig.emit(self.data)

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        row = self.sld.value()
        return element, row, self.data, self.thetas