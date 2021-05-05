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


from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
# from matplotlib.figure import Figure
import pyqtgraph
import xrftomo

class MiniReconView(pyqtgraph.GraphicsLayoutWidget):

    def __init__(self):
    # def __init__(self, parent):
        super(MiniReconView, self).__init__()
        self.keylist = []
        self.initUI()

    def initUI(self):
        custom_vb = xrftomo.CustomViewBox()
        custom_vb.disableAutoRange(axis="xy")
        custom_vb.setRange(xRange=(0,1), yRange=(0,1), padding=0)
        # custom_vb.invertY(True)

        #___________________ reconstruction view ___________________
        self.p2 = self.addPlot(viewBox = custom_vb, enableMouse = False)
        self.p2.setAutoPan(x=None, y=None)
        self.reconView = pyqtgraph.ImageItem(axisOrder = "row-major")
        self.barView = pyqtgraph.BarGraphItem(x=[0], height=[1], width=9)
        self.p2.addItem(self.reconView)
        self.p2.addItem(self.barView)
        self.p2.setMouseEnabled(x=False, y=False)
        self.p2.vb = custom_vb
