"""Read a ZIP either directly or from ordered, bounded-size binary volumes."""
from contextlib import contextmanager
from pathlib import Path
import bisect
import io
import zipfile


class Volumes(io.RawIOBase):
    def __init__(self, paths):
        self.files = [Path(p).open('rb') for p in paths]
        self.ends = []
        total = 0
        for p in paths:
            total += Path(p).stat().st_size
            self.ends.append(total)
        self.position = 0

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position

    def seek(self, offset, whence=0):
        position = offset if whence == 0 else (self.position if whence == 1 else self.ends[-1]) + offset
        if position < 0:
            raise ValueError('Negative archive offset')
        self.position = position
        return position

    def read(self, size=-1):
        if size < 0:
            size = max(0, self.ends[-1] - self.position)
        blocks = []
        while size and self.position < self.ends[-1]:
            i = bisect.bisect_right(self.ends, self.position)
            start = self.ends[i-1] if i else 0
            self.files[i].seek(self.position - start)
            block = self.files[i].read(min(size, self.ends[i] - self.position))
            if not block:
                raise OSError('Truncated archive volume')
            blocks.append(block)
            size -= len(block)
            self.position += len(block)
        return b''.join(blocks)

    def close(self):
        for f in self.files:
            f.close()
        super().close()


@contextmanager
def open_archive(path):
    path = Path(path)
    if path.exists():
        with zipfile.ZipFile(path) as archive:
            yield archive
    else:
        parts = sorted(path.parent.glob(path.name + '.[0-9][0-9][0-9]'))
        if not parts:
            raise FileNotFoundError(path)
        expected = [path.with_name(path.name + f'.{i:03d}') for i in range(1, len(parts)+1)]
        if parts != expected:
            raise ValueError('Missing or unordered archive volume')
        with Volumes(parts) as stream, zipfile.ZipFile(stream) as archive:
            yield archive
