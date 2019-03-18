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
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENTn SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
import numpy as np
from pylab import *
import xfluo
import matplotlib.pyplot as plt

class HotspotActions(QtWidgets.QWidget):
	dataSig = pyqtSignal(np.ndarray, name='dataSig')

	def __init__(self):
		super(HotspotActions, self).__init__()

    def hotspot2line(self):
        '''
        save the position of hotspots
        and align by both x and y directions (self.alignHotSpotPos3_3)
        '''



        # # self.projView.data2=self.data[7,:,:,:]
        # self.boxSize2 = self.boxSize / 2
        # self.xPos = zeros(self.projections)
        # self.yPos = zeros(self.projections)
        # self.boxPos = zeros([self.projections, self.boxSize, self.boxSize])
        # hotSpotSet = self.projViewControl.combo2.currentIndex()
        # for i in arange(self.projections):

        #     self.yPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 0]))
        #     self.xPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 1]))

        #     if self.xPos[i] != 0 and self.yPos[i] != 0:
        #         if self.yPos[i] < self.boxSize2:
        #             self.yPos[i] = self.boxSize2
        #         if self.yPos[i] > self.projView.view.data.shape[1] - self.boxSize2:
        #             self.yPos[i] = self.projView.view.data.shape[1] - self.boxSize2
        #         if self.xPos[i] < self.boxSize2:
        #             self.xPos[i] = self.boxSize2
        #         if self.xPos[i] > self.projView.view.data.shape[2] - self.boxSize2:
        #             self.xPos[i] = self.projView.view.data.shape[2] - self.boxSize2
        #         # self.boxPos[i,:,:]=self.projView.data[i,self.xPos[i]-self.boxSize2:self.xPos[i]+self.boxSize2,self.yPos[i]-self.boxSize2:self.yPos[i]+self.boxSize2]
        #         self.boxPos[i, :, :] = self.projView.view.data[i,
        #                                self.yPos[i] - self.boxSize2:self.yPos[i] + self.boxSize2,
        #                                self.xPos[i] - self.boxSize2:self.xPos[i] + self.boxSize2]
        # print self.boxPos.shape
        # print "x", self.xPos
        # print "y", self.yPos

        # ##            for i in arange(self.projections):
        # ##                  j=Image.fromarray(self.boxPos[i,:,:].astype(np.float32))
        # ##
        # ##                  j.save("/Users/youngpyohong/Documents/Work/Python/2dfit/"+str(i)+".tif")

        # self.alignHotSpotPos3_3()
        # print "hotspot done"

        pass

    def hotspot2sine(self):

        '''
        save the position of hotspots
        and align by both x and y directions (self.alignHotSpotPos3_4)
        '''


        # # self.projView.data2=self.data[7,:,:,:]
        # self.boxSize2 = self.boxSize / 2
        # self.xPos = zeros(self.projections)
        # self.yPos = zeros(self.projections)
        # self.boxPos = zeros([self.projections, self.boxSize, self.boxSize])
        # hotSpotSet = self.projViewControl.combo2.currentIndex()
        # for i in arange(self.projections):

        #     self.yPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 0]))
        #     self.xPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 1]))

        #     if self.xPos[i] != 0 and self.yPos[i] != 0:
        #         if self.yPos[i] < self.boxSize2:
        #             self.yPos[i] = self.boxSize2
        #         if self.yPos[i] > self.projView.view.data.shape[1] - self.boxSize2:
        #             self.yPos[i] = self.projView.view.data.shape[1] - self.boxSize2
        #         if self.xPos[i] < self.boxSize2:
        #             self.xPos[i] = self.boxSize2
        #         if self.xPos[i] > self.projView.view.data.shape[2] - self.boxSize2:
        #             self.xPos[i] = self.projView.view.data.shape[2] - self.boxSize2
        #         # self.boxPos[i,:,:]=self.projView.data[i,self.xPos[i]-self.boxSize2:self.xPos[i]+self.boxSize2,self.yPos[i]-self.boxSize2:self.yPos[i]+self.boxSize2]
        #         self.boxPos[i, :, :] = self.projView.view.data[i,
        #                                self.yPos[i] - self.boxSize2:self.yPos[i] + self.boxSize2,
        #                                self.xPos[i] - self.boxSize2:self.xPos[i] + self.boxSize2]
        # print self.boxPos.shape
        # print self.xPos, self.yPos

        # ##            for i in arange(self.projections):
        # ##                  j=Image.fromarray(self.boxPos[i,:,:].astype(np.float32))
        # ##
        # ##                  j.save("/Users/youngpyohong/Documents/Work/Python/2dfit/"+str(i)+".tif")

        # self.alignHotSpotPos3_4()
        # print "hotspot done"



        pass

    def setY(self):

       '''
        loads variables for aligning hotspots in y direction only
        '''



        # self.boxSize2 = self.boxSize / 2
        # self.xPos = zeros(self.projections)
        # self.yPos = zeros(self.projections)
        # self.boxPos = zeros([self.projections, self.boxSize, self.boxSize])
        # hotSpotSet = self.projViewControl.combo2.currentIndex()
        # for i in arange(self.projections):

        #     self.yPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 0]))
        #     self.xPos[i] = int(round(self.projView.view.posMat[hotSpotSet, i, 1]))

        #     if self.xPos[i] != 0 and self.yPos[i] != 0:
        #         if self.yPos[i] < self.boxSize2:
        #             self.yPos[i] = self.boxSize2
        #         if self.yPos[i] > self.projView.view.data.shape[1] - self.boxSize2:
        #             self.yPos[i] = self.projView.view.data.shape[1] - self.boxSize2
        #         if self.xPos[i] < self.boxSize2:
        #             self.xPos[i] = self.boxSize2
        #         if self.xPos[i] > self.projView.view.data.shape[2] - self.boxSize2:
        #             self.xPos[i] = self.projView.view.data.shape[2] - self.boxSize2
        #         # self.boxPos[i,:,:]=self.projView.data[i,self.xPos[i]-self.boxSize2:self.xPos[i]+self.boxSize2,self.yPos[i]-self.boxSize2:self.yPos[i]+self.boxSize2]
        #         self.boxPos[i, :, :] = self.projView.view.data[i,
        #                                self.yPos[i] - self.boxSize2:self.yPos[i] + self.boxSize2,
        #                                self.xPos[i] - self.boxSize2:self.xPos[i] + self.boxSize2]
        # print self.boxPos.shape
        # print self.xPos, self.yPos

        # self.alignHotSpotY_next()



        pass

    def clrHotspot(self):
        # self.projView.view.posMat[...] = zeros_like(self.projView.view.posMat)

        pass

        








    # def alignHotSpotPos3_3(self):
    #     '''
    #     align hotspots by fixing hotspots in one position
    #     '''
    #     self.hotSpotX = zeros(self.projections)
    #     self.hotSpotY = zeros(self.projections)
    #     self.newBoxPos = zeros(self.boxPos.shape)
    #     self.newBoxPos[...] = self.boxPos[...]
    #     ### need to change x and y's
    #     firstPosOfHotSpot = 0
    #     add = 1
    #     for i in arange(self.projections):
    #         if self.xPos[i] == 0 and self.yPos[i] == 0:
    #             firstPosOfHotSpot += add
    #         if self.xPos[i] != 0 or self.yPos[i] != 0:
    #             print self.xPos[i], self.yPos[i]
    #             img = self.boxPos[i, :, :]
    #             print img.shape
    #             a, x, y, b, c = self.fitgaussian(img)
    #             self.hotSpotY[i] = x
    #             self.hotSpotX[i] = y
    #             yshift = int(round(self.boxSize2 - self.hotSpotY[i]))
    #             xshift = int(round(self.boxSize2 - self.hotSpotX[i]))
    #             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
    #             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
    #             ##                  subplot(211)
    #             ##                  plt.imshow(self.boxPos[i,:,:])
    #             ##                  subplot(212)
    #             ##                  plt.imshow(self.newBoxPos[i,:,:])
    #             ##                  show()
    #             add = 0

    #     add2 = 0
    #     for j in arange(self.projections):

    #         if self.xPos[j] != 0 and self.yPos[j] != 0:
    #             yyshift = int(round(self.boxSize2 - self.hotSpotY[j] - self.yPos[j] + self.yPos[firstPosOfHotSpot]))
    #             xxshift = int(round(self.boxSize2 - self.hotSpotX[j] - self.xPos[j] + self.xPos[firstPosOfHotSpot]))
    #             print xxshift, yyshift
    #             self.data[:, j, :, :] = np.roll(np.roll(self.data[:, j, :, :], xxshift, axis=2),
    #                                             yyshift, axis=1)
    #         ##                        for l in arange(self.data.shape[0]):
    #         ##                              if yyshift>0:
    #         ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
    #         ##                              if yyshift<0:
    #         ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
    #         ##                              if xxshift>0:
    #         ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
    #         ##                              if xxshift<0:
    #         ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2
    #         if self.xPos[j] == 0:
    #             xxshift = 0
    #         if self.yPos[j] == 0:
    #             yyshift = 0

    #         self.xshift[j] += xxshift
    #         self.yshift[j] += yyshift

    #     self.p1[2] = self.xPos[0]

    #     print "align done"





    # def alignHotSpotPos3_4(self):
    #     '''
    #     align hotspots by fixing hotspots by fitting in a sine curve
    #     '''
    #     self.hotSpotX = zeros(self.projections)
    #     self.hotSpotY = zeros(self.projections)
    #     self.newBoxPos = zeros(self.boxPos.shape)
    #     self.newBoxPos[...] = self.boxPos[...]
    #     ### need to change x and y's
    #     firstPosOfHotSpot = 0
    #     add = 1
    #     for i in arange(self.projections):
    #         if self.xPos[i] == 0 and self.yPos[i] == 0:
    #             firstPosOfHotSpot += add
    #         if self.xPos[i] != 0 or self.yPos[i] != 0:
    #             print self.xPos[i], self.yPos[i]
    #             img = self.boxPos[i, :, :]
    #             print img.shape
    #             a, x, y, b, c = self.fitgaussian(img)
    #             self.hotSpotY[i] = x
    #             self.hotSpotX[i] = y
    #             yshift = int(round(self.boxSize2 - self.hotSpotY[i]))
    #             xshift = int(round(self.boxSize2 - self.hotSpotX[i]))
    #             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
    #             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
    #             ##                  subplot(211)
    #             ##                  plt.imshow(self.boxPos[i,:,:])
    #             ##                  subplot(212)
    #             ##                  plt.imshow(self.newBoxPos[i,:,:])
    #             ##                  show()
    #             add = 0

    #     for j in arange(self.projections):

    #         if self.xPos[j] != 0 and self.yPos[j] != 0:
    #             yyshift = int(round(self.boxSize2 - self.hotSpotY[j]))
    #             xxshift = int(round(self.boxSize2 - self.hotSpotX[j]))

    #         ##                        for l in arange(self.data.shape[0]):
    #         ##                              if yyshift>0:
    #         ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
    #         ##                              if yyshift<0:
    #         ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
    #         ##                              if xxshift>0:
    #         ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
    #         ##                              if xxshift<0:
    #         ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2
    #         if self.xPos[j] == 0:
    #             xxshift = 0
    #         if self.yPos[j] == 0:
    #             yyshift = 0

    #         self.xshift[j] += xxshift
    #         self.yshift[j] += yyshift

    #     add2 = 0

    #     global hotspotXPos, hotspotYPos
    #     hotspotXPos = zeros(self.projections)
    #     hotspotYPos = zeros(self.projections)
    #     for i in arange(self.projections):
    #         hotspotYPos[i] = int(round(self.yPos[i]))
    #         hotspotXPos[i] = int(round(self.xPos[i]))
    #     self.hotspotProj = np.where(hotspotXPos != 0)[0]
    #     print self.hotspotProj
    #     ## temp

    #     ## xfit
    #     print self.hotspotProj
    #     global a1, b4
    #     a1 = self.theta
    #     b4 = self.hotspotProj
    #     theta = self.theta[self.hotspotProj]
    #     print "theta", theta
    #     self.com = hotspotXPos[self.hotspotProj]
    #     if self.projViewControl.combo2.currentIndex() == 0:
    #         self.fitCenterOfMass(x=theta)
    #     else:
    #         self.fitCenterOfMass2(x=theta)
    #     self.alignCenterOfMass2()

    #     ## yfit
    #     for i in self.hotspotProj:
    #         self.yshift[i] += int(hotspotYPos[self.hotspotProj[0]]) - int(hotspotYPos[i])
    #         self.data[:, i, :, :] = np.roll(self.data[:, i, :, :], self.yshift[i], axis=1)
    #         print int(hotspotYPos[0]) - int(hotspotYPos[i])

    #     self.recon.sld.setValue(self.p1[2])
    #     print "align done"





    # def alignHotSpotY_next(self):
    #     '''
    #     save the position of hotspots
    #     and align by only in y directions.
    #     '''
    #     self.hotSpotX = zeros(self.projections)
    #     self.hotSpotY = zeros(self.projections)
    #     self.newBoxPos = zeros(self.boxPos.shape)
    #     self.newBoxPos[...] = self.boxPos[...]
    #     ### need to change x and y's
    #     firstPosOfHotSpot = 0
    #     add = 1
    #     for i in arange(self.projections):
    #         if self.xPos[i] == 0 and self.yPos[i] == 0:
    #             firstPosOfHotSpot += add
    #         if self.xPos[i] != 0 or self.yPos[i] != 0:
    #             print self.xPos[i], self.yPos[i]
    #             img = self.boxPos[i, :, :]
    #             print img.shape
    #             a, x, y, b, c = self.fitgaussian(img)
    #             self.hotSpotY[i] = x
    #             self.hotSpotX[i] = y
    #             yshift = int(round(self.boxSize2 - self.hotSpotY[i]))
    #             xshift = int(round(self.boxSize2 - self.hotSpotX[i]))
    #             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], xshift, axis=1)
    #             self.newBoxPos[i, :, :] = np.roll(self.newBoxPos[i, :, :], yshift, axis=0)
    #             ##                  subplot(211)
    #             ##                  plt.imshow(self.boxPos[i,:,:])
    #             ##                  subplot(212)
    #             ##                  plt.imshow(self.newBoxPos[i,:,:])
    #             ##                  show()
    #             add = 0

    #     add2 = 0
    #     for j in arange(self.projections):

    #         if self.xPos[j] != 0 and self.yPos[j] != 0:
    #             yyshift = int(round(self.boxSize2 - self.hotSpotY[j] - self.yPos[j] + self.yPos[firstPosOfHotSpot]))

    #             print yyshift
    #             self.data[:, j, :, :] = np.roll(self.data[:, j, :, :],
    #                                             yyshift, axis=1)
    #         ##                        for l in arange(self.data.shape[0]):
    #         ##                              if yyshift>0:
    #         ##                                    self.data[l,j,:yyshift,:]=ones(self.data[l,j,:yyshift,:].shape)*self.data[l,j,:yyshift,:].mean()/2
    #         ##                              if yyshift<0:
    #         ##                                    self.data[l,j,yyshift:,:]=ones(self.data[l,j,yyshift:,:].shape)*self.data[l,j,-yyshift:,:].mean()/2
    #         ##                              if xxshift>0:
    #         ##                                    self.data[l,j,:,:xxshift]=ones(self.data[l,j,:,:xxshift].shape)*self.data[l,j,:xxshift,:].mean()/2
    #         ##                              if xxshift<0:
    #         ##                                    self.data[l,j,:,xxshift:]=ones(self.data[l,j,:,xxshift:].shape)*self.data[l,j,-xxshift:,:].mean()/2

    #         if self.yPos[j] == 0:
    #             yyshift = 0

    #         self.yshift[j] += yyshift

    #     print "align done"