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
from PyQt5.QtWidgets import *
import subprocess

class LaminographyControlsWidget(QWidget):

    def __init__(self):
        super(LaminographyControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        button1size = 270       #long button (1 column)
        button12size = 200       #2/3 column button
        button2size = 143     #mid button (2 column)
        button33size = 98
        button3size = 93      #small button (almost third)
        button4size = 79     #textbox size (less than a third)

        self.elem = QComboBox(self)
        self.elem.setFixedWidth(button1size)

        self.method = QComboBox(self)
        self.method.setFixedWidth(button1size)
        methodname = ["lamni-fbp(cpu)","lamni-fbp(gpu)"]
        for k in range(len(methodname)):
            self.method.addItem(methodname[k])

        #TODO: get h5 working directory and go one level up.
        browse_lbl = QLabel("data path: ")
        self.browse = QPushButton("file path: /")
        self.browse.setFixedWidth(button1size)

        # recon_set_lbl = QLabel("reconstruction set")
        # recon_set_lbl.setFixedWidth(button2size)
        # self.recon_set = QComboBox(self)
        # self.recon_set.setFixedWidth(button2size)
        # self.recon_set.setToolTip("reconstruction group")

        recon_options_lbl = QLabel("reconstruction options")
        recon_options_lbl.setFixedWidth(button2size)
        self.recon_options = QComboBox(self)
        self.recon_options.setFixedWidth(button2size)
        options = ["step","try","full"]
        for k in range(len(options)):
            self.recon_options.addItem(options[k])

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget


        #Scroll Area Properties
        # self.scroll.setVerticalScrollBarPolicy(ScrollBarAlwaysOn)
        # self.scroll.setHorizontalScrollBarPolicy(ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        # self.scroll.setFixedWidth(button1size)
        self.populate_scroll_area()


        lami_angle_lbl = QLabel("laminography angle")
        lami_angle_lbl.setFixedWidth(button2size)
        self.lami_angle = QLineEdit("18.25")
        self.lami_angle.setFixedWidth(button2size)

        axis_center_lbl = QLabel("rotation axis center (x)")
        axis_center_lbl.setFixedWidth(button2size)
        self.axis_center = QLineEdit("0")
        self.axis_center.setFixedWidth(button2size)

        center_search_lbl = QLabel("center search width")
        center_search_lbl.setFixedWidth(button2size)
        self.center_search_width = QLineEdit("20")
        self.center_search_width.setFixedWidth(button2size)

        thresh_lbl = QLabel("Lower Threshold")
        thresh_lbl.setFixedWidth(button2size)
        self.thresh = QLineEdit("0.0")
        self.thresh.setFixedWidth(button2size)

        self.rec_btn = QPushButton('Reconstruct')
        self.rec_btn.setFixedWidth(button2size)
        self.lbl = QLabel("")
        self.lbl.setFixedWidth(button3size)
        self.rmHotspotBtn = QPushButton('remove hotspot')
        self.rmHotspotBtn.setFixedWidth(button2size)
        self.setThreshBtn = QPushButton('set L-threshold')
        self.setThreshBtn.setFixedWidth(button2size)
        self.recon_stats = QPushButton("recon stats")
        self.recon_stats.setFixedWidth(button2size)
        self.recon_all = QCheckBox("reconstruct all elements")
        self.recon_all.setChecked(False)

        # recon_set_box = QHBoxLayout()
        # recon_set_box.addWidget(recon_set_lbl)
        # recon_set_box.addWidget(self.recon_set)

        browse_box = QHBoxLayout()
        browse_box.addWidget(browse_lbl)
        browse_box.addWidget(self.browse)

        recon_options_box = QHBoxLayout()
        recon_options_box.addWidget(recon_options_lbl)
        recon_options_box.addWidget(self.recon_options)

        lami_angle_box = QHBoxLayout()
        lami_angle_box.addWidget(lami_angle_lbl)
        lami_angle_box.addWidget(self.lami_angle)

        axis_center_box = QHBoxLayout()
        axis_center_box.addWidget(axis_center_lbl)
        axis_center_box.addWidget(self.axis_center)

        search_widthBox = QHBoxLayout()
        search_widthBox.addWidget(center_search_lbl)
        search_widthBox.addWidget(self.center_search_width)

        threshBox = QHBoxLayout()
        threshBox.addWidget(thresh_lbl)
        threshBox.addWidget(self.thresh)

        reconBox = QHBoxLayout()
        reconBox.addWidget(self.rec_btn)
        reconBox.addWidget(self.recon_stats)

        postReconBox = QHBoxLayout()
        postReconBox.addWidget(self.rmHotspotBtn)
        postReconBox.addWidget(self.setThreshBtn)

        vb = QVBoxLayout()
        vb.addWidget(self.elem)
        vb.addWidget(self.method)
        vb.addLayout(browse_box)
        vb.addWidget(self.recon_all)
        vb.addWidget(self.lbl)
        vb.addWidget(self.scroll)

        vb.addLayout(recon_options_box)
        vb.addLayout(lami_angle_box)
        vb.addLayout(axis_center_box)
        vb.addLayout(search_widthBox)
        vb.addLayout(threshBox)
        vb.addLayout(reconBox)
        vb.addLayout(postReconBox)
        self.setLayout(vb)

    def populate_scroll_area(self):
        try:
            import tomocupy
            self.tcp_installed = True
            item_dict = self.op_parser()

        except:
            self.tcp_installed = False
            print("tomocupy not installed")
            return

        #item_dict[option] =  {type, description}
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        num_items = len(item_dict)
        for key in item_dict.keys():
            # op_dict[key] = [is_PATH[idx], is_FILE[idx], descriptions[idx], choices[idx],defaults[idx]]
            #[label] [text input / combobox] [QFileDialog*] [enable]
            lbl = QLabel(key)
            lbl.setToolTip(item_dict[key][2])

            if item_dict[key][0]:
                dialog_btn = QFileDialog.getExistingDirectory(self, "Open Folder", QtCore.QDir.currentPath())

            elif item_dict[key][1]:
                dialog_btn = QFileDialog.getOpenFileName(self, "Open Folder", QtCore.QDir.currentPath())

            else:
                pass

            #TODO: create comoboboxes if NOT (PATH or FILE), else create QLineEdit(Disabled)
            #TODO: set currentindex to default value



            self.vbox.addWidget(object)
        self.widget.setLayout(self.vbox)
        self.scroll.setWidget(self.widget)

    def op_parser(self):
        result = subprocess.check_output(["tomocupy", "recon_steps", "-h"]).decode().split("options:")[1]
        options = result.split("--")[1::]
        op_tmp = [i.replace("                       ","") for i in options]
        op_tmp = [i.replace("\r\n","") for i in op_tmp]
        op_tmp = [i.replace("  "," ") for i in op_tmp]
        op_tmp = [i.replace("  "," ") for i in op_tmp]
        op_tmp = [i.replace("  "," ") for i in op_tmp]
        keys = [i.split(" ")[0] for i in op_tmp]
        op_tmp = [" ".join(i.split(" ")[1::]).strip(" ") for i in op_tmp]
        default_tmp = [i.split("default: ") for i in op_tmp]

        defaults = []
        for i in default_tmp:
            if len(i)>1:
                default = i[-1].replace(")", "")
            else:
                default = None
            defaults.append(default)

        choices = []
        for i in op_tmp:
            idx_0 = i.find("{")
            idx_1 = i.find("}")
            if idx_0 == -1:
                choices.append(None)
            else:
                choices.append(i[idx_0 + 1:idx_1].split(","))

        op_tmp = [i.split("(default")[0] for i in op_tmp]
        op_tmp = [i.split("}")[::-1][0].strip("") for i in op_tmp]

        descriptions = []
        is_PATH = []
        is_FILE = []
        for i in op_tmp:
            first = i.split(" ")[0]
            if first.isupper():
                if first == "PATH":
                    is_PATH.append(True)
                else:
                    is_PATH.append(False)
                if first == "FILE":
                    is_FILE.append(True)
                else:
                    is_FILE.append(False)
                desc = " ".join(i.split(" ")[1::]).strip(" ")
                descriptions.append(desc)
            else:
                is_PATH.append(False)
                is_FILE.append(False)
                descriptions.append(i.strip(" "))

        op_dict = {}
        for idx, key in enumerate(keys):
            op_dict[key] = [is_PATH[idx], is_FILE[idx], descriptions[idx], choices[idx],defaults[idx]]
        return op_dict
