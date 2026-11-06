# The hero story (the tour of the screen, and the openrig.eu home page), in
# seconds from the start; ends as it started (nothing selected, reverb on,
# knob back where it was, pointer at rest)
# Coordinates: 1280x750 screen, the UI at 1024x600 scaled by 1.25
# A press rests ~0.25 s before dragging a knob, as a finger does: Slint's
# Flickable takes a drag that starts at once for a scroll. The editor's knobs
# sit in a vertical Flickable that takes part of a drag: knobs are turned in the
# strip under the rack
import json, sys
from xinput import *

REST = (1130, 640)
AMP = (350, 372)
REVERB = (1070, 372)
KNOB = (327, 664)           # INPUT knob in the strip under the rack
BACK = (118, 35)            # "< Rack" in the editor
EMPTY = (1040, 560)         # empty rack: clears the selection
LOOP = 12.0                 # 6 bars of the strummed loop (2 s), so the meters loop too

start = begin()
warp(*REST)
t = 0.5
move(*AMP, t, t + 0.55); tap(t + 0.65)                        # select the amp
t += 1.0
move(*KNOB, t, t + 0.5); press(t + 0.6)                       # turn its input up
drag(0, -64, t + 0.85, t + 1.5); release(t + 1.65)
t += 1.9
move(*REVERB, t, t + 0.6); press(t + 0.7); release(t + 1.25)  # hold: bypass the reverb
t += 1.45
move(*AMP, t, t + 0.55); tap(t + 0.65, 0.06); tap(t + 0.8, 0.06)  # double tap: the editor
t += 2.4
move(*BACK, t, t + 0.5); tap(t + 0.6)                         # back to the rack
t += 0.95
move(*KNOB, t, t + 0.5); tap(t + 0.6, 0.06); tap(t + 0.75, 0.06)  # double tap: input back to 0 dB
t += 1.15
move(*REVERB, t, t + 0.6); press(t + 0.7); release(t + 1.25)  # reverb on again
t += 1.45
move(*EMPTY, t, t + 0.4); tap(t + 0.5)                        # deselect
t += 0.75
move(*REST, t, LOOP - 0.05)
wait_until(LOOP + 0.6)
json.dump({'start': start, 'duration': LOOP, 'track': track}, open(sys.argv[1], 'w'))
print(f'story {LOOP} s')
