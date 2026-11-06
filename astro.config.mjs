// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { umamiInline, umamiScript } from './src/analytics.mjs';

// Where the site is served: openrig.eu at the root, or GitHub Pages under
// the repository name (SITE=https://siryu6.github.io BASE=/openrig-site)
const site = process.env.SITE ?? 'https://openrig.eu';
const base = process.env.BASE ?? '/';

export default defineConfig({
	site,
	base,
	integrations: [
		starlight({
			title: 'OpenRig',
			description:
				'Open source guitar pedalboard for the Raspberry Pi 5: neural amp captures, impulse responses and LV2 effects on a touchscreen.',
			logo: { src: './src/assets/logo-mark.svg', alt: 'OpenRig' },
			favicon: '/favicon.svg',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/Siryu6/OpenRig' }],
			editLink: { baseUrl: 'https://github.com/Siryu6/openrig-site/edit/main/' },
			components: { Footer: './src/components/DocsFooter.astro' },
			customCss: ['./src/styles/fonts.css', './src/styles/docs.css'],
			head: [
				{ tag: 'meta', attrs: { property: 'og:image', content: new URL(`${base.replace(/\/$/, '')}/og.png`, site).href } },
				{ tag: 'meta', attrs: { name: 'twitter:card', content: 'summary_large_image' } },
				{ tag: 'script', content: umamiInline },
				{ tag: 'script', attrs: { ...umamiScript, defer: true } },
			],
			sidebar: [
				{
					label: 'Getting started',
					items: [
						{ label: 'Introduction', slug: 'docs' },
						{ label: 'What you need', slug: 'docs/getting-started/hardware' },
						{ label: 'Install on a Raspberry Pi 5', slug: 'docs/getting-started/raspberry-pi' },
						{ label: 'Install on a mini PC', slug: 'docs/getting-started/mini-pc' },
						{ label: 'First start', slug: 'docs/getting-started/first-start' },
					],
				},
				{
					label: 'Playing',
					items: [
						{ label: 'Tour of the screen', slug: 'docs/using/tour' },
						{ label: 'The rack', slug: 'docs/using/rack' },
						{ label: 'Block editor', slug: 'docs/using/editor' },
						{ label: 'Plugin views', slug: 'docs/using/plugin-views' },
						{ label: 'Amps, pedals and cabinets', slug: 'docs/using/neural-blocks' },
						{ label: 'TONE3000', slug: 'docs/using/tone3000' },
						{ label: 'Presets, scenes and setlists', slug: 'docs/using/presets' },
						{ label: 'Sharing rigs', slug: 'docs/using/rigs', badge: { text: 'Soon', variant: 'note' } },
						{ label: 'Live page and footswitches', slug: 'docs/using/live' },
						{ label: 'Tuner and looper', slug: 'docs/using/tuner-looper' },
						{ label: 'MIDI', slug: 'docs/using/midi' },
					],
				},
				{
					label: 'Setting up',
					items: [
						{ label: 'Settings', slug: 'docs/setup/settings' },
						{ label: 'Inputs and outputs', slug: 'docs/setup/routing' },
						{ label: 'Updates', slug: 'docs/setup/updates' },
						{ label: 'Footswitches and encoder', slug: 'docs/setup/footswitches' },
						{ label: 'LV2 plugins', slug: 'docs/setup/lv2' },
						{ label: 'Plugin store', slug: 'docs/setup/store' },
						{ label: 'pedalboard.txt', slug: 'docs/setup/pedalboard-txt' },
						{ label: 'Performance', slug: 'docs/setup/performance' },
					],
				},
				{
					label: 'Help',
					items: [
						{ label: 'Troubleshooting', slug: 'docs/help/troubleshooting' },
						{ label: 'SSH and logs', slug: 'docs/help/ssh' },
						{ label: 'FAQ', slug: 'docs/help/faq' },
					],
				},
				{
					label: 'Developers',
					items: [
						{ label: 'Build from source', slug: 'docs/dev/build' },
						{ label: 'How it works', slug: 'docs/dev/architecture' },
						{ label: 'Contributing', slug: 'docs/dev/contributing' },
					],
				},
			],
		}),
	],
});
