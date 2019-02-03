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
from pylab import *

# from widgets.image_and_histogram_widget import ImageAndHistogramWidget
# from widgets.hotspot_controls_widget import HotspotControlsWidget


class HotspotWidget(QtWidgets.QWidget):

    def __init__(self):
        super(HotspotWidget, self).__init__()

        self.initUI()

    def initUI(self):
        self.ViewControl =xfluo.HotspotControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget()
        projViewBox = QtWidgets.QHBoxLayout()
        projViewBox.addWidget(self.ViewControl)
        projViewBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(projViewBox)

    def showHotSpot(self, data, element_names = []):

        self.data = data
        # self.tab_widget.removeTab(1)
        # self.tab_widget.insertTab(1, self.createSaveHotspotWidget(), unicode("Hotspot"))
        # self.projViewControl.numb = len(self.channelname)

        num_elements = len(element_names)
        for j in arange(num_elements):
            self.ViewControl.combo1.addItem(element_names[j])
        num_projections  = data.shape[1]
        for k in arange(num_projections):
            self.ViewControl.combo2.addItem(str(k+1))

        # self.projViewControl.combo.currentIndexChanged.connect(self.saveHotSpotPos)
        # self.ViewControl.combo1.setVisible(False)
        self.ViewControl.combo1.currentIndexChanged.connect(self.hotSpotProjShow)
        self.ViewControl.combo2.currentIndexChanged.connect(self.hotSpotProjShow)

        # self.projViewControl.sld.setValue(20)
        # self.projViewControl.sld.setRange(0, self.x / 2)
        # self.projViewControl.lcd.display(20)
        # self.projViewControl.sld.valueChanged.connect(self.projViewControl.lcd.display)
        # self.projViewControl.sld.valueChanged.connect(self.boxSizeChange)
        # self.projViewControl.btn.clicked.connect(self.alignHotSpotPos3)
        # self.projViewControl.btn2.clicked.connect(self.alignHotSpotPos4)
        # self.projViewControl.btn3.clicked.connect(self.alignHotSpotY)
        # self.projViewControl.btn4.clicked.connect(self.clearHotSpotData)
        self.ViewControl.show()

        self.imgAndHistoWidget.view.hotSpotNumb = 0
        self.imgAndHistoWidget.sld.setRange(0, num_projections - 1)
        # self.projView.sld.valueChanged.connect(self.hotSpotLCDValueChanged)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.hotSpotProjChanged)
        # self.testtest = pg.ImageView()

    def hotSpotProjShow(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.ViewControl.combo2.currentIndex()
        self.hotSpotImg = self.data[element, projection, :, :]
        self.imgAndHistoWidget.view.projView.setImage(self.hotSpotImg)

    def hotSpotProjChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, self.projView.sld.value(), :, :])
        # self.file_name_update(self.projView)
    

        # self.imgProcess.view.projView.setImage(self.imgProcessImg)

    def hotSpotSetChanged(self):
        self.imgAndHistoWidget.view.hotSpotSetNumb = self.ViewControl.combo2.currentIndex()