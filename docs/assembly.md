# Assembly & Wiring Guide

## Recommended assembly order

1. Mount the servo to the base center with M3 self-tapping screws.
2. Build one finger: hinge the distal and proximal phalanges with an M2 pin, then connect Linkage 1 and Linkage 2 into the four-bar.
3. Hinge the finger root (proximal phalanx end) to the corresponding tab on the base with an M2 pin.
4. Connect one end of Linkage 3 to the proximal phalanx; leave the other end free for now.
5. Repeat steps 2–4 for the other two fingers.
6. Fit the servo horn adapter onto the servo spline, then screw the rotary disc onto the adapter.
7. Hinge the free ends of the three Linkage-3s to the three symmetric tabs on the rotary disc.
8. Attach the 6 TPU pads to the inner faces of the phalanges (press-fit or glue).

> Use a washer at each hinge joint to reduce friction between PLA faces. Joints should rotate freely but without slop.

## Wiring (bus servo + USB-to-bus adapter)

Connect in this order, **with power off until the last step:**

1. Plug the servo into the adapter's **bus connector** (red = +, black = −, signal in the middle).
2. Connect the adapter's **USB** to the computer.
3. **Last:** connect power (e.g. 8.4 V adapter) to the adapter's power terminal (red = +, black = −).

> ⚠️ **Double-check power polarity before connecting.** A reversed supply can damage the adapter board. Verify with a multimeter that the red lead is truly positive.

## First power-on checks

- The adapter board LED should light up.
- **Windows:** Device Manager → Ports (COM & LPT) → look for `USB-SERIAL CH340 (COMx)` and note the COM number. If absent, install the CH340 driver.
- **Linux:** run `ls /dev/ttyUSB*`.

## Setting the servo ID

If your servo defaults to a different ID, use your servo vendor's GUI tool (or the `SETID` command in the host driver) to set the grasp servo's bus ID to **1** (or change `GRIPPER_SERVO_ID` in `src/single_gripper.py` to match).

## Calibration

Calibration captures the open/closed servo angles for *your specific build* (print tolerances and assembly vary). Run it once after assembly, and again before any important demo (temperature changes shift the limits slightly):

```bash
python src/single_gripper.py --port COM3 calib
```

- When prompted "fully open," push the three fingers to maximum spread by hand, press Enter.
- When prompted "fully closed," push the fingertips to just touching, press Enter.
- The reported "travel" should be roughly 40–80°. Far outside that range suggests a bad calibration.

Results are saved to `gripper_calib.json` and loaded automatically next time.

## Mechanical sanity test (before relying on the servo)

With power off, hold the base and rotate the disc by hand:

1. All three fingers should close **synchronously, symmetrically, and smoothly.**
2. No single finger should lag, stick, or rattle.
3. On release, friction should hold the fingers roughly in place.

If a finger sticks → re-ream that hinge hole with an M2 drill, deburr the print.
If fingers are out of sync → a linkage may be warped; replace it.
If the disc is very hard to turn → overall friction too high; re-ream all joints and add a little grease.
