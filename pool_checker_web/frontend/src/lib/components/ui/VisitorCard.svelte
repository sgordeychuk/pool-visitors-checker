<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Badge, Card } from '$clearlane';
	import { getCrowdLevel, getCrowdColor } from '$styles/chart-colors';

	export let poolName: string;
	export let visitorCount: number;
	export let timestamp: string;
	export let weekday: string;
	export let isSelected: boolean = false;
	export let maxVisitors: number = 150;

	const dispatch = createEventDispatcher();

	function formatTime(ts: string): string {
		return new Date(ts).toLocaleTimeString('de-CH', { hour: '2-digit', minute: '2-digit' });
	}

	$: normalized = Math.min(visitorCount / maxVisitors, 1);
	$: crowdLevel = getCrowdLevel(normalized);
	$: crowdColor = getCrowdColor(normalized);

	const statusLabels = {
		low: 'Low',
		moderate: 'Moderate',
		high: 'Busy',
		full: 'Very Busy'
	};
</script>

<button
	class="w-full text-left transition-all hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-cl-primary focus:ring-offset-2 rounded-lg"
	on:click={() => dispatch('click')}
>
	<Card
		variant={isSelected ? 'elevated' : 'default'}
		padding="lg"
		class={isSelected ? 'ring-2 ring-cl-primary h-full' : 'h-full'}
	>
		<div class="flex items-start justify-between gap-2 mb-4">
			<div class="min-w-0 flex-1">
				<h3 class="font-semibold text-cl-text-primary text-base truncate">{poolName}</h3>
				<p class="text-sm text-cl-text-muted">{weekday}</p>
			</div>
			<Badge variant={crowdLevel} size="sm" pill class="flex-shrink-0">
				{statusLabels[crowdLevel]}
			</Badge>
		</div>

		<div class="flex items-end justify-between gap-2">
			<div>
				<p class="text-4xl font-bold leading-none" style="color: {crowdColor}">{visitorCount}</p>
				<p class="text-sm text-cl-text-muted mt-1">visitors</p>
			</div>
			<p class="text-sm text-cl-text-muted">{formatTime(timestamp)}</p>
		</div>
	</Card>
</button>
