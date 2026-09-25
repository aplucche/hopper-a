// =====================================================================
//  HOPPER-A  :  rubber-band jumping toy, 42 mm cube envelope
//  PLA + standard #8 rubber bands only.  Designed for Bambu Lab A1 mini.
//
//  How it works
//  ------------
//  * FOOT  : a base plate with a central boss and a pivot block.
//  * FRAME : a "T" (stem + crossbar) pinned into the foot. Printed lying
//            flat so every tensile load runs along the filament.
//  * BODY  : a heavy puck that slides on the stem.
//  * BANDS : loop over the crossbar ends and under pegs at the bottom of
//            the body, so pushing the body DOWN stretches them.
//  * LATCH : a pedal lever in the foot. Its sear pin hooks over two barbs
//            on the body. Push the body down -> it clicks. Tap the corner
//            pedal DOWN -> the pin slips off the barbs -> the body shoots up,
//            slams the crossbar and yanks the whole toy into the air.
//            The pedal is at the corner, outside the body's path, and the
//            lever keeps rotating freely after release, so a finger on
//            the pedal cannot hold the foot down.
//
//  Views (Customizer "view"):
//    assembled  - resting state (bands relaxed)          [default]
//    cocked     - body pulled down and latched
//    firing     - pedal pressed, sear released
//    exploded   - assembly exploded along Z
//    section    - cocked state cut on the lever mid-plane
//    animate    - use View > Animate (FPS 15, Steps 120)
//    print      - all parts laid out on the 180x180 A1-mini plate
//    part       - a single part (set "part") in print orientation
//
//  Units: mm. Mechanism frame: X = lever axis (u), Y = crossbar axis (v).
//  The assembled views are rotated -45 deg so the square foot is aligned
//  with the world axes and the 42 mm envelope cube.
// =====================================================================

/* [View] */
view = "assembled"; // [assembled, cocked, firing, exploded, section, animate, print, part, info]
part = "foot";      // [foot, body, frame, lever, stem_pin, pivot_pin, sear_pin]
show_bands = true;
show_envelope = true;
show_bed = true;
bands_per_side = 2; // [1, 2, 3]

/* [Fit tuning (mm)] */
fit_slide = 0.30;   // body bore clearance per side on the stem
fit_rot   = 0.40;   // diametral clearance of lever on pivot pin
fit_pin   = 0.15;   // diametral clearance for press-in pins (holes are +this)
fit_gap   = 0.40;   // general non-contact clearance

/* [Latch tuning] */
e_bias    = 1.2;    // pivot offset beyond barb edge; bigger = lighter trigger
barb_tilt = 3;      // deg; barb face rises toward the lever (adds hold)
overtravel = 0.8;   // how far past the latch point the body must be pushed

/* [Hidden] */
$fn = 48;
eps = 0.01;

// ---------------- envelope ----------------
env        = 42;
env_margin = 0.4;
top_z      = env - env_margin;          // 41.6 top of crossbar
foot_side  = env - 2*env_margin;        // 41.2 square foot
foot_cr    = 3;                         // foot corner radius

// ---------------- foot ----------------
t_plate  = 2.0;
boss_h   = 5.5;      // half size of central boss
boss_top = 8.0;
ten_h    = 3.0;      // tenon half size (u & v)
ten_z0   = 0.4;
spin     = 3.0;      // stem pin section (square)
spin_z0  = 2.4;
spin_u0  = -boss_h;  // pin runs from here...
spin_len = 10.8;     // ...for this long (+u end stops in the groove)

// ---------------- lever / pivot ----------------
pv_d       = 2.6;                         // pivot pin diameter
lev_boss_r = (pv_d + fit_rot)/2 + 1.3;
lev_min_z  = 0.4;
z_p        = lev_min_z + lev_boss_r;      // pivot height
blk_top    = z_p + (pv_d + fit_pin)/2*sqrt(2) + 0.9;  // teardrop apex + wall
blk_v      = 6.2;                         // pivot block half width
blk_u1     = 14.0;                        // pivot block end
slot_v     = 2.8;                         // lever slot half width
lw         = 5.0;                         // lever thickness
slot_u0    = 6.0;
slot_floor_z  = 0.6;                      // lever rest stop (tail sits here)
slot_floor_u1 = 9.5;

// ---------------- sear geometry ----------------
z_b_min   = t_plate;                      // body bottoms on the plate
z_b_latch = z_b_min + overtravel;
prong_u0  = boss_h + fit_gap;             // 5.9
prong_v0  = slot_v;                       // 2.8
prong_v1  = 6.0;
pr_bot_rel   = blk_top + 0.35 - z_b_min;  // prong bottom above body bottom
barb_h       = 2.4;
barb_top_rel = pr_bot_rel + barb_h;       // barb edge height (body frame)
u_f       = 9.6;                          // barb +u face
ov        = 1.5;                          // sear overlap
sear_clr  = 0.45;
step_u    = u_f - ov - sear_clr;          // prong face above the barb
z_c       = z_b_latch + barb_top_rel;     // contact height when latched
u_p       = u_f + e_bias;                 // pivot position
lp        = 2.8;                          // sear pin section (square)
lp_u0     = u_f - ov;                     // sear pin -u face
lp_len    = 2*(prong_v1 - 0.2);           // 11.6
head_wall = 0.8;
head_u0   = lp_u0 - head_wall;
head_u1   = lp_u0 + lp + head_wall;
head_top  = z_c + lp + head_wall;
tail_u0   = 7.0;
tooth_u1  = head_u1 + 0.1;

// bow-string return spring (one #8 band doubled round two pegs)
peg_u  = 18.6;
peg_v  = 6.6;
peg_r  = 1.5;
bs_h   = 1.6;                             // band width (stands on edge)
arm_z0 = t_plate + bs_h - 0.4;            // arm rests 0.4 into the band
arm_z1 = arm_z0 + 2.6;
arm_u1 = 21.6;
pad_u0 = 20.5;
pad_u1 = 27.4;
pad_z0 = 6.0;
pad_z1 = 9.0;
win_u0 = 15.4;  win_u1 = 22.0;  win_v = 4.7;   // window under the bow-string

// ---------------- frame (T) ----------------
stem_u  = 6;          // = print thickness of the frame
stem_v  = 5;          // half width of stem
cb_mid_z0 = top_z - 5;          // 36.6
cb_mid_v  = 10.2;
cb_end_z0 = 37.6;
cb_end_z1 = 40.6;               // bands on top stay below top_z
cb_end_v  = 16.6;
knob_w    = 0.7;
bump_v0 = 5.6;  bump_v1 = 9.4;  bump_rec = 1.0;   // bumper band grooves
bump_t  = 0.8;                                     // bumper rubber thickness

// ---------------- body ----------------
R_b     = 17.0;
d3      = 12.2;                               // deep sear pocket
H_b     = d3 + 1.6;                           // 13.8
z_b_rest = cb_mid_z0 - bump_t - H_b;          // body bottom at rest
stroke  = z_b_rest - z_b_latch;
slot_u  = 5.5;                                // band slot half width
slot_v0 = 10.0;                               // band slot floor
pk_v    = 6.6;                                // pocket half width
d1      = boss_top - t_plate + fit_gap;       // boss pocket depth
p3_u1   = 15.0;
d4      = arm_z1 + fit_gap - t_plate;         // arm channel depth
p4_u0   = 11.0;
p4_v    = slot_v + 0.2;
bpeg_z0 = 1.2;  bpeg_z1 = 3.0;  bpeg_u = 2.0;  // body band peg
bpeg_v1 = 16.0; bknob = 0.7;

// ---------------- sanity checks ----------------
assert(pr_bot_rel + z_b_min >= blk_top + 0.3, "prongs hit pivot block");
assert(head_top + fit_gap <= z_b_min + d3,     "lever head hits body pocket");
assert(stroke > 15, "stroke too short");
assert(R_b <= env/2 - env_margin, "body outside envelope");

// =====================================================================
//  helpers
// =====================================================================
module rsq(s, r) offset(r=r) offset(delta=-r) square(s, center=true);

module teardrop_y(d, len) {           // hole along Y, printable (tip up)
    rotate([90,0,0]) linear_extrude(len, center=true) {
        circle(d=d);
        rotate(45) square(d/2);
    }
}

module box(p0, p1) translate(p0) cube([p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]]);

// extrude a 2D (u,z) profile across v (centered)
module uz_extrude(w) rotate([90,0,0]) linear_extrude(w, center=true) children();

// =====================================================================
//  FOOT
// =====================================================================
module foot_2d() rotate(45) rsq(foot_side, foot_cr);

module bs_peg() {
    cylinder(r=peg_r, h=bs_h + 0.4 + eps);                           // shank
    translate([0,0,bs_h + 0.4]) cylinder(r1=peg_r, r2=peg_r+0.6, h=0.6);
    translate([0,0,bs_h + 1.0]) cylinder(r=peg_r+0.6, h=0.4);
}

module foot() {
    difference() {
        union() {
            difference() {
                union() {   // 0.4 mm step at the bottom edge = elephant-foot relief
                    translate([0,0,0.4]) linear_extrude(t_plate - 0.4) foot_2d();
                    linear_extrude(0.4 + eps) offset(delta=-0.4) foot_2d();
                }
                lightening();
            }
            box([-boss_h, -boss_h, 0], [boss_h, boss_h, boss_top]);
            box([0, -blk_v, 0], [blk_u1, blk_v, blk_top]);
            for (s=[-1,1]) translate([peg_u, s*peg_v, t_plate - eps]) bs_peg();
        }
        // tenon socket
        box([-ten_h - fit_pin/2, -ten_h - fit_pin/2, -1], [ten_h + fit_pin/2, ten_h + fit_pin/2, boss_top + 1]);
        translate([0,0,boss_top - 0.6]) linear_extrude(0.6 + eps, scale=1.25)
            square(2*ten_h + fit_pin, center=true);                 // lead-in
        // stem pin groove (open at the bottom and at -u)
        box([spin_u0 - 1, -(spin + fit_pin)/2, -1],
            [spin_u0 + spin_len + 0.1, (spin + fit_pin)/2, spin_z0 + spin + 0.1]);
        // lever slot: blind over the rest-stop floor, then through
        box([slot_u0, -slot_v, slot_floor_z], [40, slot_v, 20]);
        box([slot_floor_u1, -slot_v, -1], [40, slot_v, 20]);
        // window under the bow-string
        box([win_u0, -win_v, -1], [win_u1, win_v, 10]);
        // pivot pin holes
        translate([u_p, 0, z_p]) teardrop_y(pv_d + fit_pin, 2*blk_v + 2);
    }
}

// weight-saving / CG-balancing windows in the plate (outside the body's
// landing ring and away from all features)
module lightening() {
    // four windows on the world diagonals of the plate (= u/v corners)
    for (a=[90, 180, 270]) rotate(a)
        translate([0,0,-1]) linear_extrude(t_plate + 2)
            hull() { translate([21.5, 0]) circle(r=3.2); translate([24.5, 0]) circle(r=1.8); }
    // windows under the body's band slots (bands hang below the pegs)
    for (s=[-1,1]) box([-3.5, s>0 ? 10.8 : -15.6, -1], [3.5, s>0 ? 15.6 : -10.8, t_plate + 1]);
}

// =====================================================================
//  LEVER (pedal + sear), mechanism frame, rest angle
// =====================================================================
module lever_2d() {
    difference() {
        union() {
            translate([u_p, z_p]) circle(r=lev_boss_r);
            // tail + tooth + head, top -u corner chamfered
            polygon([[tail_u0, slot_floor_z], [tooth_u1, slot_floor_z],
                     [tooth_u1, head_top], [head_u0 + 1.6, head_top],
                     [tail_u0, head_top - 1.6 - (head_u0 - tail_u0)]]);
            // arm
            translate([u_p, arm_z0]) square([arm_u1 - u_p, arm_z1 - arm_z0]);
            // ramp + pad
            polygon([[arm_u1 - 0.01, arm_z0], [arm_u1 + 1.6, pad_z0], [pad_u1, pad_z0],
                     [pad_u1, pad_z1 - 0.8], [pad_u1 - 0.8, pad_z1], [pad_u0, pad_z1],
                     [pad_u0 - 3.2, arm_z1]]);
        }
        translate([u_p, z_p]) circle(d=pv_d + fit_rot);
        translate([lp_u0 - fit_pin/2, z_c - fit_pin/2]) square(lp + fit_pin);
        // finger grip grooves on the pad
        for (i=[0:2]) translate([pad_u0 + 1.4 + i*2.0, pad_z1]) circle(r=0.45, $fn=12);
    }
}
module lever() uz_extrude(lw) lever_2d();

module pivot_rot(a) translate([u_p, 0, z_p]) rotate([0, a, 0]) translate([-u_p, 0, -z_p]) children();

// =====================================================================
//  PINS
// =====================================================================
module chamfer_bar(l, a, c=0.4) {       // bar along X, section a x a
    hull() {
        translate([c, 0, 0]) cube([l - 2*c, a, a]);
        translate([0, c, c]) cube([l, a - 2*c, a - 2*c]);
    }
}
module stem_pin()  chamfer_bar(spin_len, spin);
module sear_pin()  chamfer_bar(lp_len, lp, 0.3);
module pivot_pin() {                    // D-profile, flat side down for printing
    l = 2*blk_v;
    intersection() {
        rotate([0,90,0]) translate([-pv_d/2, 0, 0]) cylinder(d=pv_d, h=l, $fn=32);
        translate([0, -pv_d, 0.25]) cube([l, 2*pv_d, pv_d]);
    }
}
module stem_pin_assembled()  translate([spin_u0, -spin/2, spin_z0]) stem_pin();
module sear_pin_assembled()  translate([0, lp_len/2, 0]) rotate([0,0,-90]) sear_pin();
module pivot_pin_assembled() translate([u_p, blk_v, z_p]) rotate([0,0,-90]) translate([0,0,-pv_d/2]) pivot_pin();

// =====================================================================
//  FRAME (stem + crossbar)
// =====================================================================
module frame_2d() {
    // tenon (chamfered tip)
    polygon([[-ten_h + 0.5, ten_z0], [ten_h - 0.5, ten_z0], [ten_h, ten_z0 + 0.5],
              [ten_h, boss_top + 1], [-ten_h, boss_top + 1], [-ten_h, ten_z0 + 0.5]]);
    // stem with fillets into the crossbar
    offset(r=-2) offset(delta=2) union() {
        translate([-stem_v, boss_top]) square([2*stem_v, cb_mid_z0 - boss_top + 1]);
        translate([-cb_mid_v, cb_mid_z0]) square([2*cb_mid_v, top_z - cb_mid_z0]);
    }
    for (m=[0,1]) mirror([m,0]) {
        translate([cb_mid_v - 0.5, cb_end_z0]) square([cb_end_v - cb_mid_v + 0.5, cb_end_z1 - cb_end_z0]);
        translate([cb_end_v, cb_mid_z0 + 0.4]) offset(r=0.3) offset(delta=-0.3)
            square([knob_w, top_z - cb_mid_z0 - 0.4]);
    }
}
module frame() {
    difference() {
        rotate([90,0,90]) linear_extrude(stem_u, center=true) difference() {
            frame_2d();
            for (m=[0,1]) mirror([m,0]) translate([bump_v0, top_z - bump_rec]) square([bump_v1 - bump_v0, 2]);
        }
        // stem pin hole (vertical when printed)
        box([-stem_u, -(spin + fit_pin)/2, spin_z0 - fit_pin/2], [stem_u, (spin + fit_pin)/2, spin_z0 + spin + fit_pin/2]);
    }
}

// =====================================================================
//  BODY (local frame: bottom at z = 0)
// =====================================================================
module prong() {      // +v prong; the barb is the lower, thicker part
    t = tan(barb_tilt);
    translate([0, prong_v0, 0]) rotate([90,0,0]) mirror([0,0,1]) linear_extrude(prong_v1 - prong_v0)
        polygon([[prong_u0, pr_bot_rel], [u_f - 1.0, pr_bot_rel], [u_f, pr_bot_rel + 1.0],
                 [u_f, barb_top_rel], [step_u, barb_top_rel - (u_f - step_u)*t],
                 [step_u, d3 + eps], [prong_u0, d3 + eps]]);
}

module body_peg() {   // +v band peg in the slot; bands loop UNDER it
    translate([0, slot_v0 - eps, 0]) rotate([-90,0,0]) linear_extrude(bpeg_v1 - slot_v0 + eps)
        polygon([[-bpeg_u, -bpeg_z0], [bpeg_u, -bpeg_z0], [bpeg_u, -bpeg_z1],
                 [0, -bpeg_z1 - bpeg_u], [-bpeg_u, -bpeg_z1]]);
    // retaining knob at the outer end
    translate([0, bpeg_v1, 0]) rotate([-90,0,0]) linear_extrude(bknob)
        polygon([[-bpeg_u, -0.3], [bpeg_u, -0.3], [bpeg_u, -bpeg_z1],
                 [0, -bpeg_z1 - bpeg_u], [-bpeg_u, -bpeg_z1]]);
}

module body() {
    difference() {
        union() {
            difference() {
                // puck with small edge chamfers
                hull() {
                    translate([0,0,0.5]) cylinder(r=R_b, h=H_b - 1, $fn=96);
                    cylinder(r=R_b - 0.5, h=H_b, $fn=96);
                }
                // bore
                box([-(stem_u/2 + fit_slide), -(stem_v + fit_slide), -1],
                    [ stem_u/2 + fit_slide,    stem_v + fit_slide,  H_b + 1]);
                // band slots
                for (m=[0,1]) mirror([0,m,0]) box([-slot_u, slot_v0, -1], [slot_u, R_b + 1, H_b + 1]);
                // boss pocket, sear pocket, arm channel
                box([-prong_u0, -pk_v, -1], [prong_u0, pk_v, d1]);
                // mirrored on the -u side so the body's CG stays on the stem axis
                for (m=[0,1]) mirror([m,0,0]) {
                    box([prong_u0 - eps, -pk_v, -1], [p3_u1, pk_v, d3]);
                    box([p4_u0, -p4_v, -1], [R_b + 1, p4_v, d4]);
                    // relief over the bow-string band (it passes under the body rim)
                    box([p3_u1 - eps, -pk_v - 1, -1], [R_b + 1, pk_v + 1, bs_h + fit_gap + 0.4]);
                }
                // bore chamfers
                for (z=[0, H_b]) translate([0,0,z]) scale([1, 1, z==0 ? 1 : -1])
                    translate([0,0,-eps]) linear_extrude(0.8, scale=0.8)
                        square([stem_u + 2*fit_slide + 1.6, 2*stem_v + 2*fit_slide + 1.6], center=true);
            }
            for (m=[0,1]) mirror([0,m,0]) { prong(); body_peg(); }
        }
    }
}

// =====================================================================
//  RUBBER BANDS (visual only)
// =====================================================================
band_w = 1.6; band_t = 0.8;
module band_loop_uz(v) translate([0, v, 0]) uz_extrude(band_w) difference() {
    offset(r=band_t) hull() children();
    hull() children();
}
module main_bands(zb) {
    for (m=[0,1]) mirror([0,m,0]) for (i=[0:bands_per_side-1]) for (k=[0,1]) {
        v = slot_v0 + 0.9 + (2*i + k)*(band_w + 0.05) + 0.2;
        color(i==0 ? "SaddleBrown" : "Sienna") band_loop_uz(v) {
            translate([-stem_u/2, cb_end_z0]) square([stem_u, cb_end_z1 - cb_end_z0]);
            translate([-bpeg_u, zb + bpeg_z0]) square([2*bpeg_u, bpeg_z1 - bpeg_z0]);
        }
    }
}
module bumper_bands() for (m=[0,1]) mirror([0,m,0]) for (k=[0,1])
    color("DimGray") band_loop_uz(bump_v0 + 0.25 + band_w/2 + k*(band_w + 0.1))
        translate([-stem_u/2, cb_mid_z0]) square([stem_u, top_z - bump_rec - cb_mid_z0]);
module bowstring(a=0) color("Peru") translate([0,0,t_plate]) linear_extrude(bs_h) difference() {
    offset(r=2*band_t) hull() for (s=[-1,1]) translate([peg_u, s*peg_v]) circle(r=peg_r);
    hull() for (s=[-1,1]) translate([peg_u, s*peg_v]) circle(r=peg_r);
}

// =====================================================================
//  ASSEMBLY
// =====================================================================
theta_release = 16;   // deg of pedal rotation where the sear lets go

module assembly(zb, a=0, explode=0, cut=false) {
    C(cut, "SteelBlue") foot();
    C(cut, "Silver") pivot_pin_assembled();
    C(cut, "Silver") translate([0,0,-explode*0.3]) stem_pin_assembled();
    C(cut, "Gold") translate([0,0,explode*1.6]) frame();
    C(cut, "DarkOrange") translate([0,0,zb + explode*0.8]) body();
    translate([0,0,explode*0.2]) pivot_rot(a) {
        C(cut, "Crimson") lever();
        C(cut, "Silver") translate([lp_u0, 0, z_c]) sear_pin_assembled();
    }
    if (show_bands && explode == 0) {
        C(cut, "SaddleBrown") main_bands(zb);
        C(cut, "DimGray") bumper_bands();
        C(cut, "Peru") bowstring();
    }
}
// colour a part and optionally cut it on the lever mid-plane (v = 0)
module C(cut, c) color(c) if (cut) intersection() {
    children();
    translate([-50, 0, -10]) cube([100, 50, 80]);
} else children();

module world() rotate([0,0,-45]) children();

module envelope() if (show_envelope)
    %translate([-env/2, -env/2, 0]) cube(env);


// =====================================================================
//  PRINT LAYOUT  (A1 mini: 180 x 180 mm)
// =====================================================================
module part_print(p) {
    if (p == "foot")      rotate(45) foot();
    if (p == "body")      translate([0,0,H_b]) rotate([180,0,0]) body();
    if (p == "frame")     translate([0, -(top_z + ten_z0)/2, 0]) linear_extrude(stem_u) frame_print_2d();
    if (p == "lever")     translate([-(tail_u0 + pad_u1)/2, -(slot_floor_z + pad_z1)/2, 0]) linear_extrude(lw) lever_2d();
    if (p == "stem_pin")  stem_pin();
    if (p == "sear_pin")  sear_pin();
    if (p == "pivot_pin") translate([0,0,-0.25]) pivot_pin();
}
// frame profile with the pin hole, for printing flat
module frame_print_2d() difference() {
    frame_2d();
    for (m=[0,1]) mirror([m,0]) translate([bump_v0, top_z - bump_rec]) square([bump_v1 - bump_v0, 2]);
    translate([-(spin + fit_pin)/2, spin_z0 - fit_pin/2]) square(spin + fit_pin);
}

module print_plate() {
    if (show_bed) %translate([0,0,-0.6]) linear_extrude(0.5) difference() {
        square(180, center=true); square(178, center=true);
    }
    translate([-38, 30, 0]) color("SteelBlue") part_print("foot");
    translate([ 28, 30, 0]) color("DarkOrange") part_print("body");
    translate([-38,-35, 0]) rotate(90) color("Gold") part_print("frame");
    translate([ 25,-22, 0]) color("Crimson") part_print("lever");
    // pins (+1 spare each, they are tiny)
    for (i=[0,1]) {
        translate([  8 + i*6, -48, 0]) rotate(90) color("Silver") part_print("stem_pin");
        translate([ 22 + i*6, -48, 0]) rotate(90) color("Silver") part_print("sear_pin");
        translate([ 36 + i*6, -48, 0]) rotate(90) color("Silver") part_print("pivot_pin");
    }
}

// =====================================================================
//  ANIMATION: 0-.30 push down | .30-.40 latched | .40-.45 pedal |
//             .45-.50 body fires | .50-1 whole toy jumps and lands
// =====================================================================
function lerp(a, b, t) = a + (b - a)*max(0, min(1, t));
module animate_view() {
    t = $t;
    zb = t < 0.30 ? lerp(z_b_rest, z_b_min, t/0.30)
       : t < 0.33 ? lerp(z_b_min, z_b_latch, (t - 0.30)/0.03)
       : t < 0.45 ? z_b_latch
       : t < 0.50 ? lerp(z_b_latch, z_b_rest, (t - 0.45)/0.05)
       : z_b_rest;
    a  = (t > 0.40 && t < 0.52) ? lerp(0, theta_release + 4, (t - 0.40)/0.05) : 0;
    s  = (t - 0.50)/0.50;                         // flight: parabola, 5x scaled down
    hz = t > 0.50 ? 240*s*(1 - s) : 0;
    world() translate([0,0,hz]) assembly(zb, a);
    envelope();
}

// =====================================================================
//  DISPATCH
// =====================================================================
if (view == "assembled") { world() assembly(z_b_rest);  envelope(); }
if (view == "cocked")    { world() assembly(z_b_latch); envelope(); }
if (view == "firing")    { world() assembly(z_b_latch + 0.5, theta_release); envelope(); }
if (view == "exploded")  world() assembly(z_b_rest, 0, 25);
if (view == "section")   world() assembly(z_b_latch, 0, 0, true);
if (view == "animate")   animate_view();
if (view == "print")     print_plate();
if (view == "part")      part_print(part);
// single part in the mechanism frame (used by tools/check_geometry.py)
mech_part = "foot"; mech_zb = 0; mech_a = 0;
if (view == "mech") {
    if (mech_part == "foot")      foot();
    if (mech_part == "body")      translate([0,0,mech_zb]) body();
    if (mech_part == "frame")     frame();
    if (mech_part == "lever")     pivot_rot(mech_a) lever();
    if (mech_part == "sear_pin")  pivot_rot(mech_a) translate([lp_u0, 0, z_c]) sear_pin_assembled();
    if (mech_part == "stem_pin")  stem_pin_assembled();
    if (mech_part == "pivot_pin") pivot_pin_assembled();
}
if (view == "info") {
    echo(str("HOPPER ", "stroke=", stroke, " z_b_rest=", z_b_rest, " z_b_latch=", z_b_latch,
             " H_b=", H_b, " z_c=", z_c, " u_p=", u_p, " z_p=", z_p, " h=", z_c - z_p,
             " blk_top=", blk_top, " head_top=", head_top));
    cube(1);
}
