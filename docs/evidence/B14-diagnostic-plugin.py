import traceback

def pytest_configure(config):
 from app.services.operations.storage import Storage
 old=Storage.commit
 def commit(*args,**kw):
  try:return old(*args,**kw)
  except Exception as e:
   print('SANITIZED_STORAGE_DIAGNOSTIC',type(e).__name__,[(x.name,x.lineno) for x in traceback.extract_tb(e.__traceback__)])
   raise
 Storage.commit=commit
