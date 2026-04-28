from __future__ import annotations

import argparse
import math
import time
from collections.abc import Callable

import mujoco
import mujoco.viewer

from common import DEFAULT_SCENE, get_actuators, load_model, set_gripper, set_wrist


Preset = Callable[[float], tuple[float, float]]
GRIPPER_MIN = 0.0
GRIPPER_MAX = 0.014
GRIPPER_OPEN = GRIPPER_MIN
GRIPPER_CLOSED = GRIPPER_MAX
WRIST_MIN = -math.pi
WRIST_MAX = math.pi


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def open_close(t: float) -> tuple[float, float]:
    opening = 0.007 + 0.007 * math.sin(2.0 * math.pi * 0.35 * t)
    wrist = 0.0
    return wrist, clamp(opening, GRIPPER_MIN, GRIPPER_MAX)


def wrist_wave(t: float) -> tuple[float, float]:
    opening = GRIPPER_OPEN
    wrist = 0.75 * math.pi * math.sin(2.0 * math.pi * 0.20 * t)
    return clamp(wrist, WRIST_MIN, WRIST_MAX), opening


def pick_cycle(t: float) -> tuple[float, float]:
    phase = t % 6.0
    if phase < 1.5:
        opening = GRIPPER_OPEN
    elif phase < 3.0:
        opening = GRIPPER_CLOSED
    elif phase < 4.5:
        opening = GRIPPER_CLOSED
    else:
        opening = GRIPPER_OPEN

    wrist = 0.50 * math.pi * math.sin(2.0 * math.pi * t / 6.0)
    return clamp(wrist, WRIST_MIN, WRIST_MAX), clamp(opening, GRIPPER_MIN, GRIPPER_MAX)


PRESETS: dict[str, Preset] = {
    "open-close": open_close,
    "wrist-wave": wrist_wave,
    "pick-cycle": pick_cycle,
}


def step_controller(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    preset: Preset,
    duration: float,
    realtime: bool,
) -> None:
    actuators = get_actuators(model)
    start = time.time()

    while data.time < duration:
        wrist, opening = preset(data.time)
        set_wrist(data, actuators, wrist)
        set_gripper(data, actuators, opening)
        mujoco.mj_step(model, data)

        if realtime:
            target = start + data.time
            sleep_time = target - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)


def run_headless(model: mujoco.MjModel, data: mujoco.MjData, preset: Preset, duration: float) -> None:
    step_controller(model, data, preset, duration, realtime=False)
    print(f"Finished headless simulation at t={data.time:.3f}s")


def run_viewer(model: mujoco.MjModel, data: mujoco.MjData, preset: Preset, duration: float) -> None:
    actuators = get_actuators(model)
    start = time.time()

    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running() and data.time < duration:
            step_start = time.time()
            wrist, opening = preset(data.time)
            set_wrist(data, actuators, wrist)
            set_gripper(data, actuators, opening)
            mujoco.mj_step(model, data)
            viewer.sync()

            sleep_time = model.opt.timestep - (time.time() - step_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    elapsed = time.time() - start
    print(f"Finished viewer simulation at t={data.time:.3f}s, wall={elapsed:.3f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Move the exported gripper with preset actuator trajectories.")
    parser.add_argument("--scene", default=str(DEFAULT_SCENE), help="Path to scene.xml")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="open-close")
    parser.add_argument("--duration", type=float, default=12.0, help="Simulation duration in seconds")
    parser.add_argument("--headless", action="store_true", help="Run without opening the MuJoCo viewer")
    args = parser.parse_args()

    model, data = load_model(args.scene)
    preset = PRESETS[args.preset]

    if args.headless:
        run_headless(model, data, preset, args.duration)
    else:
        run_viewer(model, data, preset, args.duration)


if __name__ == "__main__":
    main()
