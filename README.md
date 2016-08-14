#svg2sfd

Convert SVG to FontForge SFD format

##Installation

```
sudo python setup.py install
```

##Usage

```
Usage: svg2sfd [-h] -i INPUT [-o OUTPUT] [-n NAME] [-f FAMILY] [-c COPYRIGHT]
               [-w WEIGHT] [-v VERSION]

Convert SVG to FontForge SFD format

optional arguments:
  -h, --help                           show this help message and exit
  -i INPUT, --input INPUT              input filename
  -o OUTPUT, --output OUTPUT           output filename
  -n NAME, --name NAME                 font name
  -f FAMILY, --family FAMILY           font family name
  -c COPYRIGHT, --copyright COPYRIGHT  font copyright
  -w WEIGHT, --weight WEIGHT           font weight/number
  -v VERSION, --version VERSION        font version number
```

##Formatting

The input SVG file should be formatted in a grid of cells 1000x1000 pixels.

Each glyph should be wrapped in a `<g></g>` group, the `id` of which represents which letter to replace. Ex:

```
<g id="A">
    Some SVG...
</g>
```

The `id` can also be a hex code in one of two formats:

```
<g id="U+1024">
    Some SVG...
</g>
<g id="0x2048">
    Some SVG...
</g>
```

Note: Here are a few things that are currently not supported:

* Transforms of any kind
* Relative positionings in the `d` attribute of the `<path>` element
* `A` support in the `<path>` element (along with a few other arc functions)