Resyth Tileset v0.1.0
=====================

This plugin expands upon the Resynthesizer plugin to synthesize
tilesets. It requires that plugin installed. Tested with GIMP 2.8.

Installation
------------

Install GIMP 2.8 and the Resynthesizer plugin, found at
<https://github.com/bootchk/resynthesizer> or
<http://www.logarithmic.net/pfh/resynthesizer>.

Then copy `plugin-resyth-tileset.py` to your plugins directory (which
can be found in GIMP's `Preferences > Folders`), and restart GIMP.

Uninstalling
------------

Delete the files added in installation.

Usage
-----

Resynth Tileset works much like the base Resynthesizer in texture
transfer mode. It expects a sample image, and input output maps
describing how to map parts of the sample to the output. However, now
the output map must be in an expected format, a 10 by 5 layout of
tiles.

Use `Filters > Tileset > Generate Resynth Tileset Output Map` to
generate an example output map with the right format. It can be edited
further to customize the output, before running `Filters > Tileset > Resynth Tileset`
to generate the actual image.

Further explanation can be found in the wiki on github: <https://github.com/boristhebrave/resynth-tiles/wiki>

License
-------
This code is licensed under the GPL3 copyright Adam Newgas 2013.

