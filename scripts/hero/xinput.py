# Pointer gestures over XTest, timed against a monotonic clock
import math, time
from Xlib import X, display
from Xlib.ext import xtest

d = display.Display()
T0 = time.monotonic()
T0_wall = time.time()
pos = [0, 0]
down = [0]
# Pointer track for the touch overlay: wall clock (as x11grab stamps frames), x, y, pressed
track = []

def log():
    track.append((time.time(), pos[0], pos[1], down[0]))

def now():
    return time.monotonic() - T0

def wait_until(t):
    while True:
        left = t - now()
        if left <= 0:
            return
        time.sleep(min(left, 0.004))

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
