"""Session-local landmark review panel; corrections never overwrite atlas coordinates."""
from pathlib import Path
import json,datetime,math
import FreeCAD as A,FreeCADGui as G
from PySide import QtWidgets,QtCore
S=Path(__file__).resolve().parent
class LandmarkReview(QtWidgets.QDialog):
 def __init__(self,doc):
  super().__init__(G.getMainWindow());self.doc=doc;self.callback=None;self.setWindowTitle('Mouse landmark review');self.setObjectName('SkellyLandmarkReviewR02');self.setWindowFlags(self.windowFlags()|QtCore.Qt.WindowStaysOnTopHint)
  layout=QtWidgets.QVBoxLayout(self);self.combo=QtWidgets.QComboBox();self.points=sorted([o for o in doc.Objects if o.Name.startswith('ReviewLM')],key=lambda o:int(o.SourceID))
  for o in self.points:self.combo.addItem('LM '+o.SourceID+' | '+o.ProposedName,o.Name)
  layout.addWidget(self.combo);self.name=QtWidgets.QLineEdit();layout.addWidget(self.name);self.note=QtWidgets.QLineEdit();self.note.setPlaceholderText('Reason for correction / anatomical evidence');layout.addWidget(self.note)
  self.message=QtWidgets.QLabel('Choose a point, then click Pick on skull.');self.message.setWordWrap(True);layout.addWidget(self.message)
  for text,fn in [('Pick new position on skull',self.pick),('Apply name / note',self.apply_text),('Reset point to original',self.reset_point),('Focus eye-region points',self.focus),('Show all 45 points',self.all_points),('Toggle detailed / existing skull',self.toggle),('Show / hide candidate eyes',self.eyes),('Save correction snapshot',self.export)]:
   b=QtWidgets.QPushButton(text);b.clicked.connect(fn);layout.addWidget(b)
  self.combo.currentIndexChanged.connect(self.select);self.select();self.resize(410,480)
 def current(self):return self.doc.getObject(self.combo.currentData())
 def select(self,*args):
  self.cancel_pick();o=self.current();self.name.setText(o.ProposedName);self.note.setText(o.ReviewerNotes);o.Visibility=True;o.Annotation.Visibility=True;G.Selection.clearSelection();G.Selection.addSelection(o)
  self.message.setText('Original coordinates are retained. Change Placement > Position or pick a skull surface point.')
 def refresh(self,o):
  o.Annotation.Position=o.Placement.Base+A.Vector(0,.35,.35);o.Annotation.LabelText=['LM '+o.SourceID+(' *' if (o.Placement.Base-o.OriginalPosition).Length>1e-8 else '')];self.doc.recompute()
 def cancel_pick(self):
  if self.callback is not None:
   G.getDocument(self.doc.Name).activeView().removeEventCallback('SoMouseButtonEvent',self.callback);self.callback=None
 def pick(self):
  self.cancel_pick();G.Selection.clearSelection();self.callback=G.getDocument(self.doc.Name).activeView().addEventCallback('SoMouseButtonEvent',self.on_click);self.message.setText('Click the visible skull surface. The point moves only when a skull surface is hit.')
 def on_click(self,event):
  if event.get('State')!='DOWN' or event.get('Button')!='BUTTON1':return
  view=G.getDocument(self.doc.Name).activeView();info=view.getObjectInfo(event['Position'])
  if not info or info.get('Object') not in ['DetailedReference','ExistingSkull']:
   self.message.setText('No skull hit. Click a visible skull surface away from a marker.');return
  p=A.Vector(info['x'],info['y'],info['z']);o=self.current();self.doc.openTransaction('Move review landmark');o.Placement.Base=p;o.ReviewState='Proposed correction';self.refresh(o);self.doc.commitTransaction();self.cancel_pick();self.message.setText('LM '+o.SourceID+' moved %.3f mm from its original position.'%(p-o.OriginalPosition).Length)
 def apply_text(self):
  o=self.current();self.doc.openTransaction('Edit landmark description');o.ProposedName=self.name.text();o.ReviewerNotes=self.note.text();o.Label='LM '+o.SourceID+' - '+o.ProposedName;o.ReviewState='Proposed correction';self.doc.commitTransaction();self.refresh(o)
 def reset_point(self):
  self.cancel_pick();o=self.current();self.doc.openTransaction('Reset landmark position');o.Placement.Base=o.OriginalPosition;o.ReviewState='Proposed correction';self.refresh(o);self.doc.commitTransaction()
 def focus(self):
  for o in self.points:o.Visibility=o.SourceID in ['7','8','9','10','11','12','13','16','51'];o.Annotation.Visibility=o.Visibility
 def all_points(self):
  for o in self.points:o.Visibility=True;o.Annotation.Visibility=True
 def toggle(self):
  self.doc.DetailedReference.Visibility=not self.doc.DetailedReference.Visibility;self.doc.ExistingSkull.Visibility=not self.doc.DetailedReference.Visibility;self.doc.ExistingSkull.ViewObject.Transparency=0
 def eyes(self):self.doc.CandidateEyes.Visibility=not self.doc.CandidateEyes.Visibility
 def export(self):
  self.cancel_pick();rows=[]
  for o in self.points:
   self.refresh(o);p=list(o.getGlobalPlacement().Base);assert all(math.isfinite(x) for x in p)
   rows.append({'source_id':o.SourceID,'proposed_name':o.ProposedName,'name_evidence':o.NameEvidence,'original_position_mm':list(o.OriginalPosition),'proposed_position_mm':p,'displacement_mm':(o.getGlobalPlacement().Base-o.OriginalPosition).Length,'review_state':str(o.ReviewState),'notes':o.ReviewerNotes})
  folder=S/'corrections';folder.mkdir(parents=True,exist_ok=True);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');path=folder/('review-'+stamp+'.json');data={'units':'mm','frame':self.doc.ReviewMetadata.CoordinateFrame,'source_study_sha256':self.doc.ReviewMetadata.SourceStudyHash,'created_utc':stamp,'landmarks':rows,'automatic_eye_refit':False}
  with path.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
  self.doc.save();self.message.setText('Saved '+path.name+'. Eye placement is unchanged.');return path
 def closeEvent(self,event):self.cancel_pick();super().closeEvent(event)
doc=A.ActiveDocument
if not doc or not doc.getObject('ReviewMetadata'):raise RuntimeError('Open the R02 landmark review before starting the panel.')
for old in G.getMainWindow().findChildren(QtWidgets.QDialog,'SkellyLandmarkReviewR02'):old.close()
panel=LandmarkReview(doc);panel.show()
# Retain the callback owner for the desktop session.
G._skelly_landmark_review=panel
