"""Download pinned Node archives on a connected PC; never install or touch IO."""
import argparse
import hashlib
from pathlib import Path
import urllib.request

def main():
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    parser.add_argument('--pc-test',action='store_true');args=parser.parse_args()
    args.directory.mkdir(parents=True,exist_ok=True)
    base='https://nodejs.org/dist/v16.20.2/'
    sums=urllib.request.urlopen(base+'SHASUMS256.txt',timeout=60).read()
    expected=dict((line.split()[1],line.split()[0]) for line in sums.decode().splitlines())
    (args.directory/'NODE_SHASUMS256.txt').write_bytes(sums)
    for arch in ['armv7l']+(['x64'] if args.pc_test else []):
        name='node-v16.20.2-linux-'+arch+'.tar.xz';dest=args.directory/name
        if not dest.exists():
            with urllib.request.urlopen(base+name,timeout=60) as src, dest.open('xb') as out:
                while True:
                    block=src.read(1024*1024)
                    if not block:break
                    out.write(block)
        digest=hashlib.sha256(dest.read_bytes()).hexdigest()
        if digest!=expected[name]:raise ValueError('HASH MISMATCH '+str(dest))
        print(digest+'  '+name)
if __name__=='__main__':main()
