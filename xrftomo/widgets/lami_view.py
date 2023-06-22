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


from PyQt5.QtCore import pyqtSignal
import pyqtgraph

class LamiView(pyqtgraph.GraphicsLayoutWidget):
    # shiftSig = pyqtSignal(str, name='sliderChangedSig')
    mouseMoveSig = pyqtSignal(int,int, name= 'mouseMoveSig')
    keyPressSig = pyqtSignal(str, name= 'keyPressSig')

    def __init__(self, parent):
        super(LamiView, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.p1 = self.addPlot(enableMouse = False)
        self.projView = pyqtgraph.ImageItem()
        self.projView.rotate(-90)
        self.p1.addItem(self.projView)
        self.p1.scene().sigMouseMoved.connect(self.mouseMoved)
        self.p1.scene().sceneRectChanged.connect(self.windowResize)
        self.p1.setMouseEnabled(x=False, y=False)

    def windowResize(self, evt):
        pass

    def mouseMoved(self, evt):
        self.moving_x = int(round(self.p1.vb.mapSceneToView(evt).x()))
        self.moving_y = int(round(self.p1.vb.mapSceneToView(evt).y()))
        self.mouseMoveSig.emit(self.moving_x, self.moving_y)

    def wheelEvent(self, ev): 
        #empty function, but leave it as it overrides some other unwanted functionality. 
        pass
