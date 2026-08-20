"""
servo_host.py  —  REFERENCE / PLACEHOLDER low-level bus-servo driver
====================================================================
This is a documented placeholder so the rest of the project imports and runs.
REPLACE the body of the serial methods with your actual bus-servo protocol,
or adapt this to wrap the driver your servo vendor provides.

The rest of the codebase only relies on this minimal interface:

    host = ServoHost(port="COM3", n_servos=4)
    angles = host.read_joints()                  # -> np.ndarray, current angles in degrees
    host.move_to_joints(target_angles, t=2.0)    # move to target (deg) over t seconds

Notes
-----
- Many hobby bus servos (e.g. serial-bus smart servos) use ASCII command frames
  such as `#<id>P<pulse>T<time>!`. The example MOVE command below mirrors that style.
- Position feedback ("read" of current angle) is vendor-specific; some servos
  reply to a READ frame with the current position, others do not. If yours does
  not support position read, you will need a servo that does — the adaptive grasp
  logic relies on reading the current angle.
- Angle<->pulse conversion below is a placeholder. Calibrate to your servo's range
  (commonly 500-2500 us mapped to 0-270 deg, but check your datasheet).
"""

import time
import numpy as np

try:
    import serial   # pyserial
except ImportError:
    serial = None


# ---- placeholder pulse/angle mapping (CALIBRATE FOR YOUR SERVO) ----
PULSE_MIN, PULSE_MAX = 500, 2500       # microseconds
ANGLE_MIN, ANGLE_MAX = 0.0, 270.0      # degrees


def angle_to_pulse(deg: float) -> int:
    deg = max(ANGLE_MIN, min(ANGLE_MAX, deg))
    frac = (deg - ANGLE_MIN) / (ANGLE_MAX - ANGLE_MIN)
    return int(PULSE_MIN + frac * (PULSE_MAX - PULSE_MIN))


def pulse_to_angle(pulse: int) -> float:
    frac = (pulse - PULSE_MIN) / (PULSE_MAX - PULSE_MIN)
    return ANGLE_MIN + frac * (ANGLE_MAX - ANGLE_MIN)


class ServoHost:
    def __init__(self, port="COM3", baudrate=115200, n_servos=4, timeout=0.1):
        self.port = port
        self.n_servos = n_servos
        # last commanded angles, used as a fallback when real feedback isn't available
        self._last_cmd = np.full(n_servos, (ANGLE_MIN + ANGLE_MAX) / 2.0, dtype=float)

        self.ser = None
        if serial is not None:
            try:
                self.ser = serial.Serial(port, baudrate, timeout=timeout)
                print(f"[ServoHost] opened {port} @ {baudrate}")
            except Exception as e:
                print(f"[ServoHost] WARNING: could not open {port}: {e}")
                print("[ServoHost] running in OFFLINE simulation mode")
        else:
            print("[ServoHost] pyserial not installed -> OFFLINE simulation mode")

    # --------------------------------------------------------
    def read_joints(self) -> np.ndarray:
        """
        Return current angles (deg) for all servos as an np.ndarray.

        PLACEHOLDER: returns the last commanded angles. Replace with a real
        position-read frame for your servo so adaptive grasping can detect stalls.
        """
        # TODO: implement vendor READ frame, parse reply, convert pulse->angle.
        return self._last_cmd.copy()

    def move_to_joints(self, target, t: float = 1.0):
        """
        Move all servos to `target` angles (deg) over `t` seconds.

        PLACEHOLDER: sends one MOVE frame per servo in the `#<id>P<pulse>T<ms>!`
        style and records the command. Replace with your protocol as needed.
        """
        target = np.asarray(target, dtype=float).ravel()
        t_ms = int(max(0.0, t) * 1000)

        for i, deg in enumerate(target[: self.n_servos]):
            sid = i + 1
            pulse = angle_to_pulse(float(deg))
            frame = f"#{sid:03d}P{pulse:04d}T{t_ms:04d}!"
            if self.ser is not None:
                try:
                    self.ser.write(frame.encode("ascii"))
                except Exception as e:
                    print(f"[ServoHost] write failed: {e}")
            # else: offline simulation, just record

        self._last_cmd[: len(target)] = target[: self.n_servos]

    def close(self):
        if self.ser is not None:
            self.ser.close()


if __name__ == "__main__":
    # tiny self-test (offline simulation is fine)
    host = ServoHost(port="COM3", n_servos=4)
    print("initial:", host.read_joints())
    host.move_to_joints([180, 180, 180, 180], t=1.0)
    print("after move:", host.read_joints())
