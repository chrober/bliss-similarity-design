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
    def bundle(self, path, package, files):
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr('SOURCE_MANIFEST.json', json.dumps({'packages': [package]}))
            for name in files:
                z.writestr(name, 'text')

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


if __name__ == '__main__':
    unittest.main()
