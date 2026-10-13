"""Fresh tutorial builds inside the pinned FreeCAD GUI; never overwrite checkpoints."""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import runpy
import FreeCAD as App
import FreeCADGui as Gui

COURSE = Path(__file__).resolve().parent


def workspace_root():
    return next(p for p in COURSE.parents if (p / 'tools/cad/toolchain.json').is_file())


def read_json(path):
    return json.loads(path.read_text())


def cube(doc, stage):
    folder = COURSE / 'workflow-cube'
    p = read_json(folder / 'parameters.json')
    block = doc.addObject('Part::Box', 'Cube')
    block.Length, block.Width, block.Height = p['length'], p['width'], p['height']
    if stage != 'cube':
        ratio = read_json(folder / '02-parameters.json')['height_to_length_ratio']
        block.setExpression('Height', f'Length * {ratio}')
    if stage in ('resized', 'hole'):
        p = read_json(folder / '03-parameters.json')
        block.Length, block.Width = p['length'], p['width']
    result = block
    if stage == 'hole':
        tool = doc.addObject('Part::Cylinder', 'HoleTool')
        tool.Radius = p['hole_diameter'] / 2
        tool.Placement.Base.z = -p['cut_extension_each_end']
        tool.setExpression('Height', f"Cube.Height + {2*p['cut_extension_each_end']} mm")
        tool.setExpression('Placement.Base.x', 'Cube.Length / 2')
        tool.setExpression('Placement.Base.y', 'Cube.Width / 2')
        result = doc.addObject('Part::Cut', 'BlockWithHole')
        result.Base, result.Tool = block, tool
        block.Visibility = tool.Visibility = False
    doc.recompute()
    expected = block.Length.Value * block.Width.Value * block.Height.Value
    if stage == 'hole':
        expected -= math.pi * tool.Radius.Value**2 * block.Height.Value
    assert result.Shape.isValid() and len(result.Shape.Solids) == 1
    assert abs(result.Shape.Volume - expected) < 1e-5


def mount(doc, stage, model, params):
    body, sketch = model['create_plate_sketch'](doc, params)
    if stage == 'sketch':
        return
    model['add_plate_pad'](doc, body, sketch, params)
    if stage == 'pad':
        return
    hole = model['add_mounting_hole_sketch'](doc, body, params)
    if stage == 'hole-sketch':
        return
    model['add_mounting_pocket'](doc, body, hole)
    if stage == 'pocket':
        return
    model['add_opposite_hole'](doc)
    if stage == 'two-holes':
        return
    model['add_opposite_row'](doc)
    if stage == 'chamfer':
        model['add_top_chamfer'](doc, params)
    elif stage == 'fillet':
        model['add_top_fillet'](doc, params)
    hole.Visibility = False


STAGES = {
    'workflow-cube': ('cube', 'linked', 'resized', 'hole'),
    'practice-mount': ('sketch', 'pad', 'hole-sketch', 'pocket', 'two-holes', 'four-holes', 'chamfer', 'fillet'),
    'fit-coupon': ('plain', 'labels'),
    'practice-camera-bracket': ('envelope', 'cradle', 'slotted-tab', 'hardware', 'retention',
                                'interfaces', 'support', 'motion', 'exploded', 'access', 'complete'),
}


def main(lesson, stage=None):
    """Return a fresh document, saved under generated/cad-foundations/<unique run>."""
    if lesson not in STAGES:
        raise ValueError(f'Choose a lesson from {tuple(STAGES)}')
    stage = stage or STAGES[lesson][-1]
    if stage not in STAGES[lesson]:
        raise ValueError(f'Choose a stage from {STAGES[lesson]}')
    folder = COURSE / lesson
    params = read_json(folder / 'parameters.json')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = workspace_root() / 'generated/cad-foundations' / f'{stamp}-{lesson}-{stage}'
    output.mkdir(parents=True, exist_ok=False)
    doc = App.newDocument('Tutorial_' + lesson.replace('-', '_'))
    doc.Label = f'Tutorial: {lesson} / {stage}'
    try:
        if lesson == 'workflow-cube':
            cube(doc, stage)
        else:
            model = runpy.run_path(str(folder / 'model.py'))
            if lesson == 'practice-mount':
                mount(doc, stage, model, params)
            elif lesson == 'fit-coupon':
                model['build_coupon'](doc, params)
                if stage == 'labels':
                    model['add_embossed_labels'](doc, params)
            else:
                base_stage = {'exploded': 'motion', 'complete': 'access'}.get(stage, stage)
                model['build_stage'](doc, params, base_stage)
                assembly = runpy.run_path(str(folder / 'assembly.py'))
                if stage in ('exploded', 'complete'):
                    assembly['create_exploded_view'](doc, params['exploded_step_mm'])
                if stage == 'complete':
                    assembly['show_assembled_view'](doc)
                    study = runpy.run_path(str(folder / 'stack_study.py'))
                    assumptions = read_json(folder / 'stack-study.json')
                    study['run_study'](params, assumptions)
                    study['attach_current_report'](doc, params, assumptions)
        doc.recompute()
        view = Gui.getDocument(doc.Name).activeView()
        view.viewAxonometric()
        view.fitAll()
        doc.saveAs(str(output / 'model.FCStd'))
        (output / 'run.json').write_text(json.dumps(dict(lesson=lesson, stage=stage,
            parameters=params, source_folder=folder.relative_to(workspace_root()).as_posix()), indent=2)+'\n')
    except Exception:
        App.closeDocument(doc.Name)
        raise
    print(f'Built {lesson}/{stage}: {doc.FileName}')
    return doc
