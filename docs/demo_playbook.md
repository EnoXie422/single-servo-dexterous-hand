# Demo Playbook

A condensed two-person demo guide. One person (A) holds and aims the gripper;
the other (B) operates the keyboard.

## Before the demo 

1. **Mechanical check** — by hand, rotate the disc and confirm all three fingers move synchronously and smoothly.
2. **Wiring** — servo → adapter bus port → USB → computer → power LAST. Verify polarity.
3. **Port** — note the COM number (Device Manager / `ls /dev/ttyUSB*`).
4. **Smoke test** — `python src/single_gripper.py --port COM3 open` should open the hand.
5. **Calibrate** — `python src/single_gripper.py --port COM3 calib` (re-run on-site even if done before; temperature shifts the limits).
6. **Dry run** — `python src/teleop_gripper.py --port COM3` and try every object once. Drop anything that fails 3×.

## Object → mode cheat sheet

| Object | Example | Mode | Pre-close | Key to success |
|---|---|---|---|---|
| Ultra-fragile | thin-wall print, egg | ULTRA | `[7]`/`[8]` | stops on contact, no extra force |
| Soft / light | toy tomato, sponge | SOFT | `[5]` | slow approach, no crushing |
| Rigid (small) | 30 mm cube, dice | NORMAL | `[7]` | standard grasp |
| Rigid (large) | 80 mm cube, cylinder | NORMAL | `[3]` | pre-close to save travel |
| Irregular | gear, linkage, figurine | NORMAL | `[5]` | three-finger envelope |
| Spherical | printed ball, ping-pong | SOFT | `[5]` | spheres suit three fingers best |
| Slippery / heavy | can, bottle, metal | FIRM | `[3]` | extra squeeze for friction |

## Grasp sizes

- **5–8 cm:** `[O]` open → A wraps over → `[SPACE]`. ~8 s.
- **9–12 cm:** `[5]`/`[6]` pre-close → A approaches → `[SPACE]`. ~10 s.
- **13–15 cm:** `[O]` → `[3]` pre-close → A reaches around → `[SPACE]`. ~12 s.

## Person B's rhythm: open → tell → wait → press → lift → wait → place → release

1. **open** — `[O]`, tell A "ready, grabbing X"
2. **tell** — say what object and which mode
3. **wait** — for A to aim and say "ready"
4. **press** — `[SPACE]`, remind A "hold still"
5. **lift** — once "grasped" shows, A lifts to show the judges
6. **wait** — A moves to the target spot
7. **place** — A holds the gripper still
8. **release** — `[R]`

## Live adjustments

- Holding but loose → `[UP]` (+3°, repeatable)
- Object being crushed → `[DOWN]` (−3°)
- Keeps slipping → `[M]` to FIRM, regrasp
- Keeps crushing → `[M]` to SOFT/ULTRA
- Object < 5 cm → pre-close `[8]` first, else fingers may slide past it

## Troubleshooting

| Symptom | Likely cause | On-the-spot fix |
|---|---|---|
| Keeps closing, crushes object | stall_thresh too high / noisy servo | `[DOWN]` ×N → `[M]` softer → regrasp |
| Stops before touching (empty grasp) | stall_thresh too low, jitter misread | `[M]` to NORMAL/FIRM → regrasp |
| Object pushed away | uneven contact, A misaligned | `[O]` → A re-aims from above → regrasp |
| Fingers jammed | servo stall or mechanical interference | `[E]` → power off 3 s → inspect → restart |
| Servo buzzing | stalling, about to overheat | `[R]` release immediately, or pull power |
| No response at all | no power / wrong COM | check LED → Device Manager → fix `--port` |


