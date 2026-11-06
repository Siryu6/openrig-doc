# A JACK client that plays strummed power chords into the pedalboard input in
# a loop, so the level meters move. Period: one bar at 120 BPM (2 s).
import sys, threading, time
import jack
import numpy as np

client = jack.Client('hero-signal')
out = client.outports.register('out')
sr = client.samplerate
rng = np.random.default_rng(3)

def pluck(freq, seconds):
    # Karplus-Strong string
    n = int(sr * seconds)
    period = int(sr / freq)
    buf = rng.uniform(-1, 1, period)
    y = np.zeros(n)
    for i in range(n):
        y[i] = buf[i % period]
        buf[i % period] = 0.996 * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return y

loop = np.zeros(int(sr * 2.0))
chord = [82.41, 123.47, 164.81]  # E power chord
hits = [0.0, 0.5, 0.75, 1.0, 1.5, 1.75]
for h in hits:
    start = int(h * sr)
    for k, f in enumerate(chord):
        s = pluck(f, 0.5)
        a = start + k * 90
        loop[a:a + len(s)] += 0.12 * s[: max(0, len(loop) - a)]
loop = loop.astype(np.float32)
pos = 0

@client.set_process_callback
def process(frames):
    global pos
    buf = out.get_array()
    idx = (np.arange(frames) + pos) % len(loop)
    buf[:] = loop[idx]
    pos = (pos + frames) % len(loop)

with client:
    for port in sys.argv[1:]:
        for _ in range(100):  # the app may still be starting
            if client.get_ports(port):
                break
            time.sleep(0.2)
        client.connect(out, port)
    print('connected', flush=True)
    threading.Event().wait()
