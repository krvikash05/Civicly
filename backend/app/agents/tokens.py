"""Offline tokenizer proxy estimates, never byte counts or provider-confirmed tokens."""
import hashlib,json,math
from functools import lru_cache
from pathlib import Path
import sentencepiece as spm
from app.active import ROOT
from .limits import MAX_COUNT_RESPONSE,MAX_RECEIPT_TOKENS

ASSET=ROOT/'.runtime/tokenizers/gemma3.model'
SHA256='1299c11d7cf632ef3b4e11937501358ada021bbdf7c47638d13c0ee982f2e79c'
URL='https://raw.githubusercontent.com/google/gemma_pytorch/014acb7ac4563a5f77c76d7ff98f31b568c16508/tokenizer/gemma3_cleaned_262144_v2.spiece.model'
VERSION='gemma3-proxy-3.8-v1'

@lru_cache(maxsize=1)
def tokenizer():
    if not ASSET.is_file():raise ValueError('OFFLINE_TOKENIZER_MISSING: run scripts/configure_tokenizer.py')
    data=ASSET.read_bytes()
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('OFFLINE_TOKENIZER_HASH_MISMATCH')
    return spm.SentencePieceProcessor(model_proto=data)

def plan(body,*,provider_count=None):
    """Count complete steering JSON as well as prompt; no chars/bytes-to-token ratio."""
    encoded=json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False)
    local=len(tokenizer().encode(encoded,out_type=int))
    if provider_count is not None:
        if type(provider_count)is not int or not 0<=provider_count<=MAX_COUNT_RESPONSE:raise ValueError('INVALID_PROVIDER_COUNT')
        allowance=provider_count+16;method='PROVIDER_COUNT_WITH_16_FRAMING_ALLOWANCE'
    else:
        allowance=math.ceil(local*1.25)+256;method='LOCAL_PROXY_ESTIMATE_25_PERCENT_PLUS_256'
    output=body['generationConfig']['maxOutputTokens']
    return {'serialized_utf8_bytes':len(encoded.encode()),'local_proxy_tokens':local,'tokenizer_version':VERSION,
        'provider_count_tokens':provider_count,'method':method,'input_allowance_tokens':allowance,'output_allowance_tokens':output,
        'total_allowance_tokens':allowance+output,'uncertainty':'Gemma3 is not verified exact for Gemini3.8; live mode additionally counts full request with provider. Framing/model accounting may differ; actual usage is authoritative.'}

def total_usage(usage):
    value=usage.get('totalTokenCount')
    return value if type(value)is int and 0<=value<=MAX_RECEIPT_TOKENS else None
