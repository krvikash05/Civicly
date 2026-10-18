"""Lossless provider-only repeated-value packing; evidence/checkpoints untouched."""
import copy,json
from collections import Counter
from app.graph.models import digest

VERSION='CONTEXT-WIRE-1'
MAX_DEPTH=48


def raw(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def pack(context):
    counts=Counter();sizes={}
    def collect(value,depth=0):
        if depth>MAX_DEPTH:raise ValueError('CONTEXT_WIRE_DEPTH')
        if isinstance(value,(dict,list,str)):
            encoded=raw(value);size=len(encoded.encode())
            if size>=48:
                key=digest(value);counts[key]+=1;sizes[key]=size
            if isinstance(value,dict):
                for v in value.values():collect(v,depth+1)
            elif isinstance(value,list):
                for v in value:collect(v,depth+1)
    # Source-tag collisions are opaque and retained literally; never interpret untrusted references.
    def escape(value):
        if isinstance(value,dict):
            if set(value) in ({'wire_ref'},{'wire_literal'}):return {'wire_literal':raw(value)}
            return {k:escape(v) for k,v in value.items()}
        if isinstance(value,list):return [escape(v) for v in value]
        return value
    source=escape(context);collect(source);values={};ids={}
    def intern(value,root=False):
        if isinstance(value,(dict,list,str)):
            key=digest(value);size=sizes.get(key,0);count=counts[key]
            if not root and count>1 and (size-24)*(count-1)>32:
                if key not in ids:
                    index=str(len(ids));ids[key]=index;values[index]=intern(value,True)
                return {'wire_ref':ids[key]}
        if isinstance(value,dict):return {k:intern(v) for k,v in value.items()}
        if isinstance(value,list):return [intern(v) for v in value]
        return value
    envelope={'wire_version':VERSION,'context':intern(source,True),'wire_values':values}
    # Size alone is insufficient: hashes tokenize differently. Keep original on proxy-token regression.
    from .tokens import tokenizer
    before=raw(context);after=raw(envelope)
    if len(after.encode())>=len(before.encode()) or len(tokenizer().encode(after))>=len(tokenizer().encode(before)):return copy.deepcopy(context)
    if unpack(envelope)!=context:raise ValueError('CONTEXT_WIRE_ROUNDTRIP_FAILED')
    return envelope


def unpack(value):
    if value.get('wire_version')!=VERSION:return copy.deepcopy(value)
    values=value['wire_values']
    def expand(item,stack=frozenset()):
        if isinstance(item,list):return [expand(v,stack) for v in item]
        if not isinstance(item,dict):return item
        if set(item)=={'wire_ref'}:
            key=item['wire_ref']
            if key in stack or key not in values:raise ValueError('CONTEXT_WIRE_REFERENCE_INVALID')
            return expand(values[key],stack|{key})
        if set(item)=={'wire_literal'}:return json.loads(item['wire_literal'])
        return {k:expand(v,stack) for k,v in item.items()}
    return expand(value['context'])
