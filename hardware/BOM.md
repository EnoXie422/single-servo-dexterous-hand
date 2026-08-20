# Bill of Materials & Print Settings

## 3D-printed parts (one complete hand)

| # | Part | Qty | Material | Function |
|---|---|---|---|---|
| 1 | Base | 1 | PLA | Main frame; mounts the servo and anchors all finger roots |
| 2 | Rotary disc | 1 | PLA | Central driving disc; splits servo rotation to the three fingers |
| 3 | Servo horn adapter | 1 | PLA | Couples the servo spline to the rotary disc |
| 4 | Linkage 1 | 3 | PLA | One per finger — part of the parallel four-bar linkage |
| 5 | Linkage 2 | 3 | PLA | One per finger — pairs with Linkage 1 for adaptive bending |
| 6 | Linkage 3 | 3 | PLA | One per finger — disc-to-finger drive link |
| 7 | Linkage 4 | 3 | PLA | One per finger — constrains distal motion |
| 8 | Linkage 5 | 3 | PLA | One per finger — completes the multi-bar kinematics |
| 9 | Distal phalanx (fingertip) | 3 | PLA | Tip segment; directly contacts the object |
| 10 | Proximal phalanx | 3 | PLA | Root segment; carries the main grip force |
| 11 | Anti-impact pad | 6 | TPU | Two per finger; soft contact surface for grip + protection |

**Total: 28 printed parts across 11 unique designs.**

## Non-printed (purchased) parts

| Type | Spec | Qty (est.) | Use |
|---|---|---|---|
| Drive servo | Bus servo, ≥15–20 kg·cm, metal gears | 1 | The single power source, mounted at the base center |
| Hinge pins / screws | M2 × 12 / 16 / 20 socket head | ~24 | Linkage hinge joints |
| Lock nuts | M2 nylon-insert | ~24 | Pair with hinge pins — rotatable but won't loosen |
| Washers | M2 stainless, Ø5 × 0.5 | ~50 | Reduce friction between linkages |
| Servo screws | M3 self-tapping × 8 mm | 4 | Servo body to base |

> Exact screw/washer counts should be confirmed against the SolidWorks mates in your assembly. The above are typical estimates.

## Recommended print settings

### PLA structural parts
| Setting | Value |
|---|---|
| Layer height | 0.15–0.20 mm |
| Wall thickness / count | 1.2 mm / 3 perimeters |
| Infill | 30–40% (50% for small linkages) |
| Infill pattern | Grid / Cubic |
| Print speed | 50–60 mm/s |
| Nozzle temp | 200–215 °C |
| Bed temp | 60 °C |
| Supports | Only near overhanging hinge bosses (>45°) |
| Brim | 5 mm |

### TPU 95A fingertip pads
| Setting | Value |
|---|---|
| Layer height | 0.20 mm |
| Wall count | 2 perimeters |
| Infill | 20% (Gyroid) |
| Print speed | 20–30 mm/s |
| Nozzle temp | 220–235 °C |
| Bed temp | 40–50 °C |
| Retraction | Short (1–2 mm) or disabled |
| Brim | 8 mm (anti-warp) |

## Print orientation tips

- **Base:** flat, bottom face down — minimizes supports and keeps the servo mounting face flat.
- **Phalanges:** on their side, so hinge-hole axes are parallel to the bed — avoids inter-layer shear cracking.
- **Linkages:** lay flat. Avoid orienting hinge-hole axes perpendicular to the print direction (weakest layer bond).
- **Rotary disc:** flat, face up.
- **Pads:** contact surface down, for a smooth gripping face.

## Estimated print time (single hand, serial printing)

| Part group | Per part | Count | Subtotal |
|---|---|---|---|
| Base | ~5 h | 1 | 5 h |
| Rotary disc | ~0.5 h | 1 | 0.5 h |
| Horn adapter | ~0.3 h | 1 | 0.3 h |
| Linkages 1–5 | ~0.4 h | 15 | 6 h |
| Phalanges | ~1.2 h | 6 | 7.2 h |
| TPU pads | ~0.3 h | 6 | 1.8 h |
| **Total** | | **28** | **~20.8 h** |
