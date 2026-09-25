"""Run one pacman.py command with graphics and save a screenshot of the final board.

Usage (from search/search):  python ../../tools/snap.py OUT.png <pacman.py args...>
Repo-level helper for the evidence/ screenshots; not part of the submission ZIP.
"""
import os
import sys
import time

os.environ['SEARCH_LOG'] = '0'          # CSVs come from the separate -q run
out = sys.argv[1]
sys.argv = ['pacman.py'] + sys.argv[2:]
sys.path.insert(0, os.getcwd())

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

from PIL import ImageGrab
import graphicsDisplay
import graphicsUtils

_finish = graphicsDisplay.PacmanGraphics.finish


def finish(self):
    root = graphicsUtils._root_window
    root.update()
    root.attributes('-topmost', True)
    root.lift()
    root.update()
    time.sleep(0.6)
    x, y = root.winfo_rootx(), root.winfo_rooty()
    w, h = root.winfo_width(), root.winfo_height()
    ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(out)
    _finish(self)


graphicsDisplay.PacmanGraphics.finish = finish

import pacman
pacman.runGames(**pacman.readCommand(sys.argv[1:]))
