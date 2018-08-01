'''
Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.

Copyright 2016. UChicago Argonne, LLC. This software was produced
under U.S. Government contract DE-AC02-06CH11357 for Argonne National
Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
U.S. Department of Energy. The U.S. Government has rights to use,
reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should
be clearly marked, so as not to confuse it with the version available
from ANL.

Additionally, redistribution and use in source and binary forms, with
or without modification, are permitted provided that the following
conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in
      the documentation and/or other materials provided with the
      distribution.

    * Neither the name of UChicago Argonne, LLC, Argonne National
      Laboratory, ANL, the U.S. Government, nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

import numpy as np
from scipy.fftpack import fft2, ifft2
from scipy import optimize


def fitCenterOfMass(x, com):
    fit_func = lambda p, x: p[0] * np.sin(2 * np.pi / 360 * (x - p[1])) + p[2]
    err_func = lambda p, x, y: fit_func(p, x) - y
    p0 = [100, 100, 100]
    p1, success = optimize.leastsq(err_func, p0[:], args=(x, com))
    ##centerOfMassDiff = fit_func(p1, x) - self.com
    return p1


def runCenterOfMass(theta, com):
    '''
    find center of mass with self.centerOfMass and fit the curve with self.fitCenterOfMass
    '''
    centerOfMass()
    return fitCenterOfMass(x=theta, com)


def fitCenterOfMass2(x, com):
    '''
    Find a position difference between center of mass of first projection
    and center of other projections.
    If we use this difference, centers will form a sine curve

    Parameters
    -----------
    ang: ndarray
          angle

    Variables
    ------------
    self.centerOfMassDiff: ndarray
          Difference of center of mass of first projections and center
          of other projections
    com: ndarray
          The position of center of mass
    '''
    fit_func = lambda p, x: p[0] * np.sin(2 * np.pi / 360 * (x - p[1])) + p1[2]
    err_func = lambda p, x, y: fit_func(p, x) - y
    p0 = [100, 100]
    p2, success = optimize.leastsq(err_func, p0[:], args=(x, com))
    centerOfMassDiff = fit_func(p2, x) - com
    return centerOfMassDiff


def runCenterOfMass2(projections, data, thickness, theta):
    '''
    second version of runCenterOfMass
    self.com: center of mass vector
    self.comelem: the element chosen for center of mass
    '''
    com = np.zeros(projections)
    temp = np.zeros(data.shape[3])
    temp2 = np.zeros(data.shape[3])
    comelem = sino.combo.currentIndex()
    for i in np.arange(projections):
        temp = sum(data[comelem, i, sino.sld.value() - thickness / 2:sino.sld.value() + thickness / 2,:] - data[comelem, i, :10, :10].mean(), axis=0)
        # temp=sum(self.data[self.comelem,i,:,:]-1, axis=0)
        numb2 = sum(temp)
        for j in np.arange(data.shape[3]):
            temp2[j] = temp[j] * j
        numb = float(sum(temp2)) / numb2
        com[i] = numb
    return fitCenterOfMass(x=theta)


def centerOfMass(projections, data):
    '''
    self.com: center of mass vector
    self.comelem: the element chosen for center of mass
    '''
    com = np.zeros(projections)
    temp = np.zeros(data.shape[3])
    temp2 = np.zeros(data.shape[3])
    comelem = comer.combo.currentIndex()
    for i in np.arange(projections):
        temp = sum(data[comelem, i, :, :] - data[comelem, i, :10, :10].mean(), axis=0)
        # temp=sum(self.data[self.comelem,i,:,:]-1, axis=0)
        numb2 = sum(temp)
        for j in np.arange(data.shape[3]):
            temp2[j] = temp[j] * j
        numb = float(sum(temp2)) / numb2
        com[i] = numb
    return com


def fitCenterOfMass(ang, com):
    '''
    Find a position difference between center of mass of first projection
    and center of other projections.
    If we use this difference, centers will be aligned in a straigh line

    Parameters
    -----------
    ang: ndarray
          angle

    Variables
    ------------
    self.centerOfMassDiff: ndarray
          Difference of center of mass of first projections and center
          of other projections
    self.com: ndarray
          The position of center of mass
    '''
    centerOfMassDiff = com[0] - com



def alignCenterOfMass(projections, data, xshift):
    '''
    Align center of Mass

    Variables
    ------------
    self.centerOfMassDiff: ndarray
          Difference of center of mass of first projections and center
          of other projections
    self.projections: number
          number of projections
    self.xshift: ndarray
          shift in x direction
    self.data: ndarray
          4D data [element,projections,y,x]
    '''
    for i in np.arange(projections):
        xshift[i] += int(self.centerOfMassDiff[i])
        data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(xshift[i])), axis=2)


def alignCenterOfMass2(hotspotProj, data, xshift, centerOfMassDiff):
    '''
    Align center of Mass

    Variables
    ------------
    self.centerOfMassDiff: ndarray
          Difference of center of mass of first projections and center
          of other projections
    self.projections: number
          number of projections
    self.xshift: ndarray
          shift in x direction
    self.data: ndarray
          4D data [element,projections,y,x]
    '''

    j = 0

    for i in hotspotProj:
        xshift[i] += int(centerOfMassDiff[j])

        data[:, i, :, :] = np.roll(data[:, i, :, :], int(round(xshift[i])), axis=2)
        j += 1


def match(matchElemIndex, projections, data, xshift, yshift):
    for i in np.arange(projections - 1):
        img = data[matchElemIndex, i, :, :]
        img1 = np.ones([img.shape[0] * 2, img.shape[1] * 2]) * data[matchElemIndex, i, :10, :10].mean()
        img1[img.shape[0] / 2:img.shape[0] * 3 / 2, img.shape[1] / 2:img.shape[1] * 3 / 2] = img
        img2 = data[matchElemIndex, i + 1, :, :]
        result = match_template(img1, img2)
        result = np.where(result == np.max(result))
        yshift[i + 1] += result[0][0] - img.shape[0] / 2
        xshift[i + 1] += result[1][0] - img.shape[1] / 2
        data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], xshift[i + 1], axis=2)
        data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], yshift[i + 1], axis=1)


def xCor(xcorElementIndex, projections, data, xshift, yshift):
    for i in np.arange(projections - 1):
        # onlyfilename=self.fileNames[i+1].rfind("/")
        img1 = data[xcorElementIndex, i, :, :]
        img2 = data[xcorElementIndex, i + 1, :, :]

        t0, t1 = crossCorrelate(img1, img2)
        data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], t0, axis=1)
        data[:, i + 1, :, :] = np.roll(data[:, i + 1, :, :], t1, axis=2)
        xshift[i + 1] += t1
        yshift[i + 1] += t0


def alignFromText(ndArrayList, alignmentList):
    '''
    align by reading text file that saved prior image registration
    alignment info is saved in following format: name of the file, xshift, yshift
    by locating where the comma(,) is we can extract information:
    name of the file(string before first comma),
    yshift(string after first comma before second comma),
    xshift(string after second comma)
    '''
    '''
    for projections in ndArrayList:
        for j in np.arange(alignmentList):
            if string.find(read[j], self.selectedFiles[i][onlyfilename + 1:]) != -1:
                #secondcol = read[j].rfind(",")  ## find second ,
                #firstcol = read[j][:secondcol].rfind(",")
                yshift[i] += int(float(read[j][secondcol + 1:-1]))
                xshift[i] += int(float(read[j][firstcol + 1:secondcol]))
                data[:, i, :, :] = np.roll(data[:, i, :, :], self.xshift[i], axis=2)
                data[:, i, :, :] = np.roll(data[:, i, :, :], self.yshift[i], axis=1)
            if string.find(read[j], "rotation axis") != -1:
                commapos = read[j].rfind(",")
                self.p1[2] = float(read[j][commapos + 1:-1])
    '''
    pass


def crossCorrelate(image1, image2):
    '''

        :param image1: 2d array
        :param image2: 2d array
        :return:
    '''
    fft_array1 = fft2(image1)
    fft_array2 = fft2(image2)

    shape = image1.shape
    c = abs(ifft2(fft_array1 * fft_array2.conjugate()))
    t0, t1 = np.unravel_index(np.argmax(c), image1.shape)
    if t0 > shape[0] // 2:
        t0 -= shape[0]
    if t1 > shape[1] // 2:
        t1 -= shape[1]

    return t0, t1


def phaseCorrelate(image1, image2):
    '''

    :param image1: 2d array
    :param image2: 2d array
    :return:
    '''
    fft_array1 = fft2(image1)
    fft_array2 = fft2(image2)

    shape = image1.shape
    c = abs(ifft2(fft_array1 * fft_array2.conjugate() / (abs(fft_array1) * abs(fft_array2))))
    t0, t1 = np.unravel_index(np.argmax(c), image1.shape)
    if t0 > shape[0] // 2:
        t0 -= shape[0]
    if t1 > shape[1] // 2:
        t1 -= shape[1]
    return t0, t1


def edgegauss(imagey, sigma=4):
    '''
    edge gauss for better cross correlation
    '''
    image = np.zeros(imagey.shape)
    image[...] = imagey[...]
    nx = image.shape[1]
    ny = image.shape[0]

    n_sigma = -log(10 ** -6)
    n_roll = max(int(1 + sigma * n_sigma), 2)
    exparg = np.float32(np.arange(n_roll) / float(sigma))
    rolloff = np.float32(1) - np.exp(-0.5 * exparg * exparg)

    ## Top edge

    xstart = 0
    xstop = nx
    iy = 0

    for i_roll in np.arange(n_roll):
        image[iy, xstart:xstop] = image[iy, xstart:xstop] * rolloff[iy]
        xstart = min(xstart + 1, nx / 2 - 1)
        xstop = max(xstop - 1, nx / 2)
        iy = min(iy + 1, ny - 1)

    ## Bottom edge

    xstart = 0
    xstop = nx
    iy = ny - 1

    for i_roll in np.arange(n_roll):
        image[iy, xstart:xstop] = image[iy, xstart:xstop] * rolloff[ny - 1 - iy]
        xstart = min(xstart + 1, nx / 2 - 1)
        xstop = max(xstop - 1, nx / 2)
        iy = max(iy - 1, 0)

    ## Left edge

    ystart = 1
    ystop = ny - 1
    ix = 0

    for i_roll in np.arange(n_roll):
        image[ystart:ystop, ix] = image[ystart:ystop, ix] * rolloff[ix]
        ystart = min(ystart + 1, ny / 2 - 1)
        ystop = max(ystop - 1, ny / 2)
        ix = min(ix + 1, nx - 1)

    ## Right edge

    ystart = 1
    ystop = ny - 1
    ix = nx - 1

    for i_roll in np.arange(n_roll):
        image[ystart:ystop, ix] = image[ystart:ystop, ix] * rolloff[nx - 1 - ix]
        ystart = min(ystart + 1, ny / 2 - 1)
        ystop = max(ystop - 1, ny / 2)
        ix = max(ix - 1, 0)

    return image



def run_unit_tests():
    '''
    Run unit test on all the alignment functions
    '''
    pass


if __name__ == "__main__":
    run_unit_tests()