# Design Principles

## 1. Core idea: do more with fewer actuators

A human hand has 20+ degrees of freedom. But does grasping really require that many motors? The answer is no. Grasping, at its core, is just "fingers wrapping around an object."

This design takes the **underactuation** route: **one servo drives three fingers and six joints.** The number of actuators (1) is far smaller than the number of degrees of freedom (6) — that is literally what "underactuated" means.

The trade-off is giving up independent control of each finger. In exchange you get three major benefits: **a drastically simpler structure, very low cost, and built-in self-adaptation.**

## 2. Transmission: how one rotation becomes three-finger motion

The motion chain flows like this:

```
Servo rotation → servo horn → main rotary disc → 3 linkage sets → 3 fingers open/close
```

The key part is the **rotary disc**. It is a centrally symmetric disc with three linkage sets attached at **120° spacing**. When the servo rotates the disc, all three linkages are pushed (or pulled) simultaneously and equally, so the three fingers close or open **synchronously and symmetrically.**

Because the three fingers are perfectly symmetric, the disc's rotation angle and the hand's openness have a **one-to-one single-valued relationship.** This reduces control to a **single-variable problem**:

```
small servo angle → hand open
large servo angle → hand closed
```

The software only needs to manage one number (the servo angle); no complex multi-axis coordination is required.

## 3. The essence of underactuation: passive adaptation

This is the cleverest part of the design and what sets it apart from an ordinary parallel gripper.

Each finger is internally a **four-bar linkage with two phalanges** (proximal + distal), giving it 2 degrees of freedom. During a grasp:

1. The servo begins closing; all three fingers curl inward together.
2. The **proximal phalanx** contacts the object first and is blocked from moving further.
3. But the servo **keeps outputting torque**, and the linkage forces the **distal phalanx** to keep curling.
4. Eventually the distal phalanx also lands on the object — the three fingers have **enveloped** it like a palm closing.

This entire process requires **no sensors and no knowledge of the object's shape or size.** It is driven entirely by the mechanism's own **passive compliance.** Whether the object is a cube, a sphere, or an irregular part, the three fingers automatically conform to its contour. That is why a single hand can handle so many object types.

## 4. Where the grip force comes from: servo holding torque

Once the object is grasped, it pushes back against the fingers. The force that maintains the grip is the servo's continuously applied **holding torque** — analogous to the constant tension in human hand muscles.

This also explains why **the hand cannot grasp anything if you rotate the disc by hand without a servo installed:** without a continuous torque source, the fingers are simply pushed open the moment the object resists.

## 5. Material strategy: rigid where it counts, soft where it touches

| Part | Material | Reason |
|---|---|---|
| Base, disc, linkages, phalanges | **PLA** | High stiffness, dimensional stability — preserves transmission accuracy |
| Fingertip pads | **TPU 95A** | Flexible deformation + high friction — increases grip, protects the object, compensates tolerances |

A hard skeleton transmits force precisely; soft fingertips contact gently — a simplified take on the biomimetic "hard bone + soft pad" idea.

## 6. Control strategy: sensing "grasped" without a force sensor

This servo has no force feedback, but it does have **position feedback.** The software exploits a clever substitute — **stall detection:**

- During a grasp, continuously read the servo angle.
- If the angle **stops changing across several sampling periods but has not yet reached the target position**, the finger has been blocked by the object → declare "grasped."
- Immediately write the current angle back to lock it — **maintaining grip force while preventing the servo from stalling continuously and overheating.**

By tuning three parameters — closing depth, speed, and detection sensitivity — the system emulates **soft / normal / firm** grip levels to handle objects ranging from a toy tomato to an aluminum can.

## One-sentence summary

> A single servo's rotation is split three ways by a rotary disc and linkages to close three fingers synchronously; passive compliance of the underactuated mechanism achieves self-adaptation to arbitrary shapes; servo holding torque provides grip force; and stall detection on position feedback substitutes for a force sensor — achieving general-purpose grasping at the lowest possible cost and complexity.

This "minimalist + adaptive" design philosophy is an important technical route in current dexterous-hand research.
