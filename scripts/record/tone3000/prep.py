# Before the capture: open the Amp block's editor and choose the Peavey 5150
# Blockletter there, as the story does at its end (Choose takes the first
# model of the tone, not the preset's), so the loop ends as it starts.
# usage: prep.py ANCHOR (unused)
from xinput import *

AMP = (350, 372)
CHOOSE = (1190, 197)
ONLY_TONE = (640, 365)      # the Peavey, the only tone in Choose for now

begin()
warp(*AMP); tap(0.2, 0.06); tap(0.35, 0.06)     # double tap: the editor
warp(*CHOOSE); tap(1.8)
warp(*ONLY_TONE); tap(2.8)
wait_until(4.0)
