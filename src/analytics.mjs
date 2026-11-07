// Umami analytics of the docs, loaded in the Starlight head. Cookieless;
// counted on docs.openrig.eu only; skipped with Do Not Track or Global Privacy
// Control. Event names are listed in the README.

/** Placeholder: setting UMAMI_WEBSITE_ID to it builds the site without a tracker */
const UMAMI_PLACEHOLDER = 'docs-website-id-not-set';

/** Umami website id of docs.openrig.eu (not openrig.eu's: that one stays with the rigs site) */
const DOCS_WEBSITE_ID = 'd6be4cd7-2560-4f20-b463-4c4a290de649';

/**
 * Umami website id, overridable with UMAMI_WEBSITE_ID when the site is built
 * (the deploy workflow passes the repository variable of that name, if set)
 */
export const UMAMI_WEBSITE_ID = process.env.UMAMI_WEBSITE_ID || DOCS_WEBSITE_ID;

/** Attributes of the Umami tracker script */
export const umamiScript = {
	src: 'https://stats.siryu.me/script.js',
	'data-website-id': UMAMI_WEBSITE_ID,
	'data-domains': 'docs.openrig.eu',
	'data-do-not-track': 'true',
	'data-performance': 'true',
	'data-before-send': 'openrigBeforeSend',
};

// Runs before the tracker: cleans what it sends and tracks what attributes can't
// reach (Markdown links, Starlight search, code copy buttons)
export const umamiInline = `(() => {
	// Keep only utm_* campaign parameters in URLs: no click IDs or other query data
	const clean = (value) => {
		if (!value) return value;
		try {
			const url = new URL(value, location.href);
			for (const key of [...url.searchParams.keys()]) if (!key.startsWith('utm_')) url.searchParams.delete(key);
			return value.startsWith('/') ? url.pathname + url.search + url.hash : url.href;
		} catch {
			return value;
		}
	};
	window.openrigBeforeSend = (type, payload) => {
		if (navigator.globalPrivacyControl) return false;
		return { ...payload, url: clean(payload.url), referrer: clean(payload.referrer) };
	};

	const track = (name, data) => window.umami && window.umami.track(name, data);
	const page = () => location.pathname;

	// Downloads, one event name per kind (as on openrig.eu): Umami lists events
	// by name, so a property alone would not tell them apart
	const downloadEvent = (url) => {
		if (url.host === 'github.com') {
			const file = url.pathname.match(/^\\/Siryu6\\/OpenRig\\/releases\\/download\\/v?([^/]+)\\/([^/]+)$/i);
			if (file) {
				const [, version, name] = file;
				let m;
				if ((m = name.match(/^openrig-os-.+-(rpi5|x86_64)\\.img\\.xz$/))) return { name: 'download-os-' + m[1], data: { version } };
				if ((m = name.match(/^openrig-.+-linux-(x86_64|aarch64)\\.tar\\.gz$/))) return { name: 'download-linux-' + m[1], data: { version } };
				if ((m = name.match(/^openrig-os-.+-(rpi5|x86_64)(-app)?\\.raucb$/)))
					return { name: 'download-bundle', data: { version, platform: m[1], kind: m[2] ? 'app' : 'system' } };
				if ((m = name.match(/^openrig-os-.+-(rpi5|x86_64)\\.sha256$/))) return { name: 'download-checksum', data: { version, target: 'os-' + m[1] } };
				if ((m = name.match(/^openrig-.+-linux-(x86_64|aarch64)\\.tar\\.gz\\.sha256$/)))
					return { name: 'download-checksum', data: { version, target: 'linux-' + m[1] } };
			}
			if (/^\\/Siryu6\\/OpenRig\\/releases/i.test(url.pathname)) return { name: 'download-page', data: { target: 'github-releases' } };
		}
		if (url.host === 'openrig.eu') {
			if (/^\\/download\\/?$/.test(url.pathname)) return { name: 'download-page', data: { target: 'openrig-download' } };
			const rig = url.pathname.match(/^\\/r\\/([^/]+)\\/download$/);
			if (rig) return { name: 'download-rig', data: { rig: rig[1], source: 'docs' } };
		}
		return null;
	};

	document.addEventListener('click', (event) => {
		const target = event.target instanceof Element ? event.target : null;
		if (!target) return;
		if (target.closest('.expressive-code .copy button')) return track('copy-code', { page: page() });
		const link = target.closest('a[href]');
		if (!link || link.hasAttribute('data-umami-event')) return;
		const url = new URL(link.href, location.href);
		// A search result: the page it leads to, never the query
		if (link.closest('#starlight__search')) return track('search-result', { target: url.pathname });
		if (url.href.startsWith('https://github.com/Siryu6/openrig-doc/edit/')) return track('edit-page', { page: page() });
		if (url.host === location.host || !url.protocol.startsWith('http')) return;
		const download = downloadEvent(url);
		if (download) return track(download.name, { ...download.data, location: 'docs', page: page() });
		track('outbound', { host: url.host, url: url.origin + url.pathname, page: page() });
	});

	// Starlight search: count openings (button, Ctrl+K or /), not what is typed
	document.addEventListener('DOMContentLoaded', () => {
		const dialog = document.querySelector('site-search dialog');
		if (!dialog) return;
		new MutationObserver(() => dialog.open && track('search-open', { page: page() })).observe(dialog, {
			attributes: true,
			attributeFilter: ['open'],
		});
	});
})();`;

/** Starlight head entries: the inline script and the tracker, or nothing without a website id */
export const umamiHead =
	UMAMI_WEBSITE_ID === UMAMI_PLACEHOLDER
		? []
		: [
				{ tag: 'script', content: umamiInline },
				{ tag: 'script', attrs: { ...umamiScript, defer: true } },
			];
if (UMAMI_WEBSITE_ID === UMAMI_PLACEHOLDER) console.warn('[analytics] UMAMI_WEBSITE_ID is the placeholder: no Umami tracker');
