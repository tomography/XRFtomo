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


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import xrftomo
import pyqtgraph
import numpy as np
import scipy.ndimage

from matplotlib import pyplot as plt
# from matplotlib.pyplot import figure, draw, pause, close
import time


class ReconstructionWidget(QtWidgets.QWidget):
    elementChangedSig = pyqtSignal(int, name='elementChangedSig')
    sldRangeChanged = pyqtSignal(int, np.ndarray, np.ndarray, name='sldRangeChanged')
    reconChangedSig = pyqtSignal(np.ndarray, name='reconChangedSig')
    reconArrChangedSig = pyqtSignal(np.ndarray, name='reconArrChangedSig')

    def __init__(self):
        super(ReconstructionWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.ViewControl = xrftomo.ReconstructionControlsWidget()
        self.ReconView = xrftomo.ReconView(self)
        self.actions = xrftomo.ReconstructionActions()
        self.actions2 = xrftomo.ImageProcessActions()
        self.writer = xrftomo.SaveOptions()

        self.file_name_title = QtWidgets.QLabel("_")
        lbl1 = QtWidgets.QLabel("x pos:")
        self.lbl2 = QtWidgets.QLabel("")
        lbl3 = QtWidgets.QLabel("y pos:")
        self.lbl4 = QtWidgets.QLabel("")
        lbl5 = QtWidgets.QLabel("Slice")
        lbl6 = QtWidgets.QLabel("value:")
        self.lbl7 = QtWidgets.QLabel("")

        self.ReconView.mouseMoveSig.connect(self.updatePanel)
        #get pixel value from Histogram widget's projview 

        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setMinimumSize(120,120)
        self.hist.setMaximumWidth(120)
        self.hist.setImageItem(self.ReconView.projView)

        self.ViewControl.combo1.currentIndexChanged.connect(self.elementChanged)
        self.ViewControl.reconGroup.currentIndexChanged.connect(self.recon_combobox_changed)
        self.ViewControl.btn.clicked.connect(self.reconstruct_params)
        # self.ViewControl.equalizeBtn.clicked.connect(self.equalize_params)
        self.ViewControl.rmHotspotBtn.clicked.connect(self.rm_hotspot_params)
        self.ViewControl.setThreshBtn.clicked.connect(self.set_thresh_params)


        self.ViewControl.btn2.clicked.connect(self.reconstruct_all_params)
        # self.ViewControl.recon2npy.clicked.connect(self.reconstruct_all_npy_params)
        self.ViewControl.mulBtn.clicked.connect(self.call_reconMultiply)
        self.ViewControl.divBtn.clicked.connect(self.call_reconDivide)
        self.ViewControl.end_indx.editingFinished.connect(self.update_y_range)
        self.ViewControl.start_indx.editingFinished.connect(self.update_y_range)
        self.ViewControl.mid_indx.editingFinished.connect(self.update_middle_index)
        self.ViewControl.recon_stats.clicked.connect(self.toggle_middle_index)
        self.sld.valueChanged.connect(self.update_recon_image)

        self.x_shifts = None
        self.y_shifts = None
        self.centers = None
        self.recon = None
        self.recon_array = None
        self.data = None
        self.data_original = None

        hb0 = QtWidgets.QHBoxLayout()
        hb0.addWidget(lbl1)
        hb0.addWidget(self.lbl2)
        hb0.addWidget(lbl3)
        hb0.addWidget(self.lbl4)
        hb0.addWidget(lbl6)
        hb0.addWidget(self.lbl7)

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(lbl5)
        hb1.addWidget(self.lcd)
        hb1.addWidget(self.sld)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addWidget(self.file_name_title)
        vb1.addLayout(hb0)
        vb1.addWidget(self.ReconView)
        vb1.addLayout(hb1)

        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.ViewControl)
        hb2.addLayout(vb1)
        hb2.addWidget(self.hist, 10)

        self.setLayout(hb2)

    def updatePanel(self,x,y):
        self.lbl2.setText(str(x))
        self.lbl4.setText(str(y))
        try:
            pixel_val = round(self.view.projView.image[abs(y)-1,x],4)
            self.lbl7.setText(str(pixel_val))
        except:
            self.lbl7.setText("")

    def showReconstruct(self):
        '''
        load window for reconstruction window
        '''
        self.write = xrftomo.SaveOptions()
        self.actions.x_shifts = self.x_shifts
        self.actions.y_shifts = self.y_shifts
        self.actions.centers = self.centers
        self.y_range = self.data.shape[2]

        self.ViewControl.combo1.clear()
        self.ViewControl.method.clear()
        self.ViewControl.reconGroup.clear()
        self.ViewControl.reconGroup.disconnect()
        methodname = ["mlem", "gridrec", "art", "pml_hybrid", "pml_quad", "fbp", "sirt", "tv"]
        for j in self.elements:
            self.ViewControl.combo1.addItem(j)
        for k in range(len(methodname)):
            self.ViewControl.method.addItem(methodname[k])
        for l in self.elements:
            self.ViewControl.reconGroup.addItem(l)
        self.recon_array = np.zeros((len(self.elements),self.y_range,self.data.shape[3],self.data.shape[3]))

        self.ViewControl.reconGroup.currentIndexChanged.connect(self.recon_combobox_changed)
        self.elementChanged()

        #TODO: recon_array will need to update with any changes to data dimensions as well as re-initialization
        # self.ViewControl.centerTextBox.setText(str(self.centers[2]))
        self.ViewControl.mulBtn.setEnabled(False)
        self.ViewControl.divBtn.setEnabled(False)
        self.ViewControl.end_indx.setText((str(self.data.shape[2])))
        self.ViewControl.mid_indx.setText((str(self.data.shape[2]//2)))

        self.sld.setRange(0, self.y_range - 1)
        self.lcd.display(0)

    def elementChanged(self):
        element = self.ViewControl.combo1.currentIndex()
        self.updateElementSlot(element)
        self.elementChangedSig.emit(element)

    def updateElementSlot(self, element):
        self.ViewControl.combo1.setCurrentIndex(element)

    def call_reconMultiply(self):
        '''
        multiply reconstruction by 10
        '''
        self.recon = self.actions.reconMultiply(self.recon)
        self.update_recon_image()

    def call_reconDivide(self):
        '''
        divide reconstuction by 10
        '''
        self.recon = self.actions.reconDivide(self.recon)
        self.update_recon_image()

    def reconstruct_params(self):
        element = self.ViewControl.combo1.currentIndex()
        center = np.array(float(self.data.shape[3]), dtype=np.float32)/2
        method = self.ViewControl.method.currentIndex()
        beta = float(self.ViewControl.beta.text())
        delta = float(self.ViewControl.delta.text())
        iters = int(self.ViewControl.iters.text())
        thetas = self.thetas
        end_indx = int(self.data.shape[2] - eval(self.ViewControl.start_indx.text()))
        start_indx = int(self.data.shape[2] - eval(self.ViewControl.end_indx.text()))
        mid_indx = int(self.data.shape[2] - eval(self.ViewControl.mid_indx.text())) -start_indx - 1
        offst_top = int(self.ViewControl.offst_top.text())
        offst_bottom = int(self.ViewControl.offst_bottom.text())


        data = self.data[:,:,start_indx:end_indx,:]
        show_stats = self.ViewControl.recon_stats.isChecked()
        num_xsections = data.shape[2]
        recons = np.zeros((data.shape[2], data.shape[3], data.shape[3]))  # empty array of size [y, x,x]
        xsection = np.zeros((1, data.shape[1], 1, data.shape[3]))  # empty array size [1(element), frames, 1(y), x]
        if offst_top !=0 or offst_bottom !=0:
            center = center + np.linspace(offst_top, offst_bottom, data.shape[2])
            shifts = np.linspace(offst_top, offst_bottom, data.shape[2])
        if self.ViewControl.recon_save.isChecked():
            try:
                savedir = QtGui.QFileDialog.getSaveFileName()[0]
                # savedir = '/Users/fabriciomarin/Documents/scans/Lin_XRF_tomo/Lin_3D2/testing/ptycho'

                if savedir == "":
                    raise IOError
                if savedir == None:
                    return
            except IOError:
                print("type the header name")
            except: 
                print("Something went horribly wrong.")

            #reconstruct one ccross section at a time and save after each loop/completion.
            start_idx = int(eval(self.ViewControl.start_indx.text()))
            for i in range(num_xsections):
                j = num_xsections-i-1
                xsection[0,:,0] = data[element,:,j]
                recon = self.actions.reconstruct(xsection, 0, center, method, beta, delta, iters, thetas, 0)
                recons[i] = recon
                self.writer.save_reconstruction(recon, savedir, start_idx+i)
            self.recon = np.array(recons)
        else:
            print("working fine")
            if method== 0 or method==2:
                for i in range(num_xsections):
                    j = num_xsections-i-1
                    xsection[0,:,0] = data[element,:,j]
                    if offst_top != 0 or offst_bottom != 0:
                        cent = center[i]
                    else:
                        cent = center
                    guess = self.actions.reconstruct(xsection, 0, cent, method, beta, delta, 5, thetas, None)
                    for k in range(5, iters):
                        #  data, element, center, method, beta, delta, iters, thetas, guess=None):
                        guess = self.actions.reconstruct(xsection, 0, center, method, beta, delta, 1, thetas, guess)
                        recons[i] = guess[0]
                        print("reconstructing row {} on iteration{}".format(i,k))

                    err, mse = self.actions.assessRecon(guess, xsection[0,:,0], thetas, show_stats)
                    print(mse)
            elif method ==1:
                for i in range(num_xsections):
                    print("reconstructing row{}/{}".format(i,num_xsections))
                    j = num_xsections - i - 1
                    xsection[0, :, 0] = data[element, :, j]
                    if offst_top != 0 or offst_bottom != 0:
                        cent = center[i]
                    else:
                        cent = center
                    recon = self.actions.reconstruct(xsection, 0, cent, method, beta, delta, 1, thetas, None)
                    if offst_top != 0 or offst_bottom != 0:
                        recon[0] = scipy.ndimage.shift(recon[0], (0,shifts[i]), output=None, order=3, mode='grid-wrap', cval=0.0, prefilter=True)
                    recons[i] = recon[0]

                    err, mse = self.actions.assessRecon(recon, xsection[0,:,0], thetas, show_stats)
                    print(mse)

            else:
                for i in range(num_xsections):
                    print("reconstructing row{}/{}".format(i,num_xsections))
                    j = num_xsections - i - 1
                    xsection[0, :, 0] = data[element, :, j]
                    if offst_top != 0 or offst_bottom != 0:
                        cent = center[i]
                    else:
                        cent = center
                    #  data, element, center, method, beta, delta, iters, thetas, guess=None):
                    recon = self.actions.reconstruct(xsection, 0, cent, method, beta, delta, iters, thetas, None)
                    recons[i] = recon[0]


                    err, mse = self.actions.assessRecon(recon, xsection[0, :, 0], thetas, show_stats)
                    print(mse)

            self.recon = np.array(recons)

        self.ViewControl.mulBtn.setEnabled(True)
        self.ViewControl.divBtn.setEnabled(True)
        self.update_recon_image()
        self.update_recon_array(self.recon)
        self.reconChangedSig.emit(self.recon)
        self.reconArrChangedSig.emit(self.recon_array)
        return

    def reconstruct_all_params(self):
        #figure out how to get a list of all selected elements
        num_elements = self.ViewControl.combo1.count()
        element_names = [self.ViewControl.combo1.itemText(i) for i in range(num_elements)]
        # box_checked = self.ViewControl.cbox.isChecked()
        center = np.array(float(self.data.shape[3]), dtype=np.float32)/2
        method = self.ViewControl.method.currentIndex()
        beta = float(self.ViewControl.beta.text())
        delta = float(self.ViewControl.delta.text())
        iters = int(self.ViewControl.iters.text())
        thetas = self.thetas
        end_indx = int(self.data.shape[2] - eval(self.ViewControl.start_indx.text()))
        start_indx = int(self.data.shape[2] - eval(self.ViewControl.end_indx.text()))
        mid_indx = int(self.data.shape[2] - eval(self.ViewControl.mid_indx.text()))
        data = self.data[:,:,start_indx:end_indx,:]

        self.recon = self.actions.reconstructAll(data, element_names, center, method, beta, delta, iters, thetas,start_indx)
        self.ViewControl.mulBtn.setEnabled(True)
        self.ViewControl.divBtn.setEnabled(True)
        self.update_recon_image()
        self.reconChangedSig.emit(self.recon)
        return

    # def reconstruct_all_npy_params(self):
    #     #figure out how to get a list of all selected elements
    #     num_elements = self.ViewControl.combo1.count()
    #     element_names = [self.ViewControl.combo1.itemText(i) for i in range(num_elements)]
    #     # box_checked = self.ViewControl.cbox.isChecked()
    #     center = np.array(float(self.data.shape[3]), dtype=np.float32)/2
    #     method = self.ViewControl.method.currentIndex()
    #     beta = float(self.ViewControl.beta.text())
    #     delta = float(self.ViewControl.delta.text())
    #     iters = int(self.ViewControl.iters.text())
    #     thetas = self.thetas
    #     end_indx = int(self.data.shape[2] - eval(self.ViewControl.start_indx.text()))
    #     start_indx = int(self.data.shape[2] - eval(self.ViewControl.end_indx.text()))
    #     mid_indx = int(self.data.shape[2] - eval(self.ViewControl.mid_indx.text()))
    #     data = self.data[:,:,start_indx:end_indx,:]

    #     #reconArray [element,stack,y,x]
    #     num_elements = data.shape[0]
    #     num_slices = data.shape[2]
    #     slice_dim = data.shape[3]

    #     for i in range(num_elements):
    #         self.recon = self.actions.reconstruct(data, i, center, method, beta, delta, iters, thetas, mid_indx, False)
    #         self.recon_array[i] = self.recon
    #         self.update_recon_image()
    #         self.reconChangedSig.emit(self.recon)
    #     self.writer.save_recon_array_2npy(self.recon_array, savedir=None, index=-1)
    #     return

    def ySizeChanged(self, ySize):
        self.ViewControl.start_indx.setText('0')
        self.ViewControl.end_indx.setText(str(ySize))
        self.ViewControl.mid_indx.setText(str(ySize//2))
        self.sld.setValue(0)
        self.sld.setMaximum(ySize)
        self.recon_array = np.zeros((len(self.elements),ySize,self.data.shape[3],self.data.shape[3]))
        #check for xSize too.
        return
        
    def xSizeChanged(self, xSize):
        self.recon_array = np.zeros((len(self.elements),self.data.shape[2],xSize,xSize))
        return

    def update_y_range(self):
        start_indx = int(self.ViewControl.start_indx.text())
        end_indx = int(self.ViewControl.end_indx.text())
        if end_indx >self.data.shape[2]:
            end_indx = self.data.shape[2]
            self.ViewControl.end_indx.setText(str(end_indx))
        if end_indx <= 0:
            end_indx = self.data.shape[2]
            self.ViewControl.end_indx.setText(str(end_indx))
        if start_indx >=end_indx:
            self.ViewControl.start_indx.setText(str(end_indx-1))
        if start_indx < 0:
            self.ViewControl.start_indx.setText(str(0))
        self.update_middle_index()

        self.sld.setRange(0, end_indx-start_indx - 1)
        self.sld.setValue(0)
        self.lcd.display(0)

    def update_middle_index(self):
        start_indx = int(self.ViewControl.start_indx.text())
        end_indx = int(self.ViewControl.end_indx.text())
        mid_indx = int(self.ViewControl.mid_indx.text())
        if mid_indx == -1:
            mid_indx = end_indx//2
        if mid_indx > end_indx:
            mid_indx = end_indx
            self.ViewControl.mid_indx.setText(str(mid_indx))
        if mid_indx < start_indx:
            mid_indx = start_indx
            self.ViewControl.mid_indx.setText(str(mid_indx))

    def toggle_middle_index(self):
        if self.ViewControl.recon_stats.isChecked():
            self.ViewControl.mid_indx.setEnabled(True)
        else:
            self.ViewControl.mid_indx.setEnabled(False)

    # def equalize_params(self):
    #     recon = self.recon 
    #     recon = self.actions.equalize_recon(recon)
    #     self.update_recon_image()
        
    def rm_hotspot_params(self):
        recon = self.recon 
        recon = self.actions.remove_hotspots(recon)
        self.update_recon_image()

    def set_thresh_params(self):
        recon = self.recon 
        threshold = float(self.ViewControl.lThresh.text())
        recon = self.actions.setThreshold(threshold,recon)
        self.update_recon_image()

    def update_recon_array(self, recon):
        indx = self.ViewControl.combo1.currentIndex()    
        #recon could be a partial reconstruction, account for this by indexing the Y range as well 
        ymin = int(eval(self.ViewControl.start_indx.text()))
        ymax = int(eval(self.ViewControl.end_indx.text()))

        self.recon_array[indx,ymin:ymax,:] = recon

    def recon_combobox_changed(self):
        indx = self.ViewControl.reconGroup.currentIndex()
        recon = self.recon_array[indx]
        self.recon = recon
        self.update_recon_image()

    def update_recon_image(self):
        index = self.sld.value()
        self.lcd.display(index)

        try:
            self.ViewControl.maxText.setText(str(self.recon[index, :, :].max()))
            self.ViewControl.minText.setText(str(self.recon[index, :, :].min()))
            self.ReconView.projView.setImage(self.recon[index, :, :])
        except:
            print("run reconstruction first")
