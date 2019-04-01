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
from PyQt5.QtCore import pyqtSignal
import xfluo
from pylab import *
import pyqtgraph
import xfluo.widgets.image_process_actions as actions
import numpy as np

class ImageProcessWidget(QtWidgets.QWidget):

    sliderChangedSig = pyqtSignal(int, name='sliderChangedSig')
    elementChangedSig = pyqtSignal(int, int, name='elementCahngedSig')
    # shiftSig = pyqtSignal(str, name='sliderChangedSig')
    dataChangedSig = pyqtSignal(np.ndarray, name='dataChangedSig')
    ySizeChanged = pyqtSignal(int, name='ySizeChanged')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")

    def __init__(self):
        super(ImageProcessWidget, self).__init__()
        self.thetas = []
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.ImageProcessControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget(self)
        mainHBox = QtWidgets.QHBoxLayout()
        mainHBox.addWidget(self.ViewControl)
        mainHBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(mainHBox)

    def showImgProcess(self, data, element_names, thetas, fnames):
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

        self.actions = xfluo.ImageProcessActions()
        self.elementChanged()
        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.combo2.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.xUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.xDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.yUpBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.yDownBtn.clicked.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.combo2.setVisible(False)
        self.ViewControl.normalizeBtn.clicked.connect(self.normalize_params)
        self.ViewControl.cropBtn.clicked.connect(self.cut_params)
        self.ViewControl.gaussian33Btn.clicked.connect(self.actions.gauss33)
        self.ViewControl.gaussian55Btn.clicked.connect(self.actions.gauss55)
        self.ViewControl.captureBackground.clicked.connect(self.copyBG_params)
        self.ViewControl.setBackground.clicked.connect(self.pasteBG_params)
        self.ViewControl.deleteProjection.clicked.connect(self.exclude_params)
        self.ViewControl.testButton.clicked.connect(self.analysis_params)

        self.imgAndHistoWidget.view.shiftSig.connect(self.shift_process)
        self.actions.dataSig.connect(self.send_data)
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

    def updateSliderSlot(self, index):
        angle = round(self.thetas[index])
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.lcd.display(angle)
        self.imgAndHistoWidget.sld.setValue(index)
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :])

    def updateElementSlot(self, element, projection = None):
        if projection == None:
           projection =  self.imgAndHistoWidget.sld.value()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, projection, :, :])
        self.ViewControl.combo1.setCurrentIndex(element)
        self.ViewControl.combo2.setCurrentIndex(projection)

    def updateFileDisplay(self, fnames, index):
        self.fnames = fnames
        self.imgAndHistoWidget.file_name_title.setText(str(self.fnames[index]))

    def imgProcessBoxSizeChange(self):
        xSize = self.ViewControl.xSize
        ySize = self.ViewControl.ySize
        self.imgAndHistoWidget.view.xSize = xSize
        self.imgAndHistoWidget.view.ySize = ySize
        self.imgAndHistoWidget.view.ROI.setSize([xSize, ySize])
        x_pos = int(round(self.imgAndHistoWidget.view.x_pos))
        y_pos = int(round(self.imgAndHistoWidget.view.y_pos))
        self.imgAndHistoWidget.view.ROI.setPos([x_pos-xSize/2, y_pos-ySize/2])

    def imageChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :])

    def shift_process(self, command):
        index = self.imgAndHistoWidget.sld.value()
        if command == 'left':
            self.actions.shiftProjectionLeft(self.data, index) 
        if command == 'right':
            self.actions.shiftProjectionRight(self.data, index) 
        if command == 'up':
            self.actions.shiftProjectionUp(self.data, index) 
        if command == 'down':
            self.actions.shiftProjectionDown(self.data, index) 
        if command == 'shiftLeft':
            self.actions.shiftDataLeft(self.data) 
        if command == 'shiftRight':
            self.actions.shiftDataRight(self.data) 
        if command == 'shigtUp':
            self.actions.shiftDataUp(self.data, self.thetas) 
        if command == 'shiftDown':
            self.actions.shiftDataDown(self.data, self.thetas) 
        if command == 'Delete':
            self.exclude_params()

    def background_value_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.background_value(img)

    def patch_params(self): 
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.patch(self.data, img, elem, proj, x_pos, y_pos, x_size, y_size)

    def normalize_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        self.actions.normalize(data, element)
        
    def cut_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.cut(self.data, img, x_pos, y_pos, x_size, y_size)
        self.ySizeChanged.emit(y_size)

    def copyBG_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.copy_background(img)

    def pasteBG_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        self.actions.paste_background(data, element, projection, x_pos, y_pos, x_size, y_size, img)

    def analysis_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.noise_analysis(img)

    def exclude_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        thetas = self.thetas
        index = projection        
        self.fnames.pop(index)    
        num_files = len(self.fnames)
        temp_thetas = np.delete(thetas, projection, 0)

        if index>0:
            index -= 1
            num_files -= 1
        else:
            num_files -= 1

        self.updateSldRange(index, temp_thetas)
        projection, self.data, self.thetas = self.actions.exclude_projection(projection, data, thetas)
        self.dataChangedSig.emit(self.data)
        self.sldRangeChanged.emit(index, self.data,  self.thetas)
        self.updateFileDisplay(self.fnames, index)
        self.fnamesChanged.emit(self.fnames,index)
        self.imageSliderChanged()

    def updateSldRange(self, index, thetas):
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.sld.setRange(0, len(thetas) -1)
        self.imgAndHistoWidget.lcd.display(thetas[index])
        self.imgAndHistoWidget.sld.setValue(index)
        self.imageChanged()
        # self.imgAndHistoWidget.view.projView.setImage(data[element, projection])

    def get_params(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.imgAndHistoWidget.sld.value()
        x_pos = self.imgAndHistoWidget.view.x_pos
        y_pos = self.imgAndHistoWidget.view.y_pos
        x_size = self.ViewControl.xSize
        y_size = self.ViewControl.ySize
        img = self.data[element, projection, 
            int(round(abs(y_pos)) - y_size/2): int(round(abs(y_pos)) + y_size/2),
            int(round(x_pos) - x_size/2): int(round(x_pos) + x_size/2)]
        return element, projection, x_pos, y_pos, x_size, y_size, img

    def send_data(self, data):
        '''
        This sends a signal one level up indicating that the data array has changed
        and to update adjacent tabs with new data
        '''
        self.dataChangedSig.emit(data)



