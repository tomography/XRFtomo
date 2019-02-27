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


from PyQt5 import QtCore
import pyqtgraph
# import MyImageItem



class HistogramWidget(pyqtgraph.GraphicsLayoutWidget):

    def __init__(self, parent):
        super(HistogramWidget, self).__init__()
        self.parent = parent
        self.hotSpotNumb = 0
        self.xSize = 10
        self.ySize = 10
        self.x_pos = 5
        self.y_pos = -5
        self.initUI()

    def initUI(self):
        self.p1 = self.addPlot(enableMouse = False)
        self.projView = pyqtgraph.ImageItem()
        self.projView.rotate(-90)
        self.projView.iniX = 0
        self.projView.iniY = -10
        self.ROI = pyqtgraph.ROI([self.projView.iniX, self.projView.iniY], [10, 10])
        self.p1.addItem(self.projView)
        self.p1.addItem(self.ROI)
        self.p1.scene().sigMouseMoved.connect(self.mouseMoved)
        self.p1.scene().sigMouseClicked.connect(self.mouseClick)
        self.p1.setMouseEnabled(x=False, y=False)

    def mouseMoved(self, evt):
        self.moving_x = self.p1.vb.mapSceneToView(evt).x()
        self.moving_y = self.p1.vb.mapSceneToView(evt).y()

    def mouseClick(self, evt):
        self.x_pos = self.moving_x
        self.y_pos = self.moving_y

        # print(self.x_pos,self.y_pos)
        self.ROI.setPos([self.x_pos-self.xSize/2,self.y_pos-self.ySize/2])

    def wheelEvent(self, ev):
        pass

    def keyPressEvent(self, ev):
        print(ev.key())
        print(ev.modifiers())
        if ev.key() == QtCore.Qt.Key_N:
            if self.hotSpotNumb < self.data.shape[0]:
                self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 0] = self.projView.iniY
                self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 1] = self.projView.iniX
                self.hotSpotNumb += 1
                if self.hotSpotNumb < self.data.shape[0]:
                    self.projView.setImage(self.data[self.hotSpotNumb, :, :])
        if ev.key() == QtCore.Qt.Key_S:
            self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 0] = 0
            self.posMat[self.hotSpotSetNumb, self.hotSpotNumb, 1] = 0
            if self.hotSpotNumb < self.data.shape[0] - 1:
                self.hotSpotNumb += 1
                self.projView.setImage(self.data[self.hotSpotNumb, :, :])
        if ev.key() == QtCore.Qt.Key_Left:
            self.parent.parent.parent.actions.shiftProjectionLeft()
        if ev.key() == QtCore.Qt.Key_Right:
            self.parent.parent.parent.actions.shiftProjectionRight()
        if ev.key() == QtCore.Qt.Key_Up:
            self.parent.parent.parent.actions.shiftProjectionUp()
        if ev.key() == QtCore.Qt.Key_Down:
            self.parent.parent.parent.actions.shiftProjectionDown()

        if (ev.modifiers() == QtCore.Qt.Key_Shift) and ev.key() == QtCore.Qt.Key_Left:
            self.parent.parent.parent.actions.shiftDataLeft()
        if ev.modifiers() == QtCore.Qt.Key_Shift and ev.key() == QtCore.Qt.Key_Right:
            self.parent.parent.parent.actions.shiftDataRight()
        if ev.modifiers() == QtCore.Qt.Key_Shift and ev.key() == QtCore.Qt.Key_Up:
            self.parent.parent.parent.actions.shiftDataUp()
        if ev.modifiers() == QtCore.Qt.Key_Shift and ev.key() == QtCore.Qt.Key_Down:
            self.parent.parent.parent.actions.shiftDataDown()
