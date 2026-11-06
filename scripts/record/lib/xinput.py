# Pointer gestures over XTest, timed against a monotonic clock
import math, time
import numpy as np
from Xlib import X, display
from Xlib.ext import xtest

d = display.Display()
T0 = time.monotonic()
T0_wall = time.time()
pos = [0, 0]
down = [0]
# Pointer track for the touch overlay: wall clock (as x11grab stamps frames), x, y, pressed
track = []
# Waits on the network cut out of the video: wall clock (start, end) of each,
# and their total, which the story clock leaves out
cuts = []
shift = [0.0]

def log():
    track.append((time.time(), pos[0], pos[1], down[0]))

def now():
    return time.monotonic() - T0 - shift[0]

def begin(at=None):
    # Start the story clock now, or at the wall clock time `at`; returns the
    # wall clock time it started at (the start of the loop)
    global T0, T0_wall
    if at is not None:
        while time.time() < at:
            time.sleep(min(at - time.time(), 0.004))
    T0, T0_wall = time.monotonic(), time.time()
    return T0_wall

def wait_until(t):
    while True:
        left = t - now()
        if left <= 0:
            return
        time.sleep(min(left, 0.004))

def screen(x, y, w, h):
    # Pixels of a screen area, RGB, as int16 (differences fit)
    raw = d.screen().root.get_image(x, y, w, h, X.ZPixmap, 0xffffffff).data
    return np.frombuffer(raw, np.uint8).reshape(h, w, 4)[..., 2::-1].astype(np.int16)

def wait_for(ready, t, timeout=30.0):
    # Waits until `ready()` (polled on the screen) and story time t: what the
    # app takes beyond t (the network) is cut out of the video, and the story
    # goes on at t. Returns the seconds cut.
    while now() < t:
        time.sleep(0.01)
    if ready():
        return 0.0
    a, m = time.time(), time.monotonic()
    while not ready():
        if time.monotonic() - m > timeout:
            raise SystemExit(f'still waiting after {timeout} s at {t:.2f} s')
        time.sleep(0.02)
    cuts.append((a, time.time()))
    shift[0] += time.monotonic() - m
    return time.monotonic() - m

def send_motion():
    xtest.fake_input(d, X.MotionNotify, x=int(round(pos[0])), y=int(round(pos[1])))
    d.sync()

def warp(x, y):
    # A touchscreen has no hover: the X pointer only moves while pressed, the
    # finger drawn on the video follows the whole track
    pos[0], pos[1] = x, y
    if down[0]:
        send_motion()
    log()

def ease(u):
    return u * u * (3 - 2 * u)  # smoothstep

def move(x, y, t0, t1, curve=0.12):
    # From where the pointer is to (x, y), between t0 and t1, along a slight arc
    sx, sy = pos
    dx, dy = x - sx, y - sy
    nx, ny = -dy * curve, dx * curve  # bulge sideways, like a hand
    wait_until(t0)
    while True:
        u = min(1.0, (now() - t0) / (t1 - t0))
        e = ease(u)
        b = math.sin(math.pi * e)
        warp(sx + dx * e + nx * b, sy + dy * e + ny * b)
        if u >= 1:
            return
        time.sleep(1 / 240)

def press(t):
    wait_until(t)
    send_motion()
    xtest.fake_input(d, X.ButtonPress, 1)
    d.sync()
    down[0] = 1
    log()

def release(t):
    wait_until(t)
    xtest.fake_input(d, X.ButtonRelease, 1)
    d.sync()
    down[0] = 0
    log()

def tap(t, hold=0.08):
    press(t)
    release(t + hold)

def drag(dx, dy, t0, t1):
    # Pointer already pressed: straight drag with easing
    move(pos[0] + dx, pos[1] + dy, t0, t1, curve=0)
