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
for provider in ['github', 'namespace']:
    for phase in ['cold', 'warm', 'edited']:
        path = folder / f'{provider}-{phase}.json'
        if not path.exists():
            continue
        record = json.loads(path.read_text())
        job = json.loads((folder / f'{provider}-{phase}-job.json').read_text())['jobs'][0]
        if job['conclusion'] != 'success':
            continue
        start, end = [datetime.fromisoformat(job[k].replace('Z', '+00:00')) for k in ['startedAt', 'completedAt']]
        total = (end-start).total_seconds()
        parts = {s['name']: s['seconds'] for s in record['steps']}
        parts['other'] = max(0, total-sum(parts.values()))
        records.append((provider, phase, total, parts))

fig, ax = plt.subplots(figsize=(10, 5.5), layout='constrained')
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
ax.set_yticks(range(len(records)), [f'{p.title()} · {s}' for p, s, _, _ in records])
ax.invert_yaxis()
ax.set_xlim(0, max(left)*1.14)
ax.set_xlabel('Whole CI job, seconds')
ax.set_title('pandas: what happens after the cache is warm?', loc='left', fontweight='bold', pad=30, fontsize=16)
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.grid(axis='x', alpha=.15)
ax.set_axisbelow(True)
ax.legend(loc='lower left', bbox_to_anchor=(0, 1.01), ncol=2, frameon=False, fontsize=9)
fig.supxlabel('One trial per condition · fresh runner and build directory · 2 compiler/test workers\nEdited = Python helper rename; different provider hardware. See linked raw evidence.', fontsize=9)
fig.savefig(folder / 'timings.png', dpi=180)
print(folder / 'timings.png')
