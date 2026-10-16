---
name: windows-virtual-gamepad
description: Install, diagnose, and operate a persistent virtual Xbox 360 gamepad on Windows, with Switch or Xbox button names and JSON input timelines. Use for actual gamepad signals and XInput verification, not keyboard or mouse automation.
---

# Windows virtual gamepad

Use the bundled tools to maintain one virtual controller between commands. Windows x64 and CPython x64 are the supported scope. Linux/macOS and native Windows ARM64 Python are not implemented. No game, emulator, window title, GUID, user name, drive, or XInput slot is assumed.

## Discover and prepare

Resolve all script paths relative to this skill directory. Read [references/operations.md](references/operations.md) for installation, button mapping, timeline schema, recovery, and removal. Read [references/validation.md](references/validation.md) when interpreting or repeating validation.

1. Run `scripts/setup.ps1 -Action doctor` to inspect the driver, permissions, and reboot indicators without changing the machine.
2. Run `scripts/setup.ps1 -Action environment` for a private Python environment. Pass `-Python` or `-VenvPath` if discovery needs an override. This action disables the Python package's bundled driver installer.
3. If the driver is missing, fetch the official pinned installer with `setup.ps1 -Action fetch-driver -InstallerPath <file.exe>`. The script checks SHA-256 and Authenticode. Use `install-driver` in elevated PowerShell only when installing the driver is within the user's requested scope. It does not auto-elevate or reboot. Interpret driver-install exit codes separately from general reboot registry hints.
4. Run `scripts/gamepad.cmd doctor`. Check Python dependencies, driver/PnP state, XInput slots, and SDL devices. If using a custom environment, set `VGAMEPAD_PYTHON` to its Python executable. The launcher never falls back to an unverified system Python.

ViGEmBus is end of life. Use the [official release](https://github.com/nefarius/ViGEmBus/releases/tag/v1.22.0) and [upstream EOL statement](https://docs.nefarius.at/projects/ViGEm/End-of-Life/); do not substitute unsigned mirrors or disable Windows signature enforcement.

## Operate

Run `start`, then `verify` **before attaching a game**. Both startup identification and verification send real stick/button input. `verify` checks Windows XInput readback; confirm the target application's response separately. `start` returns the existing server when already running.

```powershell
& '<skill-dir>/scripts/gamepad.cmd' start
& '<skill-dir>/scripts/gamepad.cmd' verify --out '<report.json>'
& '<skill-dir>/scripts/gamepad.cmd' tap A --layout switch --ms 150
& '<skill-dir>/scripts/gamepad.cmd' stick --left 0 1 --ms 300
& '<skill-dir>/scripts/gamepad.cmd' run --file '<timeline.json>'
& '<skill-dir>/scripts/gamepad.cmd' neutral
& '<skill-dir>/scripts/gamepad.cmd' stop
```

Default labels are Switch: A→Xbox B, B→A, X→Y, Y→X, ZL→LT, R→RB. Use `--layout xbox` for Xbox face labels; aliases and axis conventions are in the reference. CLI layout applies to `tap`/`stick`; each JSON step has its own `layout` (default Switch).

Use `validate --file` to check a timeline without sending input. Each step lasts1–5000ms; a request totals at most30s. Every step is a complete state, omitted controls are neutral. Sequence completion and errors restore neutral. The server serializes requests, so `neutral`/`stop` wait behind a running sequence; they are not emergency interrupts. Ctrl+C in the client alone does not stop the server's current sequence. Chunk interactive work into short requests.

Select the discovered controller in the target application's input settings. SDL index, SDL GUID, ViGEm user number, Windows XInput slot, and the game's player index are distinct. Do not automatically rewrite a game's bindings or infer the game player index from Windows enumeration. Re-query after reconnecting devices.

## Finish and recover

Use `neutral` to release controls and `stop` to release and disconnect. They are idempotent when stopped. Confirm `status` reports `running: false`. Tests should close the target application before all-button verification. The tool does not capture windows, focus applications, or inject global keyboard/mouse events.

State defaults to `%LOCALAPPDATA%/CodexVirtualGamepad`; override with `--state-dir` on every command or `VGAMEPAD_STATE_DIR`. Do not share `connection.json`: it contains a pipe authentication secret. Commands and `--out` reports omit it. The state file ACL is restricted to the current user and SYSTEM. Never print or package its contents. For stale state or failed startup, inspect `server.log` and follow the reference; do not kill a PID without verifying its command line.

Keep installation into other Codex environments separate from driver installation: `scripts/install_skill.py` copies only the skill resources into the discovered Codex skills directory. It excludes environments, state, logs, and bytecode. See the reference for registration and removal.
