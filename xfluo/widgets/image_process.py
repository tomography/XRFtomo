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


from PyQt5 import QtWidgets
import xfluo
from pylab import *
import pyqtgraph

class ImageProcessWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ImageProcessWidget, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.ImageProcessControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget(self)
        mainHBox = QtWidgets.QHBoxLayout()
        mainHBox.addWidget(self.ViewControl)
        mainHBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(mainHBox)

    def showImgProcess(self, data, element_names, thetas):
        self.data = data
        self.thetas = thetas

        for j in element_names:
            self.ViewControl.combo1.addItem(j)
        num_projections  = data.shape[1]
        for k in arange(num_projections):
            self.ViewControl.combo2.addItem(str(k+1))

        self.imgProcessProjShow()
        self.ViewControl.combo1.currentIndexChanged.connect(self.imgProcessProjShow)
        self.ViewControl.combo2.currentIndexChanged.connect(self.imgProcessProjShow)
        self.ViewControl.xUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.xDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.yUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.yDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.combo2.setVisible(False)
        self.ViewControl.bgBtn.clicked.connect(self.parent.actions.background_value)
        self.ViewControl.delHotspotBtn.clicked.connect(self.parent.actions.patch_hotspot)
        self.ViewControl.normalizeBtn.clicked.connect(self.parent.actions.normalize)
        self.ViewControl.cutBtn.clicked.connect(self.parent.actions.cut)
        # self.ViewControl.cutBtn.clicked.connect(self.updateReconBounds)
        self.ViewControl.gaussian33Btn.clicked.connect(self.parent.actions.gauss33)
        self.ViewControl.gaussian33Btn.clicked.connect(self.parent.actions.gauss55)
        self.ViewControl.captureBackground.clicked.connect(self.parent.actions.copy_background)
        self.ViewControl.setBackground.clicked.connect(self.parent.actions.set_background)
        # self.ViewControl.deleteProjection.clicked.connect(self.removeFrame)
        # self.ViewControl.testButton.clicked.connect(self.noise_analysis)
        self.ViewControl.shift_img_up.clicked.connect(self.parent.actions.shiftProjectionUp)
        self.ViewControl.shift_img_down.clicked.connect(self.parent.actions.shiftProjectionDown)
        self.ViewControl.shift_img_left.clicked.connect(self.parent.actions.shiftProjectionLeft)
        self.ViewControl.shift_img_right.clicked.connect(self.parent.actions.shiftProjectionRight)
        self.ViewControl.shift_all_up.clicked.connect(self.parent.actions.shiftDataUp)
        self.ViewControl.shift_all_down.clicked.connect(self.parent.actions.shiftDataDown)
        self.ViewControl.shift_all_left.clicked.connect(self.parent.actions.shiftDataLeft)
        self.ViewControl.shift_all_right.clicked.connect(self.parent.actions.shiftDataRight)

        self.imgAndHistoWidget.sld.setRange(0, num_projections - 1)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.imageProcessLCDValueChanged)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.imgProcessProjChanged)
        self.testtest =pyqtgraph.ImageView()

    def imgProcessProjShow(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.ViewControl.combo2.currentIndex()
        self.imgProcessImg = self.data[element, projection, :, :]
        self.imgAndHistoWidget.view.projView.setImage(self.imgProcessImg)
        self.parent.hotspotWidget.hotSpotImg = self.data[element, projection, :, :]
        self.parent.hotspotWidget.imgAndHistoWidget.view.projView.setImage(self.parent.hotspotWidget.hotSpotImg)
        self.parent.hotspotWidget.ViewControl.combo1.setCurrentIndex(element)
        self.parent.hotspotWidget.ViewControl.combo2.setCurrentIndex(projection)
        self.parent.sinogramWidget.sinoControl.combo1.setCurrentIndex(element)

    def imageProcessLCDValueChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        angle = round(self.thetas[index])
        self.imgAndHistoWidget.lcd.display(angle)
        self.imgAndHistoWidget.sld.setValue(index)
        self.parent.hotspotWidget.imgAndHistoWidget.sld.setValue(index)
        self.parent.hotspotWidget.imgAndHistoWidget.lcd.display(angle)

    def imgProcessProjChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, self.imgAndHistoWidget.sld.value(), :, :])
        # self.file_name_update(self.imgProcess)

    def imgProcessBoxSizeChange(self):
        xSize = self.ViewControl.xSize
        ySize = self.ViewControl.ySize
        self.imgAndHistoWidget.view.xSize = xSize
        self.imgAndHistoWidget.view.ySize = ySize
        self.imgAndHistoWidget.view.ROI.setSize([xSize, ySize])
        x_pos = int(round(self.imgAndHistoWidget.view.x_pos))
        y_pos = int(round(self.imgAndHistoWidget.view.y_pos))
        self.imgAndHistoWidget.view.ROI.setPos([x_pos-xSize/2, y_pos-ySize/2])


