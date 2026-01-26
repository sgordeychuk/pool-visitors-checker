<script lang="ts">
	import type { HTMLAttributes } from 'svelte/elements';

	type BadgeVariant = 'low' | 'moderate' | 'high' | 'full' | 'primary' | 'neutral';
	type BadgeSize = 'sm' | 'md' | 'lg';

	interface $$Props extends HTMLAttributes<HTMLSpanElement> {
		variant?: BadgeVariant;
		size?: BadgeSize;
		pill?: boolean;
		class?: string;
	}

	export let variant: BadgeVariant = 'neutral';
	export let size: BadgeSize = 'md';
	export let pill = false;
	let className = '';
	export { className as class };

	const baseClasses = 'inline-flex items-center font-medium';

	const variantClasses: Record<BadgeVariant, string> = {
		low: 'bg-cl-crowd-low-bg text-cl-crowd-low',
		moderate: 'bg-cl-crowd-moderate-bg text-cl-crowd-moderate',
		high: 'bg-cl-crowd-high-bg text-cl-crowd-high',
		full: 'bg-cl-crowd-full-bg text-cl-crowd-full',
		primary: 'bg-cl-primary/10 text-cl-primary',
		neutral: 'bg-cl-bg-muted text-cl-text-secondary'
	};

	const sizeClasses: Record<BadgeSize, string> = {
		sm: 'px-2 py-0.5 text-[10px]',
		md: 'px-2.5 py-1 text-cl-label',
		lg: 'px-3 py-1.5 text-cl-small'
	};

	$: radiusClass = pill ? 'rounded-cl-full' : 'rounded-cl-sm';
	$: classes = [
		baseClasses,
		variantClasses[variant],
		sizeClasses[size],
		radiusClass,
		className
	].filter(Boolean).join(' ');
</script>

<span class={classes} {...$$restProps}>
	<slot />
</span>
