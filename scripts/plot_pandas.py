"""Render measured whole-job time, including overhead, as a standalone chart.

Run: uv run --with matplotlib python scripts/plot_pandas.py
"""
from datetime import datetime
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
folder = root / 'results/pandas'
records = []
paths = list(folder.glob('*.json')) + list((folder / 'cache-misses').glob('*/*.json'))
paths = [p for p in paths if '-job' not in p.stem]
paths.sort(key=lambda p: (json.loads(p.read_text())['provider'],
                         ['cold', 'warm', 'edited'].index(json.loads(p.read_text())['phase']),
                         json.loads(p.read_text())['run_url']))
for path in paths:
    record = json.loads(path.read_text())
    job = json.loads((path.parent / f'{path.stem}-job.json').read_text())['jobs'][0]
    if job['conclusion'] != 'success':
        continue
    start, end = [datetime.fromisoformat(job[k].replace('Z', '+00:00')) for k in ['startedAt', 'completedAt']]
    total = (end-start).total_seconds()
    parts = {s['name']: s['seconds'] for s in record['steps']}
    parts['other'] = max(0, total-sum(parts.values()))
    phase = record['phase']
    if phase != 'cold' and not record['cache_files_before']:
        phase = 'repeat (cache miss)'
    records.append((record['provider'], phase, total, parts))

fig, ax = plt.subplots(figsize=(11, 7.2))
fig.subplots_adjust(left=.29, right=.95, top=.77, bottom=.18)
fig.set_facecolor('#faf9f6')
ax.set_facecolor('#faf9f6')
colors = dict(environment='#93b9c5', build='#27556a', unit='#db9a58', other='#d9d6cf')
labels = dict(environment='Environment', build='Source build', unit='Groupby tests', other='Setup, cache transfer & other overhead')
left = [0.0] * len(records)
for part in ['environment', 'build', 'unit', 'other']:
    values = [r[3][part] for r in records]
    ax.barh(range(len(records)), values, left=left, color=colors[part], label=labels[part], height=.62)
    left = [a+b for a, b in zip(left, values)]
for i, (_, _, total, _) in enumerate(records):
    ax.text(total+max(left)*.015, i, f'{total:.0f}s', va='center', fontsize=10)
ax.set_yticks(range(len(records)), [f'{"GitHub" if p == "github" else "Namespace"} · {s}' for p, s, _, _ in records])
ax.invert_yaxis()
ax.set_xlim(0, max(left)*1.14)
ax.set_xlabel('Whole CI job, seconds')
fig.suptitle('pandas: the build was only part of the wait', x=.29, y=.97, ha='left', fontweight='bold', fontsize=16)
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.grid(axis='x', alpha=.15)
ax.set_axisbelow(True)
fig.legend(*ax.get_legend_handles_labels(), loc='upper left', bbox_to_anchor=(.28, .925), ncol=2, frameon=False, fontsize=9)
fig.text(.29, .045, 'One trial per condition · fresh runner and build directory · 2 compiler/test workers\nEdited = Python helper rename; different provider hardware. See linked raw evidence.', fontsize=9)
fig.savefig(folder / 'timings.png', dpi=180)
print(folder / 'timings.png')
