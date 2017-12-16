import os
import sys
import configparser
from PIL import Image
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/matrix'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class BaseScene(object):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('../settings.ini')

        # configuration for the matrix
        self.matrix_options = RGBMatrixOptions()
        self.matrix_options.rows = 16
        self.matrix_options.chain_length = 1
        self.matrix_options.parallel = 2
        self.matrix_options.brightness = 25
        self.matrix_options.pwm_lsb_nanoseconds = 200  # slow the pulses down to mitigate ghosting

        self.matrix = RGBMatrix(options=self.matrix_options)

    def settings_error(self, error):
        """Called when an error was encountered parsing the settings file"""
        print("Settings file error: {0}".format(error))
        sys.exit(1)

    def draw_image(self, image, canvas, at_x, at_y):
        """Draw an image onto a canvas in a way to preserve transparency"""
        for y in range(image.height):
            for x in range(image.width):
                color = image.getpixel((x, y))
                if color != (0,0,0):
                    # don't draw black pixels
                    canvas.SetPixel(at_x + x, at_y + y, *color)
