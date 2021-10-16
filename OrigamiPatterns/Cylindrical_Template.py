#! /usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from abc import abstractmethod
from math import pi, sin, cos, tan, asin, acos, atan, sqrt

import inkex

from Path import Path
from Pattern import Pattern
from Cylindrical import Cylindrical


# Select name of class, inherits from Pattern
# TODO:
# 1) Implement __init__ method to get all custom options and then call Pattern's __init__
# 2) Implement generate_path_tree to define all of the desired strokes

class Template(Cylindrical):

    def __init__(self):
        """ Constructor
        """
        Pattern.__init__(self)  # Must be called in order to parse common options
        Cylindrical.__init__(self)  # Must be called in order to parse common options

        # save all custom parameters defined on .inx file
        self.add_argument('--pattern', type=self.str, default='cylindrical_template')
        self.add_argument('--radius', type=self.float, default=10.0)
        self.add_argument('--n', type=self.int, default=6)
        self.add_argument('--lines', type=self.int, default=3)

        self.add_argument('--add_attachment', type=self.bool, default=False)

        # slot options for support ring
        self.add_argument('--add_base_slot', type=self.bool, default=False)
        self.add_argument('--base_slot_position', type=self.str, default="1")
        self.add_argument('--base_height', type=self.float, default=5.0)
        self.add_argument('--base_slot_height', type=self.float, default=3.0)
        self.add_argument('--base_slot_width', type=self.float, default=3.0)

        self.add_argument('--add_middle_slot', type=self.bool, default=False)
        self.add_argument('--middle_slot_position', type=self.str, default="0")
        self.add_argument('--distance', type=self.float, default=3.0)
        self.add_argument('--middle_slot_height', type=self.float, default=3.0)
        self.add_argument('--middle_slot_width', type=self.float, default=3.0)

    def generate_cell(self):
        """ Generate the the origami cell
        """
        return []


# Main function, creates an instance of the Class and calls self.draw() to draw the origami on inkscape
# self.draw() is either a call to inkex.affect() or to svg.run(), depending on python version
if __name__ == '__main__':
    e = Template()  # remember to put the name of your Class here!
    e.draw()
