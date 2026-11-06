# OpenRig documentation

The user documentation of [OpenRig](https://github.com/Siryu6/OpenRig), the open source guitar
pedalboard, published at [docs.openrig.eu](https://docs.openrig.eu). Built with
[Astro](https://astro.build) and [Starlight](https://starlight.astro.build). The home page and
the rigs live on [openrig.eu](https://openrig.eu), a separate site.

```bash
npm install
npm run dev       # http://localhost:4321
npm run build     # static site in dist/
```

| Path | |
|---|---|
| `src/content/docs/` | Documentation, served at the root (`index.mdx` is the landing page) |
| `src/pages/privacy.astro` | Privacy page (`/privacy/`) |
| `src/links.mjs` | Links back to openrig.eu and GitHub, in the header and footer |
| `src/assets/shots/` | Screenshots of the pedalboard (2048 × 1200) |
| `public/media/` | Screen recordings (MP4 and WebM, with a poster) |
| `src/styles/` | Documentation theme, dark and light |
| `REDIRECTS.md` | Old `openrig.eu/docs/…` addresses and the Caddy redirects to here |

Screenshots come from the x86_64 OS image running in QEMU, as does the TONE3000 recording.
Captures shown in them belong to their creators on TONE3000, who are credited in the captions.

The `hero` (tour of the screen, also on the openrig.eu home page) and `live` recordings are made
by `scripts/record.sh <story>` from a release build of OpenRig on a virtual display (Xvfb,
1024×600 scaled to 1280×750) with a dummy JACK server: the story in
`scripts/record/<story>/story.py` is played with XTest, captured losslessly at 30 fps, cut to a
seamless loop with a finger drawn on it, checked with mpdecimate (frames only repeat while
nothing moves), then encoded to VP9, H.264 and a poster in `public/media/`. Re-record them for a
release that changes those pages:

```bash
cargo build --release                  # in the OpenRig repository
scripts/record.sh live /path/to/OpenRig/target/release/pedalboard
```

A new story is a folder in `scripts/record/` with `story.py`, `story.conf` and, if the app
needs setting up first, `prep.py`; the helpers are in `scripts/record/lib/`. The script lists
what it needs (Xvfb, JACK 2, ffmpeg, python-xlib, numpy, uv, optionally bwrap) and the TONE3000
tones and store plugin the preset uses, copied from the desktop app's data directory.

The site is published at [docs.openrig.eu](https://docs.openrig.eu) (`public/CNAME`) by GitHub
Pages on every push to `main`, and every 6 hours to pick up a new OpenRig release. `SITE` and
`BASE` set where it is served (`SITE=https://siryu6.github.io BASE=/openrig-doc` to serve it
under the repository name instead of the custom domain).

## Analytics

Visits are counted with a self-hosted [Umami](https://umami.is) at `stats.siryu.me`, set up in
`src/analytics.mjs` and loaded on every page by the Starlight `head`. It sets no cookies, only
counts on `docs.openrig.eu` (not local previews or github.io), and sends nothing when the browser
has Do Not Track or Global Privacy Control on, or after the opt-out on `/privacy/`. Query strings
are stripped from URLs except `utm_*` tags. Web Vitals are sent too (`data-performance`).

docs.openrig.eu is its own website in Umami. Its id is read from `UMAMI_WEBSITE_ID` when the site
is built; the deploy workflow passes the repository variable of the same name. To set it up:

1. In Umami, add a website for `docs.openrig.eu` and copy its id.
2. In the GitHub repository, *Settings → Secrets and variables → Actions → Variables*, add
   `UMAMI_WEBSITE_ID` with that id (or `gh variable set UMAMI_WEBSITE_ID --body <id>`).
3. Run the deploy workflow again.

While it is not set, the build warns and the pages load no tracker at all. The id the site used
before (`fa9bf012-…`) stays with openrig.eu, now served by the rigs site, so its history goes on
there. For a local build with the tracker: `UMAMI_WEBSITE_ID=<id> npm run build`.

| Event | Properties | When |
|---|---|---|
| `download` | `location`, `page` | Link to the GitHub releases |
| `outbound` | `host`, `url`, `page` | Any other link to another site |
| `edit-page` | `page` | "Edit page" link in the docs |
| `video-play` | `name`, `page` | First play of a docs recording |
| `copy-code` | `page` | Copy button of a code block |
| `search-open` | `page` | Docs search opened (the typed query is never sent) |
| `search-result` | `target` | Search result chosen: the page it leads to |

Links are tracked by the inline script in `src/analytics.mjs` (links to openrig.eu and GitHub
count as `outbound`); a link can also take a `data-umami-event` attribute of its own.

TONE3000 is a trademark of TONE3000; OpenRig is an independent project that uses the TONE3000
API. The site content is licensed under the GPL-3.0-or-later, like OpenRig.
