"""Generate rotational exterior envelopes; units mm. See README for evidence."""
from pathlib import Path
import json,math
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'generated/eye-tracker/adult-eyes-r01'
OUT.mkdir(parents=True,exist_ok=True)

def hermite(z,z0,z1,q0,q1,m0,m1):
 t=(z-z0)/(z1-z0);h=z1-z0
 return (2*t**3-3*t**2+1)*q0+(t**3-2*t*t+t)*h*m0+(-2*t**3+3*t*t)*q1+(t**3-t*t)*h*m1

def surface(profile,close_bottom=False,close_top=False):
 vertices=[];rings=[];faces=[];n=192
 for z,r in profile:
  if r<1e-8:
   rings.append([len(vertices)]);vertices.append([0,0,z])
  else:
   rings.append(list(range(len(vertices),len(vertices)+n)))
   vertices.extend([[r*math.cos(2*math.pi*j/n),r*math.sin(2*math.pi*j/n),z] for j in range(n)])
 for lo,hi in zip(rings,rings[1:]):
  for j in range(n):
   k=(j+1)%n
   if len(lo)==1:faces.append([lo[0],hi[k],hi[j]])
   elif len(hi)==1:faces.append([lo[j],lo[k],hi[0]])
   else:faces.extend([[lo[j],lo[k],hi[k]],[lo[j],hi[k],hi[j]]])
 for ring,z,top in [(rings[0],profile[0][0],False),(rings[-1],profile[-1][0],True)]:
  if (top and close_top) or (not top and close_bottom):
   c=len(vertices);vertices.append([0,0,z])
   for j in range(n):
    k=(j+1)%n;faces.append([c,ring[j],ring[k]] if top else [c,ring[k],ring[j]])
 m=trimesh.Trimesh(vertices=vertices,faces=faces,process=True)
 assert m.is_watertight and m.is_winding_consistent and m.volume>0
 return m

for species in ['mouse','rat']:
 if species=='mouse':
  width=3.30;length=3.34;posterior=-1.65;equator=0.0;radius=1.45;limbus_r=1.30;posterior_radius=1.65
  apex=posterior+length;cap_b=radius;cap_a=radius;cap_center=apex-radius
  limbus=cap_center+math.sqrt(radius**2-limbus_r**2)
 else:
  width=6.410;length=6.291;posterior=-3.0400940427778713;equator=-.2059113700374866;radius=2.965;limbus_r=2.82;posterior_radius=3.23
  apex=posterior+length;limbus=apex-2.11
  cap_a=2.9297427871121955;cap_b=2.8949048224741776;cap_center=apex-cap_b
 end_slope=-2*cap_a**2/cap_b**2*(limbus-cap_center)
 zs=np.r_[np.linspace(posterior,equator,129),np.linspace(equator,limbus,129)[1:]]
 qs=np.array([hermite(z,posterior,equator,0,(width/2)**2,2*posterior_radius,0) if z<=equator else hermite(z,equator,limbus,(width/2)**2,limbus_r**2,0,end_slope) for z in zs])
 assert qs.min()>-1e-10 and qs.max()<=(width/2)**2+1e-10
 assert np.diff(qs[:129]).min()>-1e-10 and np.diff(qs[128:]).max()<1e-10
 body=list(zip(zs,np.sqrt(np.maximum(qs,0))))
 cap_z=np.linspace(limbus,apex,193)
 cap=[(z,math.sqrt(max(0,cap_a**2*(1-((z-cap_center)/cap_b)**2)))) for z in cap_z]
 cap[0]=(limbus,limbus_r);cap[-1]=(apex,0)
 meshes={'sclera':surface(body,close_top=True),'cornea':surface(cap,close_bottom=True),'whole':surface(body+cap[1:])}
 rec={'species':species,'units':'mm','width_mm':width,'external_length_mm':length,'limbus_diameter_mm':2*limbus_r,'anterior_apical_radius_mm':cap_a**2/cap_b,'posterior_apical_radius_mm':posterior_radius,'posterior_z_mm':posterior,'equator_z_mm':equator,'limbus_z_mm':limbus,'apex_z_mm':apex,'limbus_squared_radius_derivative':end_slope,'construction':'Piecewise cubic Hermite squared radius for sclera; spherical mouse cap / oblate rat cap. Position and tangent continuous at equator and limbus.','meshes':{}}
 for name,m in meshes.items():
  file=OUT/f'{species}-{name}.stl';m.export(file)
  rec['meshes'][name]={'file':file.name,'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist(),'faces':len(m.faces)}
 assert abs(meshes['sclera'].volume+meshes['cornea'].volume-meshes['whole'].volume)<1e-8
 (OUT/f'{species}-definition.json').write_text(json.dumps(rec,indent=2)+'\n')
 print(species,rec['width_mm'],rec['external_length_mm'],rec['limbus_diameter_mm'],rec['anterior_apical_radius_mm'])
