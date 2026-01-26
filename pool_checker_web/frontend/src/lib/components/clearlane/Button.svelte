<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';

	type ButtonVariant = 'primary' | 'secondary' | 'ghost';
	type ButtonSize = 'sm' | 'md' | 'lg';

	type Props = {
		variant?: ButtonVariant;
		size?: ButtonSize;
		loading?: boolean;
		disabled?: boolean;
	} & Omit<HTMLButtonAttributes, 'disabled'>;

	export let variant: ButtonVariant = 'primary';
	export let size: ButtonSize = 'md';
	export let loading = false;
	export let disabled = false;

	const baseClasses =
		'inline-flex items-center justify-center font-medium rounded-cl-md transition-all duration-cl-normal focus:outline-none focus:ring-2 focus:ring-cl-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

	const variantClasses: Record<ButtonVariant, string> = {
		primary:
			'bg-cl-primary text-cl-text-on-primary hover:bg-cl-primary-hover active:bg-cl-primary-dark shadow-cl-card hover:shadow-cl-card-hover',
		secondary:
			'bg-cl-bg-surface text-cl-text-primary border border-cl-border hover:bg-cl-bg-muted hover:border-cl-border-strong',
		ghost: 'bg-transparent text-cl-text-secondary hover:bg-cl-bg-muted hover:text-cl-text-primary'
	};

	const sizeClasses: Record<ButtonSize, string> = {
		sm: 'px-3 py-1.5 text-cl-small gap-1.5',
		md: 'px-4 py-2 text-cl-body gap-2',
		lg: 'px-6 py-3 text-cl-body gap-2.5'
	};

	$: classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`;

	type $$Props = Props;
</script>

<button class={classes} disabled={disabled || loading} on:click on:focus on:blur {...$$restProps}>
	{#if loading}
		<svg
			class="animate-spin -ml-1 h-4 w-4"
			xmlns="http://www.w3.org/2000/svg"
			fill="none"
			viewBox="0 0 24 24"
		>
			<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			/>
		</svg>
	{/if}
	<slot />
</button>
