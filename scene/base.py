import os
import sys
import configparser
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