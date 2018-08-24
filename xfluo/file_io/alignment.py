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



import numpy as np



def alignFromText2(filename, data, projections, xshift, yshift):
    '''
    align by reading text file that saved prior image registration
    alignment info is saved in following format: name of the file, xshift, yshift
    by locating where the comma(,) is we can extract information:
    name of the file(string before first comma),
    yshift(string after first comma before second comma),
    xshift(string after second comma)

    '''
    try:
        fio = open(filename, 'r')
        read = fio.readlines()
        datacopy = np.zeros(data.shape)
        datacopy[...] = data[...]
        data[np.isnan(data)] = 1
        for i in np.arange(projections):
            j = i + 1
            secondcol = read[j].rfind(",")
            firstcol = read[j][:secondcol].rfind(",")
            yshift[i] += int(float(read[j][secondcol + 1:-1]))
            xshift[i] += int(float(read[j][firstcol + 1:secondcol]))
            data[:, i, :, :] = np.roll(data[:, i, :, :], xshift[i], axis=2)
            data[:, i, :, :] = np.roll(data[:, i, :, :], yshift[i], axis=1)

        fio.close()

        #self.lbl.setText("Alignment using values from Text has been completed")
        #self.updateImages()
    except IOError:
        print("choose file please")


def saveAlignToText(filename, projections, xshift, yshift):
    fio = open(filename, "w")
    #fio.writelines("rotation axis, " + str(self.p1[2]) + "\n")
    for i in range(projections):
        fio.writelines(projections[i] + ", " + str(xshift[i]) + ", " + str(yshift[i]) + "\n")
    fio.close()
