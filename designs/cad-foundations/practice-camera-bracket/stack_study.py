"""Worst-case axial stack arithmetic; no thread engagement or strength claim."""
from pathlib import Path
import itertools
import json
import math


def evaluate(params, assumptions, screw_length):
    assert params['units'] == assumptions['units'] == 'mm'
    layers = assumptions['layer_plus_minus']
    assert layers and all(0 <= tolerance < params[key] for key, tolerance in layers.items())
    screw_tolerance = assumptions['screw_length_plus_minus']
    assert 0 <= screw_tolerance < screw_length
    required = assumptions['minimum_protrusion']
    assert required >= 0
    stack = sum(params[key] for key in layers)
    stack_tolerance = sum(layers.values())
    nominal = screw_length - stack
    minimum = (screw_length - screw_tolerance) - (stack + stack_tolerance)
    maximum = (screw_length + screw_tolerance) - (stack - stack_tolerance)
    return dict(screw_length_mm=screw_length, nominal_mm=round(nominal, 6),
                minimum_mm=round(minimum, 6), maximum_mm=round(maximum, 6),
                required_minimum_mm=required, passes_minimum=minimum >= required - 1e-9)


def run_study(params, assumptions):
    results = [evaluate(params, assumptions, length) for length in assumptions['candidate_lengths']]
    # Independently enumerate every endpoint combination (2^5 here).
    for result in results:
        lengths = (result['screw_length_mm'] - assumptions['screw_length_plus_minus'],
                   result['screw_length_mm'] + assumptions['screw_length_plus_minus'])
        layer_bounds = [(params[k]-t, params[k]+t) for k, t in assumptions['layer_plus_minus'].items()]
        margins = [length-sum(stack) for length in lengths for stack in itertools.product(*layer_bounds)]
        assert math.isclose(min(margins), result['minimum_mm'], abs_tol=1e-9)
        assert math.isclose(max(margins), result['maximum_mm'], abs_tol=1e-9)
    return results


def attach_current_report(doc, params, assumptions):
    """Read-only snapshot for the current screw, checked against live geometry."""
    mapping = {'washer_thickness': 'WasherThickness', 'floor_thickness': 'FloorThickness',
               'support_thickness': 'SupportThickness', 'nut_reference_thickness': 'NutThickness',
               'screw_under_head_length': 'ScrewLength'}
    for key, prop in mapping.items():
        assert abs(params[key]-getattr(doc.Dimensions, prop).Value) < 1e-7, 'Reconcile live dimensions first.'
    result = evaluate(params, assumptions, params['screw_under_head_length'])
    measured = doc.NutReference.Shape.BoundBox.ZMin-doc.ScrewReference.Shape.BoundBox.ZMin
    assert abs(measured-result['nominal_mm']) < 1e-7
    obj = doc.getObject('StackStudy') or doc.addObject('App::FeaturePython', 'StackStudy')
    obj.Label = 'Screw stack study - hypothetical tolerance snapshot'
    for name, value in [('NominalProtrusion', result['nominal_mm']), ('MinimumProtrusion', result['minimum_mm']),
                        ('MaximumProtrusion', result['maximum_mm']), ('RequiredMinimum', result['required_minimum_mm'])]:
        if name not in obj.PropertiesList:
            obj.addProperty('App::PropertyDistance', name, 'Results (mm)')
        setattr(obj, name, value)
        obj.setEditorMode(name, 1)
    if 'PassesMinimum' not in obj.PropertiesList:
        obj.addProperty('App::PropertyBool', 'PassesMinimum', 'Results (mm)')
        obj.addProperty('App::PropertyString', 'Assumptions', 'Study')
    obj.PassesMinimum = result['passes_minimum']
    obj.Assumptions = json.dumps(assumptions, sort_keys=True)
    obj.setEditorMode('PassesMinimum', 1)
    obj.setEditorMode('Assumptions', 1)
    doc.recompute()
    return obj


if __name__ == '__main__':
    folder = Path(__file__).resolve().parent
    params = json.loads((folder/'parameters.json').read_text())
    assumptions = json.loads((folder/'stack-study.json').read_text())
    print(json.dumps(run_study(params, assumptions), indent=2))
