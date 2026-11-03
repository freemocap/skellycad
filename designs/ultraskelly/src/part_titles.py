"""Add a large name band above each part image listed in a folder's titles.json.

The band sits above the picture, so the text never covers the part. Run with the tools
Python from the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/part_titles.py generated/ultraskelly/part-images/r007

Reads <stem>-render.png and writes <stem>.png beside it.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BOLD = ['C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf']
REGULAR = ['C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/arial.ttf']
INK, DETAIL, RULE = (15, 15, 15), (60, 60, 60), (190, 190, 190)


def font(paths, size):
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise FileNotFoundError(f'no font among {paths}')


def fitted(draw, text, paths, size, width):
    """Largest font up to size that fits the text on one line within width."""
    while size > 20:
        face = font(paths, size)
        if draw.textlength(text, font=face) <= width:
            return face
        size -= 4
    return font(paths, size)


def titled(source, entry, margin=48):
    image = Image.open(source).convert('RGB')
    probe = ImageDraw.Draw(image)
    width = image.width - 2 * margin
    title = fitted(probe, entry['title'], BOLD, 110, width)
    details = [(line, fitted(probe, line, REGULAR, 46, width)) for line in entry['details']]
    title_h = title.getbbox(entry['title'])[3]
    line_h = [face.getbbox(line)[3] for line, face in details]
    band = margin + title_h + 28 + sum(h + 16 for h in line_h) + margin // 2
    out = Image.new('RGB', (image.width, image.height + band), 'white')
    out.paste(image, (0, band))
    draw = ImageDraw.Draw(out)
    y = margin
    draw.text((margin, y), entry['title'], fill=INK, font=title)
    y += title_h + 28
    for (line, face), h in zip(details, line_h):
        draw.text((margin, y), line, fill=DETAIL, font=face)
        y += h + 16
    draw.line([(margin, band - 4), (image.width - margin, band - 4)], fill=RULE, width=3)
    target = source.with_name(source.name.replace('-render.png', '.png'))
    out.save(target, optimize=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    titles = json.loads((args.folder / 'titles.json').read_text(encoding='utf-8'))
    for name, entry in titles.items():
        print(titled(args.folder / name.replace('.png', '-render.png'), entry))


if __name__ == '__main__':
    main()
