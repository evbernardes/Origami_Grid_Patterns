#! /usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from abc import abstractmethod
from math import pi, sin, cos, tan, asin, acos, atan, sqrt

import inkex

from Path import Path
from Pattern import Pattern


# Select name of class, inherits from Pattern
# TODO:
# 1) Implement __init__ method to get all custom options and then call Pattern's __init__
# 2) Implement generate_path_tree to define all of the desired strokes

def generate_slots(n, slot_position,
                    slot_height, slot_width,
                    base_height, base_width):

    if slot_height == 0 and slot_width == 0:
        return []

    slot_height = min(slot_height, base_height)
    slot_width = min(slot_width, base_width)

    rect = [  (0, 0),
              (0, slot_height),
              (slot_width, slot_height),
              (slot_width, 0)]

    dx = (base_width - slot_width) / 2
    if slot_position == -1:
        dy = 0
    elif slot_position == 0:
        dy = (base_height - slot_height) / 2
    elif slot_position == +1:
        dy = base_height - slot_height

    slot = Path(rect, 'c', closed=True) + (dx, dy)
    return [slot + (base_width * i, 0) for i in range(n)]

class Cylindrical(Pattern):

    def __init__(self):
        """ Constructor
        """
        Pattern.__init__(self)  # Must be called in order to parse common options

        # save all custom parameters defined on .inx file
        self.add_argument('--pattern', type=self.str, default='template1')
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

    @abstractmethod
    def generate_cell(self):
        """ Generate the the origami cell
        """
        pass

    def generate_all_slots(self):
        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()

        # retrieve saved parameters, and apply unit factor where needed
        radius = self.options.radius * unit_factor
        n = self.options.n
        rows = self.options.lines

        width = 2 * radius * sin(pi / n)
        distance = self.options.distance * unit_factor

        # base slots
        base_slot_height = self.options.base_slot_height * unit_factor
        base_slot_width = self.options.base_slot_width * unit_factor
        base_height = self.options.base_height * unit_factor
        base_slot_sizes = [base_slot_height, base_slot_width, base_height, width]

        base_slot_top = generate_slots(n, +int(self.options.base_slot_position), *base_slot_sizes)
        base_slot_bot = generate_slots(n, -int(self.options.base_slot_position), *base_slot_sizes)
        base_slot_bot = Path.list_add(base_slot_bot,
                                      (0, base_height + rows * self.cell_height + (rows - 1) * distance))

        # middle slots
        middle_slot_height = self.options.base_slot_height * unit_factor
        middle_slot_width = self.options.middle_slot_width * unit_factor
        middle_slot_sizes = [middle_slot_height, middle_slot_width, distance, width]

        middle_slot = generate_slots(n, +int(self.options.middle_slot_position), *middle_slot_sizes)
        middle_slots = [Path.list_add(middle_slot,
                                      (0, base_height + i * self.cell_height + (i - 1) * distance)) for i in range(1, rows)]

        return [base_slot_top, middle_slots, base_slot_bot]

    def generate_path_tree(self):
        """ Specialized path generation for your origami pattern
        """
        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()

        # retrieve saved parameters, and apply unit factor where needed
        radius = self.options.radius * unit_factor
        n = self.options.n
        rows = self.options.lines


        self.cell_height = 15 * unit_factor
        base_slot_height = self.options.base_slot_height * unit_factor
        distance = self.options.distance * unit_factor
        width = 2 * radius * sin(pi / n)
        distance = self.options.distance * unit_factor


        self.path_tree = self.generate_all_slots()
        self.edge_points = []





# Main function, creates an instance of the Class and calls self.draw() to draw the origami on inkscape
# self.draw() is either a call to inkex.affect() or to svg.run(), depending on python version
if __name__ == '__main__':
    e = Cylindrical()  # remember to put the name of your Class here!
    e.draw()
