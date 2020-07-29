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
To simplify manual editing on Inkscape, the drawn pattern is composed of subgroups of
of strokes.
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
- Waterbomb tesselation (and Magic Ball)
- Kresling tower
- Hypar (hyperbolic paraboloid approximate)

## For creation of new patterns:
- See `origami_patterns_template.inx` and `OrigamiPatterns/Template.py` for an example!

## Todo:
- Add more patterns if necessary
- Add option to draw points

## Deprecation and compatibility issues:
Deprecated functions are being replaced for Inkscape 1.0 while making sure it still works with older versions of Inkscape.
What still does not work in Inkscape 1.0:
- Dashed strokes break everything


## Simulation:
To simulate the patterns, Amanda Ghassaei's [OrigamiSimulator](http://apps.amandaghassaei.com/OrigamiSimulator/) can be used:

- Check foldability of pattern (simulation mode with semicreases for circular pleat, triangulation for hypar, etc)
- Create desired pattern with properly selected parameters
- Set default values for all stroke colors (check `File > File Import Tips` on OrigamiSimulator)
- IMPORTANT: Before saving, de-group every object, since OrigamiSimulator does not currently work with Inkscape's group transforms.
- Save as .svg
- Import .svg file from OrigamiSimulator

If pattern does not import correctly, you can try to create a bigger version of the same pattern.

