"""Build SearchProject.zip from search/search following the packaging rules in issue #15.

Usage (from the repo root):  python tools/make_zip.py
Excludes our own tests, __pycache__ and anything outside the project folder, then
unzips into a temp folder and runs the autograder and the byte-identity checks there.
Repo-level helper; the ZIP is written to the repo root and is not committed.
"""
import os
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.join(ROOT, 'search', 'search')
OUT = os.path.join(ROOT, 'SearchProject.zip')
TOP = 'SearchProject'
EXCLUDE_FILES = {'test_gbfs.py', 'test_search_edges.py',
                 'test_csv_logger.py', 'graph_problem.py'}
FORBIDDEN = ['pacman.py', 'game.py', 'util.py', 'layout.py', 'graphicsDisplay.py',
             'graphicsUtils.py', 'textDisplay.py']
BASE = 'f0c03c7'   # starter-code commit


def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(PROJECT):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for name in files:
                if name in EXCLUDE_FILES or name.endswith('.pyc'):
                    continue
                full = os.path.join(folder, name)
                z.write(full, os.path.join(TOP, os.path.relpath(full, PROJECT)).replace('\\', '/'))
    print('wrote', OUT, '%.1f MB' % (os.path.getsize(OUT) / 1e6))

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(OUT) as z:
            z.extractall(tmp)
            names = z.namelist()
        proj = os.path.join(tmp, TOP)
        bad = [n for n in names if os.path.basename(n) in EXCLUDE_FILES or '__pycache__' in n]
        print('excluded files present:', bad or 'none')
        for need in ['search.py', 'searchAgents.py', 'README.txt', 'report.pdf', 'layouts/24i3025Search.lay', 'layouts/mediumDenselyMaze.lay', 'layouts/stayEastSearch.lay',
                     'pacman.py', 'game.py', 'util.py', 'layout.py', 'autograder.py']:
            assert os.path.exists(os.path.join(proj, need)), need
        print('csv files:', sum(n.startswith(TOP + '/evidence/') and n.endswith('.csv') for n in names),
              '| screenshots:', sum(n.startswith(TOP + '/evidence/screenshots/') and n.endswith('.png') for n in names))
        for f in FORBIDDEN:
            orig = subprocess.run(
                ['git', '-c', 'safe.directory=' + ROOT.replace('\\', '/'), 'show',
                 '%s:search/search/%s' % (BASE, f)],
                cwd=ROOT, capture_output=True, check=True).stdout
            same = orig == open(os.path.join(proj, f), 'rb').read()
            print('%-18s byte-identical to starter: %s' % (f, same))
            assert same
        sa = open(os.path.join(proj, 'searchAgents.py'), encoding='utf-8').read()
        print('# DO NOT CHANGE count:', sa.count('# DO NOT CHANGE'))
        out = subprocess.run([sys.executable, 'autograder.py', '--no-graphics'], cwd=proj,
                             capture_output=True, text=True).stdout
        print(re.findall(r'^Total: .*$', out, re.M))
        print('evidence csv count after autograder:',
              len([f for f in os.listdir(os.path.join(proj, 'evidence')) if f.endswith('.csv')]))


if __name__ == '__main__':
    main()
