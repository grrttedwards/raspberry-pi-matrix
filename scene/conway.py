#!/usr/bin/env python3

# Display a WeatherClock with double-buffering.
import sys
import os
import time
import datetime as dt
import requests
from scene.base import BaseScene
from rgbmatrix import graphics
from PIL import Image
sys.path.append('../')
from animators import gameoflife


class ConwaysGame(BaseScene):

    def __init__(self):
        super().__init__()

        try:
            pass
        except KeyError as err:
            self.settings_error(err)

        self.animator = gameoflife.GameOfLifeAnimator()
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
    
    file_path = os.path.dirname(__file__) + '/'

    cell_color = graphics.Color(180, 150, 0)

    def draw_animation(self, color):
        frame = self.animator.get_frame()
        for y, row in enumerate(frame):
            for x, pixel in enumerate(row):
                if pixel:
                    self.offscreen_canvas.SetPixel(x, y, *color)
                else:
                    self.offscreen_canvas.SetPixel(x, y, 0, 0, 0)

    def run(self):
        while True:

            self.offscreen_canvas.Clear()
            self.draw_animation(color=(180,100,0))
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

            


# Main function
if __name__ == '__main__':
    ConwaysGame().run()
