<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let poolName: string;
	export let visitorCount: number;
	export let timestamp: string;
	export let weekday: string;
	export let isSelected: boolean = false;

	const dispatch = createEventDispatcher();

	function formatTime(ts: string): string {
		return new Date(ts).toLocaleTimeString('de-CH', { hour: '2-digit', minute: '2-digit' });
	}

	function getStatusColor(count: number): string {
		if (count < 50) return 'text-success-500';
		if (count < 100) return 'text-warning-500';
		return 'text-error-500';
	}

	function getStatusLabel(count: number): string {
		if (count < 50) return 'Low';
		if (count < 100) return 'Medium';
		return 'Busy';
	}
</script>

<button
	class="card p-4 w-full text-left transition-all hover:scale-[1.02] {isSelected
		? 'ring-2 ring-primary-500'
		: ''}"
	on:click={() => dispatch('click')}
>
	<div class="flex items-start justify-between">
		<div>
			<h3 class="font-semibold">{poolName}</h3>
			<p class="text-sm opacity-75">{weekday}</p>
		</div>
		<span class="badge {getStatusColor(visitorCount)}">{getStatusLabel(visitorCount)}</span>
	</div>

	<div class="mt-4 flex items-end justify-between">
		<div>
			<p class="text-4xl font-bold {getStatusColor(visitorCount)}">{visitorCount}</p>
			<p class="text-sm opacity-75">visitors</p>
		</div>
		<p class="text-sm opacity-75">{formatTime(timestamp)}</p>
	</div>
</button>
