"""Compare recorded ccache inputs and header manifests from two runners."""
import difflib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]/'results/cache-diagnosis'
github=root/'github-debug'
namespace=root/'namespace-debug'
for folder in [github,namespace]:
    if not (folder/'header-hashes.json').exists():
        raise SystemExit(f'Missing diagnostics: {folder}')
left=json.loads((github/'header-hashes.json').read_text())
right=json.loads((namespace/'header-hashes.json').read_text())
changed=[key for key in sorted(set(left['headers']) | set(right['headers'])) if left['headers'].get(key) != right['headers'].get(key)]
print(f'Header/compiler manifest differences: {len(changed)}')
for key in changed:
    print(key)
    print('  GitHub:',left['headers'].get(key))
    print('  Namespace:',right['headers'].get(key))
for name in ['prefix','python','config']:
    if left[name] != right[name]:
        print(name,left[name],right[name])
print('\nRepresentative ccache input difference (first 150 lines):')
def inputs(folder):
    # Direct inputs are enough to distinguish manifest-key changes; the full
    # representative input remains available if preprocessing differs instead.
    text=(folder/'base.ccache-input-text').read_text(errors='replace')
    return text.split('=== PREPROCESSOR MODE ===')[0].splitlines()
print('\n'.join(list(difflib.unified_diff(inputs(github),inputs(namespace),fromfile='github',tofile='namespace'))[:150]))
for folder in [github,namespace]:
    print('\n'+folder.name+' cache decisions:')
    log=(folder/'ccache-decisions.log').read_text(errors='replace')
    selected=[line for line in log.splitlines() if re.search(r'(changed|modified|mtime|size|Manifest key:|Result key:|Result:|include file)',line,re.I)]
    print('\n'.join(selected[:110]))
