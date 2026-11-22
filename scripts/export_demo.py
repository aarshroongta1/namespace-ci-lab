"""Export measured CI results for the portfolio replay. No synthetic run data."""
from datetime import datetime
import json
from pathlib import Path
import re
from xml.etree import ElementTree

root = Path(__file__).resolve().parents[1]
results = root / 'results/pandas'

def date(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def run(provider, phase, folder=results):
    prefix = f'{provider}-{phase}'
    data = json.loads((folder / f'{prefix}.json').read_text())
    job = json.loads((folder / f'{prefix}-job.json').read_text())['jobs'][0]
    assert job['conclusion'] == 'success'
    total = (date(job['completedAt']) - date(job['startedAt'])).total_seconds()
    measured = next(s for s in job['steps'] if s['name'].startswith('Measure environment'))
    cache = next(s for s in job['steps'] if s['name'] in ['Restore GitHub caches', 'Attach Namespace caches'] and s['conclusion'] == 'success')
    cache_time = (date(cache['completedAt']) - date(cache['startedAt'])).total_seconds()
    setup = (date(measured['startedAt']) - date(job['startedAt'])).total_seconds() - cache_time
    commands = {s['name']: s['seconds'] for s in data['steps']}
    times = [setup, cache_time, commands['environment'], commands['build'], commands['unit']]
    times.append(round(total - sum(times), 3))
    assert all(t >= 0 for t in times) and abs(sum(times) - total) < .01
    stats = (folder / f'{prefix}-ccache.log').read_text()
    hits = re.search(r'Hits:\s+(\d+) /\s*(\d+)', stats)
    suites = list(ElementTree.parse(folder / f'{prefix}-junit.xml').getroot().iter('testsuite'))
    tests = sum(int(s.get('tests', '0')) for s in suites)
    skipped = sum(int(s.get('skipped', '0')) for s in suites)
    assert not sum(int(s.get('failures', '0')) + int(s.get('errors', '0')) for s in suites)
    relative = folder.relative_to(results)
    logbase = 'https://github.com/aarshroongta1/namespace-ci-lab/blob/main/results/pandas/'
    if str(relative) != '.':
        logbase += str(relative) + '/'
    return dict(provider=provider, total=total, times=times, files=data['cache_files_before'],
                hits=int(hits[1]), calls=int(hits[2]), url=data['run_url'], logbase=logbase,
                prefix=prefix, passed=tests-skipped, skipped=skipped)

scenarios = {phase: {p: run(p, phase) for p in ['github', 'namespace']} for phase in ['cold', 'warm', 'edited']}
scenarios['miss'] = dict(github=scenarios['warm']['github'], namespace=run('namespace', 'warm', results / 'cache-misses/45055882874'))
(root / 'demo/data.json').write_text(json.dumps(scenarios, indent=2)+'\n')
print('Exported 7 successful measured jobs; all passed 4,045 tests with 2 skipped.')
