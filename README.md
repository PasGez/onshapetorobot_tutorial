# Onshape Gripper Export to MuJoCo

This repository documents a complete workflow to export an Onshape robotic gripper assembly to MuJoCo using [`onshape-to-robot`](https://github.com/Rhoban/onshape-to-robot).

The pipeline is:

```text
Onshape Assembly -> onshape-to-robot -> robot.xml + scene.xml + meshes -> MuJoCo viewer
```

`robot.xml` is the exported robot model. `scene.xml` includes `robot.xml` and adds the MuJoCo scene settings used by the viewer. For testing in MuJoCo, open `scene.xml`.

## References

- Onshape: https://cad.onshape.com/
- Onshape API keys: https://cad.onshape.com/user/developer/apiKeys
- onshape-to-robot documentation: https://onshape-to-robot.readthedocs.io/en/latest/
- onshape-to-robot GitHub repository: https://github.com/Rhoban/onshape-to-robot
- MuJoCo website: https://mujoco.org/
- MuJoCo GitHub releases: https://github.com/google-deepmind/mujoco/releases

## 1. Prepare the CAD in Onshape

Open your robot or gripper assembly in Onshape.

For this tutorial, use this Onshape Assembly:

```text
https://cad.onshape.com/documents/371b06a42f475c9907de5e85/w/adb936e8683c4e5f511239d8/e/13316bfea1db3d35234ddf73
```

The export must be performed from an **Assembly tab**, not from a Part Studio.

Copy the browser URL while the Assembly tab is active. The URL will be used later in `config.json`.

Expected URL format:

```text
https://cad.onshape.com/documents/<DOCUMENT_ID>/w/<WORKSPACE_ID>/e/<ELEMENT_ID>
```

## 2. Name the Onshape mates

`onshape-to-robot` recognizes joints from Onshape mates using naming conventions.

Movable joints must start with:

```text
dof_
```

Fixed connections must start with:

```text
fix_
```

Typical gripper mate names:

```text
fix_gripper_base
dof_wrist_rotation
dof_left_finger
dof_right_finger
```

Expected exported joint types:

| Onshape mate type | Name example | Exported joint type |
|---|---|---|
| Fastened mate | `fix_gripper_base` | Fixed connection |
| Revolute mate | `dof_wrist_rotation` | Revolute joint |
| Slider mate | `dof_left_finger` | Prismatic / slide joint |
| Slider mate | `dof_right_finger` | Prismatic / slide joint |

## 3. Check joint axis direction

For `onshape-to-robot`, joint motion is defined with respect to the mate frame shown in Onshape.

The important convention is:

```text
Revolute mate -> rotation around local Z axis
Slider mate   -> translation along local Z axis
```

For a two-finger gripper, decide which positive motion should close the fingers.

If a joint axis is oriented in the opposite direction, add `_inv` to the joint name:

```text
dof_right_finger_inv
```

If both slider mate Z axes point outward and positive motion should close inward, use:

```text
dof_left_finger_inv
dof_right_finger_inv
```

Do not add `_inv` blindly. First inspect the mate frame in Onshape and check the local Z axis direction.

Example of outward slider axes:

<img src="assets/images/onshape-outward-z-axes.png" alt="Onshape gripper mate Z axes pointing outward" width="700">

## 4. Assign material to parts

Before exporting your own model, assign a material to every part in the Onshape Part Studio.

<img src="assets/images/onshape-edit-material.png" alt="Onshape Edit material menu for a part" width="700">

Right-click each part, select **Edit material...**, and choose a material from the Onshape material library.

This is important because material density gives each part a mass. MuJoCo needs valid masses and inertial properties to simulate the exported model correctly.

## 5. Install Python tools

Install `onshape-to-robot` and the Python MuJoCo viewer:

```bash
python -m pip install onshape-to-robot mujoco
```

If your system uses `python3` instead of `python`:

```bash
python3 -m pip install onshape-to-robot mujoco
```

Verify the installation:

```bash
onshape-to-robot --help
python -c "import mujoco; print(mujoco.__version__)"
python -c "import mujoco.viewer; print('mujoco.viewer ok')"
```

The GUI examples also use Python's `tkinter` module. It is usually included on Windows and macOS; on some Linux systems install it with:

```bash
sudo apt install python3-tk
```

If `onshape-to-robot` is not found, see [Troubleshooting](#15-troubleshooting).

## 6. Create Onshape API keys

Go to:

```text
https://cad.onshape.com/user/developer/apiKeys
```

Create a new API key pair.

You need:

```text
ONSHAPE_ACCESS_KEY
ONSHAPE_SECRET_KEY
```

Keep the secret key private. Do not commit it to GitHub.

## 7. Create the robot project directory

Create one directory for the export files.

Windows PowerShell:

```powershell
mkdir my-robot
cd my-robot
```

Linux/macOS:

```bash
mkdir my-robot
cd my-robot
```

All following commands assume that the terminal is inside `my-robot`.

## 8. Create `.env`

Create the credential file inside `my-robot`.

Windows PowerShell:

```powershell
notepad .env
```

Linux/macOS:

```bash
nano .env
```

Add your Onshape credentials:

```text
ONSHAPE_API=https://cad.onshape.com
ONSHAPE_ACCESS_KEY=YOUR_ACCESS_KEY
ONSHAPE_SECRET_KEY=YOUR_SECRET_KEY
```

Do not add `export` in `.env`.

Correct:

```text
ONSHAPE_ACCESS_KEY=YOUR_ACCESS_KEY
```

Incorrect:

```text
export ONSHAPE_ACCESS_KEY=YOUR_ACCESS_KEY
```

Important: `onshape-to-robot` loads `.env` from the current directory or one of its parent directories. If `.env` is inside `my-robot`, run the export from inside `my-robot`.

## 9. Create `config.json`

Create the configuration file inside `my-robot`.

Windows PowerShell:

```powershell
notepad config.json
```

Linux/macOS:

```bash
nano config.json
```

Minimal MuJoCo configuration for this tutorial:

```json
{
  "url": "https://cad.onshape.com/documents/371b06a42f475c9907de5e85/w/adb936e8683c4e5f511239d8/e/13316bfea1db3d35234ddf73",
  "output_format": "mujoco",
  "assembly_name": "Assembly 1"
}
```

For your own robot, replace `url` with the Assembly URL copied from Onshape.

At this point, the project directory should contain:

```text
my-robot/
|-- .env
`-- config.json
```

## 10. Run the export

Run the command from inside `my-robot`:

```bash
onshape-to-robot .
```

If `onshape-to-robot` is installed but not available from the terminal, use the Python entry point:

```bash
python -c "from onshape_to_robot.export import main; main()" .
```

## 11. Check the generated files

After a successful MuJoCo export, `my-robot` should contain:

```text
my-robot/
|-- .env
|-- config.json
|-- robot.xml
|-- scene.xml
`-- assets/
```

Use the files this way:

```text
robot.xml -> exported robot model
scene.xml -> MuJoCo scene that includes robot.xml
assets/   -> exported meshes and part metadata
```

For viewer tests, use `scene.xml`.

## 12. Test in MuJoCo

Open the generated scene with the Python MuJoCo viewer:

```bash
python -m mujoco.viewer --mjcf scene.xml
```

On Windows PowerShell, the same command works from inside `my-robot`:

```powershell
python -m mujoco.viewer --mjcf .\scene.xml
```

If you installed the native MuJoCo release and its `bin` directory is in `PATH`, you can also use:

```bash
simulate scene.xml
```

On Windows with the native viewer:

```cmd
simulate.exe scene.xml
```

If `simulate` is not found, use the Python viewer command instead.

## 13. Check the exported joints

Open `robot.xml` and inspect the joints.

Expected examples:

```xml
<joint name="wrist_rotation" type="hinge" ... />
<joint name="left_finger" type="slide" ... />
<joint name="right_finger" type="slide" ... />
```

For a gripper, verify:

```text
positive left_finger motion  -> closes toward center
positive right_finger motion -> closes toward center
```

If both fingers open instead of closing, invert both prismatic joints in Onshape naming:

```text
dof_left_finger_inv
dof_right_finger_inv
```

If one finger closes and the other opens, invert only the wrong one:

```text
dof_left_finger
dof_right_finger_inv
```

or:

```text
dof_left_finger_inv
dof_right_finger
```

## 14. Full command sequence

From a clean terminal, the local workflow is:

```bash
python -m pip install onshape-to-robot mujoco
mkdir my-robot
cd my-robot
```

Create `.env`, then create `config.json`, then run:

```bash
onshape-to-robot .
python -m mujoco.viewer --mjcf scene.xml
```

On Windows PowerShell, after creating `.env` and `config.json`:

```powershell
onshape-to-robot .
python -m mujoco.viewer --mjcf .\scene.xml
```

## 15. Troubleshooting

### `ERROR: No Onshape API access key are set`

The `.env` file is missing, has the wrong variable names, or is not visible from the current terminal location.

Check that the file is here:

```text
my-robot/.env
```

Make sure it contains exactly:

```text
ONSHAPE_API=https://cad.onshape.com
ONSHAPE_ACCESS_KEY=YOUR_ACCESS_KEY
ONSHAPE_SECRET_KEY=YOUR_SECRET_KEY
```

Then run the export from inside `my-robot`:

```bash
cd my-robot
onshape-to-robot .
```

### `onshape-to-robot` is not recognized

The package is installed, but Python's script directory is not in `PATH`.

First check that the package is installed:

```bash
python -m pip show onshape-to-robot
```

Immediate workaround:

```bash
python -c "from onshape_to_robot.export import main; main()" .
```

Temporary Windows PowerShell `PATH` fix:

```powershell
$Scripts = python -c "import pathlib, site, sysconfig; candidates = [sysconfig.get_path('scripts'), str(pathlib.Path(site.getuserbase()) / 'Scripts'), str(pathlib.Path(site.getusersitepackages()).parent / 'Scripts')]; print(next(p for p in candidates if p and pathlib.Path(p, 'onshape-to-robot.exe').exists()))"
$env:Path += ";$Scripts"
onshape-to-robot --help
```

### `simulate` is not recognized

The native MuJoCo viewer executable is not installed or its `bin` directory is not in `PATH`.

Use the Python viewer instead:

```bash
python -m mujoco.viewer --mjcf scene.xml
```

On Windows PowerShell:

```powershell
python -m mujoco.viewer --mjcf .\scene.xml
```

If Python cannot import `mujoco`, install it first:

```bash
python -m pip install mujoco
```

### The export uses the wrong Onshape tab

Make sure the URL in `config.json` points to the Assembly tab, not the Part Studio tab.

### Fingers move in the wrong direction

Check the Z axis of the Slider Mate frame in Onshape.

Use `_inv` on the corresponding joint name if the exported direction is opposite to the desired direction.

### The robot has unexpected fixed or missing joints

Check the mate names.

Movable joints must start with:

```text
dof_
```

Fixed links should start with:

```text
fix_
```

## 16. Next examples

After you can export and open `scene.xml`, continue with the runnable control examples:

```text
robot_examples/README.md
```

That README shows how to load the model, apply joint and actuator limits, drive both fingers with a single `gripper` actuator, move the actuators with preset dynamics, and control the gripper from a small GUI.

## 17. Security note

Never commit `.env` files or API keys to GitHub.

Add `.env` to `.gitignore`:

```gitignore
.env
```

If an API secret key is accidentally shared publicly, revoke it immediately from the Onshape Developer Portal and generate a new key pair.
