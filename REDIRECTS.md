# Redirects from openrig.eu

Until this change the documentation lived at `openrig.eu/docs/`, under the home page of this
site. It now lives at the root of `docs.openrig.eu`, and `openrig.eu` is the community site
(home page, rigs, sign-in). Every page kept its path below `/docs`, so each old URL redirects
by dropping that prefix and changing the host. Heading anchors (`#…`) are unchanged and kept
by browsers across the redirect.

## Documentation pages

Generated from the build output (`dist/`): every page of this site, with its old address.

| Old URL | New URL |
| --- | --- |
| `openrig.eu/docs` | `docs.openrig.eu/` |
| `openrig.eu/docs/` | `docs.openrig.eu/` |
| `openrig.eu/docs/dev/architecture/` | `docs.openrig.eu/dev/architecture/` |
| `openrig.eu/docs/dev/build/` | `docs.openrig.eu/dev/build/` |
| `openrig.eu/docs/dev/contributing/` | `docs.openrig.eu/dev/contributing/` |
| `openrig.eu/docs/getting-started/first-start/` | `docs.openrig.eu/getting-started/first-start/` |
| `openrig.eu/docs/getting-started/hardware/` | `docs.openrig.eu/getting-started/hardware/` |
| `openrig.eu/docs/getting-started/mini-pc/` | `docs.openrig.eu/getting-started/mini-pc/` |
| `openrig.eu/docs/getting-started/raspberry-pi/` | `docs.openrig.eu/getting-started/raspberry-pi/` |
| `openrig.eu/docs/help/faq/` | `docs.openrig.eu/help/faq/` |
| `openrig.eu/docs/help/ssh/` | `docs.openrig.eu/help/ssh/` |
| `openrig.eu/docs/help/troubleshooting/` | `docs.openrig.eu/help/troubleshooting/` |
| `openrig.eu/docs/setup/footswitches/` | `docs.openrig.eu/setup/footswitches/` |
| `openrig.eu/docs/setup/lv2/` | `docs.openrig.eu/setup/lv2/` |
| `openrig.eu/docs/setup/pedalboard-txt/` | `docs.openrig.eu/setup/pedalboard-txt/` |
| `openrig.eu/docs/setup/performance/` | `docs.openrig.eu/setup/performance/` |
| `openrig.eu/docs/setup/routing/` | `docs.openrig.eu/setup/routing/` |
| `openrig.eu/docs/setup/settings/` | `docs.openrig.eu/setup/settings/` |
| `openrig.eu/docs/setup/store/` | `docs.openrig.eu/setup/store/` |
| `openrig.eu/docs/setup/updates/` | `docs.openrig.eu/setup/updates/` |
| `openrig.eu/docs/using/editor/` | `docs.openrig.eu/using/editor/` |
| `openrig.eu/docs/using/live/` | `docs.openrig.eu/using/live/` |
| `openrig.eu/docs/using/midi/` | `docs.openrig.eu/using/midi/` |
| `openrig.eu/docs/using/neural-blocks/` | `docs.openrig.eu/using/neural-blocks/` |
| `openrig.eu/docs/using/plugin-views/` | `docs.openrig.eu/using/plugin-views/` |
| `openrig.eu/docs/using/presets/` | `docs.openrig.eu/using/presets/` |
| `openrig.eu/docs/using/rack/` | `docs.openrig.eu/using/rack/` |
| `openrig.eu/docs/using/rigs/` | `docs.openrig.eu/using/rigs/` |
| `openrig.eu/docs/using/tone3000/` | `docs.openrig.eu/using/tone3000/` |
| `openrig.eu/docs/using/tour/` | `docs.openrig.eu/using/tour/` |
| `openrig.eu/docs/using/tuner-looper/` | `docs.openrig.eu/using/tuner-looper/` |

## Other pages and files of the old site

| Old URL | Now | Redirect |
| --- | --- | --- |
| `openrig.eu/` | Home page of the community site | none, same URL |
| `openrig.eu/#rigs` (rigs section of the old home page) | `openrig.eu/rigs` | none: the fragment never reaches the server, the home page links to the rigs |
| `openrig.eu/privacy/` | `openrig.eu/privacy` (the community site's policy; `docs.openrig.eu/privacy/` covers the docs) | `/privacy/` → `/privacy` |
| `openrig.eu/media/{hero,live,tone3000}.{jpg,mp4,webm}` | `docs.openrig.eu/media/…` | `/media/*` → docs |
| `openrig.eu/og.png` | `docs.openrig.eu/og.png` (the community site has its own, `/static/og.png`) | → docs |
| `openrig.eu/favicon.svg` | `openrig.eu/static/favicon.svg` | → `/static/favicon.svg` |
| `openrig.eu/t3k-mark.svg` | `openrig.eu/static/t3k-mark.svg` | → `/static/t3k-mark.svg` |
| `openrig.eu/pagefind/*` | `docs.openrig.eu/pagefind/*` | → docs (only stale cached pages ask for it) |
| `openrig.eu/sitemap-index.xml`, `/sitemap-0.xml` | `docs.openrig.eu/sitemap-index.xml`; the community site has `/sitemap.xml` | → docs |
| `openrig.eu/_astro/*` | hashed build assets, renamed on every build | none, 404 |
| `openrig.eu/404.html` | | none |

The `/static/…` targets are the community site's routes at the time of writing; check them
against its `src/assets.rs` before deploying.

## Caddy

To add to the `openrig.eu` site block, before its `reverse_proxy` to the community site.
`redir` runs before `handle_path` and `reverse_proxy` in Caddy's directive order, and
`handle_path` strips `/docs` from the URI, so `{uri}` (path and query) is what follows it.

```caddyfile
openrig.eu {
	# The documentation moved to docs.openrig.eu, same paths without /docs
	redir /docs https://docs.openrig.eu/ permanent
	handle_path /docs/* {
		redir https://docs.openrig.eu{uri} permanent
	}

	# Files of the old static site
	@docs_files path /media/* /pagefind/* /og.png /sitemap-index.xml /sitemap-0.xml
	redir @docs_files https://docs.openrig.eu{uri} permanent
	redir /favicon.svg /static/favicon.svg permanent
	redir /t3k-mark.svg /static/t3k-mark.svg permanent
	redir /privacy/ /privacy permanent

	reverse_proxy …  # the community site, unchanged
}
```

`permanent` is a 301. Use `redir … temporary` (302) first if you want to try it without
browsers caching the redirect. Check after deploying:

```bash
curl -sI https://openrig.eu/docs/using/rigs/ | grep -i '^location'   # https://docs.openrig.eu/using/rigs/
curl -sI https://openrig.eu/docs | grep -i '^location'               # https://docs.openrig.eu/
curl -sI https://openrig.eu/privacy/ | grep -i '^location'           # /privacy
```
