from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mujoco


EXAMPLE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENE = EXAMPLE_ROOT / "scene.xml"


@dataclass(frozen=True)
class Actuators:
    wrist: int
    gripper: int


def load_model(scene_path: str | Path = DEFAULT_SCENE) -> tuple[mujoco.MjModel, mujoco.MjData]:
    scene = Path(scene_path).expanduser().resolve()
    if not scene.exists():
        raise FileNotFoundError(f"MuJoCo scene not found: {scene}")

    model = mujoco.MjModel.from_xml_path(str(scene))
    data = mujoco.MjData(model)
    return model, data


def actuator_id(model: mujoco.MjModel, name: str) -> int:
    actuator = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
    if actuator < 0:
        raise ValueError(f"Actuator not found in model: {name}")
    return actuator


def joint_id(model: mujoco.MjModel, name: str) -> int:
    joint = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
    if joint < 0:
        raise ValueError(f"Joint not found in model: {name}")
    return joint


def get_actuators(model: mujoco.MjModel) -> Actuators:
    return Actuators(
        wrist=actuator_id(model, "wrist_rotation"),
        gripper=actuator_id(model, "gripper"),
    )


def set_gripper(data: mujoco.MjData, actuators: Actuators, opening: float) -> None:
    data.ctrl[actuators.gripper] = opening


def set_wrist(data: mujoco.MjData, actuators: Actuators, angle_rad: float) -> None:
    data.ctrl[actuators.wrist] = angle_rad


def list_names(model: mujoco.MjModel, object_type: mujoco.mjtObj, count: int) -> list[str]:
    names: list[str] = []
    for object_id in range(count):
        name = mujoco.mj_id2name(model, object_type, object_id)
        if name:
            names.append(name)
    return names
