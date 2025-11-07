import json
from pathlib import Path

root = Path('.').resolve()
pre_report = root/'Project_A_PreChange'/'results'/'pytest_results_pre.json'
post_report = root/'Project_B_PostChange'/'results'/'pytest_results_post.json'
out = root/'results'
out.mkdir(exist_ok=True)

def summarize(report_path, out_path):
    if not report_path.exists():
        with open(out_path,'w') as f:
            json.dump({'error':'report missing'}, f)
        return
    with open(report_path) as f:
        data = json.load(f)
    summary = {
        'duration': data.get('duration',0),
        'tests_run': data.get('summary',{}).get('total',0),
        'passed': data.get('summary',{}).get('passed',0),
        'failed': data.get('summary',{}).get('failed',0)
    }
    with open(out_path,'w') as f:
        json.dump(summary, f, indent=2)

summarize(pre_report, out/'results_pre.json')
summarize(post_report, out/'results_post.json')
print('Generated results_pre.json and results_post.json')