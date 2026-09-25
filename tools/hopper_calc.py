#!/usr/bin/env python3
"""Performance and strength calculator for the HOPPER-A toy.

Reads the live geometry from hopper.scad (view="info") and the part masses
written by tools/check_geometry.py (build/mass.json), then predicts, for
1..3 bands per side:

  * band stretch, latch force and stored energy
  * body launch speed, whole-toy take-off speed and jump height (with drag)
  * pedal (trigger) force and the minimum friction needed for the latch to hold
  * stresses and safety factors of every load-bearing PLA feature,
    including an estimate of the impact when the body hits the crossbar

Rubber model: incompressible neo-Hookean,  nominal stress = G (lam - 1/lam^2),
stored energy density W = G/2 (lam^2 + 2/lam - 3).  G for natural-rubber
office bands is typically 0.45-0.9 MPa; 0.65 MPa is used as nominal and the
low/high values bracket the prediction.  Calibrate with calibrate_band().

Usage:  python3 tools/hopper_calc.py [--md docs/PERFORMANCE.md]
"""
import json, math, os, sys, argparse
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_geometry import scad_params

G_ACC = 9.81
RHO_AIR = 1.20
INCH = 25.4

# ------------------------------------------------------------------ bands
# name: (flat length mm, width mm, thickness mm)   standard US sizes
BANDS = {
    "#8":  (7/8*INCH,   1/16*INCH, 1/32*INCH),
    "#10": (1.25*INCH,  1/16*INCH, 1/32*INCH),
    "#12": (1.75*INCH,  1/16*INCH, 1/32*INCH),
    "#16": (2.5*INCH,   1/16*INCH, 1/32*INCH),
    "#19": (3.5*INCH,   1/16*INCH, 1/32*INCH),
}
RUBBER_DENSITY = 0.95e-3        # g/mm^3
G_NOM, G_LO, G_HI = 0.65, 0.45, 0.90       # MPa
ETA_NOM, ETA_LO, ETA_HI = 0.80, 0.70, 0.88  # fraction of stored energy returned
GUIDE_LOSS = 0.95               # stem friction, bumper, band slap
CD, AREA = 1.05, 1.45e-3        # drag coefficient, mean frontal area m^2 (tumbling 41 mm toy)

# ------------------------------------------------------------------ PLA strength (100 % infill, conservative)
S_XY_TENS = 50.0     # MPa, along the filament (in-plane)
S_XY_SHEAR = 30.0
S_Z_TENS = 20.0      # MPa, across layers
S_Z_SHEAR = 15.0
S_BEAR = 50.0        # compressive bearing
PLA_RHO, PLA_C = 1240.0, 1700.0   # kg/m^3, bar wave speed m/s

def lam_stress(G, lam):
    return G*(lam - 1/lam**2)

def W(G, lam):
    return G/2*(lam**2 + 2/lam - 3)

def hull_perimeter(polys, t):
    """Length of a band of thickness t hugging the convex hull of polys (mid-line)."""
    return unary_union(polys).convex_hull.length + math.pi*t

def poly_Z(poly):
    """Elastic section modulus about the horizontal centroidal axis of a shapely polygon."""
    xs = poly.exterior.coords
    cy = poly.centroid.y
    Ix = 0.0
    for (x1, y1), (x2, y2) in zip(xs[:-1], xs[1:]):
        y1 -= cy; y2 -= cy
        a = x1*y2 - x2*y1
        Ix += a*(y1*y1 + y1*y2 + y2*y2)
    Ix = abs(Ix)/12
    miny, maxy = poly.bounds[1] - cy, poly.bounds[3] - cy
    return Ix/max(abs(miny), abs(maxy))

class Hopper:
    def __init__(self, P, mass, band="#8", wraps=2):
        self.P, self.mass = P, mass
        self.band, self.wraps = band, wraps
        Lf, w, t = BANDS[band]
        self.C0 = 2*Lf                    # relaxed circumference
        self.A = w*t                      # strand section mm^2
        self.t = t
        self.vol = self.C0*self.A         # rubber volume per band mm^3
        self.m_band = self.vol*RUBBER_DENSITY
        # anchor sections in the u-z plane
        P = self.P
        self.top = box(-P["stem_u"]/2, P["cb_end_z0"], P["stem_u"]/2, P["cb_end_z1"])
    def peg(self, zb):
        P = self.P
        return Polygon([(-P["bpeg_u"], zb + P["bpeg_z0"]), (P["bpeg_u"], zb + P["bpeg_z0"]),
                        (P["bpeg_u"], zb + P["bpeg_z1"]), (0, zb + P["bpeg_z1"] + P["bpeg_u"]),
                        (-P["bpeg_u"], zb + P["bpeg_z1"])])
    def lam(self, zb):
        L = hull_perimeter([self.top, self.peg(zb)], self.t)
        return L/(self.C0/self.wraps)
    def force_per_band(self, zb, G=G_NOM):
        return 2*self.wraps*self.A*lam_stress(G, self.lam(zb))
    def energy_per_band(self, G=G_NOM):
        P = self.P
        return self.vol*(W(G, self.lam(P["z_b_latch"])) - W(G, self.lam(P["z_b_rest"])))/1000  # J

    # --------------------------------------------------------- performance
    def masses(self, n_bands):
        m = {k: v["mass_g"] for k, v in self.mass["parts"].items()}
        m_body = m["body"]
        m_foot_side = sum(v for k, v in m.items() if k != "body")
        m_main = n_bands*self.m_band
        m_misc = 3*BANDS["#8"][0]*2*BANDS["#8"][1]*BANDS["#8"][2]*RUBBER_DENSITY  # bow-string + 2 bumpers
        return m_body, m_foot_side, m_main, m_misc

    def launch(self, n_bands, G=G_NOM, eta=ETA_NOM):
        P = self.P
        m_b, m_f, m_main, m_misc = self.masses(n_bands)
        s = P["stroke"]/1000
        E = n_bands*self.energy_per_band(G)*eta*GUIDE_LOSS - m_b/1000*G_ACC*s
        m_eff = (m_b + m_main/3)/1000       # bands move with a linear velocity profile
        v_b = math.sqrt(max(E, 0)*2/m_eff)
        p = (m_b + m_main/2)/1000*v_b
        M = (m_b + m_f + m_main + m_misc)/1000
        v0 = p/M
        h_vac = v0**2/(2*G_ACC)
        vt2 = 2*M*G_ACC/(RHO_AIR*CD*AREA)
        h = vt2/(2*G_ACC)*math.log(1 + v0**2/vt2)
        return dict(E=E, v_body=v_b, v0=v0, h=h, h_vac=h_vac, M=M*1000, m_b=m_b, m_f=m_f)

    # --------------------------------------------------------- latch
    def bowstring_torque(self, a_deg, G=G_NOM):
        """Torque (N mm) of the doubled #8 bow-string on the pedal lever at rotation a."""
        P = self.P
        Lf, w, t = BANDS["#8"]
        C = Lf  # doubled: each loop is half the circumference
        span = 2*P["peg_v"]
        L0 = 2*span + 2*math.pi*(P["peg_r"] + t/2)
        r = P["peg_u"] - P["peg_r"] - t - P["u_p"]        # inner strands, lever arm
        half = P["peg_v"] - P["peg_r"] - P["lw"]/2         # free span each side of the arm
        d = 0.4 + r*math.sin(math.radians(a_deg))          # deflection incl. preload
        stretch = 2*(math.hypot(half, d) - half)           # extra length of each inner strand
        lam = (L0 + stretch)/C                             # band slips round the pegs: shared
        T = w*t*lam_stress(G, lam)
        phi = math.atan2(d, half)
        F = 2*2*T*math.sin(phi)                            # 2 inner strands, both sides
        return F*r

    def trigger(self, n_bands, mu=0.30, G=G_NOM):
        P = self.P
        N = n_bands*self.force_per_band(P["z_b_latch"], G)
        h, e = P["h"], P["e_bias"]
        a = math.radians(P["barb_tilt"])
        L = (P["pad_u0"] + P["pad_u1"])/2 - P["u_p"]
        T_hold = self.bowstring_torque(0, G)
        T_rel = self.bowstring_torque(13, G)
        torque = N*(mu*h + h*math.sin(a) - e) + T_rel
        mu_min = (N*(e - h*math.sin(a)) - T_hold)/(N*h)
        return dict(N=N, pedal=torque/L, mu_min=mu_min, L=L, T_hold=T_hold, T_rel=T_rel)

    # --------------------------------------------------------- strength
    def stresses(self, n_bands, G=G_NOM):
        P = self.P
        N = n_bands*self.force_per_band(P["z_b_latch"], G)
        half = N/2
        out = []
        def add(name, sigma, strength, note):
            out.append((name, sigma, strength, strength/sigma if sigma > 0 else float("inf"), note))
        # sear pin: two cantilevers from the lever face to the prong centre
        arm = (P["prong_v0"] + P["prong_v1"])/2 - P["lw"]/2
        add("sear pin bending", half*arm/(P["lp"]**3/6), S_XY_TENS, "printed lying: along filament")
        # barb ledge: cantilever of (u_f - step_u), load at the edge
        ov = P["u_f"] - P["step_u"]
        bw = P["prong_v1"] - P["prong_v0"]
        add("barb ledge bending", half*ov/(bw*P["barb_h"]**2/6), S_XY_TENS, "stress in layer plane")
        add("prong tension", half/((P["step_u"] - P["prong_u0"])*bw), S_Z_TENS, "across layers")
        # pivot pin double shear, pivot block tear-out (across layers)
        add("pivot pin shear", N/(2*math.pi*P["pv_d"]**2/4), S_XY_SHEAR, "printed lying")
        wall = P["blk_v"] - P["slot_v"]
        roof = P["blk_top"] - P["z_p"] - P["pv_d"]/2*math.sqrt(2)
        add("pivot block tear-out", N/(4*wall*roof), S_Z_SHEAR, "teardrop roof, across layers")
        # crossbar end: cantilever from the mid section to the band centre
        arm = (P["cb_end_v"] - P["cb_mid_v"])/2
        hgt = P["cb_end_z1"] - P["cb_end_z0"]
        add("crossbar end bending", half*arm/(P["stem_u"]*hgt**2/6), S_XY_TENS, "frame printed flat")
        # body band peg: pentagon section, load at mid length
        peg = self.peg(0)
        arm = (P["bpeg_v1"] - P["slot_v0"])/2
        add("body peg bending", half*arm/poly_Z(peg), S_XY_TENS, "horizontal cantilever")
        # stem bending while latched: latch force acts ~u_f from the axis
        flange = P["stem_v"] - P["stem_win"]
        Z = 2*flange*P["stem_u"]**2/6
        add("stem bending (latched)", N*P["u_f"]/Z, S_XY_TENS, "frame printed flat")
        # stem shoulder bearing on the boss
        add("stem shoulder bearing", N/(2*(P["stem_v"] - P["ten_h"])*P["stem_u"]), S_BEAR, "")
        return N, out

    def impact(self, n_bands, G=G_NOM):
        """Rough peak loads when the body hits the crossbar."""
        L = self.launch(n_bands, G)
        m_b, m_f = L["m_b"]/1000, L["m_f"]/1000
        v_rel = L["v_body"]
        mu_r = m_b*m_f/(m_b + m_f)
        # bumper: two doubled #8 bands, 1.6 mm of rubber over ~38 mm^2
        k = 3.5*38/1.6*1000                      # N/m  (E_c ~ 3.5 MPa)
        x = v_rel*math.sqrt(mu_r/k)              # compression if it never bottoms out
        cap = 0.5*k*(1.1e-3)**2                  # energy the bumper can take (J)
        ke = 0.5*mu_r*v_rel**2
        # hard PLA-on-PLA part: stress wave  sigma = rho c v / 2  on the contact faces
        v_hard = math.sqrt(max(ke - cap, 0)*2/mu_r)
        sigma_wave = PLA_RHO*PLA_C*v_hard/2/1e6
        # force through the stem pin: foot parts below the pin get J = m v0 in >= 0.1 ms
        m_below = sum(self.mass["parts"][k]["mass_g"] for k in ["foot", "lever", "sear_pin", "pivot_pin", "stem_pin"])/1000
        F_pin = m_below*L["v0"]/1.0e-4
        P = self.P
        # the blow lands on the two bumper pads either side of the stem
        A_pad = (P["bump_v1"] - P["bump_v0"])*P["stem_u"]
        F_side = sigma_wave*A_pad
        # critical sections: where the top bumper groove starts, and the stem root (r=2 fillet)
        pad_c = (P["bump_v0"] + P["bump_v1"])/2
        h_grv = P["top_z"] - P["cb_mid_z0"] - P["bump_rec"]
        h_root = P["top_z"] - P["cb_mid_z0"] + 2.0
        sig_cb = max(F_side*(pad_c - P["bump_v0"])/(P["stem_u"]*h_grv**2/6),
                     F_side*(pad_c - P["stem_v"])/(P["stem_u"]*h_root**2/6))
        F_stem = m_f*L["v0"]/1.0e-4
        A_stem = 2*(P["stem_v"] - P["stem_win"])*P["stem_u"]
        return dict(v_rel=v_rel, ke=ke, bumper_cap=cap, v_hard=v_hard, sigma_wave=sigma_wave, F_pin=F_pin,
                    tau_pin=F_pin/(2*P["spin"]**2), F_stem=F_stem, sig_stem=F_stem/A_stem, sig_cb=sig_cb)

def calibrate_band(mass_g, gap_mm, pencil_d=7.0, band="#8", wraps=2):
    """Back out G (MPa) from a hanging test: one band looped `wraps` times over
    two pencils of diameter pencil_d, loaded with mass_g, pencils gap_mm apart
    (centre to centre)."""
    Lf, w, t = BANDS[band]
    lam = (2*gap_mm + math.pi*(pencil_d + t))/(2*Lf/wraps)
    F = mass_g/1000*G_ACC
    return F/(2*wraps*w*t*(lam - 1/lam**2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", help="write a markdown report here")
    args = ap.parse_args()
    P = scad_params()
    mass = json.load(open(os.path.join(ROOT, "build", "mass.json")))
    H = Hopper(P, mass)
    lines = []
    def out(s=""):
        print(s); lines.append(s)

    out("## Geometry")
    out(f"* stroke {P['stroke']:.1f} mm, body rest z = {P['z_b_rest']:.1f} mm, latched z = {P['z_b_latch']:.1f} mm")
    out(f"* main-band stretch (#8 doubled): rest lambda = {H.lam(P['z_b_rest']):.2f}, "
        f"latched lambda = {H.lam(P['z_b_latch']):.2f}")
    m_b, m_f, m_main, m_misc = H.masses(4)
    out(f"* masses at 100 % infill: body {m_b:.2f} g, foot side {m_f:.2f} g "
        f"(frame, foot, lever, pins), bands {n_band_mass(H):.2f} g each")
    out()
    out("## Predicted performance (#8 bands, each looped double)")
    out()
    out("| bands | per side | latch force | stored energy | body speed | take-off | jump height (nominal) | range (soft..stiff bands) | pedal force |")
    out("|---|---|---|---|---|---|---|---|---|")
    results = {}
    for n in (2, 4, 6):
        L = H.launch(n)
        lo = H.launch(n, G_LO, ETA_LO)
        hi = H.launch(n, G_HI, ETA_HI)
        T = H.trigger(n)
        results[n] = (L, lo, hi, T)
        out(f"| {n} | {n//2} | {T['N']:.1f} N | {n*H.energy_per_band():.3f} J | {L['v_body']:.1f} m/s | "
            f"{L['v0']:.2f} m/s | **{L['h']:.2f} m = {L['h']/0.3048:.1f} ft** | "
            f"{lo['h']/0.3048:.1f} - {hi['h']/0.3048:.1f} ft | {T['pedal']:.1f} N |")
    out()
    out(f"Assumptions: G = {G_NOM} MPa (range {G_LO}-{G_HI}), energy return {ETA_NOM:.0%} "
        f"(range {ETA_LO:.0%}-{ETA_HI:.0%}), {1-GUIDE_LOSS:.0%} guide/bumper loss, "
        f"air drag Cd {CD} on {AREA*1e6:.0f} mm^2. Height is the rise of the toy's centre of mass.")
    out()
    out("## Trigger")
    for n in (2, 4, 6):
        T = results[n][3]
        tr_lo, tr_hi = H.trigger(n, 0.2), H.trigger(n, 0.45)
        out(f"* {n} bands: pedal force {T['pedal']:.1f} N at mu=0.30 "
            f"({tr_lo['pedal']:.1f} N at mu=0.20, {tr_hi['pedal']:.1f} N at mu=0.45); "
            f"latch holds for any friction coefficient above {max(T['mu_min'], 0):.2f}")
    T = results[4][3]
    out(f"* bow-string return spring: {T['T_hold']:.1f} N mm holding torque at rest, "
        f"{T['T_rel']:.1f} N mm at the release angle; pedal lever arm {T['L']:.1f} mm")
    out()
    out("## Strength (100 % infill PLA, conservative strengths)")
    for n in (4, 6):
        N, rows = H.stresses(n)
        out()
        out(f"### {n} bands (latch load {N:.1f} N)")
        out()
        out("| feature | stress | strength | safety factor | note |")
        out("|---|---|---|---|---|")
        for name, s, st, sf, note in rows:
            out(f"| {name} | {s:.1f} MPa | {st:.0f} MPa | {sf:.1f} | {note} |")
    out()
    out("## Impact (body hitting the crossbar)")
    out()
    out("Rough, deliberately pessimistic: the blow is assumed to last only 0.1 ms and PLA's higher "
        "strength under short impacts is ignored.")
    out()
    out("| bands | impact speed | energy lost in the collision | taken by bumper bands | PLA contact stress | crossbar bending | stem tension | stem-pin shear | lowest SF |")
    out("|---|---|---|---|---|---|---|---|---|")
    for n in (2, 4, 6):
        I = H.impact(n)
        sf = min(S_BEAR/I['sigma_wave'], S_XY_TENS/I['sig_cb'], S_XY_TENS/I['sig_stem'], S_XY_SHEAR/I['tau_pin'])
        out(f"| {n} | {I['v_rel']:.1f} m/s | {I['ke']*1000:.0f} mJ | {min(I['bumper_cap'], I['ke'])*1000:.0f} mJ | "
            f"{I['sigma_wave']:.1f} MPa | {I['sig_cb']:.1f} MPa | {I['sig_stem']:.1f} MPa | {I['tau_pin']:.1f} MPa | {sf:.1f} |")
    out()
    out("## Resting preload (creep)")
    for n in (2, 4, 6):
        F = n*H.force_per_band(P["z_b_rest"])
        _, rows = H.stresses(n)
        peg = [r for r in rows if r[0] == "body peg bending"][0][1]*F/(n*H.force_per_band(P["z_b_latch"]))
        out(f"* {n} bands: {F:.1f} N permanently pulls the body onto the bumpers; worst resting stress "
            f"{peg:.1f} MPa (body pegs). PLA creeps noticeably above ~10 MPa when warm, so unhook the "
            f"bands for storage.")
    if args.md:
        with open(args.md, "w") as f:
            f.write("# HOPPER-A performance and strength report\n\n"
                    "_Generated by `tools/hopper_calc.py` from the current `hopper.scad` geometry. "
                    "Do not edit by hand._\n\n" + "\n".join(lines) + "\n")
        print("wrote", args.md)

def n_band_mass(H):
    return H.m_band

if __name__ == "__main__":
    main()
