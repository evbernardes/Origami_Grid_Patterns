#! /usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from math import pi

import inkex

from Path import Path
from Pattern import Pattern


# Select name of class, inherits from Pattern
# TODO:
# 1) Implement __init__ method to get all custom options and then call Pattern's __init__
# 2) Implement generate_path_tree to define all of the desired strokes

def reflections_diag(path):
    new_paths = [path]
    new_paths = new_paths + Path.list_reflect(new_paths, (0, 0), (1, 1))
    return new_paths + Path.list_reflect(new_paths, (0, 0), (1, -1))

def reflections_rect(path):
    new_paths = [path]
    new_paths = new_paths + Path.list_reflect(new_paths, (0, 0), (0, 1))
    return new_paths + Path.list_reflect(new_paths, (0, 0), (1, 0))
    

class MasuBox(Pattern):

    def __init__(self):
        """ Constructor
        """
        Pattern.__init__(self)  # Must be called in order to parse common options

        # save all custom parameters defined on .inx file
        self.add_argument('--pattern', type=self.str, default='template1')
        self.add_argument('--length', type=self.float, default=10.0)
        self.add_argument('--sim', type=self.bool, default=True)

    def generate_path_tree(self):
        """ Specialized path generation for your origami pattern
        """
        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()

        # retrieve saved parameters, and apply unit factor where needed
        length = self.options.length * unit_factor
        height = length
        width = length
        half_fold = 90 if self.options.sim else 180

        # generate all valleys
        corner_valleys = reflections_diag(Path([(0, -1), (0, -2), (-0.5, -1.5)], 'v'))
        short_valleys = [
            Path([(+2, +1), (+1, +2)], 'v', fold_angle = half_fold),
            Path([(-2, -1), (-1, -2)], 'v', fold_angle = half_fold)]
        long_valleys = [
            Path([(+0.5, -1.5), (+1.0, -2.0), (+2.0, -1.0), (+1.5, -0.5)], 'v', fold_angle = half_fold),
            Path([(-0.5, +1.5), (-1.0, +2.0), (-2.0, +1.0), (-1.5, +0.5)], 'v', fold_angle = half_fold)]
        valleys = Path.list_simplify([corner_valleys, long_valleys, short_valleys])

        # generate all mountains
        center_square = Path([(-1, 0.00), (0.00, -1), (+1, 0.00), (0.00, +1)], 'm', closed=True, fold_angle=half_fold)
        short_mountains = reflections_diag(Path([(0, -1), (0.5, -1.5)], 'm', fold_angle=half_fold))
        vertical_long_mountains = [
            Path([(-2, 0), (0, +2)], 'm'),
            Path([(0, -2), (+2, 0)], 'm')]
        vertical_medium_mountains = reflections_diag(Path([(-1, -2), (0, -1)], 'm'))
        horizontal_mountains = [
            Path([(-1.5, -0.5), (-0.5, -1.5)], 'm'),
            Path([(+1.5, +0.5), (+0.5, +1.5)], 'm')]
        mountains = Path.list_simplify([center_square, short_mountains, horizontal_mountains,
                                        vertical_medium_mountains, vertical_long_mountains])

        # decenter and scale
        valleys = Path.list_mul(valleys, [length / 4])
        valleys = Path.list_add(valleys, (length / 2, length / 2))
        mountains = Path.list_mul(mountains, [length / 4])
        mountains = Path.list_add(mountains, (length / 2, length / 2))

        self.edge_points = Path.generate_square(length, length).points
        self.path_tree = [valleys, mountains]

# Main function, creates an instance of the Class and calls self.draw() to draw the origami on inkscape
# self.draw() is either a call to inkex.affect() or to svg.run(), depending on python version
if __name__ == '__main__':
    e = MasuBox()  # remember to put the name of your Class here!
    e.draw()
