# Checks that the loop only repeats a frame while nothing moves: runs
# mpdecimate on the lossless loop and lists the repeated frames that fall
# while the finger moves or presses (a stutter), with the still stretches.
# usage: still.py loop.nut story.json fps
import json, re, subprocess, sys

loop, story_file, fps = sys.argv[1], sys.argv[2], int(sys.argv[3])
story = json.load(open(story_file))
start, track = story['start'], story['track']

# Times (from the start of the loop) when the finger moves (moves log the
# pointer at 240 Hz: samples further apart are a pause)
busy = []
for a, b in zip(track, track[1:]):
    moving = (round(a[1]), round(a[2])) != (round(b[1]), round(b[2])) and b[0] - a[0] < 0.05
    if moving:
        busy.append((a[0] - start, b[0] - start))

log = subprocess.run(['ffmpeg', '-nostdin', '-v', 'debug', '-i', loop, '-vf', 'mpdecimate', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
decisions = re.findall(r'(keep|drop) pts:\S+ pts_time:([0-9.]+)', log)
drops = [float(p) for d, p in decisions if d == 'drop']
total = len(decisions)
stutters = [t for t in drops if any(a <= t <= b for a, b in busy)]

runs, run = [], []
for t in drops:
    if run and t - run[-1] > 1.5 / fps:
        runs.append(run)
        run = []
    run.append(t)
if run:
    runs.append(run)
print(f'mpdecimate: {total - len(drops)} unique of {total} frames; repeats in {len(runs)} still stretches: '
      + ', '.join(f'{r[0]:.2f}-{r[-1]:.2f} s' for r in runs))
if stutters:
    print(f'warning: {len(stutters)} repeated frames while the finger moves: '
          + ', '.join(f'{t:.2f}' for t in stutters[:20]), file=sys.stderr)
else:
    print('no repeated frame while the finger moves')
