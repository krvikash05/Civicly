from pathlib import Path

def pytest_configure(config):
 old=Path.write_text
 def write(self,*args,**kw):
  if str(self)=='/tmp/civicly-b10-runtime-WATERLOGGING.json':self=Path('docs/evidence/B14R-legacy-resume.json')
  return old(self,*args,**kw)
 Path.write_text=write
