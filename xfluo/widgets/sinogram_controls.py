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


class SinogramControlsWidget(QtWidgets.QWidget):

    def __init__(self):
        super(SinogramControlsWidget, self).__init__()
        self.initUI()

    def initUI(self):
         #__________Main control window for Alignment Tab__________
        button1size = 250
        button2size = 122.5
        button33size = 78.3
        button3size = 73.3
        button4size = 58.75

        self.combo1 = QtWidgets.QComboBox(self)
        self.combo1.setFixedWidth(button1size)
        self.combo2 = QtWidgets.QComboBox(self)
        self.combo2.setFixedWidth(button1size)

        self.btn1 = QtWidgets.QPushButton('center of mass')
        self.btn1.setFixedWidth(button2size)
        self.btn2 = QtWidgets.QPushButton('x corr.')
        self.btn2.setFixedWidth(button2size)
        self.btn3 = QtWidgets.QPushButton('phase corr.')
        self.btn3.setFixedWidth(button2size)
        self.btn5 = QtWidgets.QPushButton('move2edge')
        self.btn5.setFixedWidth(button2size)
        self.btn6 = QtWidgets.QPushButton('iter align')
        self.btn6.setFixedWidth(button2size)
        self.btn7 = QtWidgets.QPushButton('align from txt')
        self.btn7.setFixedWidth(button2size)
        self.btn9 = QtWidgets.QPushButton('adjust_sino')
        self.btn9.setFixedWidth(button2size)

        self.lbl = QtWidgets.QLabel("")
        self.lbl.setFixedWidth(button2size)
        self.combo2.setVisible(False)

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(self.btn1)

        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.btn2)
        hb2.addWidget(self.btn3)

        hb3 = QtWidgets.QHBoxLayout()
        hb3.addWidget(self.btn6)
        hb3.addWidget(self.btn7)

        hb4 = QtWidgets.QHBoxLayout()
        hb4.addWidget(self.btn5)
        hb4.addWidget(self.btn9)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addLayout(hb1)
        vb1.addLayout(hb2)
        vb1.addLayout(hb3)
        vb1.addLayout(hb4)

        vb3 = QtWidgets.QVBoxLayout()
        vb3.addWidget(self.combo1)
        vb3.addWidget(self.combo2)
        vb3.addLayout(vb1)
        self.setFixedWidth(275)
        self.setLayout(vb3)

        #__________Popup window for iterative alignment__________

        self.iter_parameters = QtWidgets.QWidget()
        self.iter_parameters.resize(275,400)
        self.iter_parameters.setWindowTitle('Alignment Parameters')

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

        methodname = ["mlem", "art", "pml_hybrid", "pml_quad", "sirt", "tv"]
        self.algorithm = QtWidgets.QComboBox()
        self.algorithm.setFixedWidth(button2size)

        for j in methodname:
            self.algorithm.addItem(j)

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

        self.run_iter_align = QtWidgets.QPushButton("run iterative alignment")
        self.run_iter_align.setFixedWidth(button1size)

        # self.run_iter_align.clicked.connect(self.iter_align_params)

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
        vb00.addWidget(self.algorithm)
        vb00.addWidget(self.run_iter_align)

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

    def blur_enable(self):
        checked = self.blur_checkbox.isChecked()
        if checked:
            self.inner_radius_textbox.setEnabled(True)
            self.outer_radius_textbox.setEnabled(True)
        else:
            self.inner_radius_textbox.setEnabled(False)
            self.outer_radius_textbox.setEnabled(False)

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










