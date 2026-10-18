"""Trusted local operator accounting; no network, no blanket hold clearing."""
import argparse,json
from .spending import Ledger

def main():
    p=argparse.ArgumentParser();p.add_argument('--ledger');sub=p.add_subparsers(dest='command')
    cfg=sub.add_parser('configure');cfg.add_argument('--project-usd',required=True);cfg.add_argument('--case-usd',required=True);cfg.add_argument('--complex-usd',default='1.50');cfg.add_argument('--operator',required=True);cfg.add_argument('--reason',required=True);cfg.add_argument('--authorize',action='store_true');cfg.add_argument('--max-concurrent',type=int,default=1)
    inspect=sub.add_parser('hold');inspect.add_argument('request_id')
    resolve=sub.add_parser('resolve-hold');resolve.add_argument('request_id')
    for flag in ['operator','reason','verified-pricing','usage-sha256','evidence-ref']:resolve.add_argument('--'+flag,required=True)
    resolve.add_argument('--authorize',action='store_true')
    args=p.parse_args();ledger=Ledger(args.ledger) if args.ledger else Ledger()
    if args.command=='configure':
        if not args.authorize:p.error('Explicit --authorize required')
        ledger.update_limits(reason=args.operator+': '+args.reason,project_limit=args.project_usd,default_case_limit=args.case_usd,complex_case_limit=args.complex_usd,max_concurrent=args.max_concurrent)
    elif args.command=='resolve-hold':ledger.resolve_hold(args.request_id,authorized=args.authorize,operator=args.operator,reason=args.reason,verified_pricing=args.verified_pricing,usage_sha256=args.usage_sha256,evidence_ref=args.evidence_ref)
    print(json.dumps(ledger.inspect_hold(args.request_id) if args.command in ['hold','resolve-hold'] else ledger.summary(),indent=2))
if __name__=='__main__':main()
