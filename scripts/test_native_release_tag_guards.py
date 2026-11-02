"""Execute native release steps against a local Git remote and fake GH client."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
BASH = 'C:/Program Files/Git/usr/bin/bash.exe'
REPOS = ('bliss-guidance-lastfm', 'bliss-guidance-playcounts', 'bliss-playlist-optimizer',
         'bliss-mixer', 'bliss-learner', 'lms-better-call-bliss', 'lms-blissmixer-lab',
         'lms-guidance-library-signals', 'lms-guidance-lastfm')


def git(repo, *args):
    return subprocess.run(['git', *args], cwd=repo, check=True, text=True, capture_output=True).stdout.strip()


class ReleaseTagGuardTests(unittest.TestCase):
    def test_releases_are_immutable_and_tags_must_match_the_build_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            remote, work = root / 'remote', root / 'work'
            remote.mkdir()
            git(remote, 'init', '-q')
            git(remote, 'config', 'user.name', 'Fixture')
            git(remote, 'config', 'user.email', 'fixture@example.invalid')
            (remote / 'fixture').write_text('first')
            git(remote, 'add', 'fixture')
            git(remote, 'commit', '-qm', 'first')
            first = git(remote, 'rev-parse', 'HEAD')
            git(remote, 'tag', '-a', 'v-test', '-m', 'fixture')
            (remote / 'fixture').write_text('second')
            git(remote, 'commit', '-qam', 'second')
            second = git(remote, 'rev-parse', 'HEAD')
            subprocess.run(['git', 'clone', '-q', str(remote), str(work)], check=True)
            (work / 'release-assets').mkdir()
            (work / 'dist').mkdir()
            (work / 'release-assets' / 'fixture').write_text('asset')
            for repo in REPOS:
                with self.subTest(repo=repo):
                    (work / 'uploaded').unlink(missing_ok=True)
                    workflow = yaml.safe_load((ROOT / repo / '.github/workflows/release.yml').read_text(encoding='utf-8'))
                    job = workflow['jobs']['package-release' if repo.startswith('lms-') else 'release']
                    step = next(s for s in job['steps'] if s.get('name') == 'Publish GitHub release')
                    wrapper = "export PATH='/usr/bin':\"$PATH\"\ngh() { if [ \"$2\" = view ]; then [ \"$GH_RELEASE_EXISTS\" = yes ]; return $?; fi; if [ \"$2\" = upload ] || [ \"$2\" = create ]; then touch uploaded; return 0; fi; return 2; }\n"
                    env = dict(os.environ, TAG='v-test', VERSION='0.0.0', PRERELEASE='false',
                               GITHUB_SHA=second, RUNNER_TEMP='.', GITHUB_OUTPUT='/dev/null',
                               GITHUB_REPOSITORY='chrober/fixture', GH_RELEASE_EXISTS='yes',
                               OPTIMIZER_RELEASE='v-test', MIXER_RELEASE='v-test', LEARNER_RELEASE='v-test')
                    bad = subprocess.run([BASH, '-c', wrapper + step['run']], cwd=work, env=env, capture_output=True, text=True)
                    self.assertNotEqual(bad.returncode, 0, bad.stdout + bad.stderr)
                    self.assertIn('different source commit', bad.stderr)
                    self.assertFalse((work / 'uploaded').exists())
                    env['GITHUB_SHA'] = first
                    existing = subprocess.run([BASH, '-c', wrapper + step['run']], cwd=work, env=env, capture_output=True, text=True)
                    self.assertNotEqual(existing.returncode, 0, existing.stdout + existing.stderr)
                    self.assertIn('release already exists', existing.stderr.lower())
                    self.assertFalse((work / 'uploaded').exists())
                    env['GH_RELEASE_EXISTS'] = 'no'
                    env['GITHUB_SHA'] = second
                    bad = subprocess.run([BASH, '-c', wrapper + step['run']], cwd=work, env=env, capture_output=True, text=True)
                    self.assertNotEqual(bad.returncode, 0, bad.stdout + bad.stderr)
                    self.assertIn('different source commit', bad.stderr)
                    self.assertFalse((work / 'uploaded').exists())
                    env['GITHUB_SHA'] = first
                    existing_tag = subprocess.run([BASH, '-c', wrapper + step['run']], cwd=work, env=env, capture_output=True, text=True)
                    self.assertEqual(existing_tag.returncode, 0, existing_tag.stdout + existing_tag.stderr)
                    self.assertTrue((work / 'uploaded').exists())
                    (work / 'uploaded').unlink()
                    env['TAG'] = 'v-new'
                    good = subprocess.run([BASH, '-c', wrapper + step['run']], cwd=work, env=env, capture_output=True, text=True)
                    self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
                    self.assertTrue((work / 'uploaded').exists())
                    if not repo.startswith('lms-'):
                        notes = (work / 'release-notes.md').read_text(encoding='utf-8')
                        self.assertIn('source.tar.gz', notes)
                        self.assertIn('third-party-licenses.zip', notes)
                        self.assertIn('SOURCE_ARCHIVE_README.txt', notes)
                        self.assertIn('https://github.com/chrober/fixture/releases/download/v-new/', notes)
                    (work / 'uploaded').unlink()


if __name__ == '__main__':
    unittest.main()
