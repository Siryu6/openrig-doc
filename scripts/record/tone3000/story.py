# The TONE3000 story, in seconds from the start: from the Amp block's editor,
# Choose, TONE3000, the Trending tab, a Marshall JCM 800 capture opened, one
# model ticked, downloaded and used; then Choose and the Peavey 5150 again.
# Ends as it started: the Peavey in the editor, pointer at rest.
# Coordinates: 1280x750 screen, the UI at 1024x600 scaled by 1.25.
# It is online: the trending list, the pictures, the models and the download
# come from TONE3000. The story waits for them on the screen; what they take
# beyond the pause planned for them is cut out of the video (wait_for).
# TONE_ROW: row of the tone in the trending amps (default 3), check it in the
# app first, and the caption in src/content/docs/using/tone3000.mdx.
# usage: story.py OUT.json ANCHOR (unused)
import json, os, sys
import numpy as np
from xinput import *

REST = (1130, 640)
CHOOSE = (1190, 197)
T3K = (640, 214)                        # TONE3000 in Choose
TRENDING = (916, 173)
ROW = (520, 315 + 85 * (int(os.environ.get('TONE_ROW', 3)) - 1))
TICK = (84, 271)                        # the first model of the tone
DOWNLOAD = (1109, 667)
USE = (1149, 269)
PEAVEY = (640, 432)                     # second tone in Choose, after the Marshall
LOOP = 20.0                             # 10 bars of the strummed loop (2 s)

def listed():
    # The first five rows of the list and their pictures: placeholders are
    # alike, pictures are not
    thumbs = [screen(25, 285 + 85 * i, 60, 60) for i in range(5)]
    return all(not np.array_equal(a, b) for i, a in enumerate(thumbs) for b in thumbs[i + 1:])

def models():
    # The tone's models listed (the first model row has text)
    return np.ptp(screen(60, 250, 600, 40)) > 80

def downloaded():
    # "Use" on the first model: an orange button
    px = screen(1080, 245, 140, 50)
    return np.count_nonzero((px[..., 0] > 200) & (px[..., 1] > 120) & (px[..., 1] < 200) & (px[..., 2] < 90)) > 150

def tap_at(target, t, travel=0.5, hold=0.08):
    # Move to target from t, tap when there; returns when the tap ends
    move(*target, t, t + travel)
    tap(t + travel + 0.1, hold)
    return t + travel + 0.1 + hold

start = begin()
warp(*REST)
t = 0.5
t = tap_at(CHOOSE, t) + 0.5             # Choose: the tones on the pedalboard
t = tap_at(T3K, t) + 0.6                # TONE3000: Favorites first
t = tap_at(TRENDING, t, 0.55)           # the trending amps
wait_for(listed, t + 1.0)               # ... listed, with their pictures
t += 2.6
t = tap_at(ROW, t, 0.6)                 # the Marshall JCM 800
wait_for(models, t + 0.8)               # its models
t += 1.6
t = tap_at(TICK, t, 0.55) + 0.35        # tick the first
t = tap_at(DOWNLOAD, t, 0.6)            # download it
wait_for(downloaded, t + 1.2)
t += 2.0
t = tap_at(USE, t, 0.55) + 2.2          # use it: the Amp block plays it
t = tap_at(CHOOSE, t) + 0.6             # Choose again: both tones
t = tap_at(PEAVEY, t, 0.55) + 0.3       # the Peavey 5150 again
move(*REST, t, t + 0.7)
if t + 0.7 > LOOP - 0.3:
    raise SystemExit(f'story too long: {t + 0.7:.2f} s')
wait_until(LOOP + 0.6)
json.dump({'start': start, 'duration': LOOP, 'track': track, 'cuts': cuts}, open(sys.argv[1], 'w'))
print(f'story {LOOP} s, at rest from {t + 0.7:.2f} s, waits cut: ' + (', '.join(f'{b - a:.2f} s' for a, b in cuts) or 'none'))
