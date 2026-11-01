import struct, unittest, zlib, tempfile, json
from pathlib import Path
from camera_link import Decoder, Frame, HEADER, encode, synthetic_frame, set_control, record

class LinkTests(unittest.TestCase):
    def test_recording_preserves_synthetic_evidence_and_target_provenance(self):
        root=Path(__file__).resolve().parents[4];testroot=root/'generated/firmware-host-tests';testroot.mkdir(parents=True,exist_ok=True)
        assert testroot.resolve().is_relative_to(root.resolve())
        with tempfile.TemporaryDirectory(prefix='record-',dir=testroot) as tmp:
            assert Path(tmp).resolve().is_relative_to(testroot.resolve())
            dst=Path(tmp)/'capture';record(dst,2)
            report=json.loads((dst/'recording.json').read_text())
            self.assertEqual(report['software_target']['board_revision'],'R11')
            self.assertFalse(report['software_target']['device_identity_verified'])
            self.assertFalse(report['physical_capture_demonstrated'])
            self.assertEqual(len(report['frames']),2)
            for frame in report['frames']:
                self.assertTrue(frame['synthetic'])
                header,pixels=(dst/frame['file']).read_bytes().split(b'255\n',1)
                self.assertEqual(header,b'P5\n640 400\n')
                self.assertEqual(len(pixels),640*400)
                self.assertEqual(f'{zlib.crc32(pixels):08x}',frame['crc32'])

    def test_control_acknowledgement_and_wire_units(self):
        class Link:
            sent = b''
            response = bytearray(b'!E OK 100\n')
            def write(self, data): self.sent += data
            def read(self, count):
                result = bytes(self.response[:count]); del self.response[:count]; return result
        link = Link(); set_control(link, 'E', 100)
        self.assertEqual(link.sent, b'\nE100\n')

    def test_control_rejection_and_wrong_echo_fail(self):
        class Link:
            def __init__(self, reply): self.reply = bytearray(reply)
            def write(self, data): pass
            def read(self, count):
                result = bytes(self.reply[:count]); del self.reply[:count]; return result
        for reply in (b'!G ERR 258\n', b'!E OK 9\n', b'!G OK 7\n', b'x'*64):
            with self.assertRaises(RuntimeError): set_control(Link(reply), 'G', 8)

    def test_control_input_bounds_and_simulation_refusal(self):
        for opcode, value in [('X', 0), ('E', -1), ('G', 10**9), ('E', 1.2)]:
            with self.assertRaises(ValueError): set_control(None, opcode, value)
        with self.assertRaises(ValueError): record('must-not-create', 1, exposure_lines=100)

    def test_firmware_wire_layout_with_independent_fixture(self):
        # Known CRC-32 check vector, independent of encode().
        payload = b'123456789'
        header = bytes.fromhex('534b593101000100090001002a0000000300000000000000090000002639f4cb')
        frame, = Decoder().feed(header + payload)
        self.assertEqual(frame, Frame(9, 1, 42, 3, payload, True))

    def test_every_header_split(self):
        expected = synthetic_frame(3, 37, 11); packet = encode(expected)
        for split in range(HEADER.size + 1):
            d = Decoder()
            self.assertEqual(d.feed(packet[:split]) + d.feed(packet[split:]), [expected])

    def test_noise_corruption_and_following_frame(self):
        damaged = bytearray(encode(synthetic_frame(1, 40, 20))); damaged[-1] ^= 1
        expected = synthetic_frame(2, 40, 20); d = Decoder()
        self.assertEqual(d.feed(b'noise' + damaged + encode(expected)), [expected])
        self.assertEqual(d.rejected, 1)

    def test_absurd_lengths_are_rejected_without_buffer_growth(self):
        invalid = HEADER.pack(b'SKY1', 1, 0, 640, 400, 0, 0, 0xffffffff, 0)
        d = Decoder()
        self.assertEqual(d.feed(invalid * 10000), [])
        self.assertLessEqual(len(d.buffer), HEADER.size)
        self.assertEqual(d.rejected, 10000)

    def test_fragmented_multiple_full_frames(self):
        expected = [synthetic_frame(i) for i in range(3)]
        data = b''.join(map(encode, expected)); d = Decoder(); got = []
        for i in range(0, len(data), 511): got.extend(d.feed(data[i:i+511]))
        self.assertEqual(got, expected)
        self.assertEqual(d.buffer, b'')

    def test_real_frame_is_not_marked_synthetic(self):
        frame = Frame(2, 2, 0, 100, b'\x00\x80\xff\x01', False)
        self.assertFalse(Decoder().feed(encode(frame))[0].synthetic)

    def test_incomplete_frame_is_not_returned(self):
        packet = encode(synthetic_frame(0)); d = Decoder()
        self.assertEqual(d.feed(packet[:-1]), [])
        self.assertEqual(len(d.feed(packet[-1:])), 1)

    def test_bad_flags_and_zero_dimensions(self):
        for flags, width, height in [(2,1,1),(0,0,1),(0,1,0)]:
            d=Decoder()
            self.assertEqual(d.feed(HEADER.pack(b'SKY1',1,flags,width,height,0,0,width*height,0)),[])
            self.assertEqual(d.rejected,1)

if __name__ == '__main__': unittest.main()
