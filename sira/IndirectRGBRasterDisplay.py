# coding=utf-8
"""Simple simulator for an RGB Raster display with an indirect color scheme"""

import numpy as np
from . import DirectRGBRasterDisplay

__author__ = "Daniel Calderon"
__license__ = "MIT"


class IndirectRGBRasterDisplay(DirectRGBRasterDisplay):

    
    def __init__(self, windowSize, imageSize, displayName):
        super().__init__(windowSize, imageSize, displayName)
        self.colorPalette = None


    def setColorPalette(self, colorPalette):
        self.colorPalette = colorPalette


    def setMatrix(self, matrix):

        imgData = np.ndarray((self.imageSize[0], self.imageSize[1], 3), dtype=np.uint8)
        it = np.nditer(matrix, flags=['multi_index'])
        while not it.finished:
            colorIndex = it[0]
            color = self.colorPalette[colorIndex]
            imgData[it.multi_index] = color
            it.iternext()

        super().setMatrix(imgData)

