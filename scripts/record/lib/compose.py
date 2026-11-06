# Cuts the loop out of the lossless capture and draws the finger on it. The
# frames of the story's cuts (network waits, wall clock) are left out.
# usage: compose.py capture.nut story.json out.nut fps
import json, subprocess, sys
import numpy as np

cap, story_file, out, fps = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
W, H = 1280, 750
story = json.load(open(story_file))
track = story['track']
start = story['start']
cuts = story.get('cuts', [])
n = round(story['duration'] * fps)

# Frame times: x11grab stamps frames with the wall clock (kept by -copyts)
pts = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'packet=pts_time',
                      '-of', 'csv=p=0', cap], capture_output=True, text=True, check=True).stdout.split()
pts = sorted(float(p) for p in pts if p)
first = next(i for i, p in enumerate(pts) if p >= start)
keep = [i for i in range(first, len(pts)) if not any(a <= pts[i] < b for a, b in cuts)][:n]
if len(keep) < n:
    sys.exit(f'capture too short: {len(keep)} frames after the start, {n} needed')
print(f'capture {len(pts)} frames, loop {first}..{keep[-1] + 1}, {n / fps:.2f} s, '
      f'first frame {1000 * (pts[first] - start):.1f} ms after the start'
      + (f', {len(cuts)} waits cut: ' + ', '.join(f'{b - a:.2f} s' for a, b in cuts) if cuts else ''))
keep = set(keep)

def pointer(t):
    x, y, down = track[0][1], track[0][2], 0
    for e in track:
        if e[0] > t:
            break
        x, y, down = e[1], e[2], e[3]
    return x, y, down

R = 34
yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
dist = np.sqrt(xx ** 2 + yy ** 2)

def disc(radius, fill, ring):
    edge = np.clip(radius - dist, 0, 1)
    inner = np.clip(radius - 2.5 - dist, 0, 1)
    return edge * (fill * inner + ring * (1 - inner))

UP = disc(25, 0.22, 0.6)
DOWN = disc(22, 0.42, 0.85)

dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', cap, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', str(fps), '-i', '-', '-c:v', 'ffv1', out], stdin=subprocess.PIPE)
size = W * H * 3
for i in range(max(keep) + 1):
    raw = dec.stdout.read(size)
    if len(raw) < size:
        sys.exit('decode ended early')
    if i not in keep:
        continue
    f = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32)
    x, y, down = pointer(pts[i])
    a = DOWN if down else UP
    cx, cy = int(round(x)), int(round(y))
    x0, y0 = max(0, cx - R), max(0, cy - R)
    x1, y1 = min(W, cx + R + 1), min(H, cy + R + 1)
    if x0 < x1 and y0 < y1:
        sub = a[y0 - (cy - R):y1 - (cy - R), x0 - (cx - R):x1 - (cx - R)][..., None]
        f[y0:y1, x0:x1] = f[y0:y1, x0:x1] * (1 - sub) + 255 * sub
    enc.stdin.write(f.astype(np.uint8).tobytes())
enc.stdin.close()
enc.wait()
dec.kill()
