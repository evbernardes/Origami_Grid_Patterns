#! /usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod
import inkex
from lxml import etree
from Path import Path

class Pattern(inkex.Effect):
    """ Class that inherits inkex.Effect and further specializes it for different
    Patterns generation

    Attributes
    ----------
    styles_dict: dict
            defines styles for every possible stroke. Default values are:
            styles_dict = {'m' : mountain_style,
                           'v' : valley_style,
                           'e' : edge_style}

    topgroup: etree.SubElement
            Top Inkscape group element

    path_tree: nested list
        Contains "tree" of Path instances, defining new groups for each
        sublist

    translate: 2 sized tuple
        Defines translation to be added when drawing to Inkscape (default: 0,0)

    Methods
    -------

    effect(self)
        Main function, called when the extension is run.

    create_styles_dict(self)
        Get stroke style parameters and use them to create the styles dictionary.

    calc_unit_factor(self)
        Return the scale factor for all dimension conversions

    get_color_string(self, longColor, verbose=False)
        Convert the long into a #RRGGBB color value

    Abstract Methods
    ----------------

    __init__(self)
        Parse all options

    generate_path_tree(self)
        Generate nested list of Path

    """

    @abstractmethod
    def generate_path_tree(self):
        """ Generate nested list of Path instances
        Abstract method, must be defined in all child classes
        """
        raise NotImplementedError("Function generate_path_tree must be implemented")

    @abstractmethod
    def __init__(self):
        """ Parse all common options

        Must be reimplemented in child classes to parse specialized options
        """
        inkex.Effect.__init__(self)  # initialize the super class

        self.add_argument = self.arg_parser.add_argument

        self.add_argument('-u', '--units', type=str, default='mm')

        # bypass most style options for OrigamiSimulator
        self.add_argument('--simulation_mode', type=inkex.Boolean, default=False)

        # mountain options
        self.add_argument('--mountain_stroke_color', type=str,  default=4278190335)  # Red
        self.add_argument('--mountain_stroke_width', type=float, default=0.1)
        self.add_argument('--mountain_dashes_len', type=float, default=1.0)
        self.add_argument('--mountain_dashes_duty', type=float, default=0.5)
        self.add_argument('--mountain_dashes_bool', type=inkex.Boolean, default=True)
        self.add_argument('--mountain_bool', type=inkex.Boolean, default=True)
        self.add_argument('--mountain_bool_only', type=inkex.Boolean, default=False)

        # valley options
        self.add_argument('--valley_stroke_color', type=str, default=65535)  # Blue
        self.add_argument('--valley_stroke_width', type=float, default=0.1)
        self.add_argument('--valley_dashes_len', type=float, default=1.0)
        self.add_argument('--valley_dashes_duty', type=float, default=0.25)
        self.add_argument('--valley_dashes_bool', type=inkex.Boolean, default=True)
        self.add_argument('--valley_bool', type=inkex.Boolean, default=True)
        self.add_argument('--valley_bool_only', type=inkex.Boolean, default=False)

        # edge options
        self.add_argument('--edge_stroke_color', type=str,  default=255)  # Black
        self.add_argument('--edge_stroke_width', type=float, default=0.1)
        self.add_argument('--edge_dashes_len', type=float, default=1.0)
        self.add_argument('--edge_dashes_duty', type=float, default=0.25)
        self.add_argument('--edge_dashes_bool', type=inkex.Boolean, default=False)
        self.add_argument('--edge_bool', type=inkex.Boolean, default=True)
        self.add_argument('--edge_bool_only', type=inkex.Boolean, default=False)
        self.add_argument('--edge_single_path', type=inkex.Boolean, default=True)

        # universal crease options
        self.add_argument('--universal_stroke_color', type=str, default=4278255615)  # Magenta
        self.add_argument('--universal_stroke_width', type=float, default=0.1)
        self.add_argument('--universal_dashes_len',  type=float,  default=1.0)
        self.add_argument('--universal_dashes_duty', type=float, default=0.25)
        self.add_argument('--universal_dashes_bool', type=inkex.Boolean, default=False)
        self.add_argument('--universal_bool', type=inkex.Boolean, default=True)
        self.add_argument('--universal_bool_only', type=inkex.Boolean, default=False)

        # semicrease options
        self.add_argument('--semicrease_stroke_color', type=str, default=4294902015)  # Yellow
        self.add_argument('--semicrease_stroke_width', type=float, default=0.1)
        self.add_argument('--semicrease_dashes_len', type=float, default=1.0)
        self.add_argument('--semicrease_dashes_duty', type=float, default=0.25)
        self.add_argument('--semicrease_dashes_bool', type=inkex.Boolean, default=False)
        self.add_argument('--semicrease_bool', type=inkex.Boolean, default=True)
        self.add_argument('--semicrease_bool_only', type=inkex.Boolean, default=False)

        # cut options
        self.add_argument('--cut_stroke_color', type=str, default=16711935)  # Green
        self.add_argument('--cut_stroke_width', type=float, default=0.1)
        self.add_argument('--cut_dashes_len', type=float, default=1.0)
        self.add_argument('--cut_dashes_duty', type=float, default=0.25)
        self.add_argument('--cut_dashes_bool', type=inkex.Boolean, default=False)
        self.add_argument('--cut_bool', type=inkex.Boolean, default=True)
        self.add_argument('--cut_bool_only', type=inkex.Boolean, default=False)

        # vertex options
        self.add_argument('--vertex_stroke_color', type=str, default=255)  # Black
        self.add_argument('--vertex_stroke_width', type=float, default=0.1)
        self.add_argument('--vertex_radius', type=float, default=0.1)
        self.add_argument('--vertex_dashes_bool', type=inkex.Boolean, default=False)
        self.add_argument('--vertex_bool', type=inkex.Boolean, default=True)
        self.add_argument('--vertex_bool_only', type=inkex.Boolean, default=False)

        # here so we can have tabs - but we do not use it directly - else error
        self.add_argument('--active-tab', type=str, default='title')  # use a legitimate default

        self.path_tree = []
        self.edge_points = []
        self.vertex_points = []
        self.translate = (0, 0)
        self.styles_dict = {}

    def effect(self):
        """ Main function, called when the extension is run.
        """
        # bypass most style options if simulation mode is choosen
        self.check_simulation_mode()

        # check if any selected to print only some of the crease types:
        bool_only_list = [
            self.options.mountain_bool_only,
            self.options.valley_bool_only,
            self.options.edge_bool_only,
            self.options.universal_bool_only,
            self.options.semicrease_bool_only,
            self.options.cut_bool_only,
            self.options.vertex_bool_only
            ]

        if sum(bool_only_list) > 0:
            self.options.mountain_bool = self.options.mountain_bool and self.options.mountain_bool_only
            self.options.valley_bool = self.options.valley_bool and self.options.valley_bool_only
            self.options.edge_bool = self.options.edge_bool and self.options.edge_bool_only
            self.options.universal_bool = self.options.universal_bool and self.options.universal_bool_only
            self.options.semicrease_bool = self.options.semicrease_bool and self.options.semicrease_bool_only
            self.options.cut_bool = self.options.cut_bool and self.options.cut_bool_only
            self.options.vertex_bool = self.options.vertex_bool and self.options.vertex_bool_only

        # construct dictionary containing styles
        self.create_styles_dict()

        # get paths for selected origami pattern
        self.generate_path_tree()

        # get vertex points and add them to path tree
        vertex_radius = self.options.vertex_radius * self.calc_unit_factor()
        vertices = []
        self.vertex_points = list(set(self.vertex_points)) # remove duplicates
        for vertex_point in self.vertex_points:
            vertices.append(Path(vertex_point, style='p', radius=vertex_radius))
        self.path_tree.append(vertices)

        # Translate according to translate attribute
        g_attribs = {
            inkex.addNS('label', 'inkscape'): f'{self.options.pattern}',
            inkex.addNS('transform-center-x', 'inkscape'): str(0),
            inkex.addNS('transform-center-y', 'inkscape'): str(0),
            'transform': 'translate{self.translate}'
            }

        # add the group to the document's current layer
        layer = self.svg.get_current_layer()
        if isinstance(self.path_tree, list) and len(self.path_tree) != 1:
            self.topgroup = etree.SubElement(layer, 'g', g_attribs)
        else:
            self.topgroup = layer

        if len(self.edge_points) == 0:
            Path.draw_paths_recursively(self.path_tree, self.topgroup, self.styles_dict)
        elif self.options.edge_single_path:
            edges = Path(self.edge_points, 'e', closed=True)
            Path.draw_paths_recursively(self.path_tree + [edges], self.topgroup, self.styles_dict)
        else:
            edges = Path.generate_separated_paths(self.edge_points, 'e', closed=True)
            Path.draw_paths_recursively(self.path_tree + edges, self.topgroup, self.styles_dict)

    def check_simulation_mode(self):
        """ If simulation mode is selected, use OrigamiSimulator settings
        """
        if not self.options.simulation_mode:
            pass

        else:
            self.options.mountain_stroke_color = 4278190335
            self.options.mountain_dashes_len = 0
            self.options.mountain_dashes_bool = False
            self.options.mountain_bool_only = False
            self.options.mountain_bool = True

            self.options.valley_stroke_color = 65535
            self.options.valley_dashes_len = 0
            self.options.valley_dashes_bool = False
            self.options.valley_bool_only = False
            self.options.valley_bool = True

            self.options.edge_stroke_color = 255
            self.options.edge_dashes_len = 0
            self.options.edge_dashes_bool = False
            self.options.edge_bool_only = False
            self.options.edge_bool = True

            self.options.universal_stroke_color = 4278255615
            self.options.universal_dashes_len = 0
            self.options.universal_dashes_bool = False
            self.options.universal_bool_only = False
            self.options.universal_bool = True

            self.options.cut_stroke_color = 16711935
            self.options.cut_dashes_len = 0
            self.options.cut_dashes_bool = False
            self.options.cut_bool_only = False
            self.options.cut_bool = True

            self.options.vertex_bool = False

    def create_styles_dict(self):
        """ Get stroke style parameters and use them to create the styles dictionary,
            used for the Path generation.
        """
        unit_factor = self.calc_unit_factor()

        def create_style(style_type):
            style = {'draw': getattr(self.options, style_type+"_bool"),
                     'stroke': self.get_color_string(getattr(self.options, style_type+"_stroke_color")),
                     'fill': 'none',
                     'stroke-width': getattr(self.options, style_type+"_stroke_width") * unit_factor}

            if getattr(self.options, style_type+"_dashes_bool"):
                dash_gap_len = getattr(self.options, style_type+"_dashes_len")
                duty = getattr(self.options, style_type+"_dashes_duty")
                dash = (dash_gap_len * unit_factor) * duty
                gap = (dash_gap_len * unit_factor) * (1 - duty)
                style['stroke-dasharray'] = f'{dash} {gap}'
            return style

        self.styles_dict['m'] = create_style("mountain")
        self.styles_dict['v'] = create_style("valley")
        self.styles_dict['u'] = create_style("universal")
        self.styles_dict['s'] = create_style("semicrease")
        self.styles_dict['c'] = create_style("cut")
        self.styles_dict['e'] = create_style("edge")
        self.styles_dict['p'] = create_style("vertex")

    def get_color_string(self, long_color, verbose=False):
        """ Convert the long into a #RRGGBB color value
            - verbose=true pops up value for us in defaults
            conversion back is A + B*256^1 + G*256^2 + R*256^3
        """
        long_color = int(long_color)
        hex_color = hex(long_color)[2:-2]

        hex_color = '#' + hex_color.rjust(6, '0').upper()
        if verbose:
            inkex.utils.debug(f"long_color = {long_color}, hex = {hex_color}")

        return hex_color

    def calc_unit_factor(self):
        """ Return the scale factor for all dimension conversions.

            - The document units are always irrelevant as
              everything in inkscape is expected to be in 90dpi pixel units
        """
        # namedView = self.document.getroot().find(inkex.addNS('namedview', 'sodipodi'))
        # doc_units = self.getUnittouu(str(1.0) + namedView.get(inkex.addNS('document-units', 'inkscape')))
        # backwards compatibility
        return self.svg.unittouu(str(1.0) + self.options.units)






