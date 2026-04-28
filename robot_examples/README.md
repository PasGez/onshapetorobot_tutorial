# Robot Examples

This folder contains a ready-to-run MuJoCo export and Python examples for loading and controlling the gripper.

Expected files:

```text
robot_examples/
|-- robot.xml
|-- scene.xml
|-- assets/
`-- scripts/
```

Use `scene.xml` for simulation and viewer tests. `scene.xml` includes `robot.xml` and adds the MuJoCo scene.

## 1. Install requirements

The example scripts use:

```text
mujoco          -> pip package for simulation and viewer
tkinter         -> Python GUI module used by 03_gripper_gui.py
argparse        -> Python standard library
math            -> Python standard library
time            -> Python standard library
threading       -> Python standard library
dataclasses     -> Python standard library
pathlib         -> Python standard library
collections.abc -> Python standard library
```

Install the required pip package:

```bash
python -m pip install mujoco
```

If your system uses `python3` instead of `python`:

```bash
python3 -m pip install mujoco
```

`tkinter` is included with most Windows and macOS Python installations. On some Linux systems, install it with the system package manager:

```bash
sudo apt install python3-tk
```

Verify:

```bash
python -c "import mujoco; print(mujoco.__version__)"
python -c "import mujoco.viewer; print('mujoco.viewer ok')"
python -c "import tkinter; print('tkinter ok')"
```

## 2. Open the exported scene

From this folder:

```bash
python -m mujoco.viewer --mjcf scene.xml
```

Windows PowerShell:

```powershell
python -m mujoco.viewer --mjcf .\scene.xml
```

## 3. Load the model and inspect joints

From this folder:

```bash
python .\scripts\01_load_model.py
```

Linux/macOS:

```bash
python scripts/01_load_model.py
```

This prints the MuJoCo model dimensions, joint names, actuator names, and resolved actuator ids.

Expected actuators:

```text
wrist_rotation
gripper
```

The example model intentionally uses one gripper actuator for both fingers. Internally, `robot.xml` couples `left_finger` and `right_finger` with a fixed tendon named `gripper`. Each finger uses `coef="0.5"`, so a symmetric command of `0.014` corresponds to both finger joints moving to `0.014`.

Joint and actuator limits used by the examples:

```text
wrist_rotation joint   -> -pi to +pi rad (-180 to +180 deg)
wrist_rotation control -> -pi to +pi rad
left_finger joint      -> 0 to 0.014 m
right_finger joint     -> 0 to 0.014 m
gripper control        -> 0 to 0.014 m
```

For this exported gripper, the command convention is:

```text
gripper = 0.000 -> open
gripper = 0.014 -> closed
```

## 4. Guided `robot.xml` edits

`onshape-to-robot` exports a usable MuJoCo file, but for these examples `robot.xml` was edited manually to make the controls cleaner and safer.

Useful reference: [MuJoCo XML reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html).

The edits are all in `robot.xml`. Do not edit `scene.xml` for these control changes: `scene.xml` only includes `robot.xml` and adds the floor, lighting, and viewer scene.

### Step 1: add wrist limits

Find the wrist joint:

```xml
<joint axis="0 0 1" name="wrist_rotation" type="hinge"/>
```

Add a `range` so the joint can rotate from `-180 deg` to `+180 deg`:

```xml
<joint axis="0 0 1" name="wrist_rotation" type="hinge" range="-3.141592653589793 3.141592653589793"/>
```

### Step 2: add finger limits

Find the two slider joints:

```xml
<joint axis="0 0 1" name="right_finger" type="slide"/>
<joint axis="0 0 1" name="left_finger" type="slide"/>
```

Add the measured travel limit of `0.014 m`:

```xml
<joint axis="0 0 1" name="right_finger" type="slide" range="0 0.014"/>
<joint axis="0 0 1" name="left_finger" type="slide" range="0 0.014"/>
```

### Step 3: replace two finger actuators with one gripper actuator

The exported model may contain one actuator per finger:

```xml
<actuator>
  <position name="wrist_rotation" joint="wrist_rotation"/>
  <position name="right_finger" joint="right_finger"/>
  <position name="left_finger" joint="left_finger"/>
</actuator>
```

For the examples, both fingers are driven by one actuator named `gripper`. Add a fixed tendon before `<actuator>`:

```xml
<tendon>
  <fixed name="gripper">
    <joint joint="right_finger" coef="0.5"/>
    <joint joint="left_finger" coef="0.5"/>
  </fixed>
</tendon>
```

Then replace the old actuator block with:

```xml
<actuator>
  <position name="wrist_rotation" joint="wrist_rotation" ctrlrange="-3.141592653589793 3.141592653589793"/>
  <position name="gripper" tendon="gripper" ctrlrange="0 0.014"/>
</actuator>
```

The `coef="0.5"` values make the tendon length equal to the average of the two finger joints. With symmetric finger motion, a `gripper` command of `0.014` drives both finger joints to `0.014`.

### Step 4: tune position actuator dynamics

The exported default position actuator settings are near the top of `robot.xml`:

```xml
<position kp="50" dampratio="1"/>
```

Use this as the first place to tune actuator response:

```text
Increase kp        -> faster, stiffer target tracking
Decrease kp        -> softer, slower target tracking
Increase dampratio -> more damping, less oscillation
Decrease dampratio -> faster but more oscillatory response
```

After editing `robot.xml`, verify the result:

```bash
python .\scripts\01_load_model.py
```

Expected actuators:

```text
wrist_rotation
gripper
```

## 5. Move actuators with preset dynamics

Run a scripted actuator demo:

```bash
python .\scripts\02_preset_dynamics.py --preset open-close
```

Available presets:

```text
open-close  -> opens and closes both fingers
wrist-wave  -> rotates the wrist while keeping the gripper open
pick-cycle  -> repeats open, close, hold, release
```

Examples:

```bash
python .\scripts\02_preset_dynamics.py --preset wrist-wave --duration 15
python .\scripts\02_preset_dynamics.py --preset pick-cycle --duration 20
```

Run without opening the viewer:

```bash
python .\scripts\02_preset_dynamics.py --preset open-close --headless
```

Linux/macOS paths:

```bash
python scripts/02_preset_dynamics.py --preset open-close
```

## 6. Change actuator dynamics and commands

There are three different places to modify behavior, depending on what you want to change.

### Change physical limits

Edit `robot.xml`.

Joint limits are on the `<joint>` elements:

```xml
<joint name="wrist_rotation" type="hinge" range="-3.141592653589793 3.141592653589793"/>
<joint name="right_finger" type="slide" range="0 0.014"/>
<joint name="left_finger" type="slide" range="0 0.014"/>
```

Actuator command limits are on the `<position>` actuators:

```xml
<position name="wrist_rotation" joint="wrist_rotation" ctrlrange="-3.141592653589793 3.141592653589793"/>
<position name="gripper" tendon="gripper" ctrlrange="0 0.014"/>
```

If you discover a better maximum opening from manual simulation or robot measurements, change both the finger joint ranges and the `gripper` actuator `ctrlrange`.

### Change actuator stiffness / damping

Edit the default position actuator settings in `robot.xml`:

```xml
<position kp="50" dampratio="1"/>
```

Typical changes:

```text
Increase kp       -> tracks target faster and more stiffly
Decrease kp       -> softer, slower tracking
Increase dampratio -> more damping, less oscillation
Decrease dampratio -> faster but more oscillatory response
```

### Change scripted command trajectories

Edit `scripts/02_preset_dynamics.py`.

Global command limits are defined near the top:

```python
GRIPPER_MIN = 0.0
GRIPPER_MAX = 0.014
WRIST_MIN = -math.pi
WRIST_MAX = math.pi
```

Preset trajectories are regular Python functions:

```python
def open_close(t: float) -> tuple[float, float]:
    gripper = 0.007 + 0.007 * math.sin(2.0 * math.pi * 0.35 * t)
    wrist = 0.0
    return wrist, clamp(gripper, GRIPPER_MIN, GRIPPER_MAX)
```

Each preset returns:

```text
(wrist_target_rad, gripper_target_m)
```

Use `0.0` for open and `0.014` for closed.

To add a new preset, define a function and register it in `PRESETS`:

```python
def fast_open_close(t: float) -> tuple[float, float]:
    gripper = 0.007 + 0.007 * math.sin(2.0 * math.pi * 1.0 * t)
    wrist = 0.0
    return wrist, clamp(gripper, GRIPPER_MIN, GRIPPER_MAX)

PRESETS = {
    "open-close": open_close,
    "wrist-wave": wrist_wave,
    "pick-cycle": pick_cycle,
    "fast-open-close": fast_open_close,
}
```

Then run:

```bash
python .\scripts\02_preset_dynamics.py --preset fast-open-close
```

### Change GUI slider limits

Edit `scripts/03_gripper_gui.py`.

The GUI uses its own slider constants:

```python
GRIPPER_MIN = 0.0
GRIPPER_MAX = 0.014
WRIST_MIN = -3.141592653589793
WRIST_MAX = 3.141592653589793
```

Keep these consistent with the joint and actuator limits in `robot.xml`.

## 7. Control the gripper with a GUI

Run:

```bash
python .\scripts\03_gripper_gui.py
```

Linux/macOS:

```bash
python scripts/03_gripper_gui.py
```

The GUI exposes:

```text
Wrist rotation slider
Gripper actuator target slider
Center button
Open button
Close button
```

The MuJoCo viewer opens next to the GUI. Move the sliders to update the actuator targets in real time.

## 8. Use a different scene

All scripts accept `--scene`:

```bash
python .\scripts\01_load_model.py --scene C:\path\to\scene.xml
python .\scripts\02_preset_dynamics.py --scene C:\path\to\scene.xml --preset open-close
python .\scripts\03_gripper_gui.py --scene C:\path\to\scene.xml
```

The examples expect these actuator names:

```text
wrist_rotation
gripper
```

If your exported robot uses different names, update `scripts/common.py`.

## 9. Troubleshooting

### `ModuleNotFoundError: No module named 'mujoco'`

Install MuJoCo:

```bash
python -m pip install mujoco
```

### `Actuator not found in model`

Open `robot.xml` and check the actuator names in the `<actuator>` section.

The tutorial model contains:

```xml
<tendon>
  <fixed name="gripper">
    <joint joint="right_finger" coef="0.5"/>
    <joint joint="left_finger" coef="0.5"/>
  </fixed>
</tendon>
<actuator>
  <position name="wrist_rotation" joint="wrist_rotation" ctrlrange="-3.141592653589793 3.141592653589793"/>
  <position name="gripper" tendon="gripper" ctrlrange="0 0.014"/>
</actuator>
```

### The GUI opens but the viewer does not

First verify that the normal viewer works:

```bash
python -m mujoco.viewer --mjcf scene.xml
```

Then try the GUI again:

```bash
python .\scripts\03_gripper_gui.py
```
