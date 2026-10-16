"""Register or zip the portable resources only; never copies runtime state."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def resources():
    yield ROOT/'SKILL.md'
    for folder, extensions in [('agents', {'.yaml'}), ('scripts', {'.py', '.ps1', '.cmd', '.txt'}),
                                ('references', {'.md', '.json'})]:
        yield from sorted(p for p in (ROOT/folder).rglob('*')
                          if p.is_file() and p.suffix in extensions and '__pycache__' not in p.parts)


def manifest(root):
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256((root/p.relative_to(ROOT)).read_bytes()).hexdigest()
            for p in resources()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skills-dir', type=Path)
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--zip', type=Path)
    args = parser.parse_args()
    if args.zip:
        args.zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.zip, 'x', zipfile.ZIP_DEFLATED) as archive:
            for source in resources():
                archive.write(source, ROOT.name+'/'+source.relative_to(ROOT).as_posix())
        print(json.dumps({'zip': str(args.zip.resolve()), 'resource_files': len(list(resources()))}))
        return
    codex = Path(os.environ.get('CODEX_HOME', Path.home()/'.codex'))
    target = (args.skills_dir or codex/'skills')/ROOT.name
    target = target.resolve()
    if target == ROOT:
        raise RuntimeError('Source and destination are the same')
    if target.exists() and not args.update:
        if all((target/p.relative_to(ROOT)).is_file() for p in resources()) and manifest(target) == manifest(ROOT):
            print(json.dumps({'installed': str(target), 'already_identical': True}))
            return
        raise RuntimeError('Different skill already exists; inspect it before using --update')
    for source in resources():
        dest = target/source.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    if manifest(target) != manifest(ROOT):
        raise RuntimeError('Installed resource hash mismatch')
    print(json.dumps({'installed': str(target), 'resource_files': len(list(resources())), 'sha256_verified': True}))


if __name__ == '__main__':
    main()
