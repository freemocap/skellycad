"""Selection redirects preserve identity and reject unsafe or cyclic targets."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'designs/eye-tracker'))
from shared.model import load_manifest
from shared.paths import repository_path


class SelectionTests(unittest.TestCase):
    def setUp(self):
        scratch=ROOT/'generated/verification/selection-tests';scratch.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=scratch);self.folder=Path(self.temp.name)
        self.native=self.folder/'native.bin';self.native.write_bytes(b'exact checkpoint identity')
        self.manifest=self.folder/'model.json'
        self.data={'revision':'TEST','native_checkpoint':self.native.relative_to(ROOT).as_posix(),
                   'native_sha256':hashlib.sha256(self.native.read_bytes()).hexdigest()}
        self.manifest.write_text(json.dumps(self.data))

    def tearDown(self):self.temp.cleanup()

    def test_redirect_checks_exact_native(self):
        alias=self.folder/'active-model.json';alias.write_text(json.dumps({'selection':self.manifest.relative_to(ROOT).as_posix()}))
        record,path=load_manifest(alias)
        self.assertEqual(path,self.native);self.assertEqual(record['revision'],'TEST')

    def test_changed_native_rejected(self):
        self.native.write_bytes(b'changed')
        with self.assertRaises(ValueError):load_manifest(self.manifest)

    def test_cycle_rejected(self):
        self.manifest.write_text(json.dumps({'selection':self.manifest.relative_to(ROOT).as_posix()}))
        with self.assertRaisesRegex(ValueError,'Cyclic'):load_manifest(self.manifest)

    def test_escape_rejected(self):
        with self.assertRaises(ValueError):repository_path('../../outside.FCStd')

    def test_camera_record_form(self):
        self.data['native_checkpoint']={'path':self.data['native_checkpoint'],'sha256':self.data.pop('native_sha256')}
        self.manifest.write_text(json.dumps(self.data))
        self.assertEqual(load_manifest(self.manifest)[1],self.native)


if __name__=='__main__':unittest.main()
