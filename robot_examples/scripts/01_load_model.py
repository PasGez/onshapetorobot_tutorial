from __future__ import annotations

import argparse

import mujoco

from common import DEFAULT_SCENE, get_actuators, load_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the exported MuJoCo scene and print model information.")
    parser.add_argument("--scene", default=str(DEFAULT_SCENE), help="Path to scene.xml")
    args = parser.parse_args()

    model, data = load_model(args.scene)
    actuators = get_actuators(model)

    mujoco.mj_forward(model, data)

    print(f"Loaded scene: {args.scene}")
    print(f"nq={model.nq}, nv={model.nv}, nu={model.nu}, nbody={model.nbody}")
    print("Joints:")
    for joint_id in range(model.njnt):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, joint_id) or f"<unnamed:{joint_id}>"
        lower, upper = model.jnt_range[joint_id]
        print(f"  - {name}: range=[{lower:.6g}, {upper:.6g}]")

    print("Actuators:")
    for actuator_id in range(model.nu):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, actuator_id) or f"<unnamed:{actuator_id}>"
        lower, upper = model.actuator_ctrlrange[actuator_id]
        print(f"  - {name}: ctrlrange=[{lower:.6g}, {upper:.6g}]")

    print("Resolved actuator ids:")
    print(f"  wrist_rotation: {actuators.wrist}")
    print(f"  gripper:        {actuators.gripper}")


if __name__ == "__main__":
    main()
