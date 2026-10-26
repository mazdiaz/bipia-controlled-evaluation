"""Acquire original source without installing/running archived BIPIA code."""
import argparse
from pathlib import Path
import subprocess

COMMIT = 'a004b69ec0dd446e0afd461d98cb5e96e120a5d0'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=Path('vendor/BIPIA'))
    args = parser.parse_args()
    repo = args.repo
    if not repo.exists():
        repo.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','clone','--config','core.autocrlf=false','https://github.com/microsoft/BIPIA.git',str(repo)],check=True)
        subprocess.run(['git','-C',str(repo),'checkout','--detach',COMMIT],check=True)
    head = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD']).decode().strip()
    if head != COMMIT:
        raise SystemExit('Existing repository is not pinned. Preserve it; use another --repo directory.')
    print('Verified source commit:',head)


if __name__=='__main__':
    main()
