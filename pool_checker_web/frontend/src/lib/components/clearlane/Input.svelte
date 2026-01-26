<script lang="ts">
	import type { HTMLInputAttributes } from 'svelte/elements';

	type Props = {
		label?: string;
		hint?: string;
		error?: string;
		disabled?: boolean;
		required?: boolean;
		value?: string;
	} & Omit<HTMLInputAttributes, 'disabled' | 'required' | 'value'>;

	export let label: string | undefined = undefined;
	export let hint: string | undefined = undefined;
	export let error: string | undefined = undefined;
	export let disabled = false;
	export let required = false;
	export let value = '';

	// Generate unique ID for accessibility
	const inputId = `cl-input-${Math.random().toString(36).slice(2, 9)}`;

	const inputBaseClasses =
		'block w-full rounded-cl-md border bg-cl-bg-surface text-cl-text-primary placeholder-cl-text-muted transition-all duration-cl-fast focus:outline-none focus:ring-2 focus:ring-offset-0';

	const inputStateClasses = error
		? 'border-cl-crowd-full focus:border-cl-crowd-full focus:ring-cl-crowd-full/30'
		: 'border-cl-border focus:border-cl-primary focus:ring-cl-primary/30';

	const inputDisabledClasses = disabled ? 'opacity-50 cursor-not-allowed bg-cl-bg-muted' : '';

	$: inputClasses = `${inputBaseClasses} ${inputStateClasses} ${inputDisabledClasses} px-3 py-2 text-cl-body`;

	type $$Props = Props;
</script>

<div class="w-full">
	{#if label}
		<label for={inputId} class="block mb-1.5">
			<span class="text-cl-small font-medium text-cl-text-primary">
				{label}
				{#if required}
					<span class="text-cl-crowd-full">*</span>
				{/if}
			</span>
		</label>
	{/if}

	<input
		id={inputId}
		class={inputClasses}
		{disabled}
		{required}
		bind:value
		on:input
		on:change
		on:focus
		on:blur
		{...$$restProps}
	/>

	{#if hint && !error}
		<p class="mt-1.5 text-cl-small text-cl-text-muted">{hint}</p>
	{/if}

	{#if error}
		<p class="mt-1.5 text-cl-small text-cl-crowd-full">{error}</p>
	{/if}
</div>
