// Latest OpenRig release, read from GitHub when the site is built (never
// from the visitor's browser). Only a release whose Raspberry Pi image is
// already attached counts: the images take a few hours to build after the
// release, and the install command must point to a file that exists. The
// deploy workflow rebuilds the site on a schedule to pick new ones up.

// Used when GitHub cannot be reached (offline build)
const FALLBACK = '0.11.0';

async function fetchLatest() {
	const headers = { Accept: 'application/vnd.github+json' };
	if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
	try {
		const response = await fetch('https://api.github.com/repos/Siryu6/OpenRig/releases?per_page=20', {
			headers,
			signal: AbortSignal.timeout(10_000),
		});
		if (!response.ok) throw new Error(`GitHub answered ${response.status}`);
		for (const release of await response.json()) {
			if (release.draft || release.prerelease) continue;
			const version = release.tag_name.replace(/^v/, '');
			if (release.assets.some((a) => a.name === `openrig-os-${version}-rpi5.img.xz`)) return version;
		}
		throw new Error('no release with a Raspberry Pi image');
	} catch (error) {
		console.warn(`[release] ${error.message}; using ${FALLBACK}`);
		return FALLBACK;
	}
}

let latest;
/** Latest released version with its images, "0.3.0" */
export function latestVersion() {
	latest ??= fetchLatest();
	return latest;
}
