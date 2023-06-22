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


class ReconstructionControlsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ReconstructionControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        button1size = 270       #long button (1 column)
        button12size = 200       #2/3 column button
        button2size = 142.5     #mid button (2 column)
        button33size = 98.3
        button3size = 93.3      #small button (almost third)
        button4size = 78.75     #textbox size (less than a third)

        self.combo1 = QtWidgets.QComboBox(self)
        self.combo1.setFixedWidth(button1size)
        self.method = QtWidgets.QComboBox(self)
        self.method.setFixedWidth(button1size)
        self.recon_set = QtWidgets.QComboBox(self)
        self.recon_set.setFixedWidth(button2size)
        self.recon_set.setToolTip("reconstruction group")
        recon_set_lbl = QtWidgets.QLabel("reconstruction set")
        recon_set_lbl.setFixedWidth(button2size)


        self.btn = QtWidgets.QPushButton('Reconstruct')
        self.btn.setFixedWidth(button2size)
        self.lbl = QtWidgets.QLabel("")
        self.lbl.setFixedWidth(button3size)
        self.rmHotspotBtn = QtWidgets.QPushButton('remove hotspot')
        self.rmHotspotBtn.setFixedWidth(button2size)
        self.setThreshBtn = QtWidgets.QPushButton('set L-threshold')
        self.setThreshBtn.setFixedWidth(button2size)
        self.recon_stats = QtWidgets.QPushButton("recon stats")
        self.recon_stats.setFixedWidth(button2size)

        self.start_lbl = QtWidgets.QLabel("bottom row")
        self.start_lbl.setFixedWidth(button12size)
        self.start_indx = QtWidgets.QLineEdit("0")
        self.start_indx.setFixedWidth(button4size)
        self.end_lbl = QtWidgets.QLabel("top row")
        self.end_lbl.setFixedWidth(button12size)
        self.end_indx = QtWidgets.QLineEdit("0")
        self.end_indx.setFixedWidth(button4size)
        self.mid_lbl = QtWidgets.QLabel("middle row")
        self.mid_lbl.setFixedWidth(button12size)
        self.mid_indx = QtWidgets.QLineEdit("-1")
        self.mid_indx.setFixedWidth(button4size)
        self.mid_indx.setDisabled(True)

        # offst_top_lbl = QtWidgets.QLabel("centers offset top")
        # offst_top_lbl.setFixedWidth(button12size)
        # offst_bottom_lbl = QtWidgets.QLabel("centers offset top")
        # offst_bottom_lbl.setFixedWidth(button12size)
        # self.offst_top = QtWidgets.QLineEdit("0")
        # self.offst_top.setFixedWidth(button4size)
        # self.offst_bottom = QtWidgets.QLineEdit("0")
        # self.offst_bottom.setFixedWidth(button4size)

        self.recon_all = QtWidgets.QCheckBox("reconstruct all elements")
        self.recon_all.setChecked(False)
        self.recon_save = QtWidgets.QCheckBox("reconstruct & save simultaneously")
        self.recon_save.setChecked(False)


        self.mulBtn = QtWidgets.QPushButton("x 10")
        self.mulBtn.setFixedWidth(button2size)
        self.mulBtn.setVisible(False)
        self.divBtn = QtWidgets.QPushButton("/ 10")
        self.divBtn.setFixedWidth(button2size)
        self.divBtn.setVisible(False)
        self.maxLbl = QtWidgets.QLabel("Max")
        self.maxLbl.setFixedWidth(button2size)
        self.maxLbl.setVisible(False)
        self.minLbl = QtWidgets.QLabel("Min")
        self.minLbl.setFixedWidth(button2size)
        self.minLbl.setVisible(False)


        self.itersName = QtWidgets.QLabel("Iteration")
        self.itersName.setFixedWidth(button2size)
        self.betaName = QtWidgets.QLabel("Beta")
        self.betaName.setFixedWidth(button2size)
        self.deltaName = QtWidgets.QLabel("Delta")
        self.deltaName.setFixedWidth(button2size)
        self.lThreshLbl = QtWidgets.QLabel("Lower Threshold")
        self.lThreshLbl.setFixedWidth(button2size)

        self.iters = QtWidgets.QLineEdit("10")
        self.iters.setFixedWidth(button2size)
        self.beta = QtWidgets.QLineEdit("1")
        self.beta.setFixedWidth(button2size)
        self.delta = QtWidgets.QLineEdit("0.01")
        self.delta.setFixedWidth(button2size)
        self.lThresh = QtWidgets.QLineEdit("0.0")
        self.lThresh.setFixedWidth(button2size)

        self.maxText = QtWidgets.QLineEdit()
        self.maxText.setFixedWidth(button2size)
        self.maxText.setVisible(False)
        self.minText = QtWidgets.QLineEdit()
        self.minText.setFixedWidth(button2size)
        self.minText.setVisible(False)


        recon_setBox = QtWidgets.QHBoxLayout()
        recon_setBox.addWidget(recon_set_lbl)
        recon_setBox.addWidget(self.recon_set)


        startBox = QtWidgets.QHBoxLayout()
        startBox.addWidget(self.start_lbl)
        startBox.addWidget(self.start_indx)
        endBox = QtWidgets.QHBoxLayout()
        endBox.addWidget(self.end_lbl)
        endBox.addWidget(self.end_indx)
        midBox = QtWidgets.QHBoxLayout()
        midBox.addWidget(self.mid_lbl)
        midBox.addWidget(self.mid_indx)
        # offst_top_box = QtWidgets.QHBoxLayout()
        # offst_top_box.addWidget(offst_top_lbl)
        # offst_top_box.addWidget(self.offst_top)
        # offst_bottom_box = QtWidgets.QHBoxLayout()
        # offst_bottom_box.addWidget(offst_bottom_lbl)
        # offst_bottom_box.addWidget(self.offst_bottom)

        mdBox = QtWidgets.QHBoxLayout()
        mdBox.addWidget(self.mulBtn)
        mdBox.addWidget(self.divBtn)
        maxBox = QtWidgets.QHBoxLayout()
        maxBox.addWidget(self.maxLbl)
        maxBox.addWidget(self.maxText)
        minBox = QtWidgets.QHBoxLayout()
        minBox.addWidget(self.minLbl)

        itersBox = QtWidgets.QHBoxLayout()
        itersBox.addWidget(self.itersName)
        itersBox.addWidget(self.iters)
        betaBox = QtWidgets.QHBoxLayout()
        betaBox.addWidget(self.betaName)
        betaBox.addWidget(self.beta)
        deltaBox = QtWidgets.QHBoxLayout()
        deltaBox.addWidget(self.deltaName)
        deltaBox.addWidget(self.delta)
        threshBox = QtWidgets.QHBoxLayout()
        threshBox.addWidget(self.lThreshLbl)
        threshBox.addWidget(self.lThresh)
        reconBox = QtWidgets.QHBoxLayout()
        reconBox.addWidget(self.btn)
        reconBox.addWidget(self.recon_stats)

        postReconBox = QtWidgets.QHBoxLayout()
        # postReconBox.addWidget(self.equalizeBtn)
        postReconBox.addWidget(self.rmHotspotBtn)
        postReconBox.addWidget(self.setThreshBtn)


        vb = QtWidgets.QVBoxLayout()
        vb.addWidget(self.combo1)
        vb.addWidget(self.method)
        vb.addLayout(recon_setBox)
        vb.addLayout(endBox)
        vb.addLayout(startBox)
        vb.addLayout(midBox)
        # vb.addLayout(offst_top_box)
        # vb.addLayout(offst_bottom_box)
        vb.addWidget(self.recon_all)
        vb.addWidget(self.recon_save)
        vb.addWidget(self.lbl)
        vb.addLayout(mdBox)
        vb.addLayout(maxBox)
        vb.addLayout(minBox)
        vb.addLayout(itersBox)
        vb.addLayout(betaBox)
        vb.addLayout(deltaBox)
        vb.addLayout(threshBox)
        vb.addLayout(reconBox)
        vb.addLayout(postReconBox)

        
        self.setLayout(vb)
