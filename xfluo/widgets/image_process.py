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

from PyQt5 import QtWidgets, QtGui
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
    thetaChangedSig = pyqtSignal(np.ndarray, name='thetaChangedSig')
    fnamesChanged = pyqtSignal(list,int, name="fnamesChanged")
    alignmentChangedSig = pyqtSignal(np.ndarray, np.ndarray, list, name="alignmentChangedSig")
    
    ySizeChanged = pyqtSignal(int, name='ySizeChanged')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    refreshSig = pyqtSignal(name='refreshSig')

    def __init__(self):
        super(ImageProcessWidget, self).__init__()
        self.thetas = []
        self.initUI()

    def initUI(self):
        self.ViewControl = xfluo.ImageProcessControlsWidget()
        self.imgAndHistoWidget = xfluo.ImageAndHistogramWidget(self)
        self.actions = xfluo.ImageProcessActions()

        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.combo2.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.x_sld.valueChanged.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.xSizeTxt.textChanged.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.y_sld.valueChanged.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.ySizeTxt.textChanged.connect(self.imgProcessBoxSizeChange)
        self.ViewControl.normalizeBtn.clicked.connect(self.normalize_params)
        self.ViewControl.cropBtn.clicked.connect(self.cut_params)
        # self.ViewControl.gaussian33Btn.clicked.connect(self.actions.gauss33)
        # self.ViewControl.gaussian55Btn.clicked.connect(self.actions.gauss55)
        self.ViewControl.captureBackground.clicked.connect(self.copyBG_params)
        self.ViewControl.setBackground.clicked.connect(self.pasteBG_params)
        self.ViewControl.deleteProjection.clicked.connect(self.exclude_params)
        # self.ViewControl.testButton.clicked.connect(self.save_analysis)
        # self.ViewControl.histogramButton.clicked.connect(self.histo_signal)

        self.ViewControl.btn1.clicked.connect(self.hotspot2line_params)
        self.ViewControl.btn2.clicked.connect(self.hotspot2sine_params)
        self.ViewControl.btn3.clicked.connect(self.setY_params)
        self.ViewControl.btn4.clicked.connect(self.clrHotspot_params)
        self.ViewControl.btn4.setEnabled(False)
        self.ViewControl.btn3.setEnabled(False)
        self.ViewControl.btn2.setEnabled(False)
        self.ViewControl.btn1.setEnabled(False)

        self.imgAndHistoWidget.view.keyPressSig.connect(self.keyProcess)
        self.actions.dataSig.connect(self.send_data)
        self.actions.thetaSig.connect(self.send_thetas)
        self.imgAndHistoWidget.sld.valueChanged.connect(self.imageSliderChanged)
        
        mainHBox = QtWidgets.QHBoxLayout()
        mainHBox.addWidget(self.ViewControl)
        mainHBox.addWidget(self.imgAndHistoWidget, 10)
        self.setLayout(mainHBox)
        self.x_shifts = None
        self.y_shifts = None
        self.centers = None

        palette = self.imgAndHistoWidget.lcd.palette()
        # foreground color
        palette.setColor(palette.WindowText, QtGui.QColor(85, 85, 255))
        # background color
        palette.setColor(palette.Background, QtGui.QColor(0, 170, 255))
        # "light" border
        palette.setColor(palette.Light, QtGui.QColor(255, 255, 0))
        # "dark" border
        palette.setColor(palette.Dark, QtGui.QColor(0, 0, 0))
        # set the palette
        self.imgAndHistoWidget.lcd.setPalette(palette)


    def showImgProcess(self):
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.posMat = np.zeros((5,int(self.data.shape[1]),2))
        self.imgAndHistoWidget.view.hotSpotNumb = 0
        self.ViewControl.x_sld.setRange(1, self.data.shape[3])
        self.ViewControl.y_sld.setRange(1, self.data.shape[2])

        self.ViewControl.combo1.clear()
        self.ViewControl.combo2.clear()
        for j in self.elements:
            self.ViewControl.combo1.addItem(j)
        num_projections  = self.data.shape[1]
        for k in arange(num_projections):
            self.ViewControl.combo2.addItem(str(k+1))

        self.elementChanged()
        self.imgAndHistoWidget.sld.setRange(0, num_projections - 1)
        self.ViewControl.combo2.setVisible(False)
        self.imgAndHistoWidget.file_name_title.setText(str(self.fnames[0]))

    def imageSliderChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        self.updateFileDisplay(self.fnames, index)
        self.filename_event
        self.updateSliderSlot(index)
        self.sliderChangedSig.emit(index)

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        projection = self.ViewControl.combo2.currentIndex()
        self.updateElementSlot(element, projection)
        self.elementChangedSig.emit(element, projection)

    def filename_event(self):
        index = self.imgAndHistoWidget.sld.value()
        self.imgAndHistoWidget.file_name_title.setText(self.fnames[index])

    def save_event(self):
        # self.data_history
        # self.theta_history
        # self.x_shift_historry
        # self.y_shift_history
        pass

    def updateSliderSlot(self, index):
        #TODO: thetas not necessarily defined here when selecting new dataset. figure out how to load thetas before calling this.
        if len(self.thetas) == 0:
            return
        angle = round(self.thetas[index])
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.lcd.display(angle)
        self.imgAndHistoWidget.sld.setValue(index)
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :], border='w')

    def updateElementSlot(self, element, projection = None):
        if projection == None:
           projection =  self.imgAndHistoWidget.sld.value()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, projection, :, :], border='w')
        self.ViewControl.combo1.setCurrentIndex(element)
        self.ViewControl.combo2.setCurrentIndex(projection)

    def updateFileDisplay(self, fnames, index):
        self.fnames = fnames
        self.imgAndHistoWidget.file_name_title.setText(str(self.fnames[index]))

    def imgProcessBoxSizeChange(self):
        xSize = self.ViewControl.xSize
        ySize = self.ViewControl.ySize
        if xSize > self.data.shape[3]:
            xSize = self.data.shape[3]
            self.ViewControl.xSize = xSize
        if ySize > self.data.shape[2]:
            ySize = self.data.shape[2]
            self.ViewControl.ySize = ySize   

                     
        self.imgAndHistoWidget.view.xSize = xSize
        self.imgAndHistoWidget.view.ySize = ySize
        self.imgAndHistoWidget.view.ROI.setSize([xSize, ySize])
        x_pos = int(round(self.imgAndHistoWidget.view.x_pos))
        y_pos = int(round(self.imgAndHistoWidget.view.y_pos))
        self.imgAndHistoWidget.view.ROI.setPos([x_pos-xSize/2, y_pos-ySize/2])

    def imageChanged(self):
        index = self.imgAndHistoWidget.sld.value()
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.view.projView.setImage(self.data[element, index, :, :], border='w')
    
    def updateSldRange(self, index, thetas):
        element = self.ViewControl.combo1.currentIndex()
        self.imgAndHistoWidget.sld.setRange(0, len(thetas) -1)
        self.imgAndHistoWidget.lcd.display(thetas[index])
        self.imgAndHistoWidget.sld.setValue(index)
        self.imageChanged()
        self.posMat = np.zeros((5,int(self.data.shape[1]), 2))
        # self.imgAndHistoWidget.view.projView.setImage(data[element, projection])

    def keyProcess(self, command):
        index = self.imgAndHistoWidget.sld.value()
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data

        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        if command == 'A': #previous projection
            self.imgAndHistoWidget.sld.setValue(self.imgAndHistoWidget.sld.value() - 1)
            self.imageSliderChanged()
        if command == 'D':  #next projection
            self.imgAndHistoWidget.sld.setValue(self.imgAndHistoWidget.sld.value() + 1)
            self.imageSliderChanged()
        if command == 'left':
            self.x_shifts[index] -=1
            self.actions.shiftProjectionLeft(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'right':
            self.x_shifts[index] +=1
            self.actions.shiftProjectionRight(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'up':
            self.y_shifts[index] +=1
            self.actions.shiftProjectionUp(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'down':
            self.y_shifts[index] -=1
            self.actions.shiftProjectionDown(self.data, index) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftLeft':
            self.x_shifts -=1
            self.actions.shiftDataLeft(self.data) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftRight':
            self.x_shifts +=1
            self.actions.shiftDataRight(self.data) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftUp':
            self.y_shifts +=1
            self.actions.shiftDataUp(self.data, self.thetas) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'shiftDown':
            self.y_shifts -=1
            self.actions.shiftDataDown(self.data, self.thetas) 
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'Delete':
            self.exclude_params()
            self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        if command == 'Copy':
            self.copyBG_params()
        if command == 'Paste':
            self.pasteBG_params()
        if command == 'Next':
            self.posMat[int(hs_group), int(hs_number)-1] = [x_pos, y_pos]
            if hs_number < self.posMat.shape[1]:
                print("n")
                print("Total projections", self.posMat.shape[1], "current position", hs_number+1, "group number", hs_group + 1)
                hs_number += 1
                if hs_number < self.posMat.shape[1]:
                    self.sliderChangedSig.emit(hs_number)
                else:
                    self.sliderChangedSig.emit(hs_number-1)
                    print("This is the last projection")
            self.ViewControl.btn3.setEnabled(True)
            self.ViewControl.btn2.setEnabled(True)
            self.ViewControl.btn1.setEnabled(True)
            self.ViewControl.btn4.setEnabled(True)
        if command == 'Skip':
            self.posMat[int(hs_group), int(hs_number)-1] = [0, 0]
            if hs_number < self.posMat.shape[1]:
                hs_number += 1
                self.sliderChangedSig.emit(hs_number)

    def hotSpotSetChanged(self):
        self.imgAndHistoWidget.view.hotSpotSetNumb = self.ViewControl.combo3.currentIndex()
        # self.actions.saveHotSpotPos()

    def hotspot2line_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        posMat = self.posMat
        self.x_shifts, self.y_shifts, self.centers = self.actions.hotspot2line(element, x_size, y_size, hs_group, posMat, data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        self.ViewControl.btn4.setEnabled(True)

    def hotspot2sine_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        posMat = self.posMat
        thetas = self.thetas
        self.x_shifts, self.y_shifts, self.centers = self.actions.hotspot2sine(element, x_size, y_size, hs_group, posMat, data, thetas)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        self.ViewControl.btn4.setEnabled(True)

    def setY_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        hs_group = self.ViewControl.combo3.currentIndex()
        hs_number = self.imgAndHistoWidget.sld.value()
        posMat = self.posMat
        self.x_shifts, self.y_shifts, self.centers = self.actions.setY(element, x_size, y_size, hs_group, posMat, data)
        self.alignmentChangedSig.emit(self.x_shifts, self.y_shifts, self.centers)
        self.ViewControl.btn4.setEnabled(True)

    def clrHotspot_params(self):
        self.posMat = self.actions.clrHotspot(self.posMat)
        self.ViewControl.btn4.setEnabled(False)
        self.ViewControl.btn3.setEnabled(False)
        self.ViewControl.btn2.setEnabled(False)
        self.ViewControl.btn1.setEnabled(False)

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

    def background_value_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.background_value(img)

    def patch_params(self): 
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.patch(self.data, img, element, projection, x_pos, y_pos, x_size, y_size)

    def normalize_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        self.actions.normalize(data, element)
        
    def cut_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        self.actions.cut(self.data, img, x_pos, y_pos, x_size, y_size)
        self.ySizeChanged.emit(y_size)
        self.refreshSig.emit()

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

    def bounding_params(self):
        element, projection, x_pos, y_pos, x_size, y_size, img = self.get_params()
        data = self.data
        img = data[element, projection, :,:]
        self.actions.bounding_analysis(img)
    
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
        index, data, thetas, fnames, x_shifts, y_shifts = self.actions.exclude_projection(index, data, thetas, fnames, x_shifts, y_shifts)

        self.alignmentChangedSig.emit(x_shifts, y_shifts, self.centers)
        self.updateSldRange(index, thetas)
        self.thetaChangedSig.emit(thetas)
        self.updateFileDisplay(fnames, index)
        self.fnamesChanged.emit(fnames,index)
        self.imageSliderChanged()

        self.sldRangeChanged.emit(index, data, thetas)
        self.dataChangedSig.emit(data)

    def data_scale_factor(self):
        #sf = get txtbox value
        
        # return self.data *= sf
        pass

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

    def send_data(self, data):
        '''
        This sends a signal one level up indicating that the data array has changed
        '''

        self.dataChangedSig.emit(data)

    def send_thetas(self, thetas):
        '''
        This sends a signal one level up indicating that the theta array has changed
        '''

        self.thetaChangedSig.emit(thetas)

    def send_fnames(self, fnames):
        '''
        This sends a signal one level up indicating that the fnames array has changed
        '''
        self.fnmaesChangedSig.emit(fnames)

    def send_alignment(self, x_shifts, y_shifts):
        '''
        This sends a signal one level up indicating that the alignment information has changed. 
        '''        
        self.alignemntChangedSig.emit(x_shifts, y_shifts)
