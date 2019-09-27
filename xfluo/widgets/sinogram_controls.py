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
        button1size = 250
        button2size = 122.5
        button3size = 73.3
        button4size = 58.75
        self.slopeVal = 0

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
        self.btn4 = QtWidgets.QPushButton('x corr. 2')
        self.btn4.setFixedWidth(button2size)
        self.btn5 = QtWidgets.QPushButton('align top')
        self.btn5.setFixedWidth(button2size)
        self.btn6 = QtWidgets.QPushButton('iter align')
        self.btn6.setFixedWidth(button2size)
        self.btn7 = QtWidgets.QPushButton('align from txt')
        self.btn7.setFixedWidth(button2size)
        self.btn8 = QtWidgets.QPushButton('align bottom')
        self.btn8.setFixedWidth(button2size)
        self.btn9 = QtWidgets.QPushButton('adjust_sino')
        self.btn9.setFixedWidth(button2size)

        self.slopeText = QtWidgets.QLineEdit(str(self.slopeVal))
        self.slopeText.setFixedWidth(button2size)
        self.lbl = QtWidgets.QLabel("")
        self.lbl.setFixedWidth(button2size)
        self.combo2.setVisible(False)

        hb1 = QtWidgets.QHBoxLayout()
        hb1.addWidget(self.btn1)
        hb1.addWidget(self.btn2)

        hb2 = QtWidgets.QHBoxLayout()
        hb2.addWidget(self.btn3)
        hb2.addWidget(self.btn4)

        hb3 = QtWidgets.QHBoxLayout()
        hb3.addWidget(self.btn5)
        hb3.addWidget(self.btn6)

        hb4 = QtWidgets.QHBoxLayout()
        hb4.addWidget(self.btn7)
        hb4.addWidget(self.btn8)

        hb5 = QtWidgets.QHBoxLayout()
        hb5.addWidget(self.btn9)
        hb5.addWidget(self.slopeText)

        vb1 = QtWidgets.QVBoxLayout()
        vb1.addLayout(hb1)
        vb1.addLayout(hb2)
        vb1.addLayout(hb3)

        vb2 = QtWidgets.QVBoxLayout()
        vb2.addLayout(hb4)
        vb2.addLayout(hb5)

        vb3 = QtWidgets.QVBoxLayout()
        vb3.addWidget(self.combo1)
        vb3.addWidget(self.combo2)
        vb3.addLayout(vb1)
        vb3.addLayout(vb2)

        self.setFixedWidth(275)
        self.setLayout(vb3)