"""Find a live review by physical path before opening or rebuilding it."""
import os
from pathlib import Path


def find_open_document(app, path):
    target = os.path.normcase(str(Path(path).resolve()))
    matches = [doc for doc in app.listDocuments().values()
               if doc.FileName and os.path.normcase(str(Path(doc.FileName).resolve())) == target]
    if len(matches) > 1:
        raise RuntimeError('Multiple live documents own this path; archive the session before saving: ' + target)
    if matches:
        app.setActiveDocument(matches[0].Name)
        return matches[0]
    return None
