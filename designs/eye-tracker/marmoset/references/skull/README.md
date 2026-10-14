# Marmoset CT skull source

`female_100months_403g.stl` is the unchanged file supplied from the user's
Downloads folder on 2026-10-14. It is an ASCII STL from the Marmoset Brain
Connectome's Neuroscientific Apparatus CT collection [@marmosetCtFemale100].
The accompanying paper describes CT-derived common marmoset (*Callithrix
jacchus*) skull models [@zimmermannRollin2025Apparatus].

- [Direct STL download](https://marmosetsa.blob.core.windows.net/$web/neuroscientific_apparatus/CT/CTsAcrossAgespan/female_100months_403g.stl)
- [CT catalog](https://www.marmosetbrainconnectome.org/apparatus/ct.html?HID=CT)
- [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12319799/)
- Specimen label: female, 100 months, 403 g. These are source labels, not measurements made here.
- Size: 114,639,021 bytes; 640,726 triangles in seven connected components.
- SHA-256: `a77680b8dad5041ad0b0fd95f0a491abe6109adc3fc2ee702ca1a2202b081f6f`.

STL does not encode units. We provisionally interpret coordinates as millimetres
at scale 1.0. Bounds are X = -15.5647 to 15.8290, Y = 1.00167 to 34.1165,
Z = -12.9625 to 37.6822. From visual inspection, X is lateral, +Y is dorsal,
and +Z is anterior. Left/right sign and anatomical registration are unverified.
No anatomical landmarks or eye targets have been selected.

The source includes the jaw, attached neck vertebrae, and detached throat-region
and small fragments. The largest component is not watertight. Preserve these
features in this file; modifications belong in a separate print revision.
The [R02 print derivative](../../skull-print-r02/README.md) removes the neck and
loose fragments and simplifies internal anatomy. Its geometric changes do not
establish anatomical correctness, physical fit, or suitability for surgical use.

The CT catalog's STL download control pointed to the `.nii.gz` file when
inspected. Its viewer code instead replaces that extension with `.stl`; the
direct STL link above was verified independently on 2026-10-14.

## Attribution and storage

Credit: Marmoset Brain Connectome / Neuroscientific Apparatus contributors;
Isabela Zimmermann Rollin and colleagues, *An open access resource for marmoset
neuroscientific apparatus*, Imaging Neuroscience 3 (2025),
DOI: 10.1162/imag_a_00483.

The asset uses **CC BY-NC-SA 4.0**, per the catalog and paper's resource terms.
See [LICENSE-source.txt](LICENSE-source.txt). Retain attribution and identify
modifications when redistributing derivatives. The paper's own CC BY 4.0 license
does not replace the asset license.

The repository's existing `*.stl` Git LFS rule covers this source and the saved
print derivative. A normal Git commit stores LFS pointers; collaborators need
Git LFS to retrieve the meshes. No remote upload is performed by adding these files.
