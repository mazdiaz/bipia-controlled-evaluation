import argparse
from pathlib import Path

from .common import canonical
from .pipeline import build


def main():
    parser = argparse.ArgumentParser(description='Offline BIPIA preflight; no live API support')
    parser.add_argument('--repo',type=Path,default=Path('vendor/BIPIA'))
    parser.add_argument('--out',type=Path,default=Path('artifacts'))
    parser.add_argument('--bootstrap-repetitions',type=int,default=10000)
    parser.add_argument('--no-mock',action='store_true')
    args = parser.parse_args()
    result = build(args.repo,args.out,bootstrap_repetitions=args.bootstrap_repetitions,mock=not args.no_mock)
    print(canonical(dict(recommendation=result['recommendation'],p0={k:v['status'] for k,v in result['p0_gates'].items()},scenarios={s:dict(cases=r['cases'],planned=r['planned_invocations'],token_status=r['tokens']['status']) for s,r in result['scenarios'].items()})))


if __name__ == '__main__':
    main()
