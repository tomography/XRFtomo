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


class LaminographyControlsWidget(QtWidgets.QWidget):

    def __init__(self):
        super(LaminographyControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        button1size = 270       #long button (1 column)
        button12size = 200       #2/3 column button
        button2size = 142.5     #mid button (2 column)
        button33size = 98.3
        button3size = 93.3      #small button (almost third)
        button4size = 78.75     #textbox size (less than a third)

        self.elem = QtWidgets.QComboBox(self)
        self.elem.setFixedWidth(button1size)

        self.method = QtWidgets.QComboBox(self)
        self.method.setFixedWidth(button1size)
        methodname = ["lamni-fbp(cpu)","lamni-fbp(gpu)"]
        for k in range(len(methodname)):
            self.method.addItem(methodname[k])

        recon_set_lbl = QtWidgets.QLabel("reconstruction set")
        recon_set_lbl.setFixedWidth(button2size)
        self.recon_set = QtWidgets.QComboBox(self)
        self.recon_set.setFixedWidth(button2size)
        self.recon_set.setToolTip("reconstruction group")

        recon_options_lbl = QtWidgets.QLabel("reconstruction options")
        recon_options_lbl.setFixedWidth(button2size)
        self.recon_options = QtWidgets.QComboBox(self)
        self.recon_options.setFixedWidth(button2size)
        options = ["step","try","full"]
        for k in range(len(options)):
            self.recon_options.addItem(options[k])

        #TODO: add filename textbox?

        lami_angle_lbl = QtWidgets.QLabel("laminography angle")
        lami_angle_lbl.setFixedWidth(button2size)
        self.lami_angle = QtWidgets.QLineEdit("18.25")
        self.lami_angle.setFixedWidth(button2size)

        axis_center_lbl = QtWidgets.QLabel("rotation axis center (x)")
        axis_center_lbl.setFixedWidth(button2size)
        self.axis_center = QtWidgets.QLineEdit("0")
        self.axis_center.setFixedWidth(button2size)

        center_search_lbl = QtWidgets.QLabel("center search width")
        center_search_lbl.setFixedWidth(button2size)
        self.center_search_width = QtWidgets.QLineEdit("20")
        self.center_search_width.setFixedWidth(button2size)

        thresh_lbl = QtWidgets.QLabel("Lower Threshold")
        thresh_lbl.setFixedWidth(button2size)
        self.thresh = QtWidgets.QLineEdit("0.0")
        self.thresh.setFixedWidth(button2size)

        self.rec_btn = QtWidgets.QPushButton('Reconstruct')
        self.rec_btn.setFixedWidth(button2size)
        self.lbl = QtWidgets.QLabel("")
        self.lbl.setFixedWidth(button3size)
        self.rmHotspotBtn = QtWidgets.QPushButton('remove hotspot')
        self.rmHotspotBtn.setFixedWidth(button2size)
        self.setThreshBtn = QtWidgets.QPushButton('set L-threshold')
        self.setThreshBtn.setFixedWidth(button2size)
        self.recon_stats = QtWidgets.QPushButton("recon stats")
        self.recon_stats.setFixedWidth(button2size)
        self.recon_all = QtWidgets.QCheckBox("reconstruct all elements")
        self.recon_all.setChecked(False)

        recon_set_box = QtWidgets.QHBoxLayout()
        recon_set_box.addWidget(recon_set_lbl)
        recon_set_box.addWidget(self.recon_set)

        recon_options_box = QtWidgets.QHBoxLayout()
        recon_options_box.addWidget(recon_options_lbl)
        recon_options_box.addWidget(self.recon_options)

        lami_angle_box = QtWidgets.QHBoxLayout()
        lami_angle_box.addWidget(lami_angle_lbl)
        lami_angle_box.addWidget(self.lami_angle)

        axis_center_box = QtWidgets.QHBoxLayout()
        axis_center_box.addWidget(axis_center_lbl)
        axis_center_box.addWidget(self.axis_center)

        search_widthBox = QtWidgets.QHBoxLayout()
        search_widthBox.addWidget(center_search_lbl)
        search_widthBox.addWidget(self.center_search_width)

        threshBox = QtWidgets.QHBoxLayout()
        threshBox.addWidget(thresh_lbl)
        threshBox.addWidget(self.thresh)

        reconBox = QtWidgets.QHBoxLayout()
        reconBox.addWidget(self.rec_btn)
        reconBox.addWidget(self.recon_stats)

        postReconBox = QtWidgets.QHBoxLayout()
        postReconBox.addWidget(self.rmHotspotBtn)
        postReconBox.addWidget(self.setThreshBtn)

        vb = QtWidgets.QVBoxLayout()
        vb.addWidget(self.elem)
        vb.addWidget(self.method)
        vb.addLayout(recon_set_box)
        vb.addWidget(self.recon_all)
        vb.addWidget(self.lbl)

        vb.addLayout(recon_options_box)
        vb.addLayout(lami_angle_box)
        vb.addLayout(axis_center_box)
        vb.addLayout(search_widthBox)
        vb.addLayout(threshBox)
        vb.addLayout(reconBox)
        vb.addLayout(postReconBox)
        self.setLayout(vb)
