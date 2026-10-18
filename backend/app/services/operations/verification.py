"""B14-2 synthetic demo observation policy; no hidden truth or provider access."""
from app.graph.schema import timestamp
from app.graph.repository import PreconditionFailed

VERSION = 'B14-2'
CODES = {
 'ACTION_COMPLETED':None, 'ACTION_FAILED':None,
 'COMPARABLE_FOLLOWUP_RAINFALL':None, 'FOLLOWUP_WATERLOGGING':'boolean',
 'WEAR_EXPOSURE':None, 'FOLLOWUP_PAVEMENT':'boolean',
 'SCHEDULED_PICKUPS':'pickups', 'ACTUAL_PICKUPS':'pickups',
 'REACCUMULATION_WINDOW':'hours', 'WASTE_REACCUMULATION':'boolean',
}
REQUIRED = {
 'WATERLOGGING':('COMPARABLE_FOLLOWUP_RAINFALL','FOLLOWUP_WATERLOGGING'),
 'ROAD_DAMAGE':('WEAR_EXPOSURE','FOLLOWUP_PAVEMENT'),
 'WASTE_ACCUMULATION':('SCHEDULED_PICKUPS','ACTUAL_PICKUPS','REACCUMULATION_WINDOW','WASTE_REACCUMULATION'),
}

def validate_observation(ob, allowed):
 if ob.code not in allowed or ob.method != 'DIRECT_SYNTHETIC_FIELD_TEST':
  raise PreconditionFailed('OBSERVATION_CODE_OR_METHOD')
 if ob.result=='UNKNOWN' and ob.value is None and ob.unit is None:return
 if ob.code in CODES:
  unit=CODES[ob.code]
  if ob.unit!=unit or (unit is None and ob.value is not None):raise PreconditionFailed('OBSERVATION_UNIT')
  if unit=='boolean' and ob.value not in (0.0,1.0):raise PreconditionFailed('OBSERVATION_BOOLEAN')
  if unit in {'hours','pickups'} and (ob.value is None or ob.value<0 or (unit=='pickups' and ob.value!=int(ob.value))):raise PreconditionFailed('OBSERVATION_QUANTITY')
 elif ob.value is not None or ob.unit is not None:raise PreconditionFailed('UNSPECIFIED_MEASUREMENT_UNIT')

def evaluate(issue, targets, observations, start, end, completed_at, now):
 """Return classification and gaps; all targets must qualify, never choose one row."""
 lo,hi,done,at=map(timestamp,[start,end,completed_at,now])
 if not done<lo<=hi<=at:raise PreconditionFailed('OUTCOME_WINDOW_ORDER')
 gaps=[];adverse=False;contradictory=False;opportunity=True
 for target in targets:
  rows={code:[] for code in REQUIRED[issue]}
  for ob in observations:
   if ob.asset_id!=target:continue
   validate_observation(ob,set(REQUIRED[issue]))
   when=timestamp(ob.observed_at)
   if not lo<=when<=hi:raise PreconditionFailed('OUTCOME_EVIDENCE_OUTSIDE_WINDOW')
   if ob.result=='OBSERVED':rows[ob.code].append(ob)
   else:gaps.append(target+': unknown '+ob.code);opportunity=False
  missing=[code for code,values in rows.items() if not values]
  if missing:
   gaps.append(target+': missing '+','.join(missing));opportunity=False;continue
  final=rows[REQUIRED[issue][-1]]
  values={ob.value for ob in final}
  contradictory |= len(values)>1
  adverse |= 1.0 in values
  if issue in {'WATERLOGGING','ROAD_DAMAGE'}:
   exposure=rows[REQUIRED[issue][0]]
   if min(timestamp(x.observed_at) for x in final)<max(timestamp(x.observed_at) for x in exposure):
    gaps.append(target+': final finding precedes exposure');opportunity=False
  else:
   scheduled={x.value for x in rows['SCHEDULED_PICKUPS']};actual={x.value for x in rows['ACTUAL_PICKUPS']}
   if len(scheduled)!=1 or len(actual)!=1:contradictory=True
   elif min(scheduled)<1 or scheduled!=actual:
    gaps.append(target+': scheduled/actual pickup coverage insufficient');opportunity=False
   windows=rows['REACCUMULATION_WINDOW']
   # Equal aggregate counts do not identify vehicles or independent pickups.
   # Conservatively restart observation at the latest actual pickup timestamp.
   anchor=max(timestamp(x.observed_at) for x in rows['ACTUAL_PICKUPS'])
   if any(x.value<24 or (timestamp(x.observed_at)-anchor).total_seconds()<x.value*3600 for x in windows):
    gaps.append(target+': synthetic24hour post-pickup observation window not established');opportunity=False
   if min(timestamp(x.observed_at) for x in final)<max(timestamp(x.observed_at) for x in windows):
    gaps.append(target+': reaccumulation finding precedes window');opportunity=False
   if any(timestamp(x.observed_at)>min(timestamp(v.observed_at) for v in windows) for code in ['SCHEDULED_PICKUPS','ACTUAL_PICKUPS'] for x in rows[code]):
    gaps.append(target+': pickups follow observation window');opportunity=False
 if contradictory:return 'INCONCLUSIVE',gaps+['Contradictory observations retained; no source arbitration']
 if not opportunity:return 'MONITORING',gaps
 return ('PROBLEM_PERSISTS' if adverse else 'RESOLUTION_VERIFIED'),gaps
