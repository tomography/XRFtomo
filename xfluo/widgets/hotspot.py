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
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from pylab import *

# from widgets.image_and_histogram_widget import ImageAndHistogramWidget
# from widgets.hotspot_controls_widget import HotspotControlsWidget

class HotspotWidget(QtWidgets.QWidget):

    sliderChangedSig = pyqtSignal(int, name='sliderChangedSig')
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    sldRangeChanged = pyqtSignal(int,np.ndarray, np.ndarray, name="sldRangeChanged")
    fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")

    def __init__(self):
        super(HotspotWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.ViewControl =xfluo.HotspotControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget(self)
        projViewBox = QtWidgets.QHBoxLayout()
        projViewBox.addWidget(self.ViewControl)
        projViewBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(projViewBox)

    def showHotSpot(self, data, element_names, thetas, fnames):
        self.fnames = fnames
        self.data = data
        self.thetas = thetas
        self.ViewControl.combo1.clear()
        self.ViewControl.combo2.clear()
        for j in element_names:
            self.ViewControl.combo1.addItem(j)
        num_projections  = data.shape[1]
        for k in arange(num_projections):
            self.ViewControl.combo2.addItem(str(k+1))

        # self.ViewControl.combo.currentIndexChanged.connect(self.saveHotSpotPos)
        self.ViewControl.combo3.setVisible(False)
        self.elementChanged()
        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.combo2.currentIndexChanged.connect(self.elementChanged)

        self.ViewControl.xUpBtn.clicked.connect(self.hotSpotBoxSizeChange)
        self.ViewControl.xDownBtn.clicked.connect(self.hotSpotBoxSizeChange)
        self.ViewControl.yUpBtn.clicked.connect(self.hotSpotBoxSizeChange)
        self.ViewControl.yDownBtn.clicked.connect(self.hotSpotBoxSizeChange)
        self.ViewControl.btn1.clicked.connect(self.hotspot2line_params)
        self.ViewControl.btn2.clicked.connect(self.hotspot2sine_params)
        self.ViewControl.btn3.clicked.connect(self.setY_params)
        self.ViewControl.btn4.clicked.connect(self.clrHotspot_params)

        self.ViewControl.show()

        self.imgAndHistoWidget.view.hotSpotNumb = 0
        self.imgAndHistoWidget.sld.setRange(0, num_projections - 1)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.imageSliderChanged)
        self.imgAndHistoWidget.file_name_title.setText(str(fnames[0]))

    def imageSliderChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        self.updateFileDisplay(self.fnames, index)
        self.fnamesChanged.emit(self.fnames,index)
        self.updateSliderSlot(index)
        self.sliderChangedSig.emit(index)

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.ViewControl.combo2.currentIndex()
        self.updateElementSlot(element, projection)
        self.elementChangedSig.emit(element, projection)

    def imageChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :])

    def updateSliderSlot(self, index):
        angle = round(self.thetas[index])
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.lcd.display(angle)
        self.imgAndHistoWidget.sld.setValue(index)
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :])
        
    def updateElementSlot(self, element, projection):
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, projection, :, :])
        self.ViewControl.combo1.setCurrentIndex(element)
        self.ViewControl.combo2.setCurrentIndex(projection)

    def updateSldRange(self,  projection, data,  thetas):
        self.thetas = thetas
        self.data = data
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.sld.setRange(0, len(thetas) -1)
        self.imgAndHistoWidget.lcd.display(thetas[projection])
        self.imgAndHistoWidget.sld.setValue(projection)
        self.imgAndHistoWidget.view.projView.setImage(data[element, projection])

    def updateFileDisplay(self, fnames, index):
        self.fnames = fnames
        self.imgAndHistoWidget.file_name_title.setText(str(self.fnames[index]))


    def hotSpotBoxSizeChange(self):
        xSize = self.ViewControl.xSize
        ySize = self.ViewControl.ySize
        self.imgAndHistoWidget.view.xSize = xSize
        self.imgAndHistoWidget.view.ySize = ySize
        self.imgAndHistoWidget.view.ROI.setSize([xSize, ySize])
        x_pos = int(round(self.imgAndHistoWidget.view.x_pos))
        y_pos = int(round(self.imgAndHistoWidget.view.y_pos))
        self.imgAndHistoWidget.view.ROI.setPos([x_pos-xSize/2, y_pos-ySize/2])

    def hotSpotSetChanged(self):
        self.imgAndHistoWidget.view.hotSpotSetNumb = self.ViewControl.combo2.currentIndex()

    def hotspot2line_params(self):
        pass

    def hotspot2sine_params(self):
        pass

    def setY_params(self):
        pass

    def clrHotspot_params(self):
        pass
