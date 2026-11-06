# Before the capture: open the Live page in Stomp mode and tap the tempo to
# 100 BPM, then back to 120, so the tempo LED flashes in step with the taps
# that end the story. The LED timer counts whole milliseconds and restarts
# only when the period changes: on the tap that brings 120 BPM back, here
# and in the story. Writes the wall clock time of that tap to ANCHOR.
# usage: prep.py ANCHOR
import sys
from xinput import *

LIVE_TAB = (850, 35)
STOMP = (228, 248)
TAP = (1202, 148)

begin()
warp(*LIVE_TAB); tap(0.2)
warp(*STOMP); tap(1.2)
warp(*TAP)
tap(2.0, 0.06); tap(2.6, 0.06)          # 100 BPM
tap(5.0, 0.06); tap(5.5, 0.06)          # a new count after a pause: 120 BPM
last = track[-2][0]                     # wall clock of that press
wait_until(6.0)
open(sys.argv[1], 'w').write(repr(last))
