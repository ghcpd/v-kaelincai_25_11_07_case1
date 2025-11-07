import json, statistics, os, sys

pre_path = 'results/results_pre.json'
post_path = 'results/results_post.json'
if not os.path.exists(pre_path):
    pre_path = 'Project_A_PreChange/results/results_pre.json'
if not os.path.exists(post_path):
    post_path = 'Project_B_PostChange/results/results_post.json'

pre = json.load(open(pre_path))
post = json.load(open(post_path))

# helper
def metrics(rs):
    total = len(rs)
    passed = sum(1 for r in rs if r.get('passed'))
    lat = [r.get('duration_ms',0) for r in rs if r.get('duration_ms')]
    p50 = statistics.median(lat) if lat else 0
    p95 = sorted(lat)[max(0,int(0.95*len(lat))-1)] if lat else 0
    fallback = sum(1 for r in rs if r.get('fallback'))
    return { 'total': total, 'passed': passed, 'p50': p50, 'p95': p95, 'fallback':fallback }

metrics_pre = metrics(pre)
metrics_post = metrics(post)

report = []
report.append('# Compare Report')
report.append('\n## Summary of metrics')
report.append(f"Pre: {metrics_pre['passed']}/{metrics_pre['total']} passed; Fallbacks: {metrics_pre['fallback']}")
report.append(f"Post: {metrics_post['passed']}/{metrics_post['total']} passed; Fallbacks: {metrics_post['fallback']}")
report.append('\n## Latency')
report.append(f"Pre p50={metrics_pre['p50']:.2f}ms p95={metrics_pre['p95']:.2f}ms")
report.append(f"Post p50={metrics_post['p50']:.2f}ms p95={metrics_post['p95']:.2f}ms")

# Decision correctness diff
report.append('\n## Decision correctness per test case')
by_id = {r['id']: r for r in pre}
for p in post:
    pid = p['id']
    prev = by_id.get(pid)
    if prev:
        mismatch = prev.get('passed') != p.get('passed')
        report.append(f"- {pid}: pre_pass={prev.get('passed')} post_pass={p.get('passed')} mismatch={mismatch}")

# Observations
report.append('\n## Observations & recommended mitigations')
report.append('- v2 returns richer context; additional params are required for region-aware availability.')
report.append('- Pending/async responses require polling or webhooks; implement retry/backoff and idempotent calls.')
report.append('- Fallback frequency indicates how often the adapter uses legacy API; if high, consider a staged rollout or fixing v2 errors.')
report.append('- Monitor syncTimestamp formats and clock skew; use conservative timeouts when polling.')

open('compare_report.md','w').write('\n\n'.join(report))
print('Generated compare_report.md')
