# Origami Patterns
Inkscape extension that creates origami tesselation patterns.

## Installation:
To install a new extension, download and unpack the archive file. Copy the files into the directory listed at `Edit > Preferences > System: User extensions`

On Windows, the default directory is:
`C:\Program Files\Inkscape\share\extensions`

While on Linux, the directory is:
`/home/$USER/.config/inkscape/extensions/`

## Accessing the extension:
The extension can be found on `Extensions > Origami Patterns`

## Input parameters:
### Custom parameters (depends on desired Pattern)
- Number of lines
- Number of columns
- etc...
### Common parameters
- Desired unit (mm, cm, px, etc.)
- Color for every type of stroke (mountain creases, valley creases and edges)
- Dashes for every type os stroke
- Width for every type of stroke
### Extra parameters
- Semicreases, universal creases and cuts (for Kirigami) can also be implemented, if needed.

## Output:
Creates the pattern.
To simplify manual editing on Inkscape, the drawn pattern is composed of subgroups of strokes.
For example, ungrouping the Waterbomb tesselation, you get three distinct groups of objects:
- the mountain creases
- the valley creases
- the edges

These groups can also be divided into smaller groups:

```
waterbomb
├── edges
│   ├── bottom
│   ├── left
│   ├── right
│   └── top
│
├── mountains
│   ├── horizontal lines
│   └── vertical lines
│
└── valleys
    ├── line 1_a
    ├── line 1_b
    │
    ├── line 2_a
    ├── line 2_b
    │
    ├── ...
    │
    ├── line N_a
    └── line N_b
```

## Patterns implemented until now:
- Simple Masu Box
- Waterbomb tesselation (and Magic Ball)
- Hypar (hyperbolic paraboloid approximate)
- Circular pleat (with special simulation mode)
- Kresling tower (using parameters as defined in: [https://doi.org/10.1115/SMASIS2016-9071](https://doi.org/10.1115/SMASIS2016-9071))
- Bendy Straw (as published in: [https://doi.org/10.1115/1.4052222](https://doi.org/10.1115/1.4052222))

## Patterns planned to be implemented
- Miura Ori tesselation.

### Cylindrical Class: Subclass of Pattern for automatic generation of slots for rigid support
-  Cylindrical Kresling tower
- Bendy Straw Kresling tower
### Misc
- Rigid support for Cylindrical patterns

An OpenSCAD implementation of a belt that can be used with the support is found in: `Origami_Patterns/Support_Ring_Belt/`.


## For creation of new patterns:
- See `origa_template.inx` and `OrigamiPatterns/Template.py` for an example!
- See `origa_cylindrical_template.inx` and `OrigamiPatterns/Cylindrical_Template.py` for an example on cylindrical patterns!

## Deprecation and compatibility issues:
This extension is no longer compatible for Inkscape versions below `1.0`.

## Simulation:
To simulate the patterns, Amanda Ghassaei's [OrigamiSimulator](http://apps.amandaghassaei.com/OrigamiSimulator/) can be used:

- Check foldability of pattern (simulation mode with semicreases for circular pleat, triangulation for hypar, etc)
- Create desired pattern with properly selected parameters
- Set default values for all stroke colors (check `File > File Import Tips` on OrigamiSimulator)
- IMPORTANT: Before saving, de-group every object, since OrigamiSimulator does not currently work with Inkscape's group transforms.
- Save as .svg
- Import .svg file from OrigamiSimulator

If pattern does not import correctly, you can try to create a bigger version of the same pattern.

## TODO:
- I was unaware of many Python style guidelines when I started this project, which must be fixed.
- `Bendy` should be re-implemented as an instance of `Cylindrical`.

