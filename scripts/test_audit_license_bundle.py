import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


spec = importlib.util.spec_from_file_location('audit_license_bundle', Path(__file__).with_name('audit_license_bundle.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def bundle(self, path, package, files, *, short=False):
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('SOURCE_MANIFEST.json', json.dumps({'packages': [package]}))
            for name in files:
                z.writestr(name, '../LICENSE-MIT' if short and name.startswith('vendor/') else 'license terms ' * 8)

    def test_notice_required_and_supplement_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'licenses.zip'
            package = {'name': 'uuid-simd', 'version': '0.8.0', 'source': 'registry', 'notice_files': []}
            self.bundle(path, package, [])
            with self.assertRaises(ValueError):
                audit.audit(path)
            self.bundle(path, package, ['third-party-licenses/nugine-simd-0.8.0-LICENSE'])
            audit.audit(path)

    def test_inventoried_files_must_be_in_bundle(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'licenses.zip'
            package = {'name': 'example', 'version': '1', 'source': 'registry',
                       'notice_files': ['vendor/example/LICENSE']}
            self.bundle(path, package, [])
            with self.assertRaises(ValueError):
                audit.audit(path)
            self.bundle(path, package, ['vendor/example/LICENSE'])
            audit.audit(path)

    def test_path_only_license_is_not_a_complete_notice(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'licenses.zip'
            package = {'name': 'actix-macros', 'version': '0.1.3', 'source': 'registry',
                       'notice_files': ['vendor/actix-macros/LICENSE-MIT']}
            self.bundle(path, package, ['vendor/actix-macros/LICENSE-MIT'], short=True)
            with self.assertRaises(ValueError):
                audit.audit(path)
            with zipfile.ZipFile(path, 'a') as z:
                z.writestr('third-party-licenses/actix-macros-0.1.3-LICENSE-MIT', '../LICENSE-MIT')
            with self.assertRaises(ValueError):
                audit.audit(path)
            self.bundle(path, package, ['vendor/actix-macros/LICENSE-MIT',
                                        'third-party-licenses/actix-macros-0.1.3-LICENSE-MIT'], short=True)
            audit.audit(path)

    def test_r_efi_authors_placeholder_is_not_a_license(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'licenses.zip'
            package = {'name': 'r-efi', 'version': '5.3.0', 'source': 'registry', 'notice_files': []}
            self.bundle(path, package, ['vendor/r-efi-5.3.0/AUTHORS'], short=True)
            with self.assertRaises(ValueError):
                audit.audit(path)


if __name__ == '__main__':
    unittest.main()
