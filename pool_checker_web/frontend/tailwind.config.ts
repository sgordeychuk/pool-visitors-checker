import { join } from 'path';
import type { Config } from 'tailwindcss';
import forms from '@tailwindcss/forms';
import { skeleton } from '@skeletonlabs/tw-plugin';

export default {
	darkMode: 'class',
	content: [
		'./src/**/*.{html,js,svelte,ts}',
		join(require.resolve('@skeletonlabs/skeleton'), '../**/*.{html,js,svelte,ts}')
	],
	// Safelist classes that are dynamically generated
	safelist: [
		'bg-white/15',
		'bg-white/10',
		'bg-white/20',
		'bg-cl-bg-muted',
		'bg-cl-primary/10',
		'text-cl-primary',
		'font-medium'
	],
	theme: {
		extend: {
			// ClearLane Design System Colors
			colors: {
				'cl-primary': {
					DEFAULT: 'var(--cl-primary)',
					hover: 'var(--cl-primary-hover)',
					light: 'var(--cl-primary-light)',
					dark: 'var(--cl-primary-dark)'
				},
				'cl-bg': {
					base: 'var(--cl-bg-base)',
					surface: 'var(--cl-bg-surface)',
					elevated: 'var(--cl-bg-elevated)',
					muted: 'var(--cl-bg-muted)'
				},
				'cl-text': {
					primary: 'var(--cl-text-primary)',
					secondary: 'var(--cl-text-secondary)',
					muted: 'var(--cl-text-muted)',
					'on-primary': 'var(--cl-text-on-primary)'
				},
				'cl-crowd': {
					low: 'var(--cl-crowd-low)',
					'low-bg': 'var(--cl-crowd-low-bg)',
					moderate: 'var(--cl-crowd-moderate)',
					'moderate-bg': 'var(--cl-crowd-moderate-bg)',
					high: 'var(--cl-crowd-high)',
					'high-bg': 'var(--cl-crowd-high-bg)',
					full: 'var(--cl-crowd-full)',
					'full-bg': 'var(--cl-crowd-full-bg)'
				},
				'cl-border': {
					DEFAULT: 'var(--cl-border-default)',
					strong: 'var(--cl-border-strong)',
					subtle: 'var(--cl-border-subtle)'
				}
			},
			// ClearLane Typography
			fontFamily: {
				clearlane: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
			},
			fontSize: {
				'cl-h1': ['24px', { lineHeight: '1.25', fontWeight: '700' }],
				'cl-h2': ['18px', { lineHeight: '1.25', fontWeight: '500' }],
				'cl-body': ['16px', { lineHeight: '1.5', fontWeight: '400' }],
				'cl-small': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
				'cl-label': ['12px', { lineHeight: '1.25', fontWeight: '500', letterSpacing: '1px' }]
			},
			// ClearLane Shadows
			boxShadow: {
				'cl-card': 'var(--cl-shadow-card)',
				'cl-card-hover': 'var(--cl-shadow-card-hover)',
				'cl-prediction': 'var(--cl-shadow-prediction)',
				'cl-dropdown': 'var(--cl-shadow-dropdown)'
			},
			// ClearLane Border Radius
			borderRadius: {
				'cl-sm': 'var(--cl-radius-sm)',
				'cl-md': 'var(--cl-radius-md)',
				'cl-lg': 'var(--cl-radius-lg)',
				'cl-xl': 'var(--cl-radius-xl)',
				'cl-full': 'var(--cl-radius-full)'
			},
			// ClearLane Spacing
			spacing: {
				'cl-xs': 'var(--cl-space-xs)',
				'cl-sm': 'var(--cl-space-sm)',
				'cl-md': 'var(--cl-space-md)',
				'cl-lg': 'var(--cl-space-lg)',
				'cl-xl': 'var(--cl-space-xl)',
				'cl-2xl': 'var(--cl-space-2xl)'
			},
			// ClearLane Transitions
			transitionDuration: {
				'cl-fast': '150ms',
				'cl-normal': '250ms',
				'cl-slow': '350ms'
			}
		}
	},
	plugins: [
		forms,
		skeleton({
			themes: {
				preset: [
					{
						name: 'skeleton',
						enhancements: true
					},
					{
						name: 'modern',
						enhancements: true
					},
					{
						name: 'crimson',
						enhancements: true
					}
				]
			}
		})
	]
} satisfies Config;
