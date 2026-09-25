#!/usr/bin/env python3
"""Geometry verification for hopper.scad.

Exports every part in the mechanism frame for several mechanism states and
checks, with exact mesh booleans (manifold3d via trimesh):

  * every mesh is a closed, valid solid
  * no two parts overlap in the rest, latched and bottomed-out states
  * the sear cam: for each body height while cocking, the smallest pedal
    rotation that lets the body pass, and that the lever is then still clear
    of everything else
  * the pedal can rotate far past release (free "decoupling" swing)
  * the whole assembled toy (with bands) fits inside the 42 mm cube
  * part volumes, masses and centres of mass (written to build/mass.json)

Usage:  python3 tools/check_geometry.py        (needs openscad, trimesh, manifold3d)
"""
import json, math, os, subprocess, sys, itertools, functools
import numpy as np
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAD = os.path.join(ROOT, "hopper.scad")
TMP = os.path.join(ROOT, "build", "mech")
os.makedirs(TMP, exist_ok=True)

PLA_DENSITY = 1.24          # g/cm^3
SOLID_FILL = 0.97           # 100 % infill prints at ~97 % of solid density

failures = []
def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        failures.append(msg)

def scad_params():
    out = subprocess.run(["openscad", "-o", os.path.join(TMP, "info.echo"), "-D", 'view="info"', SCAD],
                         capture_output=True, text=True)
    txt = open(os.path.join(TMP, "info.echo")).read()
    body = txt.split("HOPPER ")[1].split('"')[0]
    return {k: float(v) for k, v in (kv.split("=") for kv in body.split())}

@functools.lru_cache(maxsize=None)
def part(name, zb=0.0, a=0.0, view="mech", extra=()):
    fn = os.path.join(TMP, f"{name}_{zb:.3f}_{a:.3f}_{view}_{'_'.join(extra)}.stl")
    if not os.path.exists(fn) or os.path.getmtime(fn) < os.path.getmtime(SCAD):
        cmd = ["openscad", "-q", "-o", fn, "-D", f'view="{view}"', "-D", f'mech_part="{name}"',
               "-D", f"mech_zb={zb}", "-D", f"mech_a={a}"]
        for e in extra:
            cmd += ["-D", e]
        subprocess.run(cmd + [SCAD], check=True)
    return trimesh.load(fn)

def overlap(m1, m2):
    if not (m1.bounds[0] < m2.bounds[1]).all() or not (m2.bounds[0] < m1.bounds[1]).all():
        return 0.0
    r = trimesh.boolean.intersection([m1, m2], engine="manifold")
    return 0.0 if r.is_empty else float(r.volume)

STATIC = ["foot", "frame", "stem_pin", "pivot_pin"]

def config(zb, a):
    parts = {n: part(n) for n in STATIC}
    parts["body"] = part("body", zb)
    parts["lever"] = part("lever", 0, a)
    parts["sear_pin"] = part("sear_pin", 0, a)
    return parts

def max_overlap(parts, only=None, tol=1e-3):
    worst = (0.0, None)
    for (n1, m1), (n2, m2) in itertools.combinations(parts.items(), 2):
        if only and n1 not in only and n2 not in only:
            continue
        if {n1, n2} == {"lever", "sear_pin"}:
            continue                      # pressed together by design
        v = overlap(m1, m2)
        if v > worst[0]:
            worst = (v, f"{n1}/{n2}")
    return worst

def main():
    P = scad_params()
    print("Parameters:", P)
    zr, zl = P["z_b_rest"], P["z_b_latch"]
    zmin = zl - 0.8

    print("\n[1] Mesh validity")
    for n in STATIC + ["body", "lever", "sear_pin"]:
        m = part(n, zr if n == "body" else 0)
        check(m.is_watertight and m.is_volume, f"{n}: closed solid ({len(m.faces)} faces)")

    print("\n[2] Interference in static states (tolerance 0.001 mm^3)")
    for label, zb in [("rest", zr), ("latched", zl), ("bottomed-out", zmin)]:
        v, who = max_overlap(config(zb, 0))
        check(v < 1e-3, f"{label:13s} zb={zb:6.2f}: max overlap {v:.4f} mm^3 {who or ''}")

    print("\n[3] Cocking: pedal rotation the barbs force while the body passes")
    worst_a = 0.0
    zb = zmin
    while zb <= 8.0:
        body = part("body", round(zb, 3))
        a = 0.0
        while a <= 40:
            if overlap(body, part("lever", 0, a)) + overlap(body, part("sear_pin", 0, a)) < 1e-3:
                break
            a += 1.0
        others = {n: part(n) for n in STATIC}
        others["body"] = body
        others["lever"] = part("lever", 0, a)
        others["sear_pin"] = part("sear_pin", 0, a)
        v, who = max_overlap(others, only={"lever", "sear_pin"})
        latched = "  <- latch point" if abs(zb - zl) < 1e-6 else ""
        print(f"     zb={zb:5.2f}  lever needs {a:4.1f} deg   other overlap {v:.4f} {who or ''}{latched}")
        check(v < 1e-3 and a < 40, f"cocking at zb={zb:.2f} is possible")
        if zb > zl + 1e-6:
            worst_a = max(worst_a, a)
        zb += 0.4
    check(part_needed_at_latch(zl) == 0.0, "at the latch height the sear pin sits over the barbs with the lever at rest")

    print("\n[4] Release: pedal angle where the body is let go (body held at latch height)")
    body = part("body", zl + 0.02)
    rel = None
    for a10 in range(0, 400, 5):
        a = a10/10
        pin = part("sear_pin", 0, a)
        # the pin is released when it no longer overlaps the barbs in plan view:
        # lift the body by 1 mm and check the pin is clear of it
        lifted = part("body", round(zl + 1.0, 3))
        if overlap(lifted, pin) < 1e-3 and overlap(lifted, part("lever", 0, a)) < 1e-3:
            rel = a
            break
    check(rel is not None and rel < 25, f"sear releases at about {rel} deg of lever rotation")

    print("\n[5] Free swing after release (foot vs lever), 0..60 deg")
    worst = 0
    for a in range(0, 61, 5):
        v = overlap(part("foot"), part("lever", 0, float(a))) + overlap(part("foot"), part("sear_pin", 0, float(a)))
        v += overlap(part("frame"), part("lever", 0, float(a)))
        worst = max(worst, v)
        if v > 1e-3:
            print(f"     contact at {a} deg: {v:.3f} mm^3")
            break
    check(worst < 1e-3 or a >= 45, f"lever swings freely to at least 45 deg (stopped at {a})")

    print("\n[6] 42 mm envelope (assembled, with bands)")
    env = part("all", zr, 0, view="assembled", extra=("show_envelope=false",))
    lo, hi = env.bounds
    print(f"     bounds x[{lo[0]:.2f},{hi[0]:.2f}] y[{lo[1]:.2f},{hi[1]:.2f}] z[{lo[2]:.2f},{hi[2]:.2f}]")
    check((hi - lo <= 42.0 + 1e-6).all(), f"fits a 42 mm cube: {np.round(hi - lo, 2)}")
    cocked = part("all", zl, 0, view="cocked", extra=("show_envelope=false",))
    lo, hi = cocked.bounds
    check((hi - lo <= 42.0 + 1e-6).all(), f"cocked toy fits too: {np.round(hi - lo, 2)}")

    print("\n[7] Masses (100 % infill, PLA)")
    mass = {}
    for n in STATIC + ["body", "lever", "sear_pin"]:
        m = part(n, zr if n == "body" else 0)
        g = m.volume/1000*PLA_DENSITY*SOLID_FILL
        c = m.center_mass
        mass[n] = {"volume_mm3": round(m.volume, 1), "mass_g": round(g, 3),
                   "cg": [round(x, 2) for x in c]}
        print(f"     {n:10s} {m.volume:8.0f} mm^3  {g:6.2f} g   CG u={c[0]:6.2f} v={c[1]:6.2f} z={c[2]:6.2f}")
    m_body = mass["body"]["mass_g"]
    m_rest = sum(v["mass_g"] for k, v in mass.items() if k != "body")
    print(f"     body (moving) {m_body:.2f} g, foot side {m_rest:.2f} g, ratio {m_body/(m_body+m_rest):.3f}")
    bc = mass["body"]["cg"]
    check(math.hypot(bc[0], bc[1]) < 0.35, f"body CG within 0.35 mm of the stem axis ({bc[0]}, {bc[1]})")
    json.dump({"params": P, "parts": mass, "release_angle_deg": rel,
               "max_cocking_angle_deg": worst_a},
              open(os.path.join(ROOT, "build", "mass.json"), "w"), indent=2)

    print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} FAILURE(S):"))
    for f in failures:
        print("   -", f)
    return 1 if failures else 0

def part_needed_at_latch(zl):
    body = part("body", round(zl, 3))
    return overlap(body, part("sear_pin", 0, 0.0)) + overlap(body, part("lever", 0, 0.0))

if __name__ == "__main__":
    sys.exit(main())
