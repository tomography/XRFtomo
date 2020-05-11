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


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
# from matplotlib.figure import Figure
import pyqtgraph
import xrftomo

class ScatterView(pyqtgraph.GraphicsLayoutWidget):
    mouseMoveSig = pyqtSignal(int,int, name= 'mouseMoveSig')
    mousePressSig =pyqtSignal(name= 'mousePressSig')
    keyPressSig = pyqtSignal(str, name= 'keyPressSig')
    roiDraggedSig = pyqtSignal(name= 'roiSizeSig')


    def __init__(self):
    # def __init__(self, parent):
        super(ScatterView, self).__init__()
        self.keylist = []
        self.initUI()

    def initUI(self):
        custom_vb = xrftomo.CustomViewBox()
        custom_vb.disableAutoRange(axis="xy")
        custom_vb.setRange(xRange=(0,1), yRange=(0,1), padding=0)
        # custom_vb.invertY(True)

        #___________________ scatter view ___________________
        self.p1 = self.addPlot(viewBox = custom_vb, enableMouse = False)
        self.p1.setAutoPan(x=None, y=None)
        self.p1.setYRange(0,1)
        self.p1.setXRange(0,1)
        self.plotView = pyqtgraph.ScatterPlotItem()
        self.plotView2 = pyqtgraph.ScatterPlotItem()
        self.ROI = pyqtgraph.LineSegmentROI(positions=([0,0],[1,1]), pos=[0,0], movable=False, maxBounds=QtCore.QRectF(0, 0, 1, 1))
        self.ROI.sigRegionChangeFinished.connect(self.roi_dragged)
        self.p1.addItem(self.plotView)
        self.p1.addItem(self.plotView2)
        self.p1.addItem(self.ROI)
        self.p1.scene().sigMouseMoved.connect(self.mouseMoved)
        self.p1.scene().sigMouseClicked.connect(self.mouseClick)
        self.p1.setMouseEnabled(x=False, y=False)
        self.p1.vb = custom_vb

    def roi_dragged(self):
        try:
            x1_pos = self.ROI.getHandles()[0].pos().x()
            y1_pos = self.ROI.getHandles()[0].pos().y()
            x2_pos = self.ROI.getHandles()[1].pos().x()
            y2_pos = self.ROI.getHandles()[1].pos().y()
        except:
            return

        try:
            if x1_pos != 0:
                self.ROI.endpoints[0].setPos(0,y1_pos)
                x1_pos = 0
            if y1_pos != 0:
                self.ROI.endpoints[0].setPos(x1_pos,0)
            if x2_pos >1:
                self.ROI.endpoints[1].setPos(1,y2_pos)
                x2_pos = 1
            if y2_pos >1:
                self.ROI.endpoints[1].setPos(x2_pos,1)
                y2_pos = 1
            self.ROI.stateChanged(finish=True)
            self.roiDraggedSig.emit()
        except:
            self.roiDraggedSig.emit()
        return

    def mouseMoved(self, evt):
        self.moving_x = round(self.p1.vb.mapSceneToView(evt).x(),3)
        self.moving_y = round(self.p1.vb.mapSceneToView(evt).y(),3)
        self.mouseMoveSig.emit(self.moving_x, self.moving_y)

    def mouseClick(self, evt):
        x2_pos = self.moving_x
        y2_pos = self.moving_y
        if evt.button() == 1:
            try:
                x1_pos = self.ROI.getHandles()[0].pos().x()
                y1_pos = self.ROI.getHandles()[0].pos().y()
            except:
                return
            try:
                if x1_pos != 0:
                    self.ROI.endpoints[0].setPos(0, y1_pos)
                    x1_pos = 0
                if y1_pos != 0:
                    self.ROI.endpoints[0].setPos(x1_pos, 0)
                if x2_pos > 1:
                    self.ROI.endpoints[1].setPos(1, y2_pos)
                    x2_pos = 1
                else:
                    self.ROI.endpoints[1].setPos(x2_pos, y2_pos)
                if y2_pos > 1:
                    self.ROI.endpoints[1].setPos(x2_pos, 1)
                    y2_pos = 1
                else:
                    self.ROI.endpoints[1].setPos(x2_pos, y2_pos)
                self.ROI.stateChanged(finish=True)
                self.mousePressSig.emit()

            except:
                self.mousePressSig.emit()

        if evt.button() == 2:
            pass

        return

    def wheelEvent(self, ev):
        #empty function, but leave it as it overrides some other unwanted functionality.
        pass

    def keyPressEvent(self, ev):
        self.firstrelease = True
        astr = ev.key()
        self.keylist.append(astr)

    def keyReleaseEvent(self, ev):
        if self.firstrelease == True:
            self.processMultipleKeys(self.keylist)

        self.firstrelease = False

        try:    #complains about an index error for some reason.
            del self.keylist[-1]
        except:
            pass
        return

    def processMultipleKeys(self, keyspressed):
        if len(keyspressed) ==1:
            pass

        if len(keyspressed) == 2:
            pass

        if len(keyspressed) >=3:
            self.keylist = []
            return
