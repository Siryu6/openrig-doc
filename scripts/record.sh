#!/usr/bin/env bash
# Records a docs video (public/media/<story>.webm, .mp4 and .jpg) from a
# desktop build of OpenRig: the app runs on a virtual X display (Xvfb) at
# 1024×600 scaled by 1.25 (1280×750), on a dummy JACK server fed with strummed
# chords, and scripts/record/<story>/story.py plays the story with XTest. The
# capture is lossless at 30 fps, cut to a seamless loop, and a translucent
# finger is drawn where the pointer is (scripts/record/lib/compose.py).
#
#   scripts/record.sh <story> /path/to/OpenRig/target/release/pedalboard
#
# Stories, in scripts/record/<story>/:
#   hero   the rack: a block selected, a knob turned, a reverb bypassed, the editor
#   live   the Live page: stomps toggled, scenes recalled, the tempo tapped
#   tone3000  the TONE3000 trending amps browsed from the Amp block, one
#          capture downloaded and loaded (online, with the user's account)
# A story has story.py (the gestures, timed from the start of the loop),
# story.conf (CAPTURE: seconds to capture; TONE3000=1 when it signs in) and
# optionally prep.py, played before the capture starts (to open a page, for
# instance).
#
# Build OpenRig in release mode first (cargo build --release). Every story
# plays the "Hard Rock" preset of scripts/record/lib/rig.py, whose models are
# TONE3000 tones read from OPENRIG_DATA (default ~/.local/share/pedalboard,
# the desktop app's data): download in the app Boss Metal Zone MT-2, Peavey
# 5150 Blockletter, Mesa Boogie 2x12 V30 - XR IR PACK and BOSS CE-2w, and
# install TAP Equalizer from the plugin store. Only these are copied; the
# app runs on a data directory of its own, never on OPENRIG_DATA. A TONE3000
# story also copies the account link (tone3000.json, connect it in Settings
# first) and copies it back if the app refreshed it: TONE3000 rotates the
# refresh token, so the old copy would no longer sign in.
#
# Needs Xvfb, jackd (JACK 2), ffmpeg with libvpx-vp9 and libx264, python3 with
# python-xlib and numpy, and uv (for the JACK-Client Python module). With
# bwrap (bubblewrap), the app reads a steady 48 °C instead of this computer's
# CPU temperature, so the top bar does not change while nothing moves.
# Environment: OPENRIG_DATA, RECORD_DISPLAY (default :77), RECORD_OUT
# (default public/media), RECORD_KEEP=1 to keep the work directory.
set -euo pipefail

story=${1:?usage: $0 <story> /path/to/pedalboard}
bin=${2:?usage: $0 <story> /path/to/pedalboard}
bin=$(realpath "$bin")
here=$(cd "$(dirname "$0")" && pwd)
lib=$here/record/lib
dir=$here/record/$story
[ -f "$dir/story.py" ] || { echo "no story '$story' in $here/record" >&2; exit 1; }
CAPTURE=15
TONE3000=
# shellcheck source=/dev/null
. "$dir/story.conf"
src=${OPENRIG_DATA:-$HOME/.local/share/pedalboard}
display=${RECORD_DISPLAY:-:77}
out=${RECORD_OUT:-$here/../public/media}
fps=30
work=$(mktemp -d "/tmp/openrig-$story.XXXXXX")
server=openrig-$story-$$
pids=()

cleanup() {
	for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done
	wait 2>/dev/null || true
	# The account link, refreshed by the app: back where it came from
	if [ -n "$TONE3000" ] && [ -f "${data:-}/tone3000.json" ] && ! cmp -s "$data/tone3000.json" "$src/tone3000.json"; then
		cp "$data/tone3000.json" "$src/tone3000.json" && chmod 600 "$src/tone3000.json"
	fi
	if [ "${RECORD_KEEP:-}" = 1 ]; then echo "kept $work"; else rm -rf "$work"; fi
}
trap cleanup EXIT

# A data directory of its own: the preset, its models, the TAP Equalizer
export HOME=$work/home
data=$HOME/.local/share/pedalboard
mkdir -p "$data/models/Tone3000"/{Amps,Cabs,Pedals} "$data/lv2" "$work/run"
chmod 700 "$work/run"
for tone in 'Pedals/Boss Metal Zone MT-2 [96210]' 'Amps/Peavey 5150 Blockletter [87953]' \
	'Cabs/Mesa Boogie 2x12 V30 - XR IR PACK [97616]' 'Pedals/BOSS CE-2w [79338]'; do
	cp -r "$src/models/Tone3000/$tone" "$data/models/Tone3000/$(dirname "$tone")/" ||
		{ echo "missing TONE3000 tone: $tone" >&2; exit 1; }
done
cp -r "$src/lv2/tap-eq.lv2" "$data/lv2/" || { echo "missing TAP Equalizer (plugin store)" >&2; exit 1; }
if [ -n "$TONE3000" ]; then
	grep -q '"session"' "$src/tone3000.json" 2>/dev/null ||
		{ echo "no TONE3000 account linked in $src (Settings > TONE3000)" >&2; exit 1; }
	cp -p "$src/tone3000.json" "$data/"
fi
python3 "$lib/rig.py" "$data"

export DISPLAY=$display JACK_DEFAULT_SERVER=$server XDG_RUNTIME_DIR=$work/run
export XDG_CONFIG_HOME=$HOME/.config XDG_DATA_HOME=$HOME/.local/share XDG_CACHE_HOME=$HOME/.cache
export SLINT_SCALE_FACTOR=1.25 FONTCONFIG_FILE=$lib/fonts.conf  # DejaVu Sans, as on the OS image
export PYTHONPATH=$lib
unset WAYLAND_DISPLAY

# A steady CPU temperature in the top bar, as on a Pi at rest
run=("$bin")
if command -v bwrap >/dev/null; then
	mkdir -p "$work/thermal/thermal_zone0"
	echo cpu-thermal >"$work/thermal/thermal_zone0/type"
	echo 48000 >"$work/thermal/thermal_zone0/temp"
	run=(bwrap --dev-bind / / --bind "$work/thermal" /sys/class/thermal -- "$bin")
else
	echo "no bwrap: the top bar shows this computer's CPU temperature" >&2
fi

Xvfb "$display" -screen 0 1280x750x24 -nolisten tcp >"$work/xvfb.log" 2>&1 &
pids+=($!)
# A long period keeps the load figure steady on a busy desktop
jackd -n "$server" -d dummy -r 48000 -p 2048 >"$work/jack.log" 2>&1 &
pids+=($!)
sleep 2
RUST_LOG=warn "${run[@]}" >"$work/app.log" 2>&1 &
pids+=($!)
for _ in $(seq 50); do python3 "$lib/resize.py" && break; sleep 0.2; done
uv run --quiet --with JACK-Client --with numpy python "$lib/strum.py" pedalboard:in_1 pedalboard:in_2 \
	>"$work/strum.log" 2>&1 &
pids+=($!)
for _ in $(seq 600); do grep -q connected "$work/strum.log" && break; sleep 0.2; done
grep -q connected "$work/strum.log" || { cat "$work/strum.log" >&2; echo "no input signal" >&2; exit 1; }
sleep 6  # models loaded, meters and load figure settled
if [ -f "$dir/prep.py" ]; then
	python3 "$dir/prep.py" "$work/anchor"
	sleep 1
fi

# Lossless capture with wall clock timestamps, the story starting 1 s in
ffmpeg -nostdin -v error -y -f x11grab -framerate $fps -draw_mouse 0 -video_size 1280x750 -i "$display" \
	-copyts -c:v ffv1 -frames:v $((CAPTURE * fps)) "$work/capture.nut" &
grab=$!
sleep 1
python3 "$dir/story.py" "$work/story.json" "$work/anchor"
wait $grab
if grep -q 'Resources running low' "$work/app.log"; then
	echo "warning: the app reported low resources (a toast may show):" >&2
	grep 'Resources running low' "$work/app.log" >&2
fi

python3 "$lib/compose.py" "$work/capture.nut" "$work/story.json" "$work/loop.nut" $fps
python3 "$lib/still.py" "$work/loop.nut" "$work/story.json" $fps

mkdir -p "$out"
ffmpeg -nostdin -v error -y -i "$work/loop.nut" -frames:v 1 -q:v 3 "$out/$story.jpg"
ffmpeg -nostdin -v error -y -i "$work/loop.nut" -pix_fmt yuv420p -c:v libx264 -preset veryslow -crf 23 \
	-tune animation -movflags +faststart -an "$out/$story.mp4"
ffmpeg -nostdin -v error -y -i "$work/loop.nut" -pix_fmt yuv420p -c:v libvpx-vp9 -b:v 0 -crf 36 \
	-deadline good -cpu-used 1 -row-mt 1 -an -pass 1 -passlogfile "$work/vp9" -f null /dev/null
ffmpeg -nostdin -v error -y -i "$work/loop.nut" -pix_fmt yuv420p -c:v libvpx-vp9 -b:v 0 -crf 36 \
	-deadline good -cpu-used 1 -row-mt 1 -an -pass 2 -passlogfile "$work/vp9" "$out/$story.webm"

for f in "$out/$story".{webm,mp4,jpg}; do echo "$(basename "$f"): $(du -k "$f" | cut -f1) KiB"; done
echo "frames: $(ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 "$out/$story.mp4")," \
	"unique: $(ffmpeg -nostdin -i "$out/$story.mp4" -vf mpdecimate -f null - 2>&1 | grep -o 'frame= *[0-9]*' | tail -1 | tr -dc 0-9)"
