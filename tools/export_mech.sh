#!/usr/bin/env bash
# Export individual parts in mechanism frame for geometry checks.
# usage: tools/export_mech.sh OUTDIR part zb angle
set -e
out=$1; part=$2; zb=${3:-0}; a=${4:-0}
openscad -q -o "$out/${part}_zb${zb}_a${a}.stl" -D "view=\"mech\"" -D "mech_part=\"$part\"" \
  -D "mech_zb=$zb" -D "mech_a=$a" "$(dirname "$0")/../hopper.scad"
