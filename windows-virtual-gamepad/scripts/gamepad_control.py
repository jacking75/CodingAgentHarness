"""Persistent Windows Xbox 360 virtual pad, extracted from the working gamepad tool.

No application configuration is changed. State is per user or --state-dir.
"""
from __future__ import annotations

import argparse
import ctypes as ct
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import secrets
import subprocess
import sys
import time
from multiprocessing.connection import Client, Listener

STATE = None
PIPE = None
XBOX = {'A': 0x1000, 'B': 0x2000, 'X': 0x4000, 'Y': 0x8000,
        'LB': 0x100, 'RB': 0x200, 'START': 0x10, 'BACK': 0x20,
        'LS': 0x40, 'RS': 0x80, 'UP': 1, 'DOWN': 2, 'LEFT': 4, 'RIGHT': 8}
SWITCH = dict(XBOX, A=XBOX['B'], B=XBOX['A'], X=XBOX['Y'], Y=XBOX['X'])
ALIASES = {'L': 'LB', 'R': 'RB', 'PLUS': 'START', 'MINUS': 'BACK',
           'LSTICK': 'LS', 'RSTICK': 'RS', 'ZL': 'LT', 'ZR': 'RT'}
ZERO = dict(buttons=0, lt=0, rt=0, lx=0, ly=0, rx=0, ry=0)


def configure(state_dir=None):
    global STATE, PIPE
    if os.name != 'nt':
        raise RuntimeError('This skill supports Windows only; Linux/macOS are not implemented')
    folder = state_dir or os.environ.get('VGAMEPAD_STATE_DIR')
    if folder is None:
        folder = Path(os.environ.get('LOCALAPPDATA', Path.home()/'AppData/Local'))/'CodexVirtualGamepad'
    STATE = Path(folder).expanduser().resolve()/'connection.json'
    PIPE = r'\\.\pipe\codex-virtual-pad-' + hashlib.sha256(
        str(STATE).casefold().encode()).hexdigest()[:20]


class PadState(ct.Structure):
    _fields_ = [('buttons', ct.c_ushort), ('lt', ct.c_ubyte), ('rt', ct.c_ubyte),
                ('lx', ct.c_short), ('ly', ct.c_short), ('rx', ct.c_short), ('ry', ct.c_short)]


class InputState(ct.Structure):
    _fields_ = [('packet', ct.c_uint32), ('pad', PadState)]


def read_xinput(index):
    state = InputState()
    dll = ct.WinDLL('xinput1_4.dll')
    dll.XInputGetState.argtypes = [ct.c_uint32, ct.POINTER(InputState)]
    result = dll.XInputGetState(index, ct.byref(state))
    if result == 1167:
        return None
    if result:
        raise OSError(result, 'XInputGetState')
    return {name: getattr(state.pad, name) for name, _ in PadState._fields_}


def validate(step):
    if not isinstance(step, dict):
        raise ValueError('Each timeline step must be an object')
    if set(step)-{'buttons', 'layout', 'left', 'right', 'ms'}:
        raise ValueError('Unknown timeline field')
    layout = step.get('layout', 'switch')
    if layout not in ('switch', 'xbox'):
        raise ValueError('layout must be switch or xbox')
    raw = step.get('buttons', [])
    if not isinstance(raw, list) or any(not isinstance(x, str) for x in raw):
        raise ValueError('buttons must be an array of names')
    buttons = [ALIASES.get(x.upper(), x.upper()) for x in raw]
    if any(x not in XBOX and x not in ('LT', 'RT') for x in buttons):
        raise ValueError('Unknown button')
    vectors = {}
    for key in ('left', 'right'):
        vector = step.get(key, [0, 0])
        if not isinstance(vector, (list, tuple)) or len(vector) != 2:
            raise ValueError('Sticks require [x,y]')
        if any(isinstance(x, bool) or not isinstance(x, (int, float)) or
               not math.isfinite(x) or not -1 <= x <= 1 for x in vector):
            raise ValueError('Stick values must be finite numbers in -1..1')
        vectors[key] = vector
    ms = step.get('ms', 150)
    if isinstance(ms, bool) or not isinstance(ms, (int, float)) or not math.isfinite(ms) or not 1 <= ms <= 5000:
        raise ValueError('Duration must be 1..5000 ms')
    return dict(buttons=buttons, layout=layout, **vectors, ms=ms)


def validate_steps(steps):
    if not isinstance(steps, list) or not 1 <= len(steps) <= 1000:
        raise ValueError('Timeline must contain 1..1000 steps')
    steps = [validate(x) for x in steps]
    if sum(x['ms'] for x in steps) > 30000:
        raise ValueError('Timeline must not exceed 30000 ms')
    return steps


class VirtualPad:
    def __init__(self):
        import vgamepad as vg
        from vgamepad.win import vigem_client as client
        self.pad = vg.VX360Gamepad()
        # ViGEm user index and SDL index need not equal Windows XInput index.
        expected = dict(ZERO, lx=9876, ly=-12345, rx=-15678, ry=19012)
        identified = False
        try:
            # Wait for Windows enumeration before sending the probe. An update
            # immediately after target_add may be lost on a second controller.
            user_index = ct.c_ulong()
            deadline = time.monotonic()+5
            while client.vigem_target_x360_get_user_index(
                    self.pad._busp, self.pad._devicep, ct.byref(user_index)) != 0x20000000:
                if time.monotonic() > deadline:
                    raise RuntimeError('ViGEm target did not finish enumeration')
                time.sleep(.05)
            self.pad.left_joystick(expected['lx'], expected['ly'])
            self.pad.right_joystick(expected['rx'], expected['ry'])
            self.pad.update()
            deadline = time.monotonic()+5
            while True:
                matches = [i for i in range(4) if read_xinput(i) == expected]
                if len(matches) == 1:
                    self.index = matches[0]
                    identified = True
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError('No unique virtual XInput slot; inspect occupied slots and driver, then retry')
                time.sleep(.05)
        finally:
            self.neutral()
            if not identified:
                del self.pad

    def neutral(self):
        self.pad.reset()
        self.pad.update()

    def set(self, step):
        step = validate(step)
        self.pad.reset()
        mapping = SWITCH if step['layout'] == 'switch' else XBOX
        for button in step['buttons']:
            if button == 'LT':
                self.pad.left_trigger(255)
            elif button == 'RT':
                self.pad.right_trigger(255)
            else:
                self.pad.press_button(mapping[button])
        self.pad.left_joystick_float(*step['left'])
        self.pad.right_joystick_float(*step['right'])
        self.pad.update()

    def sequence(self, steps):
        steps = validate_steps(steps)
        started = time.monotonic()
        events = []
        try:
            for step in steps:
                self.set(step)
                events.append({'seconds': time.monotonic()-started,
                               'expected': expected_state(step), 'actual': read_xinput(self.index)})
                time.sleep(step['ms']/1000)
        finally:
            self.neutral()
        return {'sent': steps, 'readback': events, 'released': True,
                'elapsed_seconds': time.monotonic()-started, 'xinput_index': self.index}

    def verify(self):
        cases = []
        for layout in ('switch', 'xbox'):
            for button in [*XBOX, 'LT', 'RT']:
                cases.append({'layout': layout, 'buttons': [button]})
        for stick in ('left', 'right'):
            for axis in (0, 1):
                for value in (-.75, .75):
                    vector = [0, 0]
                    vector[axis] = value
                    cases.append({stick: vector})
        cases.append({'buttons': ['A', 'ZL', 'R'], 'left': [.5, -.5], 'right': [-.25, .25]})
        results = []
        try:
            for step in cases:
                self.set(step)
                time.sleep(.04)
                actual, expected = read_xinput(self.index), expected_state(step)
                if actual != expected:
                    raise AssertionError(f'XInput mismatch for {step}: {actual} != {expected}')
                results.append({'input': step, 'expected': expected, 'actual': actual})
        finally:
            self.neutral()
        time.sleep(.04)
        neutral = read_xinput(self.index)
        if neutral != ZERO:
            raise AssertionError(f'Neutral readback failed: {neutral}')
        return {'verified_via': 'Windows XInputGetState', 'checks': results,
                'check_count': len(results), 'neutral_after_test': True,
                'neutral': neutral, 'xinput_index': self.index, 'game_response_verified': False}


def expected_state(step):
    step = validate(step)
    state = dict(ZERO)
    mapping = SWITCH if step['layout'] == 'switch' else XBOX
    for button in step['buttons']:
        if button in ('LT', 'RT'):
            state[button.lower()] = 255
        else:
            state['buttons'] |= mapping[button]
    for prefix, key in [('l', 'left'), ('r', 'right')]:
        for axis, value in zip(('x', 'y'), step[key]):
            # vgamepad uses round(), not asymmetric signed-axis scaling.
            state[prefix+axis] = round(value*32767)
    return state


def request(message):
    if STATE is None:
        configure()
    state = json.loads(STATE.read_text(encoding='utf-8'))
    if state['pipe'] != PIPE:
        raise RuntimeError('State belongs to another state directory; restart the corresponding instance')
    with Client(PIPE, family='AF_PIPE', authkey=bytes.fromhex(state['authkey'])) as conn:
        conn.send_bytes(json.dumps(message, allow_nan=False).encode())
        if not conn.poll(40):
            raise TimeoutError('Gamepad request timed out; inspect server.log')
        answer = json.loads(conn.recv_bytes(1024*1024))
    if 'error' in answer:
        raise RuntimeError(answer['error'])
    return answer


def status():
    try:
        return request({'action': 'status'})
    except (FileNotFoundError, ConnectionRefusedError, EOFError):
        return {'running': False}
    except OSError as error:
        if getattr(error, 'winerror', None) in (2, 109, 231, 233):
            return {'running': False}
        raise


def protect_file(path):
    # Only this user's SID and SYSTEM can read the local pipe authentication key.
    output = subprocess.check_output(['whoami', '/user', '/fo', 'csv', '/nh'], text=True)
    import csv
    sid = next(csv.reader([output.strip()]))[1]
    subprocess.run(['icacls', str(path), '/inheritance:r', '/grant:r',
                    '*'+sid+':(F)', '*S-1-5-18:(F)'], check=True, capture_output=True)


def serve():
    kernel = ct.WinDLL('kernel32', use_last_error=True)
    kernel.CreateMutexW.argtypes = [ct.c_void_p, ct.c_bool, ct.c_wchar_p]
    kernel.CreateMutexW.restype = ct.c_void_p
    kernel.CloseHandle.argtypes = [ct.c_void_p]
    lock = kernel.CreateMutexW(None, False, 'Local\\'+PIPE.rsplit('\\', 1)[-1])
    if not lock:
        raise ct.WinError(ct.get_last_error())
    if ct.get_last_error() == 183:
        kernel.CloseHandle(lock)
        raise RuntimeError('A server for this state directory is already starting or running')
    pad, listener = None, None
    try:
        pad = VirtualPad()
        auth = secrets.token_bytes(32)
        listener = Listener(PIPE, family='AF_PIPE', authkey=auth)
        STATE.parent.mkdir(parents=True, exist_ok=True)
        state = {'pid': os.getpid(), 'pipe': PIPE, 'authkey': auth.hex(),
                 'xinput_index': pad.index}
        temporary = STATE.with_suffix('.tmp')
        temporary.write_text(json.dumps(state), encoding='utf-8')
        protect_file(temporary)
        temporary.replace(STATE)
        running = True
        while running:
            try:
                connection = listener.accept()
            except (OSError, EOFError):
                continue
            with connection as conn:
                try:
                    if not conn.poll(5):
                        continue
                    message = json.loads(conn.recv_bytes(1024*1024))
                    action = message['action']
                    if action == 'status':
                        answer = {'running': True, 'pid': os.getpid(), 'xinput_index': pad.index,
                                  'state': read_xinput(pad.index), 'backend': 'ViGEmBus/vgamepad'}
                    elif action == 'sequence':
                        answer = pad.sequence(message['steps'])
                    elif action == 'verify':
                        answer = pad.verify()
                    elif action in ('neutral', 'stop'):
                        pad.neutral()
                        answer = {'released': True, 'stopped': action == 'stop'}
                        running = action != 'stop'
                    else:
                        raise ValueError('Unknown action')
                except Exception as error:
                    pad.neutral()
                    answer = {'error': f'{type(error).__name__}: {error}'}
                try:
                    conn.send_bytes(json.dumps(answer).encode())
                except (OSError, EOFError):
                    pass
    finally:
        if pad is not None:
            pad.neutral()
        if listener is not None:
            listener.close()
        if STATE.exists() and json.loads(STATE.read_text(encoding='utf-8')).get('pid') == os.getpid():
            STATE.unlink()
        kernel.CloseHandle(lock)


def start():
    current = status()
    if current['running']:
        return current
    STATE.parent.mkdir(parents=True, exist_ok=True)
    log = STATE.with_name('server.log')
    with log.open('w', encoding='utf-8') as output:
        process = subprocess.Popen([sys.executable, '-E', str(Path(__file__).resolve()), 'serve',
                                    '--state-dir', str(STATE.parent)],
                                   stdin=subprocess.DEVNULL, stdout=output, stderr=output,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
    deadline = time.monotonic()+12
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f'Server exited; inspect {log}')
        current = status()
        if current['running']:
            return current
        time.sleep(.1)
    raise TimeoutError(f'Server startup timed out; inspect {log}')


def sdl_devices():
    # No video initialization, window, or global input injection.
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
    try:
        import pygame
    except ImportError:
        return {'available': False, 'reason': 'Install optional pygame-ce for SDL enumeration'}
    pygame.joystick.init()
    try:
        devices = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            devices.append({'index': i, 'name': joy.get_name(), 'guid': joy.get_guid(),
                            'instance_id': joy.get_instance_id(), 'buttons': joy.get_numbuttons(),
                            'axes': joy.get_numaxes()})
        return {'available': True, 'sdl_version': pygame.get_sdl_version(), 'devices': devices}
    finally:
        pygame.joystick.quit()


def doctor():
    script = Path(__file__).with_name('diagnose.ps1')
    result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                             '-File', str(script)], capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Windows diagnostics failed; run diagnose.ps1 directly')
    packages = {}
    for name in ('vgamepad', 'pygame-ce'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    return {'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
            'packages': packages, 'windows': json.loads(result.stdout),
            'xinput_devices': {i: s for i in range(4) if (s := read_xinput(i)) is not None},
            'sdl': sdl_devices(), 'server': status()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['doctor', 'start', 'serve', 'status', 'tap', 'stick',
                                           'run', 'validate', 'verify', 'sdl', 'neutral', 'stop'])
    parser.add_argument('button', nargs='?')
    parser.add_argument('--state-dir', type=Path)
    parser.add_argument('--layout', choices=['switch', 'xbox'], default='switch')
    parser.add_argument('--ms', type=float, default=150)
    parser.add_argument('--left', nargs=2, type=float, default=[0, 0])
    parser.add_argument('--right', nargs=2, type=float, default=[0, 0])
    parser.add_argument('--file', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    configure(args.state_dir)
    if args.action == 'serve':
        serve()
        return
    if args.action == 'doctor':
        answer = doctor()
    elif args.action == 'sdl':
        answer = sdl_devices()
    elif args.action == 'start':
        answer = start()
    elif args.action == 'status':
        answer = status()
    elif args.action in ('neutral', 'stop') and not status()['running']:
        answer = {'running': False, 'released': True, 'stopped': args.action == 'stop'}
        if args.action == 'stop' and STATE.exists():
            STATE.unlink()
    elif args.action in ('tap', 'stick'):
        if args.action == 'tap' and not args.button:
            parser.error('tap requires a button')
        step = validate({'layout': args.layout, 'buttons': [args.button] if args.button else [],
                         'left': args.left, 'right': args.right, 'ms': args.ms})
        answer = request({'action': 'sequence', 'steps': [step]})
    elif args.action in ('run', 'validate'):
        if not args.file:
            parser.error('run/validate requires --file')
        steps = validate_steps(json.loads(args.file.read_text(encoding='utf-8-sig')))
        answer = ({'valid': True, 'steps': len(steps), 'duration_ms': sum(s['ms'] for s in steps)}
                  if args.action == 'validate' else request({'action': 'sequence', 'steps': steps}))
    else:
        answer = request({'action': args.action})
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(answer, indent=2), encoding='utf-8')
    print(json.dumps(answer, ensure_ascii=True, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (Exception, KeyboardInterrupt) as error:
        print(json.dumps({'error': f'{type(error).__name__}: {error}'}, ensure_ascii=True), file=sys.stderr)
        sys.exit(1)
