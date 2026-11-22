"""Reject a warm-cache benchmark when its compiler entries were not reused."""
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text()
match = re.search(r'Hits:\s+(\d+) /\s*(\d+)', text)
if not match:
    raise SystemExit('Compiler-cache statistics are missing.')
hits, calls = map(int, match.groups())
if calls == 0 or hits != calls:
    raise SystemExit(f'Expected full compiler-cache reuse; got {hits}/{calls}.')
print(f'Compiler-cache regression check passed: {hits}/{calls} hits.')
