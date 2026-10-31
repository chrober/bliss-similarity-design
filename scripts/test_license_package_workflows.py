"""Exercise plugin workflow packaging locally with dummy native executables.

Requires PyYAML, Git for Windows' bash/unzip and 7-Zip. This is an audit
smoke test, not a test of genuine native builds or Corresponding Source.
"""
import os
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[2]
BASH = Path('C:/Program Files/Git/usr/bin/bash.exe')
SEVENZIP = Path('C:/Program Files/7-Zip/7z.exe')
CONFIG = (
    ('lms-better-call-bliss', 'BetterCallBliss', 'bliss-playlist-optimizer', 'optimizer'),
    ('lms-blissmixer-lab', 'BlissMixerLab', 'bliss-mixer-lab', 'lab'),
    ('lms-guidance-library-signals', 'LibrarySignals', 'bliss-guidance-library-signals', 'library'),
    ('lms-guidance-lastfm', 'LastFmGuidance', 'bliss-guidance-lastfm', 'lastfm'),
)


class WorkflowPackageTests(unittest.TestCase):
    def test_platform_packages_include_licenses_and_selected_native_release(self):
        for repo, plugin, binary, kind in CONFIG:
            with self.subTest(repo=repo), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = ROOT / repo
                workflow = yaml.safe_load((source / '.github/workflows/release.yml').read_text(encoding='utf-8'))
                steps = workflow['jobs']['package-release']['steps']
                step = next(s for s in steps if s.get('id') == 'package')
                self.assertIn('RELEASE_VERSION', step['env'])
                self.assertIn('RELEASE_TAG', step['env'])
                script = step['run'].replace('${{ steps.meta.outputs.version }}', '9.9.9')
                shutil.copy2(source / 'LICENSE', root / 'LICENSE')
                shutil.copy2(source / 'THIRD_PARTY_NOTICES.md', root / 'THIRD_PARTY_NOTICES.md')
                (root / plugin).mkdir()
                (root / plugin / 'install.xml').write_text('<extension><version>9.9.9</version></extension>')
                subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
                subprocess.run(['git', 'config', 'user.name', 'Fixture'], cwd=root, check=True)
                subprocess.run(['git', 'config', 'user.email', 'fixture@example.invalid'], cwd=root, check=True)
                subprocess.run(['git', 'add', 'LICENSE', 'THIRD_PARTY_NOTICES.md', plugin + '/install.xml'], cwd=root, check=True)
                subprocess.run(['git', 'commit', '-qm', 'fixture'], cwd=root, check=True)
                commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
                if kind in ('optimizer', 'lab'):
                    for platform in ('aarch64-linux', 'armhf-linux', 'x86_64-linux', 'mac', 'windows'):
                        dest = root / plugin / 'Bin' / platform
                        dest.mkdir(parents=True)
                        (dest / (binary + ('.exe' if platform == 'windows' else ''))).write_bytes(b'dummy')
                else:
                    dest = root / 'native-assets'
                    dest.mkdir()
                    for platform in ('aarch64-linux', 'armhf-linux', 'x86_64-linux', 'mac', 'windows.exe'):
                        (dest / (binary + '-' + platform)).write_bytes(b'dummy')
                env = dict(os.environ, GITHUB_SHA=commit, GITHUB_OUTPUT='/dev/null', RELEASE_VERSION='9.9.9', RELEASE_TAG='v-test-plugin', OPTIMIZER_RELEASE='v-test-override',
                           MIXER_RELEASE='v-test-override', LEARNER_RELEASE='v-learner-override',
                           NATIVE_RELEASE='v-test-override', LINUX_ASSET='linux.zip',
                           MAC_ASSET='mac.zip', WINDOWS_ASSET='windows.zip')
                wrapper = "export PATH='/usr/bin':\"$PATH\"\nzip() { '/c/Program Files/7-Zip/7z.exe' a -tzip \"$3\" \"$4\" >/dev/null; }\n"
                result = subprocess.run([str(BASH), '-c', wrapper + script], cwd=root, env=env,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for platform in ('linux', 'mac', 'windows'):
                    filename = (root / f'{platform}.zip' if kind in ('optimizer', 'lab') else
                                root / f'dist/lms-guidance-{"library-signals" if kind == "library" else "lastfm"}-{platform}-9.9.9.zip')
                    if kind in ('optimizer', 'lab'):
                        filename = root / 'dist' / f'{platform}.zip'
                    with zipfile.ZipFile(filename) as archive:
                        self.assertIsNone(archive.testzip())
                        self.assertEqual(archive.read(f'{plugin}/LICENSE'), (root / 'LICENSE').read_bytes())
                        self.assertEqual(archive.read(f'{plugin}/THIRD_PARTY_NOTICES.md'),
                                         (root / 'THIRD_PARTY_NOTICES.md').read_bytes())
                        provenance = archive.read(f'{plugin}/SOURCE.md').decode()
                        self.assertEqual(provenance, archive.read(f'{plugin}/Bin/SOURCE.md').decode())
                        self.assertIn(commit, provenance)
                        self.assertIn('v-test-override', provenance)
                        self.assertIn(f'/v-test-plugin/{repo}-source-9.9.9.zip', provenance)
                        native_source = {'optimizer': 'bliss-playlist-optimizer', 'lab': 'bliss-mixer',
                                         'library': 'bliss-guidance-library-signals', 'lastfm': 'bliss-guidance-lastfm'}[kind]
                        self.assertIn(f'/v-test-override/{native_source}-source.tar.gz', provenance)
                        if kind == 'lab':
                            self.assertIn('v-learner-override', provenance)
                            self.assertIn('/v-learner-override/bliss-learner-source.tar.gz', provenance)
                        names = archive.namelist()
                        forbidden = {'linux': ('mac', 'windows'),
                                     'mac': ('aarch64-linux', 'armhf-linux', 'x86_64-linux', 'windows'),
                                     'windows': ('aarch64-linux', 'armhf-linux', 'x86_64-linux', 'mac')}[platform]
                        for wrong in forbidden:
                            self.assertFalse(any(f'{plugin}/Bin/{wrong}/' in name for name in names))
                source_zip = root / 'dist' / f'{repo}-source-9.9.9.zip'
                with zipfile.ZipFile(source_zip) as archive:
                    self.assertIn(f'{plugin}/install.xml', archive.namelist())
                    self.assertIsNone(archive.testzip())
                for algorithm in ('sha1', 'sha256'):
                    expected = getattr(hashlib, algorithm)(source_zip.read_bytes()).hexdigest()
                    self.assertEqual((source_zip.parent / (source_zip.name + '.' + algorithm)).read_text().split()[0], expected)


if __name__ == '__main__':
    unittest.main()
