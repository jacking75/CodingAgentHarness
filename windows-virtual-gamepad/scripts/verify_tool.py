"""Live acceptance test. Close gamepad-consuming applications before running."""
import argparse
import json
from pathlib import Path
import time
import gamepad_control as g


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    g.configure(args.state_dir)
    if g.status()['running']:
        raise RuntimeError('Test state directory already has a live server')
    before = {i: g.read_xinput(i) for i in range(4)}
    report = {'status': 'started', 'game_response_verified': False}
    try:
        first = g.start()
        second = g.start()
        assert first['pid'] == second['pid'], 'Repeated start created another server'
        report['start_idempotent'] = True
        report['xinput'] = g.request({'action': 'verify'})
        report['sdl'] = g.sdl_devices()
        timeline = [dict(layout='xbox', buttons=['A', 'RB'], left=[.5, -.5], ms=100),
                    dict(buttons=['ZL'], right=[.25, 0], ms=100), dict(ms=80)]
        report['timeline'] = g.request({'action': 'sequence', 'steps': timeline})
        assert g.status()['state'] == g.ZERO
        rejected = []
        for bad in [[], [{'ms': 5001}], [{'left': [float('nan'), 0]}],
                    [{'buttons': ['INVALID']}], [{'unknown': 1}], [{'ms': 5000}]*7]:
            try:
                g.validate_steps(bad)
            except ValueError:
                rejected.append(True)
            else:
                raise AssertionError('Invalid timeline accepted')
        report['invalid_client_requests_rejected'] = len(rejected)
        try:
            g.request({'action': 'sequence', 'steps': [{'buttons': ['INVALID']}]})
        except RuntimeError:
            pass
        else:
            raise AssertionError('Server accepted invalid timeline')
        assert g.status()['state'] == g.ZERO
        report['server_survives_invalid_request_neutral'] = True
        # Verify finally-neutral when a failure occurs after a real held input.
        local = g.VirtualPad()
        original_set = local.set
        calls = [0]
        def fail_second(step):
            calls[0] += 1
            if calls[0] == 2:
                raise RuntimeError('injected execution failure')
            original_set(step)
        local.set = fail_second
        try:
            local.sequence([{'buttons': ['A'], 'ms': 30}, {'ms': 30}])
        except RuntimeError:
            assert g.read_xinput(local.index) == g.ZERO
        else:
            raise AssertionError('Failure injection did not execute')
        report['execution_failure_restores_neutral'] = True
        del local.pad
        del local
        report['status'] = 'inputs_passed'
    except BaseException as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        try:
            g.request({'action': 'stop'})
        finally:
            deadline = time.monotonic()+5
            while g.STATE.exists() and time.monotonic() < deadline:
                time.sleep(.1)
            time.sleep(.2)
            after = {i: g.read_xinput(i) for i in range(4)}
            report['state_removed_after_stop'] = not g.STATE.exists()
            report['server_stopped'] = not g.status()['running']
            report['xinput_devices_before'] = sum(v is not None for v in before.values())
            report['xinput_devices_after'] = sum(v is not None for v in after.values())
            if report['status'] == 'inputs_passed':
                report['status'] = ('passed' if report['state_removed_after_stop'] and
                                    report['server_stopped'] and report['xinput_devices_before'] ==
                                    report['xinput_devices_after'] else 'failed')
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    assert report['state_removed_after_stop'] and report['server_stopped']
    assert report['xinput_devices_before'] == report['xinput_devices_after']
    print(json.dumps({'status': report['status'], 'checks': report['xinput']['check_count'],
                      'state_removed': report['state_removed_after_stop']}))


if __name__ == '__main__':
    main()
