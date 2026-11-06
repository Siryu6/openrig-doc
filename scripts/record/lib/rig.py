# Writes the data directory of the recording: the "Hard Rock" preset (also the
# session restored at start) and a synthetic hall impulse response.
# usage: rig.py DATA_DIR
import json, math, os, random, struct, sys, wave

data = sys.argv[1]
os.makedirs(os.path.join(data, 'presets'), exist_ok=True)
os.makedirs(os.path.join(data, 'models'), exist_ok=True)

# Models, relative to DATA_DIR/models: TONE3000 tones downloaded from the app
FILES = {
    '1': 'Tone3000/Pedals/Boss Metal Zone MT-2 [96210]/Boss MT-2 - Hard Rock.nam',
    '2': 'Tone3000/Amps/Peavey 5150 Blockletter [87953]/Peavey 5150 Blockletter Red.nam',
    '3': 'Tone3000/Cabs/Mesa Boogie 2x12 V30 - XR IR PACK [97616]/TF MESA 2X12 V30 - 57 R121 70-30.wav',
    '6': 'Tone3000/Pedals/BOSS CE-2w [79338]/BOSS CE-2 Wazacraft.nam',
    '7': 'Synthetic hall.wav',
}
missing = [f for f in FILES.values() if not os.path.exists(os.path.join(data, 'models', f)) and f != FILES['7']]
if missing:
    sys.exit('missing models (download these tones from TONE3000 in the app):\n  ' + '\n  '.join(missing))


def block(instance_id, uri):
    return {'Plugin': {'instance_id': instance_id, 'uri': uri, 'enabled': True, 'num_inputs': 1, 'num_outputs': 1}}


# IN → MT-2 → 5150 → 2x12 cab → TAP Equalizer → Mix (CE-2 chorus | dry) → hall → OUT
nodes = [
    block(1, 'urn:pedalboard:nam-pedal'),
    block(2, 'urn:pedalboard:nam'),
    block(3, 'urn:pedalboard:ir'),
    block(4, 'http://moddevices.com/plugins/tap/eq'),
    {'Split': {'instance_id': 5, 'split_type': 'Mix', 'enabled': True,
               'top_chain': [block(6, 'urn:pedalboard:nam-pedal')], 'bottom_chain': [],
               'ab_select_a': True, 'mix_ratio': 0.5, 'pan': [0.0, 0.0], 'num_inputs': 1, 'num_outputs': 1}},
    block(7, 'urn:pedalboard:ir-space'),
]
ids = [str(i) for i in range(1, 8)]
chain = {
    'nodes': nodes, 'params': {}, 'files': FILES, 'colors': {'6': 'blue'},
    'scenes': [{'name': name, 'enabled': {i: True for i in ids}, 'params': {}} for name in ('Rhythm', 'Lead', 'Clean')],
    'scene': 0, 'bpm': 120.0,
}
preset_id = '7d4f3a52-5b1e-4c47-9a7e-3c1f2b8e9d01'
preset = {'id': preset_id, 'name': 'Hard Rock', 'description': '', 'created_at': 1791459786,
          'modified_at': 1791459786, 'plugins': [], 'stereo_mode': False, 'tags': [], 'chain': chain}
json.dump(preset, open(os.path.join(data, 'presets', 'Hard Rock.json'), 'w'), indent=1)
json.dump({'chain': chain, 'stereo_mode': False, 'preset_id': preset_id},
          open(os.path.join(data, 'session.json'), 'w'), indent=1)

# Synthetic hall: decaying noise, 2.4 s
sr = 48000
random.seed(7)
frames = bytearray()
for i in range(int(sr * 2.4)):
    t = i / sr
    v = random.gauss(0, 0.3) * math.exp(-t * 2.9) * min(1, t / 0.012)
    frames += struct.pack('<h', max(-32767, min(32767, int(v * 32767))))
with wave.open(os.path.join(data, 'models', FILES['7']), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(bytes(frames))
