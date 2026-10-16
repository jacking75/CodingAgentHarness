# Validation and limits

The acceptance test creates controllers and presses all controls. Close games or other consumers before running it. Run from an arbitrary working directory with absolute paths to prove that project-relative paths are not required:

```powershell
& '<venv>\Scripts\python.exe' -E '<skill>\scripts\verify_tool.py' --state-dir '<isolated-state-directory>' --out '<report.json>'
```

It checks repeated start returns the same server, both face-button layouts and all14digital buttons+2triggers, both sticks at±0.75 on every axis, combined input, neutral, a timed sequence, six invalid timeline categories, server survival after an invalid request, and neutral restoration after an injected failure while a real button was held. Finally it checks stop, state-file removal, and the original count of connected XInput devices. The test uses a second temporary controller only for failure injection; it needs an additional free XInput slot. Other devices must remain unchanged during the test.

`doctor` and `verify_tool` output omit authentication keys. Do not include the state directory in transferred evidence. The existence of a driver SYS file is not proof of functioning installation; prefer PnP/service state and live readback. XInput passing is not game response passing. Timelines are wall-clock requests, not exact frame control.

On2026-10-16, the bundled test passed41XInput cases on Windows x64 with a newly created Python3.12.9 environment, vgamepad0.1.3 and pygame-ce2.5.6. It ran from a working directory outside the source project with a state path containing spaces and non-ASCII text. Repeated start, invalid requests, execution failure cleanup, and stop/state removal passed. Official driver1.22.0 package SHA-256 and Authenticode were also checked. Creating a second controller initially exposed an enumeration timing issue; startup now waits for target enumeration before its distinctive probe, while still identifying the actual Windows slot by readback.

A new Python environment tests dependency/setup isolation on the same Windows host; it does not test a different machine or the missing-driver/reboot/uninstall paths. Those paths were documented but not executed against this working shared driver. No game response was tested with the extracted tool. Follow setup/verification on another host before claiming portability there. Machine-specific absolute paths and authentication files are deliberately excluded from this bundle.
