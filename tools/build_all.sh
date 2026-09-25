#!/usr/bin/env bash
# Regenerate everything after editing hopper.scad:
#   geometry checks -> performance report -> section plots -> STL/3MF -> images
# Needs: openscad, xvfb-run (for images), python3 with trimesh manifold3d shapely scipy matplotlib lxml
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/check_geometry.py
python3 tools/hopper_calc.py --md docs/PERFORMANCE.md > /dev/null
python3 tools/section_plot.py
python3 tools/export_stl.py
R() { xvfb-run -a openscad -q -o "images/$1.png" --imgsize=1200,900 --colorscheme=Tomorrow --projection=p "--camera=$3" -D "view=\"$2\"" hopper.scad; }
R assembled assembled 0,0,19,62,0,40,145
R cocked    cocked    0,0,19,62,0,40,145
R firing    firing    3,-3,10,60,0,40,110
R exploded  exploded  0,0,45,72,0,40,230
R print     print     0,0,0,0,0,0,310
echo "build OK"
