"""Run accepted tests verbatim while preserving their historical evidence paths."""
from pathlib import Path

def pytest_configure(config):
 old=Path.write_text
 def write(self,*args,**kw):
  if str(self).startswith('docs/evidence/B13-'):
   self=self.with_name('B14-regression-'+self.name)
  return old(self,*args,**kw)
 Path.write_text=write
