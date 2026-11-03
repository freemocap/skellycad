"""Lay out before/after part images in one sheet: a row per part, earlier set left, new set right, with grams.

Run with the tools Python from the repository root:

    tools/cad/.venv/Scripts/python.exe -B designs/ultraskelly/src/compare_sheet.py generated/ultraskelly/compare-images/r011 sheet.json

sheet.json gives the title, the two set names and each part's name and grams:
{"title": "...", "note": "...", "old": "R004", "new": "R005",
 "parts": [{"stem": "clamp-u", "name": "Clamp U", "old_g": 26.0, "new_g": 17.0}, ...]}
Writes before-after.png in the image folder. Text sits in bands, never over a part.
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from part_titles import BOLD, DETAIL, INK, REGULAR, RULE, fitted


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('folder', type=Path)
    parser.add_argument('sheet', type=Path)
    args = parser.parse_args()
    spec = json.loads(args.sheet.read_text(encoding='utf-8'))
    cells = [(Image.open(args.folder / f"{p['stem']}-old.png").convert('RGB'),
              Image.open(args.folder / f"{p['stem']}-new.png").convert('RGB')) for p in spec['parts']]
    cw, ch = cells[0][0].size
    margin, gap = 48, 24
    width = 2 * cw + gap + 2 * margin
    probe = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    title = fitted(probe, spec['title'], BOLD, 84, width - 2 * margin)
    note = fitted(probe, spec['note'], REGULAR, 40, width - 2 * margin)
    head = fitted(probe, spec['new'] + ' 999.9 g', BOLD, 56, cw)
    name_face = fitted(probe, max((p['name'] for p in spec['parts']), key=len), BOLD, 60, width - 2 * margin)
    title_h, note_h = title.getbbox(spec['title'])[3], note.getbbox(spec['note'])[3]
    name_h, head_h = name_face.getbbox('Ag')[3], head.getbbox('Ag')[3]
    top = margin + title_h + 20 + note_h + margin
    row = name_h + 16 + head_h + 12 + ch + gap
    sheet = Image.new('RGB', (width, top + row * len(cells) + margin), 'white')
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), spec['title'], fill=INK, font=title)
    draw.text((margin, margin + title_h + 20), spec['note'], fill=DETAIL, font=note)
    y = top
    for p, (old, new) in zip(spec['parts'], cells):
        draw.line([(margin, y - gap // 2), (width - margin, y - gap // 2)], fill=RULE, width=3)
        draw.text((margin, y), p['name'], fill=INK, font=name_face)
        y += name_h + 16
        for i, (label, grams) in enumerate(((spec['old'], p['old_g']), (spec['new'], p['new_g']))):
            draw.text((margin + i * (cw + gap), y), f'{label}   {grams:g} g', fill=DETAIL if i == 0 else INK, font=head)
        y += head_h + 12
        sheet.paste(old, (margin, y))
        sheet.paste(new, (margin + cw + gap, y))
        y += ch + gap
    target = args.folder / 'before-after.png'
    sheet.save(target, optimize=True)
    print(target)


if __name__ == '__main__':
    main()
