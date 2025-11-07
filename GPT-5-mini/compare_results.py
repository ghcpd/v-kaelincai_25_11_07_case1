import json
import os
import statistics

def load(path):
    if not os.path.exists(path):
        return []
    return json.load(open(path))

pre = load('Project_A_PreChange/results/results_pre.json')
post = load('Project_B_PostChange/results/results_post.json')

def summarize(arr):
    lat = [r['duration'] for r in arr]
    pass_rate = sum(1 for r in arr if r.get('pass'))/len(arr) if arr else 0
    return {
        'count': len(arr),
        'p50': statistics.median(lat) if lat else None,
        'p95': (sorted(lat)[int(0.95*len(lat))-1] if lat and len(lat)>1 else (lat[-1] if lat else None)),
        'pass_rate': pass_rate
    }

metrics = {'pre': summarize(pre), 'post': summarize(post)}
os.makedirs('results', exist_ok=True)
with open('results/aggregated_metrics.json','w') as f:
    json.dump({'pre':pre,'post':post,'metrics':metrics}, f, indent=2)

with open('compare_report.md','w') as f:
    f.write('# Comparison Report\n\n')
    f.write('## Summary Metrics\n')
    f.write('**Pre-change:** ' + str(metrics['pre']) + '\n\n')
    f.write('**Post-change:** ' + str(metrics['post']) + '\n\n')
    f.write('## Per-case details\n')
    f.write('### Pre-change results\n')
    f.write(json.dumps(pre, indent=2))
    f.write('\n\n### Post-change results\n')
    f.write(json.dumps(post, indent=2))

print('Generated compare_report.md and results/aggregated_metrics.json')
