# Installation, operation, and recovery

All paths below are relative to the skill folder unless stated otherwise. Use PowerShell; quote paths containing spaces. Ordinary commands run as the current user. The tool creates a virtual Xbox 360 controller, not a replacement physical driver.

## Environment and driver

```powershell
.\scripts\setup.ps1 -Action doctor
.\scripts\setup.ps1 -Action environment
# Optional override if automatic Python discovery fails:
.\scripts\setup.ps1 -Action environment -Python '<python.exe>' -VenvPath '<new-venv-directory>'
$env:VGAMEPAD_PYTHON = '<new-venv-directory>\Scripts\python.exe'
.\scripts\gamepad.cmd doctor
```

Python discovery tries explicit `-Python`, `py -3.12`, `python`, then `uv python find 3.12`. Install CPython x64 if none exists. Setup checks version3.10–3.13/x64; Python3.12 is the tested configuration. It creates a venv with pip and installs immutable upstream vgamepad commit `3f910aa8bbde49a576683db74ad5e4a0879f8a80` (package0.1.3) plus pygame-ce2.5.6 for SDL enumeration. Git is not required: pip uses a commit archive URL. Network and trusted package indexes are needed; existing validated environments need no reinstall. `VGAMEPAD_SKIP_VIGEMBUS_INSTALL=true` is scoped to installation and restored afterward.

The launcher and setup invoke Python with `-E` to ignore inherited `PYTHONHOME`/`PYTHONPATH`. This avoids mixing standard libraries when invoked by an agent running another Python version. When calling `python.exe` directly from such a host, also use `-E`.

`doctor` reports OS/architecture, elevation, ViGEmBus system-driver state, signed driver metadata, PnP error codes, registry reboot hints, Python executable/packages, XInput0–3 and SDL name/GUID/index/instance ID. SDL enumeration initializes the joystick subsystem only. Backends may enumerate physical and virtual pads differently; GUIDs are discovery results, not constants.

If ViGEmBus is absent, download the official1.22.0 package:

```powershell
.\scripts\setup.ps1 -Action fetch-driver -InstallerPath '<downloads>\ViGEmBus_1.22.0.exe'
# In an elevated PowerShell, when driver installation is requested:
.\scripts\setup.ps1 -Action install-driver -InstallerPath '<downloads>\ViGEmBus_1.22.0.exe'
```

The script fetches [nefarius/ViGEmBus v1.22.0](https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0) and requires SHA-256 `89220A7865076B342892F98865F3499FB7C4CFD673159E89D352C360FD014C6A`, Authenticode `Valid`, and a Nefarius signer. A different hash, invalid signature, or missing elevation aborts. It never elevates itself. Do not use a package manager's unrelated driver or vgamepad's bundled older MSI. The1.22.0 installer removes the updater; the internal driver version is different, as explained by the official release.

Exit0 is success,3010/1641 indicate reboot semantics; `/norestart` requests no automatic restart. Reboot only at a user-controlled time if required, then rerun doctor/start/verify. Registry indicators are system-wide hints and do not prove that ViGEm needs a reboot. A running bus with PnP code0 plus successful live creation/readback is stronger evidence. Official [EOL statement](https://docs.nefarius.at/projects/ViGEm/End-of-Life/) applies; compatibility must be tested on each host. The script recognizes a failed exit code and does not repeatedly reinstall on blind retries.

## Button and axis conventions

| Switch/alias | Xbox signal |
|---|---|
| A / B / X / Y with `layout:switch` | B / A / Y / X |
| A / B / X / Y with `layout:xbox` | A / B / X / Y |
| L or LB / R or RB | LB / RB |
| ZL or LT / ZR or RT | left/right trigger255 |
| PLUS or START / MINUS or BACK | Start / Back |
| LSTICK or LS / RSTICK or RS | left/right stick click |
| UP / DOWN / LEFT / RIGHT | D-pad |

Stick `[x,y]`: x positive right, y positive up/forward, range−1..1. Both sticks and all buttons can be combined. Triggers currently support released/255 via names; analog trigger values are not implemented. `tap` sends a timed full state then neutral. `stick` can also include a positional button name. If a game remaps buttons or axes, inspect its settings and verify its response separately.

```powershell
.\scripts\gamepad.cmd start
.\scripts\gamepad.cmd status
.\scripts\gamepad.cmd verify --out '<evidence>\xinput.json'
.\scripts\gamepad.cmd sdl
.\scripts\gamepad.cmd tap LT --layout xbox --ms 120
.\scripts\gamepad.cmd stick --right -0.5 0.25 --ms 300
.\scripts\gamepad.cmd neutral
.\scripts\gamepad.cmd stop
```

Startup applies a distinctive brief stick pattern, reads all four XInput slots, requires a unique match, and immediately neutralizes in `finally`. It does not trust newly occupied slots or a library user index. XInput has four slots; if no slot is available, inspect connected devices rather than removing physical controllers automatically. Start the virtual device before selecting it in a game. Reconnects may move slots, so rerun discovery and verification before resuming a test.

## JSON timelines and Python API

```json
[
  {"layout":"xbox","buttons":["A","RB"],"left":[0,0.5],"ms":150},
  {"layout":"switch","buttons":["ZL"],"right":[0.25,0],"ms":200},
  {"ms":100}
]
```

```powershell
.\scripts\gamepad.cmd validate --file '<timeline.json>'
.\scripts\gamepad.cmd run --file '<timeline.json>' --out '<evidence>\timeline.json'
```

The root is a JSON array, each step an object. Allowed fields are `layout`, `buttons`, `left`, `right`, `ms`. Unknown fields, NaN/infinite axes, out-of-range values, duration<1/>5000ms, an empty timeline, >1000steps or total>30000ms are rejected before execution. Unspecified fields reset to neutral. Adjacent steps with the same button keep it held; insert a neutral interval when a release/repress is needed. Timing uses host sleep and is not frame-synchronized or real-time guaranteed. Readback events contain elapsed host seconds; immediate per-step samples are diagnostic, while `verify` uses settled samples for assertions.

Python callers can add the skill's scripts directory to `sys.path`, import `gamepad_control`, call `configure(state_dir)` if overriding, then `request({'action':'sequence','steps':[...]})`. API and CLI use the same authenticated local named pipe and JSON byte messages. The server lasts between calls and serializes requests. Client cancellation does not interrupt an already accepted timeline. Error/completion cleanup releases all controls, with a30s per-request bound. Do not use long requests where immediate cancellation matters.

## Failures and recovery

| Symptom | Action |
|---|---|
| Missing vgamepad/pygame | Run environment setup with the intended Python; inspect `doctor` executable |
| Missing/broken bus | Check signed PnP metadata, bus state, install exit code and reboot; use official installer repair only after identifying cause |
| No virtual slot | Inspect0–3 devices and other virtual-pad tools; close unused virtual instances explicitly |
| SDL sees several identical pads | Compare before/after start, instance IDs and application selection; do not hard-code the first GUID |
| Game does not react but verify passes | Select the new device in that game's input settings; check background-input and remapping settings |
| Inputs seem held | Run neutral after the current request finishes; stop disconnects; see cancellation limitation above |
| Stale connection file | `status` reports stopped, `start` replaces stale state; `stop` is safe when already stopped |
| Server startup failure | Inspect `server.log`; it contains exceptions but no intentional secret output. Check ACL permissions, missing driver, occupied slots |
| Different working directory | Use absolute skill script paths; state and resources are resolved independently of the current directory |

`connection.json` is private and ACL-restricted. Never attach it to bug reports or copy it to another machine. Reports from doctor/status/verify omit its secret. If forced termination is necessary, inspect the server PID's executable and command line first; stop only the verified helper, then confirm the virtual device disappears. Never kill every Python process. A later start/stop can clean stale state. Driver removal is not routine error recovery.

## Registration, transfer, and removal

Use an existing Python to register the skill resources:

```powershell
python .\scripts\install_skill.py
# Optional destination root for another Codex profile:
python .\scripts\install_skill.py --skills-dir '<codex-home>\skills'
```

Default destination is `$env:CODEX_HOME\skills\windows-virtual-gamepad`, or `$env:USERPROFILE\.codex\skills\windows-virtual-gamepad` when CODEX_HOME is unset. The installer copies only SKILL.md, agents metadata, scripts, and references; it excludes `.venv`, connection files, logs, bytecode, and local evidence. It rejects an existing different skill unless `--update` is explicitly supplied. Reload skills/open a new Codex session if the current session's catalog does not refresh. Invoke `$windows-virtual-gamepad`.

For a new machine, copy those resources, register them, and run environment/doctor/driver preparation there. Do not copy the old venv or authentication state. A ZIP for transfer can be created with `install_skill.py --zip <output.zip>`; it uses the same allowlist.

To remove this skill, first stop its helper using the same state directory. Confirm `status` is stopped and no target application needs it. Remove only its registered `windows-virtual-gamepad` folder and optional custom venv/state folder after resolving their absolute paths. Removing the skill does **not** require uninstalling the shared driver. If the user requests driver removal, close all clients and use Windows Installed apps' **Nefarius Virtual Gamepad Emulation Bus Driver**, or elevated `setup.ps1 -Action uninstall-driver -InstallerPath <verified.exe>`. Reboot if requested, then run doctor to confirm absence. Do not remove physical controller drivers.

## Source and licenses

The reusable controller was extracted and adapted from the existing workspace `gamepad_control.py`/`gamepad.cmd` described in GAMEPAD_CONTROL.md. This bundle contains no game assets or app-specific adapters. The upstream [vgamepad](https://github.com/yannbouteiller/vgamepad) dependency is MIT, [ViGEmBus](https://github.com/nefarius/ViGEmBus) is BSD-3-Clause, and [pygame-ce](https://github.com/pygame-community/pygame-ce) is LGPL with additional SDL/dependency notices. Dependencies are installed from their original distributions; retain their notices. No driver binary, external library source, or Nintendo asset is bundled.
