#!/usr/bin/env python3
"""Draw true cross-sections of the latch (u-z plane) for the docs.

Top row: the lever mid-plane (v = 0).  Bottom row: the prong plane
(v = 4.4 mm) where the sear pin rests on the barbs.
Columns: resting, cocked/latched, pedal pressed (released).
Writes images/latch_sections.png.
"""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_geometry import part, scad_params, ROOT

COL = {"foot": "#4a7fb0", "frame": "#d9b43a", "body": "#f08a24", "lever": "#c8283c",
       "sear_pin": "#9a9a9a", "stem_pin": "#9a9a9a", "pivot_pin": "#9a9a9a"}

def draw(ax, meshes, v, title, xlim=(-8, 29), ylim=(-1, 17)):
    for name, m in meshes.items():
        sec = m.section(plane_origin=[0, v, 0], plane_normal=[0, 1, 0])
        if sec is None:
            continue
        for ent in sec.discrete:
            pts = [(p[0], p[2]) for p in ent]
            ax.add_patch(Polygon(pts, closed=True, fc=COL[name], ec="k", lw=0.5, alpha=0.95))
    ax.axhline(0, color="k", lw=1.5)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.25)

def main():
    P = scad_params()
    zr, zl = P["z_b_rest"], P["z_b_latch"]
    rel = 16.0
    states = [("resting (body up)", zr, 0.0), ("cocked & latched", zl, 0.0),
              (f"pedal pressed {rel:.0f} deg -> fires", zl + 0.02, rel)]
    fig, axes = plt.subplots(2, 3, figsize=(15, 6.4))
    for col, (label, zb, a) in enumerate(states):
        meshes = {n: part(n) for n in ["foot", "frame", "stem_pin", "pivot_pin"]}
        meshes["body"] = part("body", zb)
        meshes["lever"] = part("lever", 0, a)
        meshes["sear_pin"] = part("sear_pin", 0, a)
        draw(axes[0, col], meshes, 0.0, f"{label} - lever plane v=0")
        draw(axes[1, col], meshes, 4.4, f"{label} - barb plane v=4.4")
    for ax in axes[1]:
        ax.set_xlabel("u (mm, toward pedal corner)", fontsize=8)
    for ax in axes[:, 0]:
        ax.set_ylabel("z (mm)", fontsize=8)
    handles = [plt.Rectangle((0, 0), 1, 1, fc=COL[k]) for k in ["foot", "frame", "body", "lever", "sear_pin"]]
    fig.legend(handles, ["foot", "frame (T)", "body", "pedal lever", "pins"], loc="lower center", ncol=5, fontsize=9)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out = os.path.join(ROOT, "images", "latch_sections.png")
    fig.savefig(out, dpi=110)
    print("wrote", out)

if __name__ == "__main__":
    main()
