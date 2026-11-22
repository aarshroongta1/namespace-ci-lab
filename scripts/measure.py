"""Measure an upstream CI slice, preserving command output and exit status."""
import json
import os
from pathlib import Path
import platform
import subprocess
import time

root = Path(__file__).resolve().parents[1]
out = root / 'results'
out.mkdir(exist_ok=True)
source = root / 'upstream'
phase = os.environ['PHASE']
provider = os.environ['PROVIDER']
if phase == 'edited':
    with (source / 'packages/vite/src/node/constants.ts').open('a') as f:
        f.write('\n// Namespace CI experiment: source edit, unchanged dependency lockfile.\n')
store = root / 'cache-store'
record = dict(provider=provider, phase=phase, source_sha=subprocess.check_output(
    ['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip(),
    source_modified=phase == 'edited', run_url=os.environ['RUN_URL'],
    cpu_count=os.cpu_count(), platform=platform.platform(),
    memory_kib=next(line.strip() for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemTotal:')),
    cache_files_before=sum(1 for p in store.rglob('*') if p.is_file()), steps=[])
commands = [('install', ['pnpm', 'install', '--frozen-lockfile', '--store-dir', str(store)]),
            ('build', ['pnpm', 'run', 'build']), ('unit', ['pnpm', 'run', 'test-unit'])]
try:
    for name, command in commands:
        start = time.monotonic()
        log = out / f'{provider}-{phase}-{name}.log'
        with log.open('w') as f:
            result = subprocess.run(command, cwd=source, stdout=f, stderr=subprocess.STDOUT)
        record['steps'].append(dict(name=name, seconds=round(time.monotonic()-start, 3), exit_code=result.returncode))
        print(log.read_text()[-10000:], flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
finally:
    record['cache_files_after'] = sum(1 for p in store.rglob('*') if p.is_file())
    (out / f'{provider}-{phase}.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2), flush=True)
