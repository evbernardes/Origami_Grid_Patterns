#! /usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod
from math import pi, sin
from itertools import accumulate

import inkex
from Path import Path
from Pattern import Pattern

def generate_slot_line(n, slot_position,
                       slot_height, slot_width,
                       base_height, base_width):
    """ Helper function for generation of entire line
    of slots
    """

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
    """ Class that inherits Pattern and further specializes it for different
    Cylindrical classes generation.

    Abstract Methods
    ----------------

    parse_parameters(self)
        Parse custom parameters of Cylindrical pattern

    generate_cell(self)
        Generate the the origami cell

    """

    def __init__(self):
        """ Constructor """
        Pattern.__init__(self)  # Must be called in order to parse common options

        # save all custom parameters defined on .inx file
        self.add_argument('--radius', type=self.float, default=10.0)
        self.add_argument('--sides', type=self.int, default=6)
        self.add_argument('--rows', type=self.int, default=3)
        self.add_argument('--extra_column', type=self.bool, default=False)

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

        self.path_tree = []
        self.edge_points = []
        self.vertex_points = []
        self.translate = (0, 0)

    @abstractmethod
    def parse_parameters(self):
        """ Parse custom parameters of Cylindrical pattern """
        raise NotImplementedError("Function parse_parameters must be implemented")

    @abstractmethod
    def generate_cell(self):
        """ Generate the the origami cell """
        raise NotImplementedError("Function generate_cell must be implemented")

    def generate_path_tree(self):
        """ Specialized path generation for your origami pattern """
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
            self.options.add_middle_slot = False

        self.parse_parameters()

        # pre-calculate width before adding one to sides, for easier attachment
        self.options.width = 2 * self.options.radius * sin(pi / self.options.sides)
        self.options.cols = self.options.sides + self.options.extra_column

        # get cell definitions
        cell_data = self.generate_cell()

        # calculate divider if it doesn't exist
        if 'divider' not in cell_data:
            points = Path.get_points(cell_data['interior'])
            x = [p[0] for p in points if p[1] == 0]
            cell_data['divider'] = Path([(min(x), 0),
                                         (max(x), 0)], style='m')

        points = Path.get_points(cell_data['divider'])
        x = [p[0] for p in points]
        DX = max(x) - min(x)

        if 'edge_right' not in cell_data and 'edge_left' in cell_data:
            cell_data['edge_right'] = []
            for edge_left in cell_data['edge_left']:
                edge_right = edge_left + (DX, 0)
                edge_right.invert()
                cell_data['edge_right'].append(edge_right)

        if 'edge_right' in cell_data and 'edge_left' not in cell_data:
            cell_data['edge_left'] = []
            for edge_right in cell_data['edge_right']:
                edge_left = edge_right + (-DX, 0)
                edge_left.invert()
                cell_data['edge_left'].append(edge_left)

        cell_data['dx'], cell_data['dy'] = self.get_dxdy(cell_data)

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

    def get_dxdy(self, cell_data):
        """ Get starting position of rows and columns"""
        dx = [0]
        dy = [0]
        for edge in cell_data['edge_left']:
            dx.append(edge.points[1][0] - edge.points[0][0])
            dy.append(edge.points[1][1] - edge.points[0][1])
        return list(accumulate(dx)), list(accumulate(dy))

    def generate_interior(self, cell_data):
        """ Retrieve conversion factor for selected unit"""
        unit_factor = self.calc_unit_factor()
        rows = self.options.rows
        base_height = self.options.base_height * unit_factor
        distance = self.options.distance * unit_factor

        interiors = []
        for i in range(rows):
            dx = cell_data['dx'][i]
            dy = cell_data['dy'][i] + base_height + i * distance
            pattern = cell_data['interior'][i]
            interiors.append(Path.list_add(pattern, (dx, dy)))
        return interiors

    def generate_horizontal_dividers(self, cell_data):
        """ Return lines dividing cell rows """
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
            dy = cell_data['dy'][i] + base_height + (i - 1) * distance
            dividers.append(divider + (dx, dy))
            if self.options.add_middle_slot:
                dividers.append(divider + (dx, dy + distance))

        if self.options.add_base_slot:
            dx = cell_data['dx'][-1]
            dy = cell_data['dy'][-1] + base_height + (rows - 1) * distance
            dividers.append(divider + (dx, dy))

        return dividers

    def generate_all_slots(self, cell_data):
        """ Return lines of all in base and between cells,
        According to options
        """
        dx_ = cell_data['dx']
        dy_ = cell_data['dy']

        # retrieve conversion factor for selected unit
        unit_factor = self.calc_unit_factor()

        # retrieve saved parameters, and apply unit factor where needed
        cols = self.options.cols
        rows = self.options.rows
        width = self.options.width * unit_factor

        dist = self.options.distance * unit_factor
        base_height = self.options.base_height * unit_factor
        height = [dy_[i] + base_height + (i - 1) * dist for i in range(rows+1)]

        base = {'left': [],
                'right': [],
                'slots': []}

        if self.options.add_base_slot:
            base_slot_height = self.options.base_slot_height * unit_factor
            base_slot_width = self.options.base_slot_width * unit_factor
            base_slot_sizes = [base_slot_height, base_slot_width, base_height, width]

            base_slot_top = generate_slot_line(
                cols, +int(self.options.base_slot_position), *base_slot_sizes)
            base_slot_bot = generate_slot_line(
                cols, -int(self.options.base_slot_position), *base_slot_sizes)

            base['slots'] = [base_slot_top, Path.list_add(base_slot_bot, (dx_[-1], height[-1]))]

            base['left'] = [Path([(0, 0), (0, base_height)], style = 'e'),
                            Path([(dx_[-1], height[-1]),
                                  (dx_[-1], height[-1] + base_height)], style = 'e')]

            base['right'] = [Path([(dx_[-1] + cols*width, height[-1] + base_height),
                                   (dx_[-1] + cols*width, height[-1] + base_height)], style = 'e'),
                             Path([(cols*width, base_height),
                                   (cols*width, 0)], style = 'e')]

        middle = {'left': [],
                  'right': [],
                  'slots': []}

        if self.options.add_middle_slot:
            middle_slot_height = self.options.middle_slot_height * unit_factor
            middle_slot_width = self.options.middle_slot_width * unit_factor
            middle_slot_sizes = [middle_slot_height, middle_slot_width, dist, width]

            middle_slot = generate_slot_line(
                cols, +int(self.options.middle_slot_position), *middle_slot_sizes)

            middle['slots'] = [Path.list_add(middle_slot,
                                          (dx_[i], height[i]))
                                           for i in range(1, rows)]

            middle['left'] = [Path([(0, 0),
                                    (0, dist)], style='e') +
                              (dx_[i+1], dy_[1] + dist + height[i]) for i in range(rows-1)]

            middle['right'] = [
                Path([(0, height[rows-2] + base_height + (rows - 1) * dist),
                      (0, dy_[-2] + base_height +  (rows - 2) * dist)], style='e') +
                            (dx_[-(i+2)] + cols*width, -dy_[i] - i*dist) for i in range(rows - 1)]

        return base, middle

    def generate_fused_edge_points(self, base, middle, cell_data):
        """ Generate edge lines """
        unit_factor = self.calc_unit_factor()
        base_height = self.options.base_height * unit_factor
        distance = self.options.distance * unit_factor
        rows = self.options.rows

        edges = []
        # top, left corner
        if self.options.add_base_slot:
            edges.append(base['left'][0])

        for i in range(rows):
            cell_left = cell_data['edge_left'][i]
            dx = cell_data['dx'][i]
            edges.append(
                cell_left + (dx, cell_data['dy'][i] + base_height + i * distance))

            if self.options.add_middle_slot and i < rows - 1:
                edges.append(middle['left'][i] + (0, 0))

        # bottom, left corner
        if self.options.add_base_slot:
            edges.append(base['left'][1])

        # bottom, right corner
        if self.options.add_base_slot:
            edges.append(base['right'][0])

        for i in range(rows):
            cell_right = cell_data['edge_right'][-(i + 1)]
            dx = cell_data['dx'][-(i + 2)]
            edges.append(
                cell_right + \
                    (dx, cell_data['dy'][rows - i - 1] + base_height + (rows - i - 1) * distance))

        # TODO: Study why I had added the following lines
        #     if self.options.add_middle_slot and i < rows - 1:
        #         edges.append(middle['right'][i] + (0, 0))

        # top, right corner
        if self.options.add_base_slot:
            edges.append(base['right'][1])

        return Path.get_points(edges)
