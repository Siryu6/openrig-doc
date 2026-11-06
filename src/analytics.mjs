// Umami analytics, shared by the landing page layout and the Starlight docs.
// Cookieless; counted on openrig.eu only; skipped with Do Not Track or Global
// Privacy Control. Event names are listed in the README.

/** Attributes of the Umami tracker script */
export const umamiScript = {
	src: 'https://stats.siryu.me/script.js',
	'data-website-id': 'fa9bf012-2401-4451-9d2d-08922a9f8063',
	'data-domains': 'openrig.eu',
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
		if (url.host === 'github.com' && /^\\/Siryu6\\/OpenRig\\/releases/i.test(url.pathname))
			return track('download', { location: 'docs', page: page() });
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
