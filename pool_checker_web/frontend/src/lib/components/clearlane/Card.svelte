<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	type CardVariant = 'default' | 'elevated' | 'prediction';
	type CardPadding = 'none' | 'sm' | 'md' | 'lg';

	interface $$Props extends HTMLAttributes<HTMLDivElement> {
		variant?: CardVariant;
		padding?: CardPadding;
		hoverable?: boolean;
		class?: string;
	}

	export let variant: CardVariant = 'default';
	export let padding: CardPadding = 'md';
	export let hoverable = false;
	let className = '';
	export { className as class };

	const baseClasses = 'rounded-cl-md transition-all duration-cl-normal';

	const variantClasses: Record<CardVariant, string> = {
		default: 'bg-cl-bg-surface border border-cl-border shadow-cl-card',
		elevated: 'bg-cl-bg-elevated shadow-cl-card-hover',
		prediction: 'bg-cl-primary text-cl-text-on-primary shadow-cl-prediction'
	};

	const paddingClasses: Record<CardPadding, string> = {
		none: '',
		sm: 'p-3',
		md: 'p-4',
		lg: 'p-6'
	};

	$: hoverClasses = hoverable
		? 'cursor-pointer hover:shadow-cl-card-hover hover:-translate-y-0.5'
		: '';

	$: classes = [
		baseClasses,
		variantClasses[variant],
		paddingClasses[padding],
		hoverClasses,
		className
	].filter(Boolean).join(' ');
</script>

<div class={classes} {...$$restProps}>
	<slot />
</div>
