<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Pool } from '$lib/api';

	export let pool: Pool | null = null;

	const dispatch = createEventDispatcher();

	let name = pool?.name ?? '';
	let url = pool?.url ?? '';
	let element_id = pool?.element_id ?? '';
	let timezone = pool?.timezone ?? 'CET';
	let scrape_start_time = pool?.scrape_start_time ?? '05:50';
	let scrape_end_time = pool?.scrape_end_time ?? '22:10';
	let scrape_interval_minutes = pool?.scrape_interval_minutes ?? 10;
	let is_active = pool?.is_active ?? true;

	function handleSubmit() {
		dispatch('save', {
			name,
			url,
			element_id,
			timezone,
			scrape_start_time,
			scrape_end_time,
			scrape_interval_minutes,
			is_active
		});
	}

	function handleCancel() {
		dispatch('cancel');
	}
</script>

<form on:submit|preventDefault={handleSubmit} class="space-y-4">
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<label class="label">
			<span>Pool Name *</span>
			<input class="input" type="text" bind:value={name} required placeholder="City Hallenbad" />
		</label>

		<label class="label">
			<span>Element ID *</span>
			<input class="input" type="text" bind:value={element_id} required placeholder="SSD-4_visitornumber" />
			<span class="text-xs opacity-75">DOM element ID containing the visitor count</span>
		</label>
	</div>

	<label class="label">
		<span>URL *</span>
		<input class="input" type="url" bind:value={url} required placeholder="https://example.com/pool" />
	</label>

	<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
		<label class="label">
			<span>Timezone</span>
			<select class="select" bind:value={timezone}>
				<option value="CET">CET (Central European)</option>
				<option value="UTC">UTC</option>
				<option value="US/Eastern">US/Eastern</option>
				<option value="US/Pacific">US/Pacific</option>
			</select>
		</label>

		<label class="label">
			<span>Start Time</span>
			<input class="input" type="time" bind:value={scrape_start_time} />
		</label>

		<label class="label">
			<span>End Time</span>
			<input class="input" type="time" bind:value={scrape_end_time} />
		</label>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<label class="label">
			<span>Scrape Interval (minutes)</span>
			<input class="input" type="number" bind:value={scrape_interval_minutes} min="1" max="60" />
		</label>

		<label class="flex items-center space-x-2 mt-6">
			<input class="checkbox" type="checkbox" bind:checked={is_active} />
			<span>Active (scraping enabled)</span>
		</label>
	</div>

	<div class="flex gap-2 pt-4">
		<button type="submit" class="btn variant-filled-primary">
			{pool ? 'Update Pool' : 'Create Pool'}
		</button>
		<button type="button" class="btn variant-ghost-surface" on:click={handleCancel}>
			Cancel
		</button>
	</div>
</form>
