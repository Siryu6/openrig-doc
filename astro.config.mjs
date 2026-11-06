// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { umamiInline, umamiScript } from './src/analytics.mjs';

// Where the docs are served: docs.openrig.eu at the root, or GitHub Pages under
// the repository name (SITE=https://siryu6.github.io BASE=/openrig-doc)
const site = process.env.SITE ?? 'https://docs.openrig.eu';
const base = process.env.BASE ?? '/';

export default defineConfig({
	site,
	base,
	integrations: [
		starlight({
			title: 'OpenRig Docs',
			description:
				'Documentation of OpenRig, the open source guitar pedalboard for the Raspberry Pi 5: install it, play it, set it up.',
			logo: { src: './src/assets/logo-mark.svg', alt: 'OpenRig' },
			favicon: '/favicon.svg',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/Siryu6/OpenRig' }],
			editLink: { baseUrl: 'https://github.com/Siryu6/openrig-doc/edit/main/' },
			components: {
				Footer: './src/components/DocsFooter.astro',
				SocialIcons: './src/components/SocialIcons.astro',
			},
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
						{ label: 'Introduction', link: '/' },
						{ label: 'What you need', slug: 'getting-started/hardware' },
						{ label: 'Install on a Raspberry Pi 5', slug: 'getting-started/raspberry-pi' },
						{ label: 'Install on a mini PC', slug: 'getting-started/mini-pc' },
						{ label: 'First start', slug: 'getting-started/first-start' },
					],
				},
				{
					label: 'Playing',
					items: [
						{ label: 'Tour of the screen', slug: 'using/tour' },
						{ label: 'The rack', slug: 'using/rack' },
						{ label: 'Block editor', slug: 'using/editor' },
						{ label: 'Plugin views', slug: 'using/plugin-views' },
						{ label: 'Amps, pedals and cabinets', slug: 'using/neural-blocks' },
						{ label: 'TONE3000', slug: 'using/tone3000' },
						{ label: 'Presets, scenes and setlists', slug: 'using/presets' },
						{ label: 'Sharing rigs', slug: 'using/rigs', badge: { text: 'Soon', variant: 'note' } },
						{ label: 'Live page and footswitches', slug: 'using/live' },
						{ label: 'Tuner and looper', slug: 'using/tuner-looper' },
						{ label: 'MIDI', slug: 'using/midi' },
					],
				},
				{
					label: 'Setting up',
					items: [
						{ label: 'Settings', slug: 'setup/settings' },
						{ label: 'Inputs and outputs', slug: 'setup/routing' },
						{ label: 'Updates', slug: 'setup/updates' },
						{ label: 'Footswitches and encoder', slug: 'setup/footswitches' },
						{ label: 'LV2 plugins', slug: 'setup/lv2' },
						{ label: 'Plugin store', slug: 'setup/store' },
						{ label: 'pedalboard.txt', slug: 'setup/pedalboard-txt' },
						{ label: 'Performance', slug: 'setup/performance' },
					],
				},
				{
					label: 'Help',
					items: [
						{ label: 'Troubleshooting', slug: 'help/troubleshooting' },
						{ label: 'SSH and logs', slug: 'help/ssh' },
						{ label: 'FAQ', slug: 'help/faq' },
					],
				},
				{
					label: 'Developers',
					items: [
						{ label: 'Build from source', slug: 'dev/build' },
						{ label: 'How it works', slug: 'dev/architecture' },
						{ label: 'Contributing', slug: 'dev/contributing' },
					],
				},
			],
		}),
	],
});
