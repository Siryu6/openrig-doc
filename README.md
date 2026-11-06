# OpenRig website

The website and user documentation of [OpenRig](https://github.com/Siryu6/OpenRig), the open
source guitar pedalboard. Built with [Astro](https://astro.build) and
[Starlight](https://starlight.astro.build).

```bash
npm install
npm run dev       # http://localhost:4321
npm run build     # static site in dist/
```

| Path | |
|---|---|
| `src/pages/index.astro` | Landing page |
| `src/content/docs/docs/` | Documentation, served under `/docs/` |
| `src/assets/shots/` | Screenshots of the pedalboard (2048 × 1200) |
| `public/media/` | Screen recordings (MP4 and WebM, with a poster) |
| `src/styles/` | Landing page and documentation themes |

Screenshots and recordings come from the x86_64 OS image running in QEMU, except the home page
video. Captures shown in them belong to their creators on TONE3000, who are credited in the
captions.

The home page video (`public/media/hero.*`) is recorded by `scripts/record-hero.sh` from a
release build of OpenRig on a virtual display (Xvfb, 1024×600 scaled to 1280×750) with a dummy
JACK server: the story in `scripts/hero/story.py` is played with XTest, captured losslessly at
30 fps, cut to a seamless 12 s loop with a finger drawn on it, then encoded to VP9, H.264 and a
poster. Re-record it for a release that changes the rack:

```bash
cargo build --release                  # in the OpenRig repository
scripts/record-hero.sh /path/to/OpenRig/target/release/pedalboard
```

The script lists what it needs (Xvfb, JACK 2, ffmpeg, python-xlib, numpy, uv) and the TONE3000
tones and store plugin the preset uses, read from the desktop app's data directory.

The site is published at [openrig.eu](https://openrig.eu) by GitHub Pages on every push to
`main`. `SITE` and `BASE` set where it is served (`BASE=/openrig-site` to serve it under the
repository name instead of the custom domain).

## Analytics

Visits are counted with a self-hosted [Umami](https://umami.is) at `stats.siryu.me`, set up in
`src/analytics.mjs` and loaded on every page (landing layout and Starlight `head`). It sets no
cookies, only counts on `openrig.eu` (not local previews or github.io), and sends nothing when
the browser has Do Not Track or Global Privacy Control on, or after the opt-out on `/privacy`.
Query strings are stripped from URLs except `utm_*` tags. Web Vitals are sent too
(`data-performance`).

| Event | Properties | When |
|---|---|---|
| `get-started` | `location` | Hero "Get started" button |
| `download` | `location`, `version` / `page` | Link to the GitHub releases |
| `github` | `location`, `target` | Link to the OpenRig repository, its issues or changelog |
| `docs-link` | `location`, `target` | Landing page link into the docs |
| `outbound` | `host`, `url`, `page` | Any other link to another site |
| `edit-page` | `page` | "Edit page" link in the docs |
| `video-play` | `name`, `page` | First play of a docs recording |
| `copy-code` | `page` | Copy button of a code block |
| `search-open` | `page` | Docs search opened (the typed query is never sent) |
| `search-result` | `target` | Search result chosen: the page it leads to |
| `rigs-follow` | `target` (`reddit` / `github`) | Home page rigs section, while the rigs site is not live |
| `rigs-browse` | `location` | "Browse rigs" on the home page, once the rigs site is live |

The rigs section of the home page (`src/components/Rigs.astro`) says "Coming soon" and asks to
follow the project until `RIGS_LIVE` is set to `true` in `src/rigs.mjs`; it then links to
`RIGS_URL` with "Browse rigs".

Links take a `data-umami-event` attribute where they are written in a component; links in the
Markdown, the search and code blocks are tracked by the inline script in `src/analytics.mjs`.

TONE3000 is a trademark of TONE3000; OpenRig is an independent project that uses the TONE3000
API. The site content is licensed under the GPL-3.0-or-later, like OpenRig.
