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
class ReconstructionControlsWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ReconstructionControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
        button1size = 270       #long button (1 column)
        button12size = 200       #2/3 column button
        button2size = 143     #mid button (2 column)
        button33size = 98
        button3size = 93      #small button (almost third)
        button4size = 79     #textbox size (less than a third)

        self.combo1 = QtWidgets.QComboBox(self)
        self.combo1.setFixedWidth(button1size)

        self.populate_scroll_area()

        self.middle_row_lbl.setVisible(False)
        self.middle_row_lbl.setVisible(False)
        self.beta_lbl.setVisible(False)
        self.delta_lbl.setVisible(False)
        self.lower_thresh_lbl.setVisible(False)
        self.beta.setVisible(False)
        self.delta.setVisible(False)
        self.lower_thresh.setVisible(False)

        vb = QtWidgets.QVBoxLayout()
        vb.addWidget(self.combo1)
        vb.addWidget(self.recon_scroll)

        self.setLayout(vb)
    def populate_scroll_area(self):
        self.recon_scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.recon_scroll.setWidgetResizable(True)
        item_dict = {} #[type(button, file, path, dropdown), descriptions[idx], choices[idx],defaults[idx]]
        item_dict["method"] = ["dropdown", "reconstruction methods"]
        item_dict["top_row"] = ["label", "index of top cross section to reconstruct"]
        item_dict["middle_row"] = ["label", "index of top middle cross section to reconstruct"]
        item_dict["bottom_row"] = ["label", "index of lower middle cross section to reconstruct"]
        item_dict["iteration"] = ["label", "number of reconsturction iteration"]
        item_dict["recon_all"] = ["checkbox", "reconstruct all loaded elements"]
        item_dict["recon_save"] = ["checkbox", "reconstruct and save simultaneously"]
        item_dict["beta"] = ["label", "mlem parameter"]
        item_dict["delta"] = ["label", "mlem parameter"]
        item_dict["lower_thresh"] = ["label", "cut-off display value"]
        item_dict["reconstruct"] = ["button", "run reconstruction"]
        item_dict["recon_stats"] = ["button", "show reconstruction statisticks"]
        item_dict["remove_hotspot"] = ["button", "remove hotspots from reconstruction"]

        vb_recon = QVBoxLayout()
        for key in item_dict.keys():
            widget_type = item_dict[key][0]
            attrs = item_dict[key]
            if widget_type == "dropdown":
                setattr(self, key, QComboBox())
                vb_recon.addWidget(self.__dict__[key])
            elif widget_type == "label":
                line = QHBoxLayout()
                lbl = key + "_lbl"
                setattr(self, lbl, QLabel(key))
                setattr(self, key, QLineEdit(""))
                line.addWidget(self.__dict__[lbl])
                line.addWidget(self.__dict__[key])
                vb_recon.addLayout(line)
            if widget_type == "checkbox":
                setattr(self, key, QCheckBox(attrs[1]))
                vb_recon.addWidget(self.__dict__[key])
            elif widget_type == "button":
                setattr(self, key, QPushButton(key))
                vb_recon.addWidget(self.__dict__[key])
                self.__dict__[key].setToolTip(attrs[1])

        self.recon_scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        vb_recon.setSpacing(0)
        vb_recon.setContentsMargins(0, 0, 0, 0)
        self.recon_scroll_widget.setLayout(vb_recon)
        self.recon_scroll.setWidget(self.recon_scroll_widget)
        return