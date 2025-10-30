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
import xrftomo

class LaminographyTomocupy(QWidget):

    def __init__(self, parent):
        super(LaminographyTomocupy, self).__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        button1size = self.parent.button1size       #long button (1 column)

        self.populate_scroll_area()
        vb = QVBoxLayout()
        vb.addWidget(self.tomocupy_scroll)
        self.setLayout(vb)
        self.setMinimumWidth(button1size)

    def populate_scroll_area(self):
        self.tomocupy_scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.tomocupy_scroll.setWidgetResizable(True)

        item_dict = {}
        item_dict["browse"] = [["label","path"], "location where data is stored", None, ""]
        item_dict["generate"] = [["label","button"], "generate folder structure in data path", None, None]
        item_dict["fbp-filter"] = [["label","dropdown"], "filter choice", ["ramp", "shepp"], "shepp"]
        item_dict["rotation-axis"] = [["label","linedit"], "rotation axis given by x-position", None, ""]
        item_dict["lamino-angle"] = [["label","linedit"], "laminography tilt angle", None, "18.25"]

        # Check if tomocupy is available - this allows debugger to stop properly
        import importlib
        import warnings
        import subprocess
        
        # Method 1: Check if tomocupy command is available (avoids pkg_resources warning)
        def check_tomocupy_command():
            try:
                result = subprocess.run(["tomocupy", "--help"], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                return False
        
        # Method 2: Check if module can be imported (with warning suppression)
        def check_tomocupy_module():
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
                try:
                    tomocupy_spec = importlib.util.find_spec("tomocupy")
                    return tomocupy_spec is not None
                except Exception:
                    return False
        
        # Use command check first (cleaner), fallback to module check
        tomocupy_available = check_tomocupy_command() or check_tomocupy_module()
        
        # Alternative approach: Simple try-except with explicit breakpoint
        tomocupy = None
        if tomocupy_available:
            try:
                # Suppress warnings during import
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    import tomocupy
                    print("DEBUG: tomocupy imported successfully")
            except ImportError as e:
                print(f"DEBUG: tomocupy import failed: {e}")
                tomocupy = None
        else:
            print("DEBUG: tomocupy not available")
        try:
            # Check if tomocupy is properly installed and functional
            if tomocupy is not None:
                tomocupy_dict = self.op_parser()
                self.tcp_installed = True
                widget_dict = item_dict | tomocupy_dict 
            else:
                raise ImportError("tomocupy module not found")
        except Exception as e:
            self.tcp_installed = False
            print(f"tomocupy not installed or not functional: {e}")
            print("using CPU settings")
            widget_dict = item_dict 


        vb_lami = self.create_widgets(widget_dict)
        self.tomocupy_widget = QWidget()  # Widget that contains the collection of Vertical Box
        vb_lami.setSpacing(0)
        vb_lami.setContentsMargins(0, 0, 0, 0)
        self.tomocupy_widget.setLayout(vb_lami)
        self.tomocupy_scroll.setWidget(self.tomocupy_widget)

        return

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

        op_dict = {}
        for key in keys:
            op_dict[key] = [None, None, None, None]

        for i, line in enumerate(default_tmp):
            key = list(op_dict.keys())[i]
            if len(line)>1:
                default = line[-1].replace(")", "")

            else:
                default = None
            op_dict[key][3] = default

        for i, line in enumerate(op_tmp):
            key = list(op_dict.keys())[i]
            idx_0 = line.find("{")
            idx_1 = line.find("}")
            if idx_0 == -1:
                choice = None
            else:
                choice = line[idx_0 + 1:idx_1].split(",")
            op_dict[key][2] = choice

        op_tmp = [i.split("(default")[0] for i in op_tmp]
        op_tmp = [i.split("}")[::-1][0].strip("") for i in op_tmp]

        for i, line in enumerate(op_tmp):
            key = list(op_dict.keys())[i]
            first = line.split(" ")[0]
            if first.isupper():
                if first == "PATH":
                    op_dict[key][0] = ["label", "path"]
                elif first == "FILE":
                    op_dict[key][0] = ["label", "file"]
                else:
                    op_dict[key][0] = ["label", "linedit"]
                desc = " ".join(line.split(" ")[1::]).strip(" ")
                op_dict[key][1] = desc
            else:
                if op_dict[key][2] is not None:
                    op_dict[key][0] = ["label", "dropdown"]
                else:
                    op_dict[key][0] = ["label", "linedit"]
                desc = line.strip(" ")
                op_dict[key][1] = desc

        return op_dict

    def create_widgets(self,item_dict):
        widgetsizes = [240, 115, 50]
        vb_lami = QVBoxLayout()
        self.num_lines= len(item_dict.keys())
        self.line_names = []
        for i, key in enumerate(item_dict.keys()):
            widget_items = item_dict[key][0]
            attrs = item_dict[key]
            widgetsize = widgetsizes[len(widget_items)-1]

            self.line_names.append(key)

            line_num = "line_{}".format(i)
            setattr(self, line_num, QHBoxLayout())
            line = self.__dict__[line_num]

            for widget in widget_items:
                #TODO: add line number and extra button to each line
                if widget == "dropdown":
                    setattr(self, key, QComboBox())
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    options = attrs[2]
                    default = attrs[3]
                    for option in options:
                        object.addItem(option)
                    # Check if default value exists in options list
                    if default in options:
                        idx = options.index(default)
                        object.setCurrentIndex(idx)
                    else:
                        # If default is not in options, set to first option or 0
                        object.setCurrentIndex(0)
                    line.addWidget(object)

                elif widget == "label":
                    name = key+"_lbl"
                    setattr(self, name, QLabel())
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    object.setToolTip(attrs[1])
                    object.setText(key)
                    line.addWidget(object)

                elif widget == "linedit":
                    setattr(self, key, QLineEdit())
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText(attrs[3])
                    line.addWidget(object)

                elif widget == "checkbox":
                    setattr(self, key, QCheckBox(attrs[1]))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setChecked(attrs[3])
                    line.addWidget(object)

                elif widget == "button":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    line.addWidget(object)

                elif widget == "file":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText(attrs[3])
                    object.clicked.connect(self.get_file)
                    line.addWidget(object)

                elif widget == "path":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText(attrs[3])
                    object.clicked.connect(self.get_path)
                    line.addWidget(object)
                else:
                    print("invalid option")

            button_name = "btn_{}".format(i)
            setattr(self, button_name, QPushButton("+"))
            line_btn = self.__dict__[button_name]
            line_btn.setCheckable(True)
            line_btn.setObjectName(str(button_name))
            line_btn.setFixedWidth(25)
            line.addWidget(line_btn)
            vb_lami.addLayout(line)
        return vb_lami

    def get_file(self):
        try:
            sender = self.sender
            file = QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
            sender().setText(file)
        except:
            return

    def get_path(self):
        sender = self.sender
        path = QFileDialog.getExistingDirectory(self, "Open Directory", QtCore.QDir.currentPath())
        sender().setText(path)

