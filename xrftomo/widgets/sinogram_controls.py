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
class SinogramControlsWidget(QtWidgets.QWidget):

    def __init__(self):
        super(SinogramControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
         #__________Main control window for Alignment Tab__________
        button1size = 270       #long button (1 column)
        button12size = 200
        button2size = 143     #mid button (2 column)
        button33size = 98
        button3size = 93      #small button (almost third)
        button4size = 79     #textbox size (less than a third)

        self.combo1 = QtWidgets.QComboBox(self)
        self.combo1.setFixedWidth(button1size)

        self.scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.scroll.setWidgetResizable(True)
        self.populate_scroll_area()
        vb3 = QtWidgets.QVBoxLayout()
        vb3.addWidget(self.combo1)
        vb3.addWidget(self.scroll)


        self.setLayout(vb3)
        self.setMaximumWidth(290)

        #popup window for sinusoid tools
        self.populate_sine_controls()

        #popup window for hostpot tools
        self.populate_hs_controls()

    #__________Popup window for iterative alignment__________

        self.iter_parameters = QtWidgets.QWidget()
        self.iter_parameters.resize(275,400)
        self.iter_parameters.setWindowTitle('Iter Alignment Parameters')

        iter_label = QtWidgets.QLabel("iterations")
        iter_label.setFixedWidth(button2size)
        self.iter_textbox = QtWidgets.QLineEdit("5")
        self.iter_textbox.setFixedWidth(button2size)
        self.iter_textbox.returnPressed.connect(self.validate_parameters)

        padding_label = QtWidgets.QLabel("padding")
        padding_label.setFixedWidth(button2size)
        self.paddingX_textbox = QtWidgets.QLineEdit("0")
        self.paddingX_textbox.setFixedWidth(button4size)
        self.paddingX_textbox.returnPressed.connect(self.validate_parameters)
        self.paddingY_textbox = QtWidgets.QLineEdit("0")
        self.paddingY_textbox.setFixedWidth(button4size)
        self.paddingY_textbox.returnPressed.connect(self.validate_parameters)

        self.blur_checkbox = QtWidgets.QCheckBox("blur")
        self.blur_checkbox.setChecked(True)
        self.blur_checkbox.stateChanged.connect(self.blur_enable)
        self.blur_checkbox.setFixedWidth(button2size)

        inner_radius_label = QtWidgets.QLabel("inner Radius")
        inner_radius_label.setFixedWidth(button2size)
        self.inner_radius_textbox = QtWidgets.QLineEdit("0.8")
        self.inner_radius_textbox.setFixedWidth(button2size)
        self.inner_radius_textbox.returnPressed.connect(self.validate_parameters)

        outer_radius_label = QtWidgets.QLabel("outer Radius")
        outer_radius_label.setFixedWidth(button2size)
        self.outer_radius_textbox = QtWidgets.QLineEdit("0.9")
        self.outer_radius_textbox.setFixedWidth(button2size)
        self.outer_radius_textbox.returnPressed.connect(self.validate_parameters)

        center_label = QtWidgets.QLabel("center")
        center_label.setFixedWidth(button2size)
        self.center_textbox = QtWidgets.QLineEdit("")
        self.center_textbox.setFixedWidth(button2size)
        self.center_textbox.returnPressed.connect(self.validate_parameters)

        recon_alg_label = QtWidgets.QLabel("recon alg")
        recon_alg_label.setFixedWidth(button2size)
        align_alg_label = QtWidgets.QLabel("align alg")
        align_alg_label.setFixedWidth(button2size)
        self.joint_btn = QtWidgets.QPushButton("joint")
        self.joint_btn.setFixedWidth(button3size)
        self.joint_btn.setCheckable(True)
        self.joint_btn.setChecked(True)
        self.seq_btn = QtWidgets.QPushButton("seq")
        self.seq_btn.setFixedWidth(button3size)
        self.seq_btn.setCheckable(True)

        methodname = ["mlem", "art", "pml_hybrid", "pml_quad", "sirt", "tv"]
        self.recon_alg = QtWidgets.QComboBox()
        self.recon_alg.setFixedWidth(button2size)

        iter_group = QtWidgets.QButtonGroup(self)
        iter_group.addButton(self.joint_btn)
        iter_group.addButton(self.seq_btn)
        iter_group.setExclusive(True)

        for j in methodname:
            self.recon_alg.addItem(j)

        upsample_factor_label = QtWidgets.QLabel("upsample factor")
        self.upsample_factor_textbox = QtWidgets.QLineEdit("100")
        self.upsample_factor_textbox.setFixedWidth(button2size)
        self.upsample_factor_textbox.returnPressed.connect(self.validate_parameters)

        self.save_checkbox =QtWidgets.QCheckBox("save iterations")
        self.save_checkbox.setChecked(False)
        self.save_checkbox.setFixedWidth(button2size)

        self.debug_checkbox =QtWidgets.QCheckBox("debug checkbox")
        self.debug_checkbox.setChecked(True)
        self.debug_checkbox.setFixedWidth(button2size)

        self.run_alignmnet = QtWidgets.QPushButton("run alignment")
        self.run_alignmnet.setFixedWidth(button1size)

        hb00 = QtWidgets.QHBoxLayout()
        hb00.addWidget(iter_label)
        hb00.addWidget(self.iter_textbox)

        hb01 = QtWidgets.QHBoxLayout()
        hb01.addWidget(padding_label)
        hb01.addWidget(self.paddingX_textbox)
        hb01.addWidget(self.paddingY_textbox)

        hb02 = QtWidgets.QHBoxLayout()
        hb02.addWidget(inner_radius_label)
        hb02.addWidget(self.inner_radius_textbox)

        hb03 = QtWidgets.QHBoxLayout()
        hb03.addWidget(outer_radius_label)
        hb03.addWidget(self.outer_radius_textbox)

        hb04 = QtWidgets.QHBoxLayout()
        hb04.addWidget(upsample_factor_label)
        hb04.addWidget(self.upsample_factor_textbox)

        hb05 = QtWidgets.QHBoxLayout()
        hb05.addWidget(center_label)
        hb05.addWidget(self.center_textbox)

        hb06 = QtWidgets.QHBoxLayout()
        hb06.addWidget(recon_alg_label)
        hb06.addWidget(self.recon_alg)

        hb07 = QtWidgets.QHBoxLayout()
        hb07.addWidget(align_alg_label)
        hb07.addWidget(self.joint_btn)
        hb07.addWidget(self.seq_btn)

        vb00 = QtWidgets.QVBoxLayout()
        vb00.addLayout(hb00)
        vb00.addLayout(hb01)
        vb00.addWidget(self.blur_checkbox)
        vb00.addLayout(hb02)
        vb00.addLayout(hb03)
        vb00.addLayout(hb04)
        vb00.addLayout(hb05)
        vb00.addWidget(self.save_checkbox)
        vb00.addWidget(self.debug_checkbox)
        vb00.addLayout(hb06)
        vb00.addLayout(hb07)
        vb00.addWidget(self.run_alignmnet)

        #parameter setting logic

        if not self.blur_checkbox.isChecked():
            self.inner_radius_textbox.setEnabled(False)
            self.outer_radius_textbox.setEnabled(False)
            self.inner_radius_textbox = None
            self.outer_radius_textbox = None

        if self.blur_checkbox.isChecked():
            self.inner_radius_textbox.setEnabled(True)
            self.outer_radius_textbox.setEnabled(True)
            #pull up save dialogue
            #save sinograms to folder

        #split padding textbod entry into two integers
        #if len of split array is one, consider the second as zeros.
        #if len is greater than 2, enable warning icon next to textboxx
        #if empty, consider padding = 0,0

        #check that rin < rout:
        #if false, throw warning
        # if any > 1, throw warning,
        #if nany < 0, throw warning

        if self.center_textbox == "":
            self.center_textbox = None

        self.iter_parameters.setLayout(vb00)

    #__________Popup window for sinogram adjustmnet button__________


        self.sino_manip = QtWidgets.QWidget()
        self.sino_manip.resize(275,300)
        self.sino_manip.setWindowTitle('sinogram adjustment parameters')

        shift_label = QtWidgets.QLabel("shift up")
        slope_adjust_label = QtWidgets.QLabel("apply slope ")

        self.shift_textbox = QtWidgets.QLineEdit("0")
        self.slope_adjust_textbox = QtWidgets.QLineEdit("0")
        self.run_sino_adjust = QtWidgets.QPushButton("Run sinogram adjustments")

        hb11 = QtWidgets.QHBoxLayout()
        hb11.addWidget(shift_label)
        hb11.addWidget(self.shift_textbox)

        hb12 = QtWidgets.QHBoxLayout()
        hb12.addWidget(slope_adjust_label)
        hb12.addWidget(self.slope_adjust_textbox)

        vb10 = QtWidgets.QVBoxLayout()
        vb10.addLayout(hb11)
        vb10.addLayout(hb12)
        vb10.addWidget(self.run_sino_adjust)

        self.sino_manip.setLayout(vb10)


        #__________Popup window for move2edge button__________


        self.move2edge = QtWidgets.QWidget()
        self.move2edge.resize(275,300)
        self.move2edge.setWindowTitle('shift object to top/bottom edge')

        self.top_checkbox = QtWidgets.QCheckBox("move to top edge")
        self.top_checkbox.setChecked(True)

        self.bottom_checkbox = QtWidgets.QCheckBox("move to bottom edge")
        self.bottom_checkbox.setChecked(False)

        button_group = QtWidgets.QButtonGroup(self)
        button_group.addButton(self.top_checkbox)
        button_group.addButton(self.bottom_checkbox)
        button_group.setExclusive(True)

        threshold_label = QtWidgets.QLabel("threshold (1-100):")
        threshold_label.setFixedWidth(button2size)

        self.threshold_textbox = QtWidgets.QLineEdit("10")
        self.threshold_textbox.setFixedWidth(button2size)

        self.run_move2edge = QtWidgets.QPushButton("Run move2edge")
        self.run_move2edge.setFixedWidth(button1size)

        hb21 = QtWidgets.QHBoxLayout()
        hb21.addWidget(threshold_label)
        hb21.addWidget(self.threshold_textbox)

        vb20 = QtWidgets.QVBoxLayout()
        vb20.addWidget(self.top_checkbox)
        vb20.addWidget(self.bottom_checkbox)
        vb20.addLayout(hb21)
        vb20.addWidget(self.run_move2edge)

        self.move2edge.setLayout(vb20)

        #__________Popup window for center-find button__________   

        self.center_parameters = QtWidgets.QWidget()
        self.center_parameters.resize(275,300)
        self.center_parameters.setWindowTitle('center-finiding options')

        method = ["tomopy center-find", "Vacek's center-find"]
        self.options = QtWidgets.QComboBox()
        self.options.setFixedWidth(button1size)

        self.move2center = QtWidgets.QPushButton("Move to center")
        self.move2center.setFixedWidth(button1size)

        for j in method:
            self.options.addItem(j)

        self.stack1 = QtWidgets.QWidget()
        self.stack2 = QtWidgets.QWidget()

        self.stack1UI()
        self.stack2UI()

        self.Stack = QtWidgets.QStackedWidget (self)
        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.options)
        vbox.addWidget(self.Stack)
        vbox.addWidget(self.move2center)

        self.center_parameters.setLayout(vbox)
        self.options.currentIndexChanged.connect(self.display)

        #__________Popup window for PIRT button__________
        self.pirt_scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.pirt_scroll.setWidgetResizable(True)
        self.pirt_parameters = QtWidgets.QWidget()
        self.pirt_parameters.resize(310,300)
        self.pirt_parameters.setWindowTitle('Parallel Iterative Reconstruction for Tomography')
        widgetsizes = [300, 135, 75]
        pirt_dict = {}
        pirt_dict["ntau"] = [["label", "linedit"], "size of the object",None, None]
        pirt_dict["ntheta"] = [["label", "linedit"], "number of projection anlges", None, None]
        pirt_dict["anglefile"] = [["label", "file"], "hdf5 file containing projection angles", None, None]
        pirt_dict["sinofile"] = [["label", "file"], "hdf5 file containing sinograms", None, None]
        pirt_dict["nslices"] = [["label", "linedit"], "number of 3D slices", None, "1"]
        pirt_dict["nsubcomms"] = [["label", "linedit"], "number of concurrent solves", None, "1"]
        pirt_dict["overall_sweeps"] = [["label", "linedit"], "number of sweeps over all slices", None, "1"]
        pirt_dict["alt_outer_its"] = [["label", "linedit"], "number of outer iterations for alternating solve", None, "15"]
        pirt_dict["alt_sample_its"] = [["label", "linedit"], "number of (inner) iterations for sample solve", None, "5"]
        pirt_dict["alt_shifts_its"] = [["label", "linedit"], "number of (inner) iterations for shifts solve", None, "2"]
        pirt_dict["joint_its"] = [["label", "linedit"], "number of iterations for joint solve",None, "100"]
        pirt_dict["matfile"] = [["label", "file"], "petsc binary file containing the projection matrix", None, None]
        pirt_dict["joint"] = [["checkbox"], "enable joint CoR error correction", None, False]
        pirt_dict["alternating"] = [[ "checkbox"], "enable alternating CoR error correction", None, False]
        pirt_dict["regularize"] = [[ "checkbox"], "enable adaptive L1 regularization", None, False]
        pirt_dict["combine_mean"] = [[ "checkbox"], "combine shifts from concurrent solves via their mean", None, False]
        pirt_dict["combine_median"] = [[ "checkbox"], "combine shifts from concurrent solves via their median", None, False]
        pirt_dict["synthetic"] = [[ "checkbox"], "generate sinogram from sample before reconstruction", None, False]
        pirt_dict["run alignment"] = [["button"], "generate sinogram from sample before reconstruction", None, False]

        pirt_v_box = QVBoxLayout()
        for i, key in enumerate(pirt_dict.keys()):
            widget_items = pirt_dict[key][0]
            attrs = pirt_dict[key]
            widgetsize = widgetsizes[len(widget_items) - 1]

            pirt_line_num = "pirt_line_{}".format(i)
            setattr(self, pirt_line_num, QHBoxLayout())
            pirt_line = self.__dict__[pirt_line_num]

            for widget in widget_items:

                if widget == "file":
                    setattr(self, key, QPushButton())
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setText(attrs[3])
                    object.clicked.connect(self.get_file)
                    pirt_line.addWidget(object)
                elif widget == "button":
                    setattr(self, key, QPushButton(key))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    pirt_line.addWidget(object)
                elif widget == "checkbox":
                    setattr(self, key, QCheckBox(attrs[1]))
                    object = self.__dict__[key]
                    object.setFixedWidth(widgetsize)
                    object.setChecked(attrs[3])
                    pirt_line.addWidget(object)
                elif widget == "linedit":
                    name = key + "_lndt"
                    setattr(self, name, QLineEdit(attrs[3]))
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    pirt_line.addWidget(object)
                elif widget == "label":
                    name = key + "_lbl"
                    setattr(self, name, QLabel(key))
                    object = self.__dict__[name]
                    object.setFixedWidth(widgetsize)
                    object.setToolTip(attrs[1])
                    pirt_line.addWidget(object)
            pirt_v_box.addLayout(pirt_line)

        self.pirt_scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        pirt_v_box.setSpacing(0)
        pirt_v_box.setContentsMargins(0, 0, 0, 0)
        self.pirt_scroll_widget.setLayout(pirt_v_box)
        self.pirt_scroll.setWidget(self.pirt_scroll_widget)
        self.pirt_parameters.setLayout(pirt_v_box)
        #TODO: create function that creates widgets based on dictionary input.

    def get_file(self):
        try:
            sender = self.sender
            file = QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
            sender().setText(file)
        except:
            return
    def populate_hs_controls(self):
        self.hs_scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.hs_scroll.setWidgetResizable(True)
        line_dict = {}
        line_dict["hotspot_mode_chbx"] = ["checkbox","enable hotspot selection"]
        line_dict["hs_group"] = ["dropdown", "hotspot group", 5]
        line_dict["fit_line"] = ["button","fit to line"]
        line_dict["fit_sine"] = ["button","fit to sine"]
        line_dict["fit_y"] = ["button", "fit along Y"]
        line_dict["clear_data"] = ["button", "clear data"]
        vb_hs = QVBoxLayout()
        for key in line_dict.keys():
            attrs = line_dict[key]
            if attrs[0] == "dropdown":
                setattr(self, key, QComboBox())
                for i in range(5):
                    self.__dict__[key].addItem(str(i + 1))
                vb_hs.addWidget(self.__dict__[key])
            elif attrs[0] == "checkbox":
                setattr(self, key, QCheckBox(attrs[1]))
                vb_hs.addWidget(self.__dict__[key])
            else:
                setattr(self, key, QPushButton(key))
                vb_hs.addWidget(self.__dict__[key])

        self.hs_scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        vb_hs.setSpacing(0)
        vb_hs.setContentsMargins(0, 0, 0, 0)
        self.hs_scroll_widget.setLayout(vb_hs)
        self.hs_scroll.setWidget(self.hs_scroll_widget)

        self.hotspot_parameters = QtWidgets.QWidget()
        self.hotspot_parameters.resize(275, 400)
        self.hotspot_parameters.setWindowTitle('hotspot Alignment Parameters')
        layout = QVBoxLayout()
        layout.addWidget(self.hs_scroll)
        self.hotspot_parameters.setLayout(layout)
        return

    def populate_sine_controls(self):
        self.sino_scroll = QScrollArea()  # Scroll Area which contains the widgets, set as the centralWidget
        self.sino_scroll.setWidgetResizable(True)
        line_dict = {}
        line_dict["freq"] = ["frequency", "1"]
        line_dict["amp"] = ["amplitude", "10"]
        line_dict["phase"] = ["phase", "0"]
        line_dict["offst"] = ["offset", "0"]
        line_dict["set2line"] = [None, None]
        vb_sine = QVBoxLayout()
        for key in line_dict.keys():
            attrs = line_dict[key]
            if attrs[0] != None :
                line = QHBoxLayout()
                lbl = key+"_lbl"
                sld = key+"_sld"
                setattr(self, lbl, QLabel(attrs[0]))
                setattr(self,key, QLineEdit(attrs[1]))
                setattr(self, sld, QSlider())
                line.addWidget(self.__dict__[lbl])
                line.addWidget(self.__dict__[key])
                line.addWidget(self.__dict__[sld])
                vb_sine.addLayout(line)

            else:
                setattr(self, key, QPushButton(key))
                vb_sine.addWidget(self.__dict__[key])

        self.sino_scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        vb_sine.setSpacing(0)
        vb_sine.setContentsMargins(0, 0, 0, 0)
        self.sino_scroll_widget.setLayout(vb_sine)
        self.sino_scroll.setWidget(self.sino_scroll_widget)

        self.sino_parameters = QtWidgets.QWidget()
        self.sino_parameters.resize(275, 400)
        self.sino_parameters.setWindowTitle('sinusoid Alignment Parameters')
        layout = QVBoxLayout()
        layout.addWidget(self.sino_scroll)
        self.sino_parameters.setLayout(layout)
        return

    def populate_scroll_area(self):
        item_dict = {}  # [type(button, file, path, dropdown), descriptions[idx], choices[idx],defaults[idx]]

        item_dict["constrain_roi"] = ["checkbox", "constrain registration to ROI"]
        item_dict["constrain_x"] = ["checkbox", "do not shift along x axis"]
        item_dict["constrain_y"] = ["checkbox", "do not shift along y axis"]
        item_dict["cross_correlate_sinogram"] = ["button", "cross correlate sinogram slices"]
        item_dict["y_sum"] = ["button", "cross correlate sums along horizontal direction"]
        item_dict["dy_sum"] = ["button", "cross correlate difference of sums along horizontal direction"]
        item_dict["push2edge"] = ["button", "cross correlate difference of sums along horizontal direction"]
        item_dict["center_of_mass"] = ["button", "center of mass"]
        item_dict["xcor"] = ["button", "cross correlate"]
        item_dict["phasecor"] = ["button", "phas correlation"]
        item_dict["iterative"] = ["button", "iterative alignment"]
        item_dict["pirt"] = ["button", "pirt alignment"]
        item_dict["from_file"] = ["button", "align from text"]
        item_dict["adjust_sino"] = ["button", "tweak sinogram slope and position"]
        item_dict["center"] = ["button", "find and move to center of rotation"]
        item_dict["opflow"] = ["button", "optical flow alignment"]
        item_dict["change_rotation_axis"] = ["button", "redefine rotation axis"]
        item_dict["fit_peaks"] = ["button", "align to brightest spot"]
        item_dict["sinusoid_align"] = ["button", "define and manipulate sinusoid to align sinogram"]
        item_dict["hotspot_align"] = ["button", "select hostposts as fiducials to create a sine curve"]

        self.line_names = list(item_dict.keys())
        num_lines = len(self.line_names)

        for key in item_dict.keys():
            attrs = item_dict[key]
            if item_dict[key][0] == "checkbox":
                setattr(self, key, QCheckBox(attrs[1]))
            elif item_dict[key][0] == "button":
                setattr(self, key, QPushButton(key))
                self.__dict__[key].setToolTip(attrs[1])

        self.scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        for i in range(num_lines):
            line = self.__dict__[self.line_names[i]]
            line.objectName = self.line_names[i]
            self.vbox.addWidget(line)
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.scroll_widget.setLayout(self.vbox)
        self.scroll.setWidget(self.scroll_widget)

        self.iterative.setVisible(False)
        self.pirt.setVisible(False)
        self.opflow.setVisible(False)
        self.cross_correlate_sinogram.setVisible(False)
        self.dy_sum.setVisible(False)
        self.center.setVisible(False)
        self.phasecor.setVisible(False)
        self.adjust_sino.setVisible(False)
        self.change_rotation_axis.setVisible(False)
        return

    def populate_scroll_area2(self):
        #TODO: Two scroll widgets cannot share the same widget (i.e lamino-angle) so you have to show/hide only relevant options depending on method.

        #TODO: check if PIRT installed
        self.pirt_installed = True

        """
        if self.pirt_installed:
            item_dict = self.op_parser()
            self.line_names = list(item_dict.keys())
            num_lines = len(self.line_names)

            for key in item_dict.keys():
                attrs = item_dict[key]
                setattr(self, key, Line(key, attrs))

            self.scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
            self.vbox = QVBoxLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
            for i in range(num_lines):
                line = self.__dict__[self.line_names[i]]
                line.objectName = self.line_names[i]
                self.vbox.addWidget(line)
            self.vbox.setSpacing(0)
            self.vbox.setContentsMargins(0, 0, 0, 0)
            self.scroll_widget.setLayout(self.vbox)
            self.scroll.setWidget(self.scroll_widget)

        else:
            line_names = ["fbp-filter", "rotation-axis", "lamino-angle"]
            self.line_names = line_names
            item_dict = {}
            item_dict["fbp-filter"] = [False, False, "filter choice", ["ramp","shepp"], "shepp"]
            item_dict["rotation-axis"] = [False, False, "rotation axis given by x-position", None, ""]
            item_dict["lamino-angle"] = [False, False, "laminography tilt angle", None, "18.25"]
            for key in line_names:
                attrs = item_dict[key]
                setattr(self, key, Line(key, attrs))
            self.scroll_widget = QWidget()  # Widget that contains the collection of Vertical Box
            self.vbox = QVBoxLayout()  # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
            for i in range(len(line_names)):
                line = self.__dict__[line_names[i]]
                line.objectName = line_names[i]
                self.vbox.addWidget(line)
            self.vbox.setSpacing(0)
            self.vbox.setContentsMargins(0, 0, 0, 0)
            self.scroll_widget.setLayout(self.vbox)
            self.scroll.setWidget(self.scroll_widget)
        """

    def stack1UI(self):
        button1size = 250       #long button (1 column)
        button2size = 123     #mid button (2 column)
        button33size = 78.3
        button3size = 73.3      #small button (almost third)
        button4size = 59     #textbox size (less than a third)

        #options for tomopy center-finding algorithm
        slice_label = QtWidgets.QLabel("slice index")
        slice_label.setFixedWidth(button2size)
        self.slice_textbox = QtWidgets.QLineEdit("-1")
        self.slice_textbox.setFixedWidth(button2size)
        self.slice_textbox.returnPressed.connect(self.validate_move2center_parameters)

        init_label = QtWidgets.QLabel("init. guess for center")
        init_label.setFixedWidth(button2size)
        self.init_textbox = QtWidgets.QLineEdit(str("-1"))
        self.init_textbox.setFixedWidth(button2size)
        self.init_textbox.returnPressed.connect(self.validate_move2center_parameters)

        tol_label = QtWidgets.QLabel("sub-pix accuracy")
        tol_label.setFixedWidth(button2size)
        self.tol_textbox = QtWidgets.QLineEdit("0.5")
        self.tol_textbox.setFixedWidth(button2size)
        self.tol_textbox.returnPressed.connect(self.validate_move2center_parameters)

        self.mask_checkbox =QtWidgets.QCheckBox("mask")
        self.mask_checkbox.setChecked(False)
        self.mask_checkbox.setFixedWidth(button2size)
        self.mask_checkbox.stateChanged.connect(self.mask_enable)

        ratio_label = QtWidgets.QLabel("circular mask : recon. edge")
        ratio_label.setFixedWidth(button2size)
        self.ratio_textbox = QtWidgets.QLineEdit("1")
        self.ratio_textbox.setFixedWidth(button2size)
        self.ratio_textbox.returnPressed.connect(self.validate_move2center_parameters)

        self.find_center_1 = QtWidgets.QPushButton("Find rotation axis")
        self.find_center_1.setFixedWidth(button2size)
        self.center_1 = QtWidgets.QLabel("center: 0")
        self.center_1.setFixedWidth(button2size)

        hb01 = QtWidgets.QHBoxLayout()
        hb01.addWidget(slice_label)
        hb01.addWidget(self.slice_textbox)

        hb02 = QtWidgets.QHBoxLayout()
        hb02.addWidget(init_label)
        hb02.addWidget(self.init_textbox)

        hb03 = QtWidgets.QHBoxLayout()
        hb03.addWidget(tol_label)
        hb03.addWidget(self.tol_textbox)

        hb04 = QtWidgets.QHBoxLayout()
        hb04.addWidget(self.mask_checkbox)
        hb04.setAlignment(QtCore.Qt.AlignLeft)

        hb05 = QtWidgets.QHBoxLayout()
        hb05.addWidget(ratio_label)
        hb05.addWidget(self.ratio_textbox)

        hb06 = QtWidgets.QHBoxLayout()
        hb06.addWidget(self.find_center_1)
        hb06.addWidget(self.center_1)

        vb00 = QtWidgets.QVBoxLayout()
        vb00.addLayout(hb01)
        vb00.addLayout(hb02)
        vb00.addLayout(hb03)
        vb00.addLayout(hb04)
        vb00.addLayout(hb05)
        vb00.addLayout(hb06)

        self.stack1.setLayout(vb00)

    def stack2UI(self):
        button1size = 250       #long button (1 column)
        button2size = 123     #mid button (2 column)
        button33size = 78.3
        button3size = 73.3      #small button (almost third)
        button4size = 59     #textbox size (less than a third)

        modes = ["Mean","Median", "Local"]
        self.ave_mode = QtWidgets.QComboBox()
        self.ave_mode.setFixedWidth(button1size)

        for j in modes:
            self.ave_mode.addItem(j)

        limit_label = QtWidgets.QLabel("limit")
        limit_label.setFixedWidth(button2size)
        self.limit_textbox = QtWidgets.QLineEdit("-1")
        self.limit_textbox.setFixedWidth(button2size)
        self.limit_textbox.returnPressed.connect(self.validate_move2center_parameters)

        self.find_center_2 = QtWidgets.QPushButton("Find rotation axis.")
        self.find_center_2.setFixedWidth(button2size)
        self.center_2 = QtWidgets.QLabel("center: 0")
        self.center_2.setFixedWidth(button2size)

        hb11 = QtWidgets.QHBoxLayout()
        hb11.addWidget(limit_label)
        hb11.addWidget(self.limit_textbox)

        hb12 = QtWidgets.QHBoxLayout()
        hb12.addWidget(self.find_center_2)
        hb12.addWidget(self.center_2)

        vb10 = QtWidgets.QVBoxLayout()
        vb10.addLayout(hb11)
        vb10.addLayout(hb12)

        self.stack2.setLayout(vb10)

    def display(self,i):
        self.Stack.setCurrentIndex(i)

    def mask_enable(self):
        checked = self.mask_checkbox.isChecked()
        if checked:
            self.ratio_textbox.setEnabled(True)
        else:
            self.ratio_textbox.setEnabled(False)
            
    def blur_enable(self):
        checked = self.blur_checkbox.isChecked()
        if checked:
            self.inner_radius_textbox.setEnabled(True)
            self.outer_radius_textbox.setEnabled(True)
        else:
            self.inner_radius_textbox.setEnabled(False)
            self.outer_radius_textbox.setEnabled(False)


    def validate_move2center_parameters(self, init_center = None):
        valid = True
        if init_center == None:
            pass
        else:
            self.init_textbox.setText(str(init_center))
            return

        layout_stack = self.options.currentIndex()
        if layout_stack == 0: 

            try: #check slice index value
                slice_index = self.slice_textbox.text()
                if slice_index == "":
                    self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    slice_index = int(self.slice_textbox.text())
                    if slice_index%1 == 0 and slice_index >= 0:
                        slice_index = int(slice_index)
                        self.slice_textbox.setText(str(slice_index))
                        self.slice_textbox.setStyleSheet('* {background-color: }')
                    elif slice_index%1 != 0:
                        self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
                    else:
                        self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.slice_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
            
            try: #check initial guess
                init_center = self.init_textbox.text()
                if init_center == "":
                    self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    init_center = int(self.init_textbox.text())
                    if init_center%1 == 0 and init_center >= 0:
                        init_center = int(init_center)
                        self.init_textbox.setText(str(init_center))
                        self.init_textbox.setStyleSheet('* {background-color: }')
                    elif init_center%1 != 0:
                        self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
                    else:
                        self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.init_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

            try: #check tolerance
                tol = self.tol_textbox.text()
                if tol == "":
                    self.tol_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    tol = float(self.tol_textbox.text())
                    if tol > 0:
                        tol = float(tol)
                        self.tol_textbox.setText(str(tol))
                        self.tol_textbox.setStyleSheet('* {background-color: }')
                    else:
                        self.tol_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.tol_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

            try: #check ratio
                mask_enabled = self.mask_checkbox.isChecked()
                ratio = self.ratio_textbox.text()
                if ratio == "" and mask_enabled:
                    self.ratio_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
                else:
                    ratio = float(self.ratio_textbox.text())
                    if ratio > 0 and ratio <=1 and mask_enabled:
                        self.ratio_textbox.setText(str(ratio))
                        self.ratio_textbox.setStyleSheet('* {background-color: }')
                    elif not mask_enabled:
                        self.ratio_textbox.setStyleSheet('* {background-color: }')
                    else:
                        self.ratio_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.ratio_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

        if layout_stack == 1:

            try: #check iters value
                limit = self.limit_textbox.text()
                if limit == "":
                    self.limit_textbox.setStyleSheet('* {background-color: }')
                else:
                    limit = float(self.limit_textbox.text())
                    if limit > 0:
                        self.limit_textbox.setText(str(limit))
                        self.limit_textbox.setStyleSheet('* {background-color: }')
                    else:
                        self.limit_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                        valid = False
            except ValueError:
                valid = False
                self.limit_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

        return valid



    def validate_parameters(self):
        valid = True
        try: #check iters value
            iters = float(self.iter_textbox.text())
            if iters%1 == 0 and iters > 0:
                iters = int(iters)
                self.iter_textbox.setText(str(iters))
                self.iter_textbox.setStyleSheet('* {background-color: }')

            elif iters%1 != 0:
                self.iter_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                self.iter_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
        except ValueError:
            valid = False
            self.iter_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
        
        try: #check padding value
            padX = int(self.paddingX_textbox.text())
            padY = int(self.paddingY_textbox.text())
            if padX >=0 and padX% 1 == 0:
                self.paddingX_textbox.setStyleSheet('* {background-color: }')
            else:
                self.paddingX_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            if padY >=0 and padY% 1 == 0:
                self.paddingY_textbox.setStyleSheet('* {background-color: }')
            else:
                self.paddingY_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
        except ValueError:
            valid = False
            self.paddingX_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
            self.paddingY_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

        try: #check inner value
            inner = float(self.inner_radius_textbox.text())
            outer = float(self.outer_radius_textbox.text())
            blur_enabled = self.blur_checkbox.isChecked()
            if inner > 0 and inner <=1 and inner < outer and blur_enabled:
                self.inner_radius_textbox.setText(str(inner))
                self.inner_radius_textbox.setStyleSheet('* {background-color: }')

            elif not blur_enabled:
                self.inner_radius_textbox.setStyleSheet('* {background-color: }')

            else:
                self.inner_radius_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False

        except ValueError:
            valid = False
            self.inner_radius_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
        
        try: #check outer value
            outer = float(self.outer_radius_textbox.text())
            inner = float(self.inner_radius_textbox.text())
            blur_enabled = self.blur_checkbox.isChecked()

            if outer > 0 and outer <=1 and outer > inner and blur_enabled:
                self.outer_radius_textbox.setText(str(outer))
                self.outer_radius_textbox.setStyleSheet('* {background-color: }')

            elif not blur_enabled:
                self.outer_radius_textbox.setStyleSheet('* {background-color: }')

            else:
                self.outer_radius_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False

        except ValueError: 
            valid = False
            self.outer_radius_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
        
        try: #check center value
            center = self.center_textbox.text()
            if center == "":
                self.center_textbox.setStyleSheet('* {background-color: }')
            else:
                center = float(center)
                if center%1 == 0 and center > 0:
                    center = int(center)
                    self.center_textbox.setText(str(center))
                    self.center_textbox.setStyleSheet('* {background-color: }')
                else:
                    self.center_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                    valid = False
        except ValueError:
            valid = False
            self.center_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

        try: #check upsample value
            upsample_factor = float(self.upsample_factor_textbox.text())
            if upsample_factor%1 == 0 and upsample_factor > 0 and upsample_factor <=100:
                upsample_factor = int(upsample_factor)
                self.upsample_factor_textbox.setText(str(upsample_factor))
                self.upsample_factor_textbox.setStyleSheet('* {background-color: }')
            else:
                self.upsample_factor_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
        except ValueError:
            valid = False
            self.upsample_factor_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')



        try: #check sinogram shift value
            shift = float(self.shift_textbox.text())
            if shift%1 == 0:
                shift = int(shift)
                self.shift_textbox.setText(str(shift))
                self.shift_textbox.setStyleSheet('* {background-color: }')

            elif shift%1 != 0:
                self.shift_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                self.shift_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
        except ValueError:
            valid = False
            self.shift_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
        
        try: #check sinogram shift value
            slope = float(self.slope_adjust_textbox.text())
            if slope%1 == 0:
                slope = int(slope)
                self.slope_adjust_textbox.setText(str(slope))
                self.slope_adjust_textbox.setStyleSheet('* {background-color: }')

            elif slope%1 != 0:
                self.slope_adjust_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                self.slope_adjust_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
        except ValueError:
            valid = False
            self.slope_adjust_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')


        try: #check move2edge threshold value
            threshold = float(self.threshold_textbox.text())
            if threshold%1 == 0 and threshold>=1 and threshold<=100:
                threshold = int(threshold)
                self.threshold_textbox.setText(str(threshold))
                self.threshold_textbox.setStyleSheet('* {background-color: }')

            elif threshold%1 != 0:
                self.threshold_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
            else:
                self.threshold_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')
                valid = False
        except ValueError:
            valid = False
            self.threshold_textbox.setStyleSheet('* {background-color: rgb(255,200,200) }')

        return valid










