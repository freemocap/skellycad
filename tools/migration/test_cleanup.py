"""Safety checks for restoration and relocation contracts."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import restore_cleanup
import replay_cleanup
from plan_cleanup import relocate, numbered


class RestoreTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[2] / 'generated/verification/cleanup-tests'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name)
        self.records = self.root / 'records'
        self.records.mkdir()
        self.dest = self.root / 'generated/replay/test'
        self.data = b'preserved native input'
        self.name = 'designs/example/source.bin'
        (self.records / 'inventory.json').write_text(json.dumps({'records': [
            {'path': self.name, 'sha256': hashlib.sha256(self.data).hexdigest()}]}))
        with zipfile.ZipFile(self.records / 'source-before.zip', 'w') as z:
            z.writestr(self.name, self.data)
        self.patch_root = patch.object(restore_cleanup, 'ROOT', self.root)
        self.patch_records = patch.object(restore_cleanup, 'RECORDS', self.records)
        self.patch_root.start(); self.patch_records.start()

    def tearDown(self):
        self.patch_root.stop(); self.patch_records.stop(); self.temp.cleanup()

    def test_restores_exact_bytes_and_skips_identical(self):
        self.assertEqual(restore_cleanup.restore(self.dest, include_generated=False), 1)
        self.assertEqual((self.dest / self.name).read_bytes(), self.data)
        self.assertEqual(restore_cleanup.restore(self.dest, include_generated=False), 0)

    def test_refuses_overwrite(self):
        target = self.dest / self.name
        target.parent.mkdir(parents=True)
        target.write_bytes(b'new user work')
        with self.assertRaises(ValueError):
            restore_cleanup.restore(self.dest, include_generated=False)
        self.assertEqual(target.read_bytes(), b'new user work')

    def test_refuses_main_checkout(self):
        with self.assertRaises(ValueError):
            restore_cleanup.restore(self.root, include_generated=False)

    def test_refuses_archive_traversal(self):
        with zipfile.ZipFile(self.records / 'source-before.zip', 'w') as z:
            z.writestr('../../outside', b'bad')
        with self.assertRaises(ValueError):
            restore_cleanup.restore(self.dest, include_generated=False)

    def test_bad_hash_stops_restore(self):
        with zipfile.ZipFile(self.records / 'source-before.zip', 'w') as z:
            z.writestr(self.name, b'changed')
        with self.assertRaises(ValueError):
            restore_cleanup.restore(self.dest, include_generated=False)

    def test_prefix_filter(self):
        self.assertEqual(restore_cleanup.restore(self.dest, ['other/'], False), 0)

    def test_split_volume_restore(self):
        archive = self.records / 'source-before.zip'
        data = archive.read_bytes()
        for i, start in enumerate(range(0, len(data), 37), 1):
            archive.with_name(archive.name + f'.{i:03d}').write_bytes(data[start:start+37])
        archive.unlink()
        self.assertEqual(restore_cleanup.restore(self.dest, include_generated=False), 1)
        self.assertEqual((self.dest / self.name).read_bytes(), self.data)


class MapTests(unittest.TestCase):
    def test_prefix_boundary(self):
        self.assertEqual(relocate('a/b/file', {'a/b': 'c'}), 'c/file')
        self.assertEqual(relocate('a/bb/file', {'a/b': 'c'}), 'a/bb/file')

    def test_sortable_revision_and_layout(self):
        self.assertEqual(numbered('print-r32-l04'), 'r032-l004-print')
        self.assertEqual(numbered('lowered-cameras-r43'), 'r043-lowered-cameras')



class CurrentOverlayTests(unittest.TestCase):
    def setUp(self):
        scratch=Path(__file__).resolve().parents[2]/'generated/verification/cleanup-tests'
        scratch.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch);self.root=Path(self.temp.name)
        self.records=self.root/'records';self.records.mkdir()
        self.dest=self.root/'generated/replay/scoped';(self.dest/'legacy').mkdir(parents=True)
        self.owners={'designs/a/src':'legacy','designs/b/src':'legacy'}
        (self.records/'current-source-owners.json').write_text(json.dumps(self.owners))
        (self.records/'move-map.json').write_text(json.dumps({'files':[
            {'new':'designs/a/src/main.py','old':'legacy/main.py'},
            {'new':'designs/b/src/other.py','old':'legacy/other.py'}]}))
        for name,data in [('designs/a/src/main.py','edited'),('designs/a/src/new.py','new module'),
                          ('designs/b/src/other.py','other edit'),('designs/a/src/managed_components/cache.bin','cache'),
                          ('generated/replay/scoped/legacy/main.py','baseline'),('generated/replay/scoped/legacy/other.py','retained')]:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
        self.patches=[patch.object(replay_cleanup,'ROOT',self.root),patch.object(replay_cleanup,'RECORDS',self.records)]
        for p in self.patches:p.start()

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.temp.cleanup()

    def test_scoped_overlay_includes_new_modules_and_preserves_other_owners(self):
        files=replay_cleanup.overlay_current(self.dest,['designs/a/src'])
        self.assertEqual(len(files),2)
        self.assertEqual((self.dest/'legacy/main.py').read_text(),'edited')
        self.assertEqual((self.dest/'legacy/new.py').read_text(),'new module')
        self.assertEqual((self.dest/'legacy/other.py').read_text(),'retained')
        self.assertFalse((self.dest/'legacy/managed_components').exists())

    def test_collision_rejected_before_copying(self):
        (self.root/'designs/b/src/new.py').write_text('conflicting module')
        with self.assertRaises(ValueError):replay_cleanup.overlay_current(self.dest)
        self.assertEqual((self.dest/'legacy/main.py').read_text(),'baseline')

    def test_new_script_resolves_through_its_source_owner(self):
        self.assertEqual(replay_cleanup.original_script('designs/a/src/new.py'),'legacy/new.py')

if __name__ == '__main__':
    unittest.main()
