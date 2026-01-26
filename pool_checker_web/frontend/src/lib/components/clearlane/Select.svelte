<script lang="ts">
	import type { HTMLSelectAttributes } from 'svelte/elements';

	interface SelectOption {
		value: string;
		label: string;
		disabled?: boolean;
	}

	type Props = {
		options: SelectOption[];
		label?: string;
		hint?: string;
		error?: string;
		placeholder?: string;
		disabled?: boolean;
		required?: boolean;
		value?: string;
	} & Omit<HTMLSelectAttributes, 'disabled' | 'required' | 'value'>;

	export let options: SelectOption[] = [];
	export let label: string | undefined = undefined;
	export let hint: string | undefined = undefined;
	export let error: string | undefined = undefined;
	export let placeholder: string | undefined = undefined;
	export let disabled = false;
	export let required = false;
	export let value = '';

	// Generate unique ID for accessibility
	const selectId = `cl-select-${Math.random().toString(36).slice(2, 9)}`;

	const selectBaseClasses =
		'block w-full rounded-cl-md border bg-cl-bg-surface text-cl-text-primary transition-all duration-cl-fast focus:outline-none focus:ring-2 focus:ring-offset-0 appearance-none cursor-pointer';

	const selectStateClasses = error
		? 'border-cl-crowd-full focus:border-cl-crowd-full focus:ring-cl-crowd-full/30'
		: 'border-cl-border focus:border-cl-primary focus:ring-cl-primary/30';

	const selectDisabledClasses = disabled ? 'opacity-50 cursor-not-allowed bg-cl-bg-muted' : '';

	$: selectClasses = `${selectBaseClasses} ${selectStateClasses} ${selectDisabledClasses} px-3 py-2 pr-10 text-cl-body`;

	type $$Props = Props;
</script>

<div class="w-full">
	{#if label}
		<label for={selectId} class="block mb-1.5">
			<span class="text-cl-small font-medium text-cl-text-primary">
				{label}
				{#if required}
					<span class="text-cl-crowd-full">*</span>
				{/if}
			</span>
		</label>
	{/if}

	<div class="relative">
		<select
			id={selectId}
			class={selectClasses}
			{disabled}
			{required}
			bind:value
			on:change
			on:focus
			on:blur
			{...$$restProps}
		>
			{#if placeholder}
				<option value="" disabled selected={!value}>{placeholder}</option>
			{/if}
			{#each options as option}
				<option value={option.value} disabled={option.disabled}>
					{option.label}
				</option>
			{/each}
		</select>

		<!-- Dropdown arrow -->
		<div
			class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-cl-text-muted"
		>
			<svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</div>
	</div>

	{#if hint && !error}
		<p class="mt-1.5 text-cl-small text-cl-text-muted">{hint}</p>
	{/if}

	{#if error}
		<p class="mt-1.5 text-cl-small text-cl-crowd-full">{error}</p>
	{/if}
</div>
