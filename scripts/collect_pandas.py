"""Download completed pandas evidence without mixing it with other experiments."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

repo = 'aarshroongta1/namespace-ci-lab'
out = Path(__file__).resolve().parents[1] / 'results/pandas'
out.mkdir(parents=True, exist_ok=True)
for run_id in sys.argv[1:]:
    run = json.loads(subprocess.check_output(
        ['gh', 'run', 'view', run_id, '-R', repo, '--json', 'status,conclusion,jobs,url,createdAt'], text=True))
    if run['status'] != 'completed':
        raise SystemExit(f'Run {run_id} is not complete')
    artifacts = json.loads(subprocess.check_output(
        ['gh', 'api', f'repos/{repo}/actions/runs/{run_id}/artifacts'], text=True))['artifacts']
    artifact = next(a for a in artifacts if a['name'].startswith('pandas-'))
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['gh', 'run', 'download', run_id, '-R', repo, '-n', artifact['name'], '-D', tmp], check=True)
        records = []
        for path in Path(tmp).rglob('*.json'):
            record = json.loads(path.read_text())
            if record.get('run_url') == run['url'] and 'steps' in record:
                records.append((path, record))
        path, record = records[0]
        prefix = f"{record['provider']}-{record['phase']}"
        destination = out if run['conclusion'] == 'success' else out / 'failed-attempts' / run_id
        destination.mkdir(parents=True, exist_ok=True)
        for evidence in path.parent.glob(prefix + '*'):
            shutil.copyfile(evidence, destination / evidence.name)
        (destination / f'{prefix}-job.json').write_text(json.dumps(run, indent=2)+'\n')
        print(f"{run_id}: {run['conclusion']} -> {destination}")
