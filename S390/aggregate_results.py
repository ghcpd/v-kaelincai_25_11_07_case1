import json
import statistics
import os

def load_results(path):
    with open(path) as f:
        return json.load(f)

def analyze(results):
    total = len(results)
    passed = sum(1 for r in results if r.get('passed'))
    pass_rate = passed/total if total>0 else 0
    durations = [r['result'].get('duration') for r in results if r.get('result') and r['result'].get('duration')]
    durations = [d for d in durations if d is not None]
    if durations:
        p50 = statistics.median(durations)
        # p95: take 95th percentile
        durations_sorted = sorted(durations)
        idx = min(len(durations_sorted)-1, max(0, int(len(durations_sorted)*0.95)-1))
        p95 = durations_sorted[idx]
    else:
        p50 = p95 = None
    errors = sum(1 for r in results if r.get('result') is None or r.get('result').get('available') is None and r.get('result') is None)
    fallback_count = sum(1 for r in results if (r.get('result') and 'fallback' in (r.get('result').get('note','') or '') ) or (r.get('note') and 'fallback' in r.get('note','')))
    return {'total': total, 'passed': passed, 'pass_rate': pass_rate, 'p50': p50, 'p95': p95, 'errors': errors, 'fallbacks': fallback_count}

if __name__ == '__main__':
    pre = load_results(os.path.join('Project_A_PreChange','results','results_pre.json'))
    post = load_results(os.path.join('Project_B_PostChange','results','results_post.json'))
    pre_metrics = analyze(pre)
    post_metrics = analyze(post)
    out = {'pre': pre_metrics, 'post': post_metrics}
    with open(os.path.join('results','aggregated_metrics.json'), 'w') as f:
        json.dump(out, f, indent=2)
    # generate a simple markdown report
    md = []
    md.append('# Compare Report')
    md.append('\n## Summary')
    md.append(f"- Pre-change pass_rate: {pre_metrics['pass_rate']:.2f} ({pre_metrics['passed']}/{pre_metrics['total']})")
    md.append(f"- Post-change pass_rate: {post_metrics['pass_rate']:.2f} ({post_metrics['passed']}/{post_metrics['total']})")
    md.append('\n## Latency p50/p95')
    md.append(f"- Pre-change p50: {pre_metrics['p50']}, p95: {pre_metrics['p95']}")
    md.append(f"- Post-change p50: {post_metrics['p50']}, p95: {post_metrics['p95']}")
    md.append('\n## Errors and Fallbacks')
    md.append(f"- Pre-change errors: {pre_metrics['errors']}, fallbacks: {pre_metrics['fallbacks']}")
    md.append(f"- Post-change errors: {post_metrics['errors']}, fallbacks: {post_metrics['fallbacks']}")

    with open('compare_report.md', 'w') as f:
        f.write('\n'.join(md))
    print('Generated compare_report.md and results/aggregated_metrics.json')
