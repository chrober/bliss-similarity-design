#!/usr/bin/env python3
"""Check dependency notice coverage in a generated license bundle.

This is an inventory check, not a determination of legal compliance.
"""
import json
from pathlib import Path
import sys
import zipfile


SUPPLEMENTS = {
    ('rsqlite-vfs', '0.1.1'): 'rsqlite-vfs-0.1.1-LICENSE',
    ('winapi-i686-pc-windows-gnu', '0.4.0'): 'winapi-windows-gnu-0.4.0-LICENSE',
    ('winapi-x86_64-pc-windows-gnu', '0.4.0'): 'winapi-windows-gnu-0.4.0-LICENSE',
    ('uuid-simd', '0.8.0'): 'nugine-simd-0.8.0-LICENSE',
    ('vsimd', '0.8.0'): 'nugine-simd-0.8.0-LICENSE',
    ('alloc-stdlib', '0.2.2'): 'alloc-stdlib-0.2.2-LICENSE',
    ('convert_case', '0.4.0'): 'convert_case-0.4.0-LICENSE',
    ('fuchsia-zircon-sys', '0.3.3'): 'fuchsia-zircon-sys-0.3.3-LICENSE',
    ('fxhash', '0.2.1'): 'fxhash-0.2.1-LICENSE',
    ('kernel32-sys', '0.2.2'): 'winapi-legacy-LICENSE',
    ('ws2_32-sys', '0.2.1'): 'winapi-legacy-LICENSE',
    ('winapi-build', '0.1.1'): 'winapi-legacy-LICENSE',
    ('stdweb-derive', '0.5.3'): 'stdweb-internal-LICENSE',
    ('stdweb-internal-macros', '0.2.9'): 'stdweb-internal-LICENSE',
    ('stdweb-internal-runtime', '0.1.5'): 'stdweb-internal-LICENSE',
    ('valuable', '0.1.1'): 'valuable-0.1.1-LICENSE',
}


def audit(path):
    with zipfile.ZipFile(path) as bundle:
        members = set(bundle.namelist())
        manifest = json.loads(bundle.read('SOURCE_MANIFEST.json'))
        missing = []
        for package in manifest['packages']:
            if not package['source']:
                continue
            notice_paths = package['notice_files']
            if notice_paths:
                missing.extend(f"{package['name']}: {p}" for p in notice_paths if p not in members)
                continue
            key = package['name'], package['version']
            supplement = SUPPLEMENTS.get(key)
            # Older generated inventories did not index this embedded license.
            if key == ('r-efi', '5.3.0') and 'vendor/r-efi-5.3.0/AUTHORS' in members:
                continue
            if not supplement or 'third-party-licenses/' + supplement not in members:
                missing.append(f'{key[0]} {key[1]}: no inventoried or reviewed supplemental notice')
        if missing:
            raise ValueError('\n'.join(missing))
        print(f"{path}: {len(manifest['packages'])} packages inventoried; notice coverage verified")


if __name__ == '__main__':
    for argument in sys.argv[1:]:
        audit(Path(argument))
