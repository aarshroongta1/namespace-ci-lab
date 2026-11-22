"""Save ccache decisions and public compiler/header inputs, without dumping env."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
source = root/'upstream-pandas'
out = root/os.environ['RESULTS_DIRECTORY']
out.mkdir(parents=True, exist_ok=True)
debug = Path(os.environ['CCACHE_DEBUGDIR'])
logs = []
for path in debug.rglob('*.ccache-log'):
    text = path.read_text(errors='replace')
    relative = str(path.relative_to(debug))
    logs.append(f'FILE: {relative}\n{text}')
(out/'ccache-decisions.log').write_text('\n\n'.join(logs))
for pattern, label in [('*.ccache-input-text','input')]:
    for path in debug.rglob(pattern):
        if 'meson-generated_base.pyx.c.o.' in path.name:
            shutil.copyfile(path, out/'base.ccache-input-text')
            break
subprocess.run(['ccache','--show-config'], stdout=(out/'ccache-config.txt').open('w'), check=True)
probe = r'''
import hashlib,json,os,sys,sysconfig
from pathlib import Path
import numpy
base=Path(sys.prefix)
files={}
for label,directory in [('python',Path(sysconfig.get_path('include'))),('numpy',Path(numpy.get_include()))]:
    for path in directory.rglob('*.h'):
        files[label+':'+str(path.relative_to(directory))]=hashlib.sha256(path.read_bytes()).hexdigest()
for name in ['x86_64-conda-linux-gnu-cc','x86_64-conda-linux-gnu-c++']:
    path=base/'bin'/name
    stat=path.stat()
    files['compiler:'+name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size=stat.st_size,mtime_ns=stat.st_mtime_ns,realpath=str(path.resolve()))
for name in ['/usr/include/features.h','/usr/include/stdlib.h','/usr/include/x86_64-linux-gnu/bits/libc-header-start.h']:
    p=Path(name)
    if p.exists(): files[name]=hashlib.sha256(p.read_bytes()).hexdigest()
print(json.dumps(dict(prefix=str(base),headers=files,python=sys.version,config={k:sysconfig.get_config_var(k) for k in ['CC','CXX','CFLAGS','CONFIG_ARGS','SOABI']}),indent=2))
'''
result = subprocess.run(['pixi','run','--locked','-e','py312','python','-c',probe],cwd=source,capture_output=True,text=True)
(out/'header-hashes.json').write_text(result.stdout)
(out/'probe-errors.log').write_text(result.stderr)
models = sorted(set(line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')))
(out/'hardware.json').write_text(json.dumps(dict(cpu_models=models),indent=2)+'\n')
print(f'Saved {len(logs)} ccache decisions, representative compiler input, and header hashes.')
