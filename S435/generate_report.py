import json
import os
import statistics

pre_path = 'results/results_pre.json'
post_path = 'results/results_post.json'

with open(pre_path) as f:
    pre = json.load(f)
with open(post_path) as f:
    post = json.load(f)

metrics = {}

def compute_metrics(data):
    latencies = [d.get('latency') for d in data if d.get('latency') is not None]
    statuses = [d.get('status') for d in data]
    errors = sum(1 for s in statuses if s >= 400)
    passed = sum(1 for d in data if d.get('passed'))
    total = len(data)
    fallback_count = sum(1 for d in data if (d.get('body', {}).get('result', {}).get('note') or '').startswith('fallback') or (d.get('body', {}).get('meta', {}).get('fallback')==True))

    p50 = statistics.median(latencies) if latencies else None
    p95 = None
    if latencies:
        lat_sorted = sorted(latencies)
        idx = int(0.95 * len(lat_sorted)) - 1
        idx = max(0, min(idx, len(lat_sorted)-1))
        p95 = lat_sorted[idx]

    return {
        'count': total,
        'passed': passed,
        'errors': errors,
        'latencies': latencies,
        'p50': p50,
        'p95': p95,
        'fallback_count': fallback_count
    }

metrics['pre'] = compute_metrics(pre)
metrics['post'] = compute_metrics(post)

# Accuracy
metrics['pre']['accuracy'] = metrics['pre']['passed']/metrics['pre']['count'] if metrics['pre']['count'] else None
metrics['post']['accuracy'] = metrics['post']['passed']/metrics['post']['count'] if metrics['post']['count'] else None

with open('results/aggregated_metrics.json', 'w') as out:
    json.dump(metrics, out, indent=2)

# Generate markdown report
lines = []
lines.append('# Comparison Report: Pre vs Post Change\n')
lines.append('## Summary Metrics\n')
lines.append('| Metric | Pre (v1) | Post (v2) | Difference |')
lines.append('|---|---|---|---|')
lines.append(f"| Total Tests | {metrics['pre']['count']} | {metrics['post']['count']} | {metrics['post']['count']-metrics['pre']['count']} |")
lines.append(f"| Passed | {metrics['pre']['passed']} | {metrics['post']['passed']} | {metrics['post']['passed']-metrics['pre']['passed']} |")
lines.append(f"| Errors | {metrics['pre']['errors']} | {metrics['post']['errors']} | {metrics['post']['errors']-metrics['pre']['errors']} |")
lines.append(f"| Accuracy | {metrics['pre']['accuracy']} | {metrics['post']['accuracy']} | {metrics['post']['accuracy']-metrics['pre']['accuracy']} |")
lines.append(f"| p50 Latency (s) | {metrics['pre']['p50']} | {metrics['post']['p50']} | { (metrics['post']['p50'] - metrics['pre']['p50']) if (metrics['pre']['p50'] and metrics['post']['p50']) else None } |")
lines.append(f"| p95 Latency (s) | {metrics['pre']['p95']} | {metrics['post']['p95']} | { (metrics['post']['p95'] - metrics['pre']['p95']) if (metrics['pre']['p95'] and metrics['post']['p95']) else None } |")
lines.append(f"| Fallbacks | N/A | {metrics['post']['fallback_count']} | N/A |")

lines.append('\n## Per-Test Observations\n')
for p, q in zip(pre, post):
    note_pre = p.get('body', {}).get('result', {}).get('note') if p.get('body') else str(p.get('body'))
    note_post = q.get('body', {}).get('result', {}).get('note') if q.get('body') else str(q.get('body'))
    lines.append(f"- Test {p['id']}: pre note: `{note_pre}` | post note: `{note_post}` | pre passed: {p['passed']} -> post passed: {q['passed']}")

lines.append('\n## Key Observations\n')
lines.append('- v2 allows region/warehouse-aware availability and can reduce false positives for availability in multi-region setups.\n')
lines.append('- v2 introduced async/pending responses; the service uses polling with timeout and falls back to v1 when pending is unresolved.\n')
lines.append('- In tests, fallback frequency was ' + str(metrics['post']['fallback_count']) + '.\n')
lines.append('\n## Recommendations\n')
lines.append('- Add observability for pending responses (count, latency) to detect increased async activity.\n')
lines.append('- Use staged rollout: canary v2 for a subset of regions and implement feature flag to toggle per region.\n')
lines.append('- Implement circuit breakers and exponential backoff for high latency or errors from v2.\n')

with open('compare_report.md', 'w') as f:
    f.write('\n'.join(lines))

print('Report generated at compare_report.md and results/aggregated_metrics.json')
