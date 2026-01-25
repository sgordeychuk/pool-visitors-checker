<script lang="ts">
	import type { HeatmapData } from '$lib/api';

	export let data: HeatmapData;

	const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
	const hours = Array.from({ length: 17 }, (_, i) => i + 6); // 6 AM to 10 PM (pool opens at 6 AM)

	function getValue(weekday: string, hour: number): number | null {
		const cell = data.data.find((c) => c.weekday === weekday && c.hour === hour);
		return cell ? cell.value : null;
	}

	function getColor(value: number | null): string {
		if (value === null) return 'bg-surface-700';

		const normalized = (value - data.min_value) / (data.max_value - data.min_value);

		// Color scale from green (low) to yellow (medium) to red (high)
		if (normalized < 0.33) {
			return 'bg-success-500';
		} else if (normalized < 0.66) {
			return 'bg-warning-500';
		} else {
			return 'bg-error-500';
		}
	}

	function getOpacity(value: number | null): string {
		if (value === null) return 'opacity-20';
		const normalized = (value - data.min_value) / (data.max_value - data.min_value);
		const opacity = 0.3 + normalized * 0.7;
		return `opacity-${Math.round(opacity * 100)}`;
	}

	function formatHour(hour: number): string {
		return `${hour.toString().padStart(2, '0')}:00`;
	}
</script>

<div class="overflow-x-auto">
	<table class="w-full text-xs md:text-sm">
		<thead>
			<tr>
				<th class="p-1 md:p-2 text-left"></th>
				{#each hours as hour}
					<th class="p-1 md:p-2 text-center font-normal opacity-75">{formatHour(hour)}</th>
				{/each}
			</tr>
		</thead>
		<tbody>
			{#each weekdays as weekday}
				<tr>
					<td class="p-1 md:p-2 font-medium whitespace-nowrap">{weekday.slice(0, 3)}</td>
					{#each hours as hour}
						{@const value = getValue(weekday, hour)}
						<td class="p-0.5 md:p-1">
							<div
								class="w-6 h-6 md:w-8 md:h-8 rounded flex items-center justify-center text-white text-xs {getColor(value)}"
								style="opacity: {value !== null ? 0.3 + ((value - data.min_value) / (data.max_value - data.min_value)) * 0.7 : 0.2}"
								title="{weekday} {formatHour(hour)}: {value !== null ? Math.round(value) : 'No data'}"
							>
								{#if value !== null}
									<span class="hidden md:inline">{Math.round(value)}</span>
								{/if}
							</div>
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>

	<!-- Legend -->
	<div class="flex items-center justify-center gap-4 mt-4 text-xs">
		<div class="flex items-center gap-1">
			<div class="w-4 h-4 rounded bg-success-500 opacity-50"></div>
			<span>Low ({Math.round(data.min_value)})</span>
		</div>
		<div class="flex items-center gap-1">
			<div class="w-4 h-4 rounded bg-warning-500 opacity-70"></div>
			<span>Medium</span>
		</div>
		<div class="flex items-center gap-1">
			<div class="w-4 h-4 rounded bg-error-500"></div>
			<span>High ({Math.round(data.max_value)})</span>
		</div>
	</div>
</div>
