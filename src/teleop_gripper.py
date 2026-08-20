"""
teleop_gripper.py
=================
Keyboard teleoperation for the single-servo three-finger hand.
Designed for a two-person demo: person A holds/aims the gripper, person B presses keys.

Four grip modes, switchable live with [M]:
  ULTRA   ultra-fragile: thin-wall prints (<1mm), eggs
  SOFT    soft/light:    toy tomato, sponge ball, thin-wall prints (2-3mm)
  NORMAL  rigid objects: printed cubes/cylinders/gears/blocks (default)
  FIRM    slippery/heavy: cans, bottles, metal parts

Run:
  python teleop_gripper.py --port COM3
"""

import sys
import time
import argparse
import numpy as np

from servo_host import ServoHost
from single_gripper import SingleServoGripper, SOFT_MIN, SOFT_MAX


# ============================================================
#  Cross-platform single-key reader
# ============================================================
try:
    import msvcrt   # Windows
    def get_key():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):
            ch2 = msvcrt.getch()
            return {b'H': 'UP', b'P': 'DOWN', b'K': 'LEFT', b'M': 'RIGHT'}.get(ch2, '?')
        try:
            c = ch.decode('utf-8').lower()
        except UnicodeDecodeError:
            return '?'
        if c == ' ': return 'SPACE'
        if c == '\r': return 'ENTER'
        if c == '\x1b': return 'ESC'
        return c
except ImportError:
    import termios, tty   # Linux / macOS
    def get_key():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    return {'A': 'UP', 'B': 'DOWN', 'C': 'RIGHT', 'D': 'LEFT'}.get(ch3, '?')
                return 'ESC'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        if ch == ' ': return 'SPACE'
        if ch in ('\r', '\n'): return 'ENTER'
        return ch.lower()


# ============================================================
#  Grip mode profiles
# ============================================================
GRASP_PROFILES = {
    'ULTRA':  dict(max_close_ratio=0.85, duration=4.0, stall_thresh=0.4, stall_count=2),
    'SOFT':   dict(max_close_ratio=0.90, duration=3.5, stall_thresh=0.6, stall_count=2),
    'NORMAL': dict(max_close_ratio=0.95, duration=2.5, stall_thresh=1.0, stall_count=3),
    'FIRM':   dict(max_close_ratio=1.00, duration=1.5, stall_thresh=1.5, stall_count=3),
}
PROFILE_DESC = {
    'ULTRA':  'ultra-gentle (thin-wall prints / eggs)',
    'SOFT':   'soft (toy tomato / sponge ball)',
    'NORMAL': 'normal (rigid printed parts / blocks)',
    'FIRM':   'firm (slippery / heavy objects like cans)',
}
PROFILE_ORDER = ['SOFT', 'NORMAL', 'FIRM', 'ULTRA']   # [M] cycle order


BANNER = r"""
==================================================================
  Single-Servo Three-Finger Hand - Teleoperation (v2.0)
  Objects: 5-15 cm, 4 selectable grip modes
==================================================================
"""

HELP = """
+---------------------- KEY MAP ----------------------+
|  [SPACE]   grasp (uses CURRENT mode, main action)   |
|  [M]       cycle grip mode (SOFT->NORMAL->FIRM->ULTRA)|
|  [O]       open fully                               |
|  [R]       release                                  |
|  [1-9]     pre-close to 10%-90%                      |
|  [UP][DN]  fine-tune +/- 3 deg (after grasping)     |
|  [I]       show current status                      |
|  [H]       show this help                           |
|  [E]       emergency stop (lock current position)   |
|  [Q]       quit                                     |
+-----------------------------------------------------+
"""


def progress_bar(ratio, width=24):
    n = int(round(ratio * width))
    return "[" + "#" * n + "-" * (width - n) + "]"


def show_status(g, profile, holding, msg=""):
    try:
        cur = g._read_pos()
    except Exception as e:
        print(f"  ! servo read failed: {e}")
        return
    rng = g.closed_deg - g.open_deg
    ratio = (cur - g.open_deg) / rng if abs(rng) > 1e-3 else 0
    ratio = max(0.0, min(1.0, ratio))
    state = "OPEN" if ratio < 0.1 else ("CLOSED" if ratio > 0.9 else "MID")
    hold = "[HOLDING]" if holding else "[empty]"
    print(f"  servo {cur:6.1f}deg  {progress_bar(ratio)} {ratio*100:5.1f}%  {state} {hold}")
    print(f"  mode: [{profile}]  {PROFILE_DESC[profile]}")
    if msg:
        print(f"  >>> {msg}")


def teleop_loop(g):
    print(BANNER)
    print(HELP)

    current_profile = 'NORMAL'
    holding_object  = False

    show_status(g, current_profile, holding_object, "ready")
    print("\n-> auto-opening...")
    g.open_hand()
    show_status(g, current_profile, holding_object, "opened - A can aim at the target now")

    while True:
        print("\nkey > ", end='', flush=True)
        key = get_key()
        print(key)

        if key in ('q', 'ESC'):
            print("\n-> releasing before exit...")
            g.release()
            print("bye!")
            return
        elif key == 'h':
            print(HELP)
        elif key == 'i':
            show_status(g, current_profile, holding_object)
        elif key == 'm':
            idx = PROFILE_ORDER.index(current_profile)
            current_profile = PROFILE_ORDER[(idx + 1) % len(PROFILE_ORDER)]
            print(f"-> mode: [{current_profile}] {PROFILE_DESC[current_profile]}")
        elif key == 'o':
            print("-> open"); g.open_hand(); holding_object = False
            show_status(g, current_profile, holding_object, "opened")
        elif key == 'r':
            print("-> release"); g.release(); holding_object = False
            show_status(g, current_profile, holding_object, "released")
        elif key in ('SPACE', 'ENTER'):
            if holding_object:
                print("  (already holding - press [R] to release first)")
                continue
            params = GRASP_PROFILES[current_profile]
            print(f"-> grasp [{current_profile}]  (keep the gripper STILL!)")
            result = g.grasp(**params)
            if result['grasped']:
                holding_object = True
                show_status(g, current_profile, holding_object,
                            f"grasped! locked at {result['final']:.1f}deg")
                print("   A can lift/move the object now; press [R] when done")
            else:
                show_status(g, current_profile, holding_object, "no object, closed fully")
        elif key in '123456789':
            ratio = int(key) / 10.0
            print(f"-> pre-close to {int(ratio*100)}%")
            g.set_grip(ratio, duration=0.8); holding_object = False
            show_status(g, current_profile, holding_object,
                        f"pre-closed {int(ratio*100)}% (press [SPACE] for final contact)")
        elif key == 'UP':
            cur = g._read_pos(); new = cur + 3.0
            print(f"-> tighten +3 ({cur:.1f}->{new:.1f})")
            g._send(new, duration=0.3); time.sleep(0.35)
            show_status(g, current_profile, holding_object, "tightened")
        elif key == 'DOWN':
            cur = g._read_pos(); new = cur - 3.0
            print(f"-> loosen -3 ({cur:.1f}->{new:.1f})")
            g._send(new, duration=0.3); time.sleep(0.35)
            show_status(g, current_profile, holding_object, "loosened")
        elif key == 'e':
            cur = g._read_pos()
            print(f"!! E-STOP, locking at {cur:.1f}deg")
            g._send(cur, duration=0.05)
            show_status(g, current_profile, holding_object, "locked")
        else:
            print(f"  unknown key {key!r}, press [H] for help")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM3")
    parser.add_argument("--skip-calib-check", action="store_true")
    args = parser.parse_args()

    print(f"Connecting to {args.port} ...")
    host = ServoHost(port=args.port)
    g = SingleServoGripper(host)

    if not args.skip_calib_check:
        from single_gripper import CALIB_FILE
        if not CALIB_FILE.exists():
            print("\n! Not calibrated. Calibrate now? (y/n): ", end='')
            if input().strip().lower() == 'y':
                g.calibrate()

    try:
        teleop_loop(g)
    except KeyboardInterrupt:
        print("\n\n! Ctrl+C - trying to release...")
        try:
            g.release()
        except Exception:
            pass


if __name__ == "__main__":
    main()
