"""Record CRC-checked grayscale snapshots; simulation never masquerades as capture."""
from dataclasses import dataclass
from pathlib import Path
import argparse, hashlib, json, struct, time, zlib

HEADER = struct.Struct('<4sHHHHIQII')
MAX_PAYLOAD = 1280 * 800

@dataclass(frozen=True)
class Frame:
    width: int
    height: int
    sequence: int
    timestamp_us: int
    pixels: bytes
    synthetic: bool

def encode(frame):
    if not 0 < frame.width <= 1280 or not 0 < frame.height <= 800:
        raise ValueError('Unsupported dimensions')
    if len(frame.pixels) != frame.width * frame.height:
        raise ValueError('Incorrect payload length')
    return HEADER.pack(b'SKY1', 1, int(frame.synthetic), frame.width, frame.height,
                       frame.sequence, frame.timestamp_us, len(frame.pixels),
                       zlib.crc32(frame.pixels)) + frame.pixels

class Decoder:
    """Incremental decoder with bounded storage and recovery after a corrupt frame."""
    def __init__(self):
        self.buffer = bytearray()
        self.rejected = 0

    def feed(self, chunk):
        # The caller may supply arbitrarily large chunks. Process bounded slices.
        result = []
        for offset in range(0, len(chunk), 4096):
            self.buffer.extend(chunk[offset:offset + 4096])
            while True:
                start = self.buffer.find(b'SKY1')
                if start < 0:
                    self.buffer[:] = self.buffer[-3:]
                    break
                del self.buffer[:start]
                if len(self.buffer) < HEADER.size:
                    break
                _, version, flags, width, height, seq, stamp, length, crc = HEADER.unpack_from(self.buffer)
                if (version != 1 or flags not in (0, 1) or not 0 < width <= 1280
                    or not 0 < height <= 800 or length != width * height or length > MAX_PAYLOAD):
                    self.rejected += 1; del self.buffer[0]; continue
                end = HEADER.size + length
                if len(self.buffer) < end:
                    break
                pixels = bytes(self.buffer[HEADER.size:end])
                if zlib.crc32(pixels) != crc:
                    self.rejected += 1; del self.buffer[0]; continue
                result.append(Frame(width, height, seq, stamp, pixels, bool(flags)))
                del self.buffer[:end]
        return result

def synthetic_frame(sequence, width=640, height=400):
    # Exactly the firmware synthetic pattern. No simulated optical performance.
    row = bytes(range(256)) * ((width + 255) // 256 + 2)
    pixels = b''.join(row[(y + sequence) % 256:(y + sequence) % 256 + width]
                      for y in range(height))
    return Frame(width, height, sequence, sequence * 1000000, pixels, True)

def set_control(link, opcode, value):
    if opcode not in ('E', 'G') or type(value) is not int or not 0 <= value < 1_000_000_000:
        raise ValueError('Expected E/G and a nonnegative integer below 1e9')
    link.write(f'\n{opcode}{value}\n'.encode('ascii'))
    deadline = time.monotonic() + 3
    response = bytearray()
    while time.monotonic() < deadline and len(response) < 64:
        byte = link.read(1)
        if not byte: continue
        response.extend(byte)
        if byte == b'\n': break
    expected = f'!{opcode} OK {value}\n'.encode('ascii')
    if response != expected:
        raise RuntimeError(f'Camera rejected or did not acknowledge control: {bytes(response)!r}')

def record(destination, count, port=None, exposure_lines=None, gain_index=None):
    if not port and (exposure_lines is not None or gain_index is not None):
        raise ValueError('Sensor controls require a real port; simulation cannot verify settings')
    contract_path=Path(__file__).resolve().parents[1]/'board-contract.json'
    contract_bytes=contract_path.read_bytes();contract=json.loads(contract_bytes)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    decoder = Decoder(); manifest = []; serial_link = None
    if port:
        import serial
        serial_link = serial.Serial(port, baudrate=115200, timeout=.2, write_timeout=1)
        serial_link.reset_input_buffer()
    try:
        if exposure_lines is not None: set_control(serial_link, 'E', exposure_lines)
        if gain_index is not None: set_control(serial_link, 'G', gain_index)
        for number in range(count):
            if serial_link:
                serial_link.write(b'F'); deadline = time.monotonic() + 7
                frames = []
                while not frames and time.monotonic() < deadline:
                    frames = decoder.feed(serial_link.read(4096))
                if not frames:
                    raise TimeoutError('No complete frame; check UART diagnostics and USB connection')
                frame = frames[0]
            else:
                packet = encode(synthetic_frame(number))
                frames = []
                for offset in range(0, len(packet), 509):
                    frames.extend(decoder.feed(packet[offset:offset + 509]))
                frame = frames[0]
            name = f'{number:05d}.pgm'
            (destination / name).write_bytes(f'P5\n{frame.width} {frame.height}\n255\n'.encode() + frame.pixels)
            manifest.append({'file': name, 'sequence': frame.sequence, 'timestamp_us': frame.timestamp_us,
                             'synthetic': frame.synthetic, 'crc32': f'{zlib.crc32(frame.pixels):08x}',
                             'width': frame.width, 'height': frame.height})
    finally:
        if serial_link: serial_link.close()
        (destination / 'recording.json').write_text(json.dumps({
            'transport': 'USB CDC' if port else 'software loopback',
            'requested_frames': count, 'frames': manifest, 'rejected_packets': decoder.rejected,
            'requested_controls': {'exposure_lines': exposure_lines, 'gain_index': gain_index},
            'software_target': {'board_revision': contract['board_revision'],
                                'contract_sha256': hashlib.sha256(contract_bytes).hexdigest(),
                                'device_identity_verified': False},
            'physical_capture_demonstrated': bool(manifest) and all(not f['synthetic'] for f in manifest) and port is not None,
        }, indent=2) + '\n')
    return manifest

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--frames', type=int, default=3)
    ap.add_argument('--exposure-lines', type=int)
    ap.add_argument('--gain-index', type=int)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--simulate', action='store_true')
    mode.add_argument('--port')
    args = ap.parse_args()
    if not 1 <= args.frames <= 10000: ap.error('--frames must be 1..10000')
    print(json.dumps(record(args.output, args.frames, args.port, args.exposure_lines, args.gain_index), indent=2))
