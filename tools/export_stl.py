#!/usr/bin/env python3
"""Export print-ready files into stl/:
  * one STL per part, in print orientation, centred on the origin
  * hopper_plate.3mf : every part as a separate object laid out for the
    A1 mini (180 x 180) plate -- open directly in Bambu Studio
  * hopper_plate.stl : the same plate as a single mesh
Also verifies the plate: 10 separate bodies, all on the bed, inside 180 x 180.
"""
import os, subprocess, sys
import numpy as np, trimesh
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, "hopper.scad")
OUT = os.path.join(ROOT, "stl")
os.makedirs(OUT, exist_ok=True)
PARTS = ["foot", "body", "frame", "lever", "stem_pin", "sear_pin", "pivot_pin"]

def scad(out, *defs):
    cmd = ["openscad", "-q", "-o", out]
    for d in defs:
        cmd += ["-D", d]
    subprocess.run(cmd + [SCAD], check=True)

for p in PARTS:
    fn = os.path.join(OUT, f"hopper_{p}.stl")
    scad(fn, 'view="part"', f'part="{p}"')
    m = trimesh.load(fn)
    assert m.is_watertight, p
    assert abs(m.bounds[0][2]) < 1e-6, f"{p} not on the bed"
    print(f"{p:10s} {m.extents.round(1)} mm, {m.volume:7.0f} mm^3")

plate = os.path.join(OUT, "hopper_plate.stl")
scad(plate, 'view="print"', "show_bed=false")
m = trimesh.load(plate)
bodies = m.split(only_watertight=False)
lo, hi = m.bounds
print(f"plate: {len(bodies)} separate bodies, x[{lo[0]:.1f},{hi[0]:.1f}] y[{lo[1]:.1f},{hi[1]:.1f}] z[{lo[2]:.1f},{hi[2]:.1f}]")
ok = len(bodies) == 10 and (np.abs(m.bounds[:, :2]) <= 88).all() and abs(lo[2]) < 1e-6
ok &= all(abs(b.bounds[0][2]) < 1e-6 for b in bodies)
scene = trimesh.Scene()
names = []
for b in sorted(bodies, key=lambda b: -b.volume):
    names.append(f"part_{len(names)}")
    scene.add_geometry(b, geom_name=names[-1])
# Bambu Studio expects the plate centre at (90, 90)
scene.apply_translation([90, 90, 0])
with open(os.path.join(OUT, "hopper_plate.3mf"), "wb") as f:
    f.write(trimesh.exchange.threemf.export_3MF(scene))
print("wrote stl/hopper_plate.3mf with", len(names), "objects")
print("PLATE OK" if ok else "PLATE CHECK FAILED")
sys.exit(0 if ok else 1)
