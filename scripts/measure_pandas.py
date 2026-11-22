"""Measure a bounded pandas source-build CI slice on a fresh runner."""
import json
import os
from pathlib import Path
import platform
import subprocess
import time

root = Path(__file__).resolve().parents[1]
source = root / 'upstream-pandas'
out = root / os.environ.get('RESULTS_DIRECTORY', 'results/pandas')
out.mkdir(parents=True, exist_ok=True)
phase, provider = os.environ['PHASE'], os.environ['PROVIDER']
prefix = f'{provider}-{phase}'
if phase == 'edited':
    path = source / 'pandas/core/groupby/groupby.py'
    text = path.read_text()
    start, end = text.index('    def prod('), text.index('    def min(')
    original = text[start:end]
    assert original.count('prod_compat') == 2
    path.write_text(text[:start] + original.replace('prod_compat', 'product_compat') + text[end:])
    (out / f'{prefix}.patch').write_text(subprocess.check_output(['git', 'diff'], cwd=source, text=True))
cache = Path(os.environ['PIXI_CACHE_DIR']).parent
record = dict(project='pandas', provider=provider, phase=phase,
              cohort=os.environ['COHORT'], run_url=os.environ['RUN_URL'],
              source_sha=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip(),
              cpu_count=os.cpu_count(), platform=platform.platform(),
              memory=next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')),
              cache_files_before=sum(p.is_file() for p in cache.rglob('*')),
              steps=[])
commands = [
    ('environment', ['pixi', 'install', '--locked', '-e', 'py312']),
    ('build', ['pixi', 'run', '--locked', '-e', 'py312', 'bash', '-c',
               'export CC="ccache $(command -v x86_64-conda-linux-gnu-cc || command -v gcc)" '
               'CXX="ccache $(command -v x86_64-conda-linux-gnu-c++ || command -v g++)"; '
               'echo "CC=$CC CXX=$CXX"; '
               'python -m pip install --verbose --editable . --no-build-isolation --no-deps '
               '--config-settings builddir=build/py312 --config-settings compile-args=-j2']),
    ('unit', ['pixi', 'run', '--locked', '-e', 'py312', 'python', '-m', 'pytest',
              'pandas/tests/groupby/test_reductions.py', 'pandas/tests/groupby/test_groupby.py',
              '-q', '-n', '2', '--dist=worksteal', '-m', 'not slow and not network and not single_cpu',
              '--junitxml=' + str(out / f'{prefix}-junit.xml')]),
]
subprocess.run(['ccache', '--zero-stats'], check=True)
try:
    if phase == 'cold' and record['cache_files_before']:
        raise RuntimeError('Cold trial found existing cached files. Use a fresh cohort.')
    if phase != 'cold' and not record['cache_files_before']:
        raise RuntimeError('Requested a warm cache, but found no cached files.')
    for name, command in commands:
        start = time.monotonic()
        log = out / f'{prefix}-{name}.log'
        with log.open('w') as stream:
            result = subprocess.run(command, cwd=source, stdout=stream, stderr=subprocess.STDOUT)
        record['steps'].append(dict(name=name, seconds=round(time.monotonic()-start, 3), exit_code=result.returncode))
        print(log.read_text()[-14000:], flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
finally:
    record['cache_files_after'] = sum(p.is_file() for p in cache.rglob('*'))
    for name, command in [('ccache', ['ccache', '--show-stats', '--verbose']),
                          ('versions', ['pixi', 'list', '--locked', '-e', 'py312'])]:
        result = subprocess.run(command, cwd=source, capture_output=True, text=True)
        (out / f'{prefix}-{name}.log').write_text(result.stdout + result.stderr)
    (out / f'{prefix}.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2), flush=True)
