"""
single_gripper.py
=================
Core controller for a single-servo, three-finger underactuated hand (1 DOF control).

Mechanism: a central bus servo drives a rotary disc; three linkages translate the
single rotation into synchronous opening/closing of three fingers. Because the three
fingers are symmetric, the whole hand is controlled by ONE variable: the servo angle.

Depends on a low-level driver `servo_host.ServoHost` that provides:
    host.read_joints()                 -> np.ndarray of current joint angles (deg)
    host.move_to_joints(target, t=...) -> move to target angles over t seconds
(See servo_host.py for the expected interface — replace with your hardware driver.)

Usage:
    python single_gripper.py --port COM3 calib    # calibrate open/closed limits
    python single_gripper.py --port COM3 grasp    # adaptive grasp demo
    python single_gripper.py --port COM3 open
"""

import time
import json
import argparse
import numpy as np
from pathlib import Path

from servo_host import ServoHost


# ============================================================
#  Configuration
# ============================================================
GRIPPER_SERVO_ID  = 1     # bus ID of the grasp servo (set via your servo GUI/SETID)
GRIPPER_SERVO_IDX = 0     # index of this servo in the read_joints() array
                          # typically = bus ID - 1, may vary by host implementation

# Default angles (deg) — only meaningful AFTER you run calibrate()
DEFAULT_OPEN_DEG   = 180.0
DEFAULT_CLOSED_DEG = 230.0

# Software limits — keep the servo away from mechanical hard stops
SOFT_MIN = 120.0
SOFT_MAX = 280.0

# Other servos on the bus that are NOT part of this mechanism.
# If they are powered but unused, we read-then-write them unchanged to hold them still.
# If you have NO other servos connected, set OTHER_SERVOS_PRESENT = False.
N_OTHER_SERVOS = 3
OTHER_SERVOS_PRESENT = True

CALIB_FILE = Path(__file__).parent / "gripper_calib.json"


# ============================================================
#  Controller
# ============================================================
class SingleServoGripper:

    def __init__(self, host):
        self.host = host
        self.open_deg   = DEFAULT_OPEN_DEG
        self.closed_deg = DEFAULT_CLOSED_DEG
        if CALIB_FILE.exists():
            self.load_calibration()

    # -------- low-level I/O --------
    def _read_pos(self) -> float:
        """Read the grasp servo's current angle (deg)."""
        joints = self.host.read_joints()
        return float(joints[GRIPPER_SERVO_IDX])

    def _send(self, target_deg: float, duration_s: float):
        """Move the grasp servo to target_deg; hold any other servos in place."""
        target_deg = float(np.clip(target_deg, SOFT_MIN, SOFT_MAX))

        if OTHER_SERVOS_PRESENT:
            current = np.array(self.host.read_joints(), dtype=float)
            target = current.copy()
            target[GRIPPER_SERVO_IDX] = target_deg
        else:
            target = np.full(1 + N_OTHER_SERVOS, target_deg, dtype=float)
            target[GRIPPER_SERVO_IDX] = target_deg

        self.host.move_to_joints(target, t=duration_s)

    # -------- high-level actions --------
    def open_hand(self, duration=0.8):
        """Open fully."""
        self._send(self.open_deg, duration)
        time.sleep(duration + 0.05)
        return self._read_pos()

    def close_hand(self, duration=1.2):
        """Close fully WITHOUT object detection (no-load demo only — will stall on an object!)."""
        self._send(self.closed_deg, duration)
        time.sleep(duration + 0.05)
        return self._read_pos()

    def set_grip(self, ratio: float, duration=1.0):
        """Set openness. ratio 0.0 = fully open, 1.0 = fully closed (linear interpolation)."""
        ratio = float(np.clip(ratio, 0.0, 1.0))
        target = self.open_deg + ratio * (self.closed_deg - self.open_deg)
        self._send(target, duration)
        time.sleep(duration + 0.05)

    def release(self, duration=0.6):
        return self.open_hand(duration)

    # =========================================================
    #  CORE: adaptive grasp via stall detection
    # =========================================================
    def grasp(self,
              max_close_ratio: float = 1.0,
              duration:        float = 2.0,
              stall_thresh:    float = 1.0,
              stall_count:     int   = 3,
              poll_dt:         float = 0.08,
              verbose:         bool  = True):
        """
        Ramp toward 'closed' while polling position. If the angle stops changing
        (< stall_thresh deg) for stall_count consecutive samples while still >2 deg
        from target, the object has been contacted: lock the current position to
        hold the grip and prevent the servo from stalling/overheating.

        Returns dict: {grasped: bool, final: float, reason: 'stall'|'reached', time_s: float}
        """
        target_deg = self.open_deg + max_close_ratio * (self.closed_deg - self.open_deg)
        target_deg = float(np.clip(target_deg, SOFT_MIN, SOFT_MAX))

        if verbose:
            now = self._read_pos()
            print(f"[grasp] start {now:.1f} deg -> target {target_deg:.1f} deg  ({duration}s)")

        self._send(target_deg, duration)

        prev   = self._read_pos()
        stalls = 0
        t0     = time.time()
        time.sleep(poll_dt)

        while time.time() - t0 < duration + 0.3:
            cur   = self._read_pos()
            delta = abs(cur - prev)
            dist  = abs(cur - target_deg)

            if delta < stall_thresh and dist > 2.0:
                stalls += 1
            else:
                stalls = 0

            if stalls >= stall_count:
                self._send(cur, 0.1)   # lock current position
                elapsed = time.time() - t0
                if verbose:
                    print(f"[grasp] OBJECT detected, locked at {cur:.1f} deg ({elapsed:.2f}s)")
                return {'grasped': True, 'final': cur, 'reason': 'stall', 'time_s': elapsed}

            prev = cur
            time.sleep(poll_dt)

        cur = self._read_pos()
        elapsed = time.time() - t0
        if verbose:
            print(f"[grasp] no object, closed to {cur:.1f} deg ({elapsed:.2f}s)")
        return {'grasped': False, 'final': cur, 'reason': 'reached', 'time_s': elapsed}

    # -------- graded grasps --------
    def grasp_soft(self):
        """Gentle — eggs, fruit, soft prints."""
        return self.grasp(max_close_ratio=0.85, duration=3.0, stall_thresh=0.8, stall_count=2)

    def grasp_normal(self):
        """General-purpose — most rigid objects."""
        return self.grasp(max_close_ratio=0.95, duration=2.0, stall_thresh=1.0, stall_count=3)

    def grasp_firm(self):
        """Secure — heavy or slippery objects."""
        return self.grasp(max_close_ratio=1.0, duration=1.5, stall_thresh=1.5, stall_count=3)

    # -------- calibration / persistence --------
    def calibrate(self):
        print("\n========== Single-servo gripper calibration ==========")
        print("The servo is powered during calibration; move it gently to avoid")
        print("damaging the gears (power off temporarily if it won't budge).\n")

        print("[1/2] Push the three fingers to FULLY OPEN, then press Enter:")
        input()
        time.sleep(0.3)
        self.open_deg = self._read_pos()
        print(f"  open  = {self.open_deg:.2f} deg\n")

        print("[2/2] Push the fingers to JUST CLOSED (tips touching, no force), then press Enter:")
        input()
        time.sleep(0.3)
        self.closed_deg = self._read_pos()
        print(f"  closed = {self.closed_deg:.2f} deg\n")

        self.save_calibration()
        rng = abs(self.closed_deg - self.open_deg)
        print(f"travel = {rng:.1f} deg  (saved to {CALIB_FILE.name})")
        print("======================================================\n")

    def save_calibration(self):
        CALIB_FILE.write_text(json.dumps(
            {"open_deg": self.open_deg, "closed_deg": self.closed_deg}, indent=2))

    def load_calibration(self):
        try:
            data = json.loads(CALIB_FILE.read_text())
            self.open_deg   = float(data["open_deg"])
            self.closed_deg = float(data["closed_deg"])
            print(f"[calibration loaded] open={self.open_deg:.1f}  closed={self.closed_deg:.1f}")
        except Exception as e:
            print(f"[calibration load failed, using defaults] {e}")


# ============================================================
#  CLI
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Single-servo three-finger gripper")
    parser.add_argument("--port", default="COM3")
    parser.add_argument("cmd", nargs="?", default="demo",
                        choices=["demo", "calib", "open", "close", "grasp", "soft", "firm", "half"])
    args = parser.parse_args()

    print(f"Connecting to {args.port} ...")
    host = ServoHost(port=args.port)
    g = SingleServoGripper(host)

    if args.cmd == "calib":
        g.calibrate()
    elif args.cmd == "open":
        g.open_hand()
    elif args.cmd == "close":
        g.close_hand()
    elif args.cmd == "half":
        g.set_grip(0.5)
    elif args.cmd == "grasp":
        g.open_hand(); time.sleep(0.5)
        g.grasp_normal(); time.sleep(3); g.release()
    elif args.cmd == "soft":
        g.open_hand(); time.sleep(0.5)
        g.grasp_soft(); time.sleep(3); g.release()
    elif args.cmd == "firm":
        g.open_hand(); time.sleep(0.5)
        g.grasp_firm(); time.sleep(3); g.release()
    elif args.cmd == "demo":
        print("\n=== Single-servo gripper demo ===\n")
        print("(1) open");        g.open_hand();      time.sleep(1)
        print("(2) half close");  g.set_grip(0.5);    time.sleep(1.5)
        print("(3) open");        g.open_hand();      time.sleep(1)
        print("(4) adaptive grasp"); g.grasp_normal(); time.sleep(2)
        print("(5) release");     g.release();        time.sleep(1)
        print("\n=== done ===\n")


if __name__ == "__main__":
    main()
