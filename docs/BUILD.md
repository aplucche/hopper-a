# Build guide

## 1. Print (Bambu Lab A1 mini, PLA)

Open `stl/hopper_plate.3mf` in Bambu Studio. Every part is already laid out in its print orientation.

| setting | value | why |
|---|---|---|
| material | PLA | |
| layer height | 0.20 mm (0.16 mm if you want smoother pins) | |
| walls | 3 | |
| **infill** | **100 %** | The strength numbers assume it. The body/foot mass split (7.3 g / 7.1 g) is tuned for it too. |
| supports | **none** | Everything is designed to print without them. |
| brim | optional, 3 mm on the pins | |
| elephant-foot compensation | 0.1–0.15 mm | Keeps the slots and holes true. |

Print orientations, all already set in the files:

* **foot**: flat. The pivot holes are teardrops, so they bridge cleanly.
* **frame**: lying flat. This is essential, because the stem and crossbar work in tension along the filament.
* **body**: upside down. The pockets open upward and the band pegs have 45° roofs.
* **lever**: flat.
* **pins**: lying down. Two spares of each are included, since they are tiny and easy to lose.

## 2. You need

**7 × #8 rubber bands** (7/8" × 1/16"):

* 4 main bands
* 1 trigger return band
* 2 bumper bands

Fewer or more main bands also work; see the table in the README. For the main bands, **only #8 bands looped double have been modelled**.

## 3. Assemble (about 5 minutes)

1. **Lever**
   1. Drop the red pedal lever into the slot in the foot. The tall tooth goes toward the centre and the pad goes toward the cut-out corner.
   2. Push the round **pivot pin** in from the side, through the pivot block and the lever, until it is flush on both sides.
   3. Check that the lever swings freely. If it doesn't, ream the lever hole with a 3 mm drill bit by hand.
2. **Sear pin**: press the 2.8 mm square pin into the square hole at the top of the lever tooth. Centre it so it sticks out the same amount on each side.
3. **Return band ("bow-string")**
   1. Loop one #8 band doubled (twist it into an 8 and fold it) around the two mushroom pegs next to the pedal.
   2. Make sure it passes *under* the pedal arm, closest to the pivot.
   3. Check: the pedal should now spring back up by itself when pressed.
4. **Bumpers**: wrap one #8 band 2–3 turns around each of the two grooves on top of the crossbar. The rubber under the crossbar is what the body hits.
5. **Body onto the frame**
   1. Look into the bottom of the orange body and find the two small hanging **barbs**.
   2. Slide the body onto the stem from the stem's *bottom* end, with the barbs on the pedal side.
6. **Frame into the foot**
   1. Push the square tenon on the bottom of the stem into the square socket in the foot.
   2. Lift the body out of the way, then push the square **stem pin** through the tenon from the side *opposite* the pedal. It slides along the groove under the boss until it is flush.
   3. The pin is what stops the frame pulling out of the foot on every jump.
7. **Main bands**
   1. Twist each band into an 8 and fold it into a double loop.
   2. Hook it over one crossbar end.
   3. Stretch it down the body's side slot and hook it *under* the peg at the bottom of the slot.
   4. Put **the same number of bands on each side**. Uneven bands tip the body on the stem and waste energy.

## 4. Use

1. **Cock it**
   1. Stand the toy on a table.
   2. Straddle the crossbar with two fingers and push the body straight down until it **clicks**. This takes 50 N with 4 bands, a firm push.
   3. Let go slowly: the body rises 0.8 mm and seats on the latch.
2. **Fire it**
   1. Put it down, clear of your face.
   2. **Tap the corner pedal downward** with a fingertip or fingernail and take your finger straight off.
   3. The toy fires after about 3 mm of pedal travel.
3. **Safety**
   * Never cock it pointing at anyone's face, and keep eyes above the table plane.
   * Don't leave it cocked, and unhook the main bands for storage. The permanent pull makes PLA creep, especially somewhere warm like a car.
   * Replace bands as soon as they show cracks.
   * **Never exceed 6 main bands.**

## 5. Tuning (all Customizer parameters in `hopper.scad`)

| symptom | fix |
|---|---|
| pedal too stiff | raise `e_bias` by 0.2 mm (default 1.2) |
| fires by itself after cocking | lower `e_bias` by 0.2 mm, or raise `barb_tilt` |
| pins fall out / won't go in | `fit_pin` −0.05 / +0.05 |
| body binds on the stem | `fit_slide` +0.05 |
| lever stiff on its pivot | `fit_rot` +0.1 |

After changing parameters, run `tools/build_all.sh` to re-check the geometry and re-export the print files.

## 6. Calibrating the prediction to your bands

Rubber band stiffness varies about ±40 % between brands, and that is where most of the uncertainty in the jump height comes from. To calibrate:

1. Loop one band double over two pencils. Hang a known mass (for example a 500 g water bottle) from the lower pencil.
2. Measure the centre-to-centre gap between the pencils.
3. Run

   ```
   python3 -c "import sys; sys.path.insert(0,'tools'); from hopper_calc import calibrate_band; print(calibrate_band(MASS_G, GAP_MM))"
   ```

4. Put the resulting `G` (MPa) into `G_NOM` in `tools/hopper_calc.py`.
