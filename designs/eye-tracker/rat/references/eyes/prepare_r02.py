"""Partition the preserved C envelope and center it on its analytic volume centroid."""
from pathlib import Path
import hashlib
import json
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[4]/'generated/eye-tracker/rat/eye-materials-r02'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    record = json.loads((HERE/'validation.json').read_text())['variants']['C-oblate-cornea']
    source = HERE/'stl'/record['file']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sha256']
    mesh = trimesh.load_mesh(source, process=True)
    seam = record['limbus_z_mm']
    pieces = [
        (record['body_radial_semiaxis_mm'], record['body_axial_semiaxis_mm'],
         record['body_center_z_mm'], -6.291/2, seam),
        (record['cap_radial_semiaxis_mm'], record['cap_axial_semiaxis_mm'],
         record['cap_center_z_mm'], seam, 6.291/2)]
    volume = moment = 0.
    for a,b,c,low,high in pieces:
        def integral(z):
            u = z-c
            return np.pi*a*a*(u-u**3/(3*b*b))
        def first_moment(z):
            u = z-c
            return np.pi*a*a*(c*(u-u**3/(3*b*b))+u*u/2-u**4/(4*b*b))
        volume += integral(high)-integral(low)
        moment += first_moment(high)-first_moment(low)
    shift = moment/volume
    assert abs(mesh.center_mass[2]-shift) < .001
    z = mesh.triangles[:,:,2]
    lower = np.all(z <= seam+1e-6, axis=1)
    upper = np.all(z >= seam-1e-6, axis=1)
    assert np.all(lower ^ upper), 'Every exterior triangle belongs to exactly one region'
    results = {}
    centered = mesh.copy()
    centered.vertices[:,2] -= shift
    centered.export(OUT/'rat-eye-r02-whole.stl')
    for name,mask in [('sclera',lower),('cornea',upper)]:
        part = mesh.submesh([np.flatnonzero(mask)], append=True, repair=False)
        boundary = part.edges_unique[np.bincount(part.edges_unique_inverse)==1]
        ring = np.unique(boundary)
        assert len(ring) == 192
        assert np.allclose(part.vertices[ring,2],seam,atol=1e-6)
        ring = ring[np.argsort(np.arctan2(part.vertices[ring,1],part.vertices[ring,0]))]
        center = len(part.vertices)
        vertices = np.vstack((part.vertices,[0,0,part.vertices[ring[0],2]]))
        closing = np.array([[center,ring[j],ring[(j+1)%len(ring)]] for j in range(len(ring))])
        if name == 'cornea':
            closing = closing[:,::-1]
        faces = np.vstack((part.faces,closing))
        result = trimesh.Trimesh(vertices=vertices,faces=faces,process=True)
        result.vertices[:,2] -= shift
        path = OUT/f'rat-eye-r02-{name}.stl'
        result.export(path)
        loaded = trimesh.load_mesh(path,process=True)
        assert loaded.is_volume and loaded.is_watertight and loaded.body_count == 1
        assert loaded.euler_number == 2 and loaded.area_faces.min() > 1e-10
        results[name] = dict(path=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            exterior_faces=int(mask.sum()),closing_faces=192,
                            volume_mm3=float(loaded.volume),centroid_mm=loaded.center_mass.tolist(),
                            watertight=True,connected_bodies=1)
    assert abs(sum(v['volume_mm3'] for v in results.values())-mesh.volume) < 1e-4
    definition = dict(revision='rat-eye-r02',units='mm',source='[@hughes1979RatEye]',
        geometry='C-oblate-cornea r01, partitioned at its existing limbus; original exterior triangles retained',
        source_sha256=record['sha256'],origin='Analytic volume centroid of the complete uniform exterior envelope',
        origin_in_r01_coordinates_mm=[0,0,float(shift)],
        axes={'z': 'Anterior: outward through corneal apex',
              'y': 'Superior: chosen up direction orthogonal to Z',
              'x': 'Y cross Z; X cross Y = Z'},
        symmetry='Geometry is rotationally symmetric. The up direction fixes otherwise arbitrary roll.',
        apex_mm=[0,0,6.291/2-shift],posterior_pole_mm=[0,0,-6.291/2-shift],
        limbus_z_mm=seam-shift,analytic_volume_mm3=volume,
        surfaces={
            'sclera': dict(radial_semiaxis_mm=record['body_radial_semiaxis_mm'],
                           axial_semiaxis_mm=record['body_axial_semiaxis_mm'],
                           center_z_mm=record['body_center_z_mm']-shift,
                           retained_region='z <= limbus_z_mm'),
            'cornea': dict(radial_semiaxis_mm=record['cap_radial_semiaxis_mm'],
                           axial_semiaxis_mm=record['cap_axial_semiaxis_mm'],
                           center_z_mm=record['cap_center_z_mm']-shift,
                           retained_region='z >= limbus_z_mm')},
        whole_mesh=dict(path='rat-eye-r02-whole.stl',
                        sha256=hashlib.sha256((OUT/'rat-eye-r02-whole.stl').read_bytes()).hexdigest()),
        centered_mesh_centroid_mm=centered.center_mass.tolist(),
        components=results,
        tissue_note='Cornea and sclera are colored solid envelope regions, not anatomical wall-thickness models. Their shared planar closing disk is an internal CAD partition.',
        axes_note='Axes are display guides, excluded from whole-eye and component STL geometry.')
    (OUT/'eye-definition.json').write_text(json.dumps(definition,indent=2)+'\n')
    print(json.dumps(definition,indent=2))


if __name__ == '__main__':
    main()
