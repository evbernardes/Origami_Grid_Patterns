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

def generate_slot_line(n, slot_position,
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
    slots = [slot + (base_width * i, 0) for i in range(n)]

    divider = Path([(base_width, 0), (base_width, base_height)], style='m')
    dividers = [divider + (base_width*i, 0) for i in range(n-1)]
    return slots + dividers

class Cylindrical(Pattern):

    def __init__(self):
        """ Constructor
        """
        Pattern.__init__(self)  # Must be called in order to parse common options

        # save all custom parameters defined on .inx file
        self.add_argument('--radius', type=self.float, default=10.0)
        self.add_argument('--sides', type=self.int, default=6)
        self.add_argument('--rows', type=self.int, default=3)

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

    def generate_path_tree(self):
        """ Specialized path generation for your origami pattern
        """
        # zero distances when slot option not selected
        if not self.options.add_base_slot:
            self.options.base_height = 0
            self.options.base_slot_height = 0
        if not self.options.add_middle_slot:
            self.options.distance = 0
            self.options.middle_slot_height = 0
        if self.options.base_height == 0:
            self.options.add_base_slot = False
        if self.options.distance == 0:
            self.options.add_middle_slot = True

        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()

        # pre-calculate width before adding one to sides, for easier attachment
        self.options.width = 2 * self.options.radius * sin(pi / self.options.sides)
        if self.options.add_attachment:
            self.options.sides = self.options.sides + 1

        # retrieve saved parameters, and apply unit factor where needed
        radius = self.options.radius * unit_factor
        sides = self.options.sides
        rows = self.options.rows

        # get cell definitions
        cell_data = self.generate_cell()
        cell_data['dx'] = [0]+cell_data['dx'] # add an extra first element of value zero

        # get all slots and vertical dividers between slots
        base, middle = self.generate_all_slots(cell_data)
        slots = [[base['slots'], middle['slots']]]

        # get horizontal dividers between cells
        dividers = self.generate_horizontal_dividers(cell_data)

        # finish by replicating the actual interior
        interior = self.generate_interior(cell_data)

        # use slots and cell data to create the full edge paths
        self.edge_points = self.generate_fused_edge_points(base, middle, cell_data)

        self.path_tree = [dividers, interior]
        if len(self.vertex_points) == 0:
            self.vertex_points = Path.get_points(self.path_tree)
        self.path_tree.append(slots)

    def generate_interior(self, cell_data):
        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()
        rows = self.options.rows
        base_height = self.options.base_height * unit_factor
        distance = self.options.distance * unit_factor

        interiors = []

        for i in range(rows):
            dx = cell_data['dx'][i]
            dy = base_height + i * (distance + cell_data['height'])
            pattern = cell_data['interior'][0]
            interiors.append(Path.list_add(pattern, (dx, dy)))

        return interiors


    def generate_horizontal_dividers(self, cell_data):
        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()
        rows = self.options.rows
        base_height = self.options.base_height * unit_factor
        distance = self.options.distance * unit_factor

        divider = cell_data['divider']
        dividers = []

        if self.options.add_base_slot:
            dividers.append(divider + (0, base_height))

        for i in range(1, rows):
            dx = cell_data['dx'][i]
            dy = base_height + i * cell_data['height'] + (i - 1) * distance
            dividers.append(divider + (dx, dy))
            if self.options.add_middle_slot:
                dividers.append(divider + (dx, dy + distance))

        if self.options.add_base_slot:
            dx = cell_data['dx'][-1]
            dy = base_height + rows * cell_data['height'] + (rows - 1) * distance
            dividers.append(divider + (dx, dy))

        return dividers
        # pass


    def generate_all_slots(self, cell_data):
        cell_height = cell_data['height']
        cell_dx = cell_data['dx']

        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()

        # retrieve saved parameters, and apply unit factor where needed
        radius = self.options.radius * unit_factor
        sides = self.options.sides
        rows = self.options.rows
        width = self.options.width * unit_factor

        distance = self.options.distance * unit_factor
        base_height = self.options.base_height * unit_factor

        base = {'left': [],
                'right': [],
                'slots': []}

        height_bottom_slot = base_height + rows * cell_height + (rows - 1) * distance
        if self.options.add_base_slot:
            base_slot_height = self.options.base_slot_height * unit_factor
            base_slot_width = self.options.base_slot_width * unit_factor
            base_slot_sizes = [base_slot_height, base_slot_width, base_height, width]

            base_slot_top = generate_slot_line(sides, +int(self.options.base_slot_position), *base_slot_sizes)
            base_slot_bot = generate_slot_line(sides, -int(self.options.base_slot_position), *base_slot_sizes)


            base['slots'] = [base_slot_top, Path.list_add(base_slot_bot, (cell_dx[-1], height_bottom_slot))]

            base['left'] = [Path([(0, 0), (0, base_height)], style = 'e'),
                            Path([(cell_dx[-1], height_bottom_slot), (cell_dx[-1], height_bottom_slot + base_height)], style = 'e')]

            base['right'] = [Path([(cell_dx[-1]+sides*width, height_bottom_slot + base_height), (cell_dx[-1]+sides*width, height_bottom_slot)], style = 'e'),
                             Path([(sides*width, base_height), (sides*width, 0)], style = 'e')]

        middle = {'left': [],
                  'right': [],
                  'slots': []}

        if self.options.add_middle_slot:
            middle_slot_height = self.options.middle_slot_height * unit_factor
            middle_slot_width = self.options.middle_slot_width * unit_factor
            middle_slot_sizes = [middle_slot_height, middle_slot_width, distance, width]

            middle_slot = generate_slot_line(sides, +int(self.options.middle_slot_position), *middle_slot_sizes)
            middle['slots'] = [Path.list_add(middle_slot,
                                          (cell_dx[i], base_height + i * cell_height + (i - 1) * distance)) for i in range(1, rows)]

            middle['left'] = [Path([(0, base_height + cell_height), (0, base_height + cell_height + distance)], style='e') +
                              (cell_dx[i+1], i * (cell_height + distance)) for i in range(rows-1)]

            middle['right'] = [
                Path([(0, base_height + (rows - 1) * (cell_height + distance)), (0, base_height +  (rows - 1) * (cell_height + distance) - distance)], style='e') +
                            (cell_dx[-(i+2)] + sides*width, -i * (cell_height + distance)) for i in range(rows - 1)]

        return base, middle

    def generate_fused_edge_points(self, base, middle, cell_data):
        unit_factor = self.calc_unit_factor()
        base_height = self.options.base_height * unit_factor
        distance = self.options.distance * unit_factor
        rows = self.options.rows

        edges = []
        if self.options.add_base_slot: edges.append(base['left'][0])
        for i in range(rows):
            cell_left = cell_data['edge_left'][i]
            dx = cell_data['dx'][i]
            edges.append(cell_left + (dx, base_height + i * (cell_data['height'] + distance)))
            if self.options.add_middle_slot and i < rows - 1:
                edges.append(middle['left'][i] + (0, 0))
        if self.options.add_base_slot: edges.append(base['left'][1])

        if self.options.add_base_slot: edges.append(base['right'][0])
        for i in range(rows):
            cell_right = cell_data['edge_right'][-(i + 1)]
            dx = cell_data['dx'][-(i + 2)]
            edges.append(cell_right + (dx, base_height + (rows - i - 1) * (cell_data['height'] + distance)))
            if self.options.add_middle_slot and i < rows - 1:
                edges.append(middle['right'][i] + (0, 0))
        if self.options.add_base_slot: edges.append(base['right'][1])

        return Path.get_points(edges)

