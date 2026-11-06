# The Live page story, in seconds from the start: two stomps toggled and
# back, three scenes recalled, the tempo tapped to 95 BPM and back to 120.
# Ends as it started: Stomp mode, every block on, Rhythm, 120 BPM, pointer at
# rest. Coordinates: 1280x750 screen, the UI at 1024x600 scaled by 1.25.
# The loop starts a whole number of beats after the tap of prep.py that sets
# 120 BPM, and ends a whole number of beats after its own, so the tempo LED
# flashes across the seam as everywhere else; 20 s is also 10 bars of the
# strummed loop (2 s).
# usage: story.py OUT.json ANCHOR
import json, sys, time
from xinput import *

REST = (1180, 700)
SCENES, STOMP = (92, 248), (228, 248)
TAP = (1202, 148)
TILE = [(169, 398), (483, 398), (797, 398), (1110, 398), (169, 625), (483, 625), (797, 625), (1110, 625)]
LOOP = 20.0
BEAT = 0.5

anchor = float(open(sys.argv[2]).read())
beats = int((time.time() + 0.5 - anchor) / BEAT) + 1
start = begin(anchor + beats * BEAT)
warp(*REST)

def tap_at(target, t, travel=0.5, hold=0.08):
    # Move to target from t, tap when there; returns when the tap ends
    move(*target, t, t + travel)
    tap(t + travel + 0.1, hold)
    return t + travel + 0.1 + hold

t = 0.4
t = tap_at(TILE[0], t) + 0.55          # Stomp: the drive off
t = tap_at(TILE[5], t) + 0.55          # the hall off
t = tap_at(TILE[0], t) + 0.45          # drive on again
t = tap_at(TILE[5], t, 0.45) + 0.6     # hall on again
t = tap_at(SCENES, t) + 0.55           # Scenes mode
t = tap_at(TILE[1], t) + 0.55          # Lead
t = tap_at(TILE[2], t, 0.45) + 0.55    # Clean
t = tap_at(TILE[0], t) + 0.4           # Rhythm
move(*TAP, t, t + 0.55)                # Tap tempo: 95 BPM
t += 0.65
for i in range(5):
    tap(t + i * 60 / 95, 0.06)
t += 4 * 60 / 95 + 2.3                 # a pause: the next taps start a new count
t = round(t / BEAT) * BEAT
for i in range(5):                     # back to 120 BPM
    tap(t + i * BEAT, 0.06)
t += 4 * BEAT
t = tap_at(STOMP, t + 0.25) + 0.3      # Stomp mode again
move(*REST, t, LOOP - 0.05)
wait_until(LOOP + 0.6)
json.dump({'start': start, 'duration': LOOP, 'track': track}, open(sys.argv[1], 'w'))
print(f'story {LOOP} s, last tap at {t:.2f} s')
