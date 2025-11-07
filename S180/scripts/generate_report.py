import json
from pathlib import Path
root = Path('.').resolve()
pre = root/'results'/'results_pre.json'
post = root/'results'/'results_post.json'
report = root/'compare_report.md'

p = {'passed': 'unknown', 'duration': 'n/a'}
q = {'passed': 'unknown', 'duration': 'n/a'}
if pre.exists():
    p = json.load(pre)
if post.exists():
    q = json.load(post)

with open(report, 'w') as f:
    f.write('# Comparison Report\n\n')
    f.write('## Summary\n\n')
    f.write(f'- Pre-change: passed={p.get("passed")}, duration={p.get("duration")}\n')
    f.write(f'- Post-change: passed={q.get("passed")}, duration={q.get("duration")}\n')
    f.write('\n## Observations\n\n')
    f.write('- Compare correctness and latency.\n')
    f.write('\n## Recommendations\n\n')
    f.write('- Use canary rollout, monitoring and circuit breakers.\n')

print('compare_report.md generated')