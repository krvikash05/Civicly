"""Offline guard tests; alter disposable copies, never backend contracts."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from check_contracts import ROOT, SOURCES, capture


class ContractGuardTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / 'contracts').mkdir()
        for name in SOURCES:
            shutil.copyfile(ROOT / 'contracts' / name, self.root / 'contracts' / name)

    def edit_routes(self, change):
        path = self.root / 'contracts/api_endpoints.json'
        doc = json.loads(path.read_text())
        change(doc['routes'])
        path.write_text(json.dumps(doc))

    def test_unchanged_copy_matches(self):
        self.assertEqual(capture(self.root), capture(ROOT))

    def test_schema_change_detected(self):
        before = capture(self.root)
        path = self.root / 'contracts/api_models.json'
        doc = json.loads(path.read_text())
        doc['$defs']['Ack']['description'] = 'changed contract'
        path.write_text(json.dumps(doc))
        self.assertNotEqual(before, capture(self.root))

    def test_duplicate_route_rejected(self):
        self.edit_routes(lambda rows: rows.append(dict(rows[0])))
        with self.assertRaisesRegex(ValueError, 'Duplicate route'):
            capture(self.root)

    def test_missing_schema_rejected(self):
        self.edit_routes(lambda rows: rows[0].update(response_schema_id='MissingSchema'))
        with self.assertRaisesRegex(ValueError, 'Missing schema'):
            capture(self.root)


if __name__ == '__main__':
    unittest.main()
