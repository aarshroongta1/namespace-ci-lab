"""Render only measured successful runs; missing phases stay visibly missing."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = []
for path in (root / 'results').glob('*.json'):
    record = json.loads(path.read_text())
    if 'steps' not in record:
        continue
    steps = {s['name']: s for s in record['steps']}
    ok = len(steps) == 3 and all(s['exit_code'] == 0 for s in steps.values())
    times = [f"{steps[name]['seconds']:.2f}" if name in steps else '—' for name in ['install', 'build', 'unit']]
    total = f"{sum(s['seconds'] for s in steps.values()):.2f}" if ok else 'failed'
    row = [record['provider'], record['phase'], *times, total,
           str(record['cache_files_before']), f"[run]({record['run_url']})"]
    rows.append((record['provider'], ['cold', 'warm', 'edited'].index(record['phase']), row))
header = '| Provider | Phase | Install (s) | Build (s) | Unit tests (s) | Command total (s) | Cache files before | Evidence |\n'
header += '|---|---|---:|---:|---:|---:|---:|---|\n'
body = '\n'.join('| ' + ' | '.join(row) + ' |' for _, _, row in sorted(rows))
text = '# Measured results\n\n' + header + body + '\n\nCommand totals exclude cache transfer and other job overhead. Missing rows are not measured. See README for scope and limitations.\n'
(root / 'RESULTS.md').write_text(text)
print(text)
