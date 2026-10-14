#!/usr/bin/env python3
"""Small JSON CLI for the installed AssetFurnace studio. No model downloads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import uuid

ROOT = Path(__file__).resolve().parents[3]
REPO = ROOT / 'runtimes/image-to-3dlab'
BASE = 'http://127.0.0.1:8777'


def request(path, data=None, content_type='application/json', timeout=10, raw=False):
    req = Request(BASE + path, data=data, headers={'Content-Type': content_type})
    with urlopen(req, timeout=timeout) as response:
        body = response.read()
    return body if raw else json.loads(body)


def save(path, value):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def receipt(path):
    value = json.loads(path.read_text())
    job_id = value.get('job_id', '')
    if value.get('skill') != 'assetfurnace' or not re.fullmatch(r'[A-Za-z0-9_-]{1,200}', job_id):
        raise ValueError('No accepted job in this receipt. Do not resubmit an unknown request.')
    return value, '/api/generate/' + quote(job_id, safe='')


def verify(glb, manifest):
    data = glb.read_bytes()
    if len(data) < 20:
        raise ValueError('GLB is truncated')
    magic, version, length, json_length, kind = struct.unpack_from('<4sIII4s', data)
    if magic != b'glTF' or version != 2 or length != len(data) or kind != b'JSON':
        raise ValueError('Invalid GLB header/length')
    model = json.loads(data[20:20 + json_length])
    if not model.get('meshes') or not model.get('images') or not model.get('textures'):
        raise ValueError('Expected a textured mesh in the GLB')
    record = json.loads(manifest.read_text())
    digest = hashlib.sha256(data).hexdigest()
    if record.get('output', {}).get('sha256') != digest:
        raise ValueError('GLB SHA-256 does not match its provenance manifest')
    if not record.get('license') or record.get('backend') != 'pixal3d':
        raise ValueError('Expected Pixal3D license/provenance record')
    return {'verified': True, 'glb': str(glb.resolve()), 'manifest': str(manifest.resolve()),
            'sha256': digest, 'bytes': len(data), 'meshes': len(model['meshes']),
            'images': len(model['images']), 'license': record['license'],
            'timings_seconds': record.get('timings_seconds')}


def preflight():
    catalog = request('/api/catalog')
    backend = next((b for b in catalog['backends'] if b['id'] == 'pixal3d'), {})
    if backend.get('state') != 'ready' or not request('/api/setup?backend=pixal3d').get('ready'):
        raise ValueError('Pixal3D is not ready. No setup/download was started.')
    if catalog.get('running_setup') or request('/api/chains').get('running'):
        raise ValueError('AssetFurnace already has an active setup/chain; wait for it.')
    try:
        with urlopen('http://127.0.0.1:7860/api/status', timeout=3) as response:
            busy = json.load(response).get('busy')
    except URLError:
        busy = False  # DevAI is often not running; AssetFurnace still works locally.
    if busy:
        raise ValueError('DevAI is busy using the shared GPU; wait for that task.')
    return backend


def generate(args):
    image = args.image.expanduser().resolve()
    if not image.is_file() or image.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}:
        raise ValueError('Supply an existing PNG/JPG/WebP/BMP file')
    if image.stat().st_size >= 49 * 1024 * 1024:
        raise ValueError('Image exceeds the upload budget (49 MiB plus multipart headers)')
    preflight()
    sys.path.insert(0, str(REPO))
    from image_to_3dlab.provenance import validate_run_policy
    profile = validate_run_policy('pixal3d', args.use_case, args.distribution, True)
    settings = {'backend': 'pixal3d', 'res': 1024, 'seed': args.seed,
                'steps': 'auto' if args.steps == 'auto' else 12,
                'output_name': args.name or image.stem}
    record = {'skill': 'assetfurnace', 'submission_state': 'submitting', 'input': str(image),
              'settings': settings, 'intent': {'use_case': args.use_case,
                  'distribution': args.distribution, 'allow_conditional': True},
              'license_conditions': list(profile.conditions)}
    target = args.receipt.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x') as handle:  # An existing receipt must never cause a second job.
        json.dump(record, handle, ensure_ascii=False, indent=2)
    boundary = 'af-' + uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="settings"\r\n\r\n'
            + json.dumps(settings) + f'\r\n--{boundary}\r\nContent-Disposition: form-data; '
            + f'name="image"; filename="input{image.suffix.lower()}"\r\n'
            + 'Content-Type: application/octet-stream\r\n\r\n').encode()
    body += image.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
    try:
        accepted = request('/api/generate', body, f'multipart/form-data; boundary={boundary}', 300)
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,200}', accepted.get('job_id', '')):
            raise ValueError('Server did not return a valid job ID')
    except Exception as exc:
        # An interrupted upload/response may already have created a live server job.
        record.update(submission_state='unknown', error=str(exc))
        save(target, record)
        raise RuntimeError(f'Submission not confirmed. Inspect {target}; do not automatically retry.') from exc
    record.update(accepted, submission_state='accepted')
    save(target, record)
    return {'receipt': str(target), **accepted}


def fetch(args):
    record, route = receipt(args.receipt)
    state = request(route + '/status')
    if state['status'] != 'done':
        raise ValueError(f'Job is {state["status"]}; no completed artifact yet')
    target = args.glb.expanduser().resolve()
    if target.suffix.lower() != '.glb':
        raise ValueError('Destination must end in .glb')
    manifest = target.with_suffix('.json')
    if target.exists() or manifest.exists():
        raise ValueError('Destination already exists; choose a new path')
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive partial files preserve existing files, including on interrupted retries.
    partial = target.with_name(target.name + '.part')
    partial_manifest = manifest.with_name(manifest.name + '.part')
    with partial.open('xb') as handle:
        handle.write(request(route + '/result.glb', timeout=60, raw=True))
    with partial_manifest.open('xb') as handle:
        handle.write(request(route + '/manifest.json', timeout=30, raw=True))
    verify(partial, partial_manifest)
    partial.rename(target)
    partial_manifest.rename(manifest)
    result = verify(target, manifest)
    record['local_result'] = result
    save(args.receipt, record)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('status', help='Read live catalog; does not start services')
    commands.add_parser('start', help='Start the local studio without opening a browser')
    p = commands.add_parser('generate', help='Submit one Pixal3D job and save its receipt')
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--name')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--steps', choices=['auto', '12'], default='auto')
    p.add_argument('--use-case', choices=['showcase', 'game'], default='showcase')
    p.add_argument('--distribution', choices=['private', 'public', 'worldwide'], default='private')
    for command in ['job', 'wait', 'cancel', 'fetch']:
        p = commands.add_parser(command)
        p.add_argument('--receipt', type=Path, required=True)
        if command == 'wait':
            p.add_argument('--timeout', type=int, choices=range(1, 56), default=45, metavar='1..55')
        if command == 'fetch':
            p.add_argument('--glb', type=Path, required=True)
    p = commands.add_parser('verify')
    p.add_argument('--glb', type=Path, required=True)
    p.add_argument('--manifest', type=Path)
    args = parser.parse_args(argv)
    if args.action == 'start':
        result = subprocess.run(['zsh', str(ROOT / 'AssetFurnace_시작.command'), '--no-browser'],
                                capture_output=True, text=True, check=True)
        value = {'started': True, 'message': result.stdout.strip(), 'url': BASE}
    elif args.action == 'status':
        catalog = request('/api/catalog')
        value = {'url': BASE, 'running_setup': catalog.get('running_setup'),
                 'backends': [{k: b.get(k) for k in ('id', 'state', 'supported_here')}
                              for b in catalog['backends']],
                 'running_chain': request('/api/chains').get('running')}
    elif args.action == 'generate':
        value = generate(args)
    elif args.action == 'verify':
        value = verify(args.glb, args.manifest or args.glb.with_suffix('.json'))
    elif args.action == 'fetch':
        value = fetch(args)
    else:
        record, route = receipt(args.receipt)
        if args.action == 'cancel':
            value = request(route + '/cancel', b'{}')
        else:
            deadline = time.monotonic() + (args.timeout if args.action == 'wait' else 0)
            while True:
                value = request(route + '/status')
                if value['status'] in {'done', 'error', 'cancelled'} or time.monotonic() >= deadline:
                    break
                time.sleep(min(5, max(0, deadline - time.monotonic())))
            value.update(job_id=record['job_id'], receipt=str(args.receipt.resolve()))
    print(json.dumps(value, ensure_ascii=False, indent=2))
    if isinstance(value, dict) and value.get('status') in {'error', 'cancelled'}:
        return 2
    if args.action == 'wait' and value.get('status') != 'done':
        return 3  # Pending is not success and must not trigger resubmission.
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except HTTPError as exc:
        print(json.dumps({'error': 'HTTP error', 'status': exc.code,
                          'detail': exc.read().decode(errors='replace')[:2000]}), file=sys.stderr)
        raise SystemExit(1)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
