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
# from widgets.sinogram_view import SinogramView
# from widgets.sinogram_controls_widget import SinogramControlsWidget
import pyqtgraph
from pylab import *
import numpy as np

class SinogramWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(SinogramWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.sinoControl = xfluo.SinogramControlsWidget()
        self.sinoView = xfluo.SinogramView()
        self.lbl = QtWidgets.QLabel('Row y')
        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
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
        sinoBox.addWidget(self.sinoControl)
        sinoBox.addLayout(vb1)
        sinoBox.addWidget(self.hist, 10)

        self.setLayout(sinoBox)

    def showSinogram(self, data, element_names, thetas):
        '''
        loads sinogram tabS
        '''
        self.data = data
        ## self.tab_widget.removeTab(2)
        ## self.tab_widget.insertTab(2, self.createSinoWidget(), unicode("Sinogram"))
        num_elements = len(element_names)
        for j in range(num_elements):
            self.sinoControl.combo1.addItem(element_names[j])

        # self.sino.btn.clicked.connect(self.runCenterOfMass2)
        # self.sino.btn2.clicked.connect(self.sinoShift)
        self.sld.setRange(1, self.data.shape[2])
        self.lcd.display(1)
        self.sld.valueChanged.connect(self.lcd.display)
        self.sld.valueChanged.connect(self.sinogram)
        self.sinoControl.combo1.currentIndexChanged.connect(self.sinogram)
        self.show()

    def sinogram(self):
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
        # self.file_name_update(self.sino)
        thickness = 10
        element = self.sinoControl.combo1.currentIndex()
        sinodata = self.data[element, :, :, :]
        self.parent.imageProcessWidget.ViewControl.combo1.setCurrentIndex(element)
        self.parent.hotspotWidget.ViewControl.combo1.setCurrentIndex(element)
        self.sinogramData = zeros([sinodata.shape[0] * thickness, sinodata.shape[2]], dtype=float32)

        num_projections = self.data.shape[1]
        for i in arange(num_projections):
            self.sinogramData[i * thickness:(i + 1) * thickness, :] = sinodata[i, self.sld.value()-1, :]

        global sinofig

        sinofig = self.sinogramData
        self.sinogramData[isinf(self.sinogramData)] = 0.001
        self.sinoView.projView.setImage(self.sinogramData)
        # self.view.projView.setRect(QtCore.QRect(round(self.theta[0]), 0, round(self.theta[-1])- round(self.theta[0]), self.sinogramData.shape[1]))
        self.sinoView.projData = self.sinogramData
        self.sinoView.getShape()
        return

    def sinoShift(self):

        for i in arange(self.projections):
            self.data[:,i,:,:] = np.roll(self.data[:,i,:,:], self.view.regShift[i])
