"""Collect the controlled runner/cache comparison and export its visual replay."""
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree

root = Path(__file__).resolve().parents[1]
repo = 'aarshroongta1/namespace-ci-lab'
run_id = sys.argv[1]
def gh(*args):
    return json.loads(subprocess.check_output(['gh', *args], text=True))
def date(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))
run = gh('api', f'repos/{repo}/actions/runs/{run_id}')
jobs = gh('api', f'repos/{repo}/actions/runs/{run_id}/jobs')['jobs']
if run['status'] != 'completed':
    raise SystemExit('Wait for the comparison to finish.')
results = root / 'results/pandas-migration'
results.mkdir(parents=True, exist_ok=True)
(results / 'workflow.json').write_text(json.dumps(run, indent=2)+'\n')
(results / 'jobs.json').write_text(json.dumps(jobs, indent=2)+'\n')
variants = []
for variant, title, description in [
    ('github', 'GitHub', 'Existing runner and archive cache'),
    ('namespace-runner', 'Namespace runner', 'Only the runner changes; archive cache stays'),
    ('namespace-volume', 'Namespace with Cache Volume', 'Same runner; cached paths mounted on a volume'),
]:
    job = next(j for j in jobs if j['name'] == variant)
    if job['conclusion'] != 'success':
        raise SystemExit(f'{variant}: {job["conclusion"]}; not a valid passing result.')
    folder = results / variant
    folder.mkdir(exist_ok=True)
    artifact = f'pandas-migration-{variant}-{run_id}'
    with tempfile.TemporaryDirectory() as temp:
        subprocess.run(['gh','run','download',run_id,'-R',repo,'-n',artifact,'-D',temp],check=True)
        for file in Path(temp).rglob('*'):
            if file.is_file():
                shutil.copyfile(file, folder / file.name)
    prefix = f'{variant}-edited'
    data = json.loads((folder / f'{prefix}.json').read_text())
    steps = {s['name']:s for s in data['steps']}
    assert len(steps) == 3 and all(s['exit_code']==0 for s in steps.values())
    cache = next(s for s in job['steps'] if s['name'] in ['Restore existing cache archive','Attach Namespace Cache Volume'] and s['conclusion']=='success')
    measure = next(s for s in job['steps'] if s['name']=='Build pandas and run groupby checks')
    # GitHub timestamps are second-resolution. Wait includes dispatch and scheduling.
    wait = (date(job['started_at'])-date(run['created_at'])).total_seconds()
    cache_time = (date(cache['completed_at'])-date(cache['started_at'])).total_seconds()
    setup = (date(measure['started_at'])-date(job['started_at'])).total_seconds()-cache_time
    commands = [steps[k]['seconds'] for k in ['environment','build','unit']]
    total = (date(job['completed_at'])-date(run['created_at'])).total_seconds()
    times = [wait,setup,cache_time,*commands]
    times.append(round(total-sum(times),3))
    assert all(x>=0 for x in times) and abs(sum(times)-total)<.01
    stats=(folder/f'{prefix}-ccache.log').read_text()
    hits=re.search(r'Hits:\s+(\d+) /\s*(\d+)',stats)
    suites=list(ElementTree.parse(folder/f'{prefix}-junit.xml').getroot().iter('testsuite'))
    tests=sum(int(s.get('tests','0')) for s in suites)
    skipped=sum(int(s.get('skipped','0')) for s in suites)
    assert not sum(int(s.get('failures','0'))+int(s.get('errors','0')) for s in suites)
    assert data['cache_files_before']>0
    variants.append(dict(id=variant,title=title,description=description,total=total,
        job_seconds=total-wait,times=times,passed=tests-skipped,skipped=skipped,
        hits=int(hits[1]),calls=int(hits[2]),files=data['cache_files_before'],
        url=job['html_url'],prefix=prefix,
        logbase=f'https://github.com/{repo}/blob/main/results/pandas-migration/{variant}/'))
export=dict(run_id=run_id,created_at=run['created_at'],head_sha=run['head_sha'],
            workflow_url=run['html_url'],variants=variants)
(root/'demo/migration.json').write_text(json.dumps(export,indent=2)+'\n')
lines=['# pandas: controlled runner migration comparison','',
       'All three configurations ran in one workflow dispatch, with the same source edit, build, tests, and dependency lockfile.','',
       '| Configuration | Wait to start | Job runtime | Dispatch to passing result | Build | Cache restore/attach | Compiler hits | Tests |',
       '|---|---:|---:|---:|---:|---:|---:|---|']
for v in variants:
    lines.append(f'| [{v["title"]}]({v["url"]}) | {v["times"][0]:.0f}s | {v["job_seconds"]:.0f}s | {v["total"]:.0f}s | {v["times"][4]:.2f}s | {v["times"][2]:.0f}s | {v["hits"]}/{v["calls"]} | {v["passed"]:,} passed |')
lines += ['', 'The first comparison changes the runner while retaining actions/cache. The second changes to Namespace Cache Volumes on the same Namespace runner profile. The existing archive was populated on GitHub; the Cache Volume was populated by earlier Namespace builds. Restored data does not imply reusable compiler outputs: the runner-only migration hit just 3/59 calls. The reason for those mismatches was not isolated. Do not attribute the runner-only/volume gap solely to storage speed. One run per configuration, not a broad benchmark. No upstream PR was opened.']
(root/'MIGRATION_RESULTS.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
