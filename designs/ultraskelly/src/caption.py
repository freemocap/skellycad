"""Draw part labels and a caption band on each image listed in a folder's captions.json.

Part labels come from <image>.labels.json (written by explain.py): each points at a projected
anchor on its part and is drawn in a white box with a leader line, nudged to avoid overlaps.
Run with the tools Python from the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/caption.py generated/ultraskelly/explain/r004

Writes <name>-captioned.png beside each source image.
"""
import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = ['C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/arial.ttf']
INK, LINE, BOX = (20, 20, 20), (90, 90, 90), (255, 255, 255)


def font(size):
    for path in FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def overlaps(a, b, pad=6):
    return not (a[2] + pad < b[0] or b[2] + pad < a[0] or a[3] + pad < b[1] or b[3] + pad < a[1])


def draw_marks(image, marks, size=30):
    draw = ImageDraw.Draw(image)
    face = font(size)
    placed = []
    for mark in sorted(marks, key=lambda m: m['y']):
        text = '\n'.join(mark['text'])
        left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=face)
        w, h = right - left + 16, bottom - top + 12
        # Labels go outward, toward the nearer side margin, so they cover less of the parts.
        x0 = mark['x'] + 30 if mark['x'] >= image.width / 2 else mark['x'] - 30 - w
        x0 = min(max(x0, 4), image.width - w - 4)
        y_start = mark['y'] + 30 if mark['below'] else mark['y'] - 30 - h
        # Try the preferred spot, then alternate further away above and below it.
        for k in [0] + [s * n for n in range(1, 10) for s in (1, -1)]:
            y0 = min(max(y_start + k * (h + 6), 4), image.height - h - 4)
            box = (x0, y0, x0 + w, y0 + h)
            if not any(overlaps(box, other[0]) for other in placed):
                break
        placed.append((box, mark, text, top))
    for box, mark, _text, _top in placed:  # all leader lines first, so boxes stay on top
        x_edge = box[0] if box[0] > mark['x'] else box[2]
        corner = (x_edge, box[3] if box[3] < mark['y'] else box[1])
        draw.line([corner, (mark['x'], mark['y'])], fill=LINE, width=3)
        draw.ellipse([mark['x'] - 6, mark['y'] - 6, mark['x'] + 6, mark['y'] + 6], fill=LINE)
    for box, _mark, text, top in placed:
        draw.rectangle(box, fill=BOX, outline=LINE, width=2)
        draw.multiline_text((box[0] + 8, box[1] + 4 - top), text, fill=INK, font=face, spacing=4)


def caption(source, text, size=34, width_chars=95):
    image = Image.open(source).convert('RGB')
    marks_path = source.with_suffix('.labels.json')
    if marks_path.exists():
        draw_marks(image, json.loads(marks_path.read_text(encoding='utf-8')))
    face = font(size)
    lines = textwrap.wrap(text, width_chars)
    band = int(size * 1.35 * len(lines) + size)
    out = Image.new('RGB', (image.width, image.height + band), 'white')
    out.paste(image, (0, band))
    draw = ImageDraw.Draw(out)
    for i, line in enumerate(lines):
        draw.text((size // 2, size // 2 + int(i * size * 1.35)), line, fill=INK, font=face)
    draw.line([(0, band - 2), (image.width, band - 2)], fill=(180, 180, 180), width=2)
    target = source.with_name(source.stem + '-captioned.png')
    out.save(target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    captions = json.loads((args.folder / 'captions.json').read_text(encoding='utf-8'))
    for name, text in captions.items():
        if (args.folder / name).exists():
            print(caption(args.folder / name, text))


if __name__ == '__main__':
    main()
