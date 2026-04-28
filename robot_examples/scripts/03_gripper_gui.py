from __future__ import annotations

import argparse
import threading
import time
import tkinter as tk
from tkinter import ttk

import mujoco
import mujoco.viewer

from common import DEFAULT_SCENE, get_actuators, load_model, set_gripper, set_wrist


GRIPPER_MIN = 0.0
GRIPPER_MAX = 0.014
GRIPPER_OPEN = GRIPPER_MIN
GRIPPER_CLOSED = GRIPPER_MAX
WRIST_MIN = -3.141592653589793
WRIST_MAX = 3.141592653589793


class CommandState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.wrist = 0.0
        self.gripper = 0.007
        self.running = True

    def set(self, wrist: float, gripper: float) -> None:
        with self._lock:
            self.wrist = wrist
            self.gripper = gripper

    def stop(self) -> None:
        with self._lock:
            self.running = False

    def get(self) -> tuple[bool, float, float]:
        with self._lock:
            return self.running, self.wrist, self.gripper


def simulation_loop(scene: str, state: CommandState) -> None:
    model, data = load_model(scene)
    actuators = get_actuators(model)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            running, wrist, gripper = state.get()
            if not running:
                break

            set_wrist(data, actuators, wrist)
            set_gripper(data, actuators, gripper)
            mujoco.mj_step(model, data)
            viewer.sync()
            time.sleep(model.opt.timestep)

    state.stop()


def build_gui(scene: str) -> None:
    state = CommandState()
    sim_thread = threading.Thread(target=simulation_loop, args=(scene, state), daemon=True)
    sim_thread.start()

    root = tk.Tk()
    root.title("MuJoCo Gripper Control")
    root.geometry("420x220")

    wrist_var = tk.DoubleVar(value=0.0)
    gripper_var = tk.DoubleVar(value=0.007)

    def update_command(*_: object) -> None:
        state.set(wrist_var.get(), gripper_var.get())

    wrist_var.trace_add("write", update_command)
    gripper_var.trace_add("write", update_command)

    ttk.Label(root, text="Wrist rotation [rad]").pack(anchor="w", padx=16, pady=(16, 4))
    ttk.Scale(root, from_=WRIST_MIN, to=WRIST_MAX, orient="horizontal", variable=wrist_var).pack(
        fill="x", padx=16
    )

    ttk.Label(root, text="Gripper actuator target [m]").pack(anchor="w", padx=16, pady=(16, 4))
    ttk.Scale(root, from_=GRIPPER_MIN, to=GRIPPER_MAX, orient="horizontal", variable=gripper_var).pack(
        fill="x", padx=16
    )

    values = ttk.Label(root)
    values.pack(anchor="w", padx=16, pady=16)

    def refresh_label() -> None:
        running, wrist, gripper = state.get()
        values.config(text=f"wrist={wrist:+.3f} rad   gripper={gripper:.4f} m")
        if running:
            root.after(50, refresh_label)
        else:
            root.destroy()

    def on_close() -> None:
        state.stop()
        root.destroy()

    ttk.Button(root, text="Center", command=lambda: (wrist_var.set(0.0), gripper_var.set(0.007))).pack(
        side="left", padx=(16, 8), pady=8
    )
    ttk.Button(root, text="Open", command=lambda: gripper_var.set(GRIPPER_OPEN)).pack(
        side="left", padx=8, pady=8
    )
    ttk.Button(root, text="Close", command=lambda: gripper_var.set(GRIPPER_CLOSED)).pack(
        side="left", padx=8, pady=8
    )

    root.protocol("WM_DELETE_WINDOW", on_close)
    refresh_label()
    root.mainloop()
    state.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Open a small GUI to control the exported gripper.")
    parser.add_argument("--scene", default=str(DEFAULT_SCENE), help="Path to scene.xml")
    args = parser.parse_args()

    build_gui(args.scene)


if __name__ == "__main__":
    main()
