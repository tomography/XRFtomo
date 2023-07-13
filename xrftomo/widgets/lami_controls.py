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

        self.browse_lbl = QLabel("data path: ")
        self.browse = QPushButton("file path: /")
        self.browse.setFixedWidth(button1size)

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.scroll2 = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget

        self.scroll.setWidgetResizable(True)
        self.scroll2.setWidgetResizable(True)
        self.populate_scroll_area()

        self.generate_lbl = QLabel("Generate folder structure in data path")
        self.generate_lbl.setFixedWidth(button12size)
        self.generate = QPushButton("generate")
        self.generate.setFixedWidth(button3size)

        self.show_ops = QPushButton("show more")
        self.show_ops.setCheckable(True)
        self.show_ops.setChecked(False)
        self.show_ops.setFixedWidth(button3size)

        self.rec_btn = QPushButton('Reconstruct')
        self.rec_btn.setFixedWidth(button2size)
        self.lbl = QLabel("")
        self.lbl.setFixedWidth(button3size)
        self.rmHotspotBtn = QPushButton('remove hotspot')
        self.rmHotspotBtn.setFixedWidth(button2size)
        self.recon_stats = QPushButton("recon stats")
        self.recon_stats.setFixedWidth(button2size)
        self.recon_all = QCheckBox("reconstruct all elements")
        self.recon_all.setChecked(False)

        browse_box = QHBoxLayout()
        browse_box.addWidget(self.browse_lbl)
        browse_box.addWidget(self.browse)

        generate_box = QHBoxLayout()
        generate_box.addWidget(self.generate_lbl)
        generate_box.addWidget(self.generate)

        reconBox = QHBoxLayout()
        reconBox.addWidget(self.rec_btn)
        reconBox.addWidget(self.recon_stats)

        postReconBox = QHBoxLayout()
        postReconBox.addWidget(self.rmHotspotBtn)

        vb = QVBoxLayout()
        vb.addWidget(self.elem)
        vb.addWidget(self.method)
        vb.addLayout(browse_box)
        vb.addLayout(generate_box)
        vb.addWidget(self.recon_all)
        vb.addWidget(self.show_ops)
        vb.addWidget(self.lbl)
        vb.addWidget(self.scroll)
        vb.addWidget(self.scroll2)
        vb.addLayout(reconBox)
        vb.addLayout(postReconBox)
        self.setLayout(vb)

    def populate_scroll_area(self):
        self.line_names = []
        try:
            import tomocupy
            self.tcp_installed = True
            item_dict = self.op_parser()
            self.line_names = list(item_dict.keys())
            num_lines = len(self.line_names)

            for key in item_dict.keys():
                attrs = item_dict[key]
                setattr(self, key, Line(key, attrs))

            self.scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
            vbox = QVBoxLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
            for i in range(num_lines):
                line = self.__dict__[self.line_names[i]]
                line.objectName = self.line_names[i]
                vbox.addWidget(line)
            vbox.setSpacing(0)
            vbox.setContentsMargins(0, 0, 0, 0)

            self.scroll_widget.setLayout(vbox)
            self.scroll.setWidget(self.scroll_widget)
        except:
            self.tcp_installed = False
            print("tomocupy not installed, using CPU settings")

        line_names = ["fbp-filter", "rotation-axis", "lamino-angle"]
        # op_dict[key] = [is_PATH[idx], is_FILE[idx], descriptions[idx], choices[idx],defaults[idx]]
        item_dict = {}
        item_dict["fbp-filter"] = [False, False, "filter choice", ["ramp","shepp"], "shepp"]
        item_dict["rotation-axis"] = [False, False, "rotation axis given by x-position", None, ""]
        item_dict["lamino-angle"] = [False, False, "laminography tilt angle", None, "18.25"]
        for key in line_names:
            attrs = item_dict[key]
            setattr(self, key, Line(key, attrs))
        self.scroll_widget2 = QWidget()  # Widget that contains the collection of Vertical Box
        vbox = QVBoxLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        for i in range(len(line_names)):
            line = self.__dict__[line_names[i]]
            line.objectName = line_names[i]
            vbox.addWidget(line)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.scroll_widget2.setLayout(vbox)
        self.scroll2.setWidget(self.scroll_widget2)

    def op_parser(self):
        result = subprocess.check_output(["tomocupy", "recon_steps", "-h"]).decode().split("options:")[1]
        options = result.split("--")[2::]
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


class Line(QtWidgets.QWidget):
    def __init__(self, name, attrs):
        super(Line, self).__init__()
        self.attrs = attrs

        hbox = QHBoxLayout()

        # op_dict[key] = [is_PATH[idx], is_FILE[idx], descriptions[idx], choices[idx],defaults[idx]]
        #[QFileDilog / Label] [text input / combobox]  [enable]

        if attrs[0]:
            self.item1 = QPushButton(name)
            self.item1.clicked.connect(self.get_path)
            self.item2 = QLineEdit(attrs[4])
        elif attrs[1]:
            self.item1 = QPushButton(name)
            self.item1.clicked.connect(self.get_file)
            self.item2 = QLineEdit(attrs[4])
        elif attrs[3] is None:
            self.item1 = QLabel(name)
            self.item2 = QLineEdit("")
            self.item2.setToolTip(str(attrs[2]))
        else:
            self.item1 = QLabel(name)
            self.item1.setToolTip(attrs[2])
            self.item2 = QComboBox()
            self.item2.setToolTip(str(attrs[2]))
            for option in attrs[3]:
                self.item2.addItem(option)
        #TODO: set currentndex to default value

        self.item3 = QPushButton("+")
        # item3.setChecked(False)
        self.item3.setCheckable(True)
        self.item3.setObjectName(str(name))
        self.item3.setToolTip(str(attrs[2]))

        self.item1.setFixedWidth(120)
        self.item2.setFixedWidth(120)
        self.item3.setFixedWidth(25)
        hbox.addWidget(self.item1)
        hbox.addWidget(self.item2)
        hbox.addWidget(self.item3)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0,0,0,0)
        self.setLayout(hbox)
        self.setContentsMargins(0,0,0,0)
    def get_file(self):
        sender = self.sender
        file = QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
        pass

    def get_path(self):
        sender = self.sender
        path = QFileDialog.getExistingDirectory(self, "Open Directory", QtCore.QDir.currentPath())
        pass
