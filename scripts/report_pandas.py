"""Summarize successful measured trials and preserve failure visibility."""
from datetime import datetime
import json
from pathlib import Path
from xml.etree import ElementTree

root = Path(__file__).resolve().parents[1]
folder = root / 'results/pandas'
rows = []

def duration(start, end):
    return (datetime.fromisoformat(end.replace('Z', '+00:00')) - datetime.fromisoformat(start.replace('Z', '+00:00'))).total_seconds()

for path in folder.glob('*.json'):
    data = json.loads(path.read_text())
    if 'steps' not in data:
        continue
    steps = {s['name']: s for s in data['steps']}
    if len(steps) != 3 or any(s['exit_code'] != 0 for s in steps.values()):
        continue
    prefix = path.stem
    job = json.loads((folder / f'{prefix}-job.json').read_text())['jobs'][0]
    caching = [s for s in job['steps'] if s['name'] in ['Restore GitHub caches', 'Attach Namespace caches'] and s['conclusion'] == 'success']
    cache_seconds = sum(duration(s['startedAt'], s['completedAt']) for s in caching)
    junit = ElementTree.parse(folder / f'{prefix}-junit.xml')
    suites = list(junit.getroot().iter('testsuite'))
    tests = sum(int(s.attrib.get('tests', 0)) for s in suites)
    failures = sum(int(s.attrib.get('failures', 0)) + int(s.attrib.get('errors', 0)) for s in suites)
    skipped = sum(int(s.attrib.get('skipped', 0)) for s in suites)
    row = [data['provider'], data['phase'],
           *[f"{steps[s]['seconds']:.2f}" for s in ['environment', 'build', 'unit']],
           f"{cache_seconds:.0f}", f"{duration(job['startedAt'], job['completedAt']):.0f}",
           f'{tests-skipped-failures} passed / {skipped} skipped', f"[run]({data['run_url']})"]
    rows.append((data['provider'], ['cold', 'warm', 'edited'].index(data['phase']), row))

table = '| Runner | Phase | Environment (s) | Build (s) | Tests (s) | Cache attach/restore (s) | Whole job (s) | Test result | Evidence |\n'
table += '|---|---|---:|---:|---:|---:|---:|---|---|\n'
table += '\n'.join('| '+' | '.join(row)+' |' for _, _, row in sorted(rows))
text = '# pandas: measured CI results\n\n' + table + '\n\n'
text += 'Only successful trials appear in this table. Raw evidence is in [results/pandas](results/pandas/). Failed setup attempts, if downloaded, are preserved separately.\n\n'
text += 'Whole-job time includes setup, package installation, evidence upload and post-job cache handling; it is not just build time. Cache times come from GitHub step timestamps at one-second resolution. These are individual trials, not a statistical benchmark. The edited phase is a behavior-preserving Python helper rename, not a Cython or C++ change.\n'
(root / 'PANDAS_RESULTS.md').write_text(text)
print(text)
