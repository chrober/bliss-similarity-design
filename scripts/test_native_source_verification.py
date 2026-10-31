"""Test source-archive provenance validation used by plugin releases."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


SCRIPTS = [Path('D:/LMS') / repo / 'scripts/verify_native_source.py' for repo in (
    'lms-better-call-bliss', 'lms-blissmixer-lab',
    'lms-guidance-lastfm', 'lms-guidance-library-signals')]


class NativeSourceVerificationTests(unittest.TestCase):
    def test_archive_requires_matching_commit_and_valid_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source'
            source.mkdir()
            sha = 'a' * 40
            (source / 'SOURCE_MANIFEST.json').write_text(json.dumps({'schema_version': 1, 'source_commit': sha, 'packages': []}))
            (source / 'Cargo.lock').write_text('fixture')
            (source / 'Cargo.toml').write_text('fixture')
            (source / '.cargo').mkdir()
            (source / '.cargo' / 'config.toml').write_text('fixture')
            (source / 'vendor').mkdir()
            archive = root / 'component-source.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                tar.add(source, arcname='source')
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            (root / (archive.name + '.sha256')).write_text(f'{digest}  {archive.name}\n')
            for script in SCRIPTS:
                def verify(commit):
                    return subprocess.run(['py', '-3.14', str(script), str(archive), commit], capture_output=True, text=True)
                self.assertEqual(verify(sha).returncode, 0, script)
                self.assertNotEqual(verify('b' * 40).returncode, 0, script)
                self.assertNotEqual(verify('').returncode, 0, script)
            archive.write_bytes(archive.read_bytes() + b'tampered')
            for script in SCRIPTS:
                self.assertNotEqual(subprocess.run(['py', '-3.14', str(script), str(archive), sha], capture_output=True).returncode, 0, script)


if __name__ == '__main__':
    unittest.main()
