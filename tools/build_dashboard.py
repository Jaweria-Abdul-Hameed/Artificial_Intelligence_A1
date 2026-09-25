"""Build tools/dashboard.html: an interactive results explorer for the experiment matrix.

Usage (from the repo root):  python tools/build_dashboard.py
Reads tools/results.json and evidence/screenshots, writes one self-contained HTML file.
Repo-level helper; not part of the submission ZIP.
"""
import base64
import io
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, 'search', 'search', 'evidence', 'screenshots')
data = json.load(open(os.path.join(ROOT, 'tools', 'results.json')))


def inline(label):
    path = os.path.join(SHOTS, label + '.png')
    img = Image.open(path).convert('RGB')
    img.thumbnail((720, 720))
    buf = io.BytesIO()
    img.quantize(96).save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


runs = []
for e in data['experiments']:
    runs.append({'id': e['label'], 'task': e['task'], 'name': e['description'], 'cmd': e['command'],
                 'cost': e['cost'], 'nodes': e['nodes'], 'secs': e['seconds'],
                 'csv': e['csv'][0] if e['csv'] else '', 'img': inline(e['label'])})

PAGE = open(os.path.join(ROOT, 'tools', 'dashboard_template.html'), encoding='utf-8').read()
PAGE = PAGE.replace('/*RUNS*/[]', json.dumps(runs)).replace('/*GRADES*/[]', json.dumps(data['autograder']))
out = os.path.join(ROOT, 'tools', 'dashboard.html')
open(out, 'w', encoding='utf-8').write(PAGE)
print('wrote', out, '%.0f KB' % (os.path.getsize(out) / 1024.0))
