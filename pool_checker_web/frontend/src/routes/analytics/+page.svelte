<script lang="ts">
	import { onMount } from 'svelte';
	import { pools, selectedPool } from '$lib/stores/pools';
	import { isAuthenticated } from '$lib/stores/auth';
	import { api, type HeatmapData, type TrendData, type DailySummary, type WeekdayAverage } from '$lib/api';
	import TrendChart from '$lib/components/charts/TrendChart.svelte';
	import HeatmapChart from '$lib/components/charts/HeatmapChart.svelte';
	import WeekdayComparisonChart from '$lib/components/charts/WeekdayComparisonChart.svelte';

	let heatmapData: HeatmapData | null = null;
	let trendData: TrendData | null = null;
	let dailySummary: DailySummary[] = [];
	let weekdayAverages: WeekdayAverage[] = [];
	let peakHours: { peak_hour: number | null; quietest_hour: number | null; by_hour: any[] } | null = null;
	let loading = true;
	let trendPeriod: 'weekly' | 'monthly' = 'weekly';

	$: if ($isAuthenticated && $selectedPool) {
		loadAnalytics();
	}

	async function loadAnalytics() {
		if (!$selectedPool) return;
		loading = true;
		try {
			[heatmapData, trendData, dailySummary, peakHours, weekdayAverages] = await Promise.all([
				api.getHeatmapData($selectedPool.id),
				api.getTrends($selectedPool.id, trendPeriod),
				api.getDailySummary($selectedPool.id),
				api.getPeakHours($selectedPool.id),
				api.getWeekdayAverages($selectedPool.id)
			]);
		} catch (error) {
			console.error('Failed to load analytics:', error);
		}
		loading = false;
	}

	async function changeTrendPeriod(period: 'weekly' | 'monthly') {
		trendPeriod = period;
		if ($selectedPool) {
			trendData = await api.getTrends($selectedPool.id, period);
		}
	}

	onMount(async () => {
		await pools.loadPools();
	});

	function formatHour(hour: number): string {
		return `${hour.toString().padStart(2, '0')}:00`;
	}
</script>

<svelte:head>
	<title>Analytics - Pool Visitor Tracker</title>
</svelte:head>

{#if loading}
	<div class="flex justify-center items-center h-64">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
	</div>
{:else}
	<div class="space-y-8">
		<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
			<h1 class="h1">Analytics</h1>
			{#if $pools.pools.length > 0}
				<select
					class="select w-full md:w-64"
					value={$pools.selectedPoolId}
					on:change={(e) => pools.selectPool(Number(e.currentTarget.value))}
				>
					{#each $pools.pools as pool}
						<option value={pool.id}>{pool.name}</option>
					{/each}
				</select>
			{/if}
		</header>

		{#if $selectedPool}
			<!-- Peak Hours Summary -->
			{#if peakHours}
				<section class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div class="card p-6 text-center">
						<p class="text-sm opacity-75 mb-2">Peak Hour</p>
						<p class="text-4xl font-bold text-error-500">
							{peakHours.peak_hour !== null ? formatHour(peakHours.peak_hour) : '-'}
						</p>
						<p class="text-sm opacity-75 mt-2">Busiest time on average</p>
					</div>
					<div class="card p-6 text-center">
						<p class="text-sm opacity-75 mb-2">Quietest Hour</p>
						<p class="text-4xl font-bold text-success-500">
							{peakHours.quietest_hour !== null ? formatHour(peakHours.quietest_hour) : '-'}
						</p>
						<p class="text-sm opacity-75 mt-2">Best time to visit</p>
					</div>
				</section>
			{/if}

			<!-- Heatmap -->
			{#if heatmapData && heatmapData.data.length > 0}
				<section class="card p-4 md:p-6">
					<h2 class="h3 mb-4">Weekly Heatmap</h2>
					<p class="text-sm opacity-75 mb-4">Average visitors by day and hour (6 AM - 10 PM)</p>
					<HeatmapChart data={heatmapData} />
				</section>
			{/if}

			<!-- Weekday Comparison Chart -->
			{#if weekdayAverages.length > 0}
				<section class="card p-4 md:p-6">
					<h2 class="h3 mb-2">Best Time to Visit</h2>
					<p class="text-sm opacity-75 mb-4">Compare hourly averages by weekday - toggle days to find the best time</p>
					<WeekdayComparisonChart data={weekdayAverages} />
				</section>
			{/if}

			<!-- Trend Chart -->
			{#if trendData && trendData.data.length > 0}
				<section class="card p-4 md:p-6">
					<div class="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-4">
						<h2 class="h3">Visitor Trends</h2>
						<div class="btn-group variant-ghost-surface">
							<button
								class:variant-filled-primary={trendPeriod === 'weekly'}
								on:click={() => changeTrendPeriod('weekly')}
							>
								Weekly
							</button>
							<button
								class:variant-filled-primary={trendPeriod === 'monthly'}
								on:click={() => changeTrendPeriod('monthly')}
							>
								Monthly
							</button>
						</div>
					</div>
					<div class="h-64 md:h-80">
						<TrendChart
							labels={trendData.data.map((d) => d.period)}
							data={trendData.data.map((d) => d.average_visitors)}
							label="Average Visitors"
						/>
					</div>
				</section>
			{/if}

			<!-- Hourly Distribution -->
			{#if peakHours && peakHours.by_hour.length > 0}
				{@const filteredHours = peakHours.by_hour.filter((h) => h.hour >= 6 && h.hour <= 22)}
				<section class="card p-4 md:p-6">
					<h2 class="h3 mb-4">Hourly Distribution</h2>
					<p class="text-sm opacity-75 mb-4">Overall average visitors by hour (all days combined)</p>
					<div class="h-64 md:h-80">
						<TrendChart
							labels={filteredHours.map((h) => formatHour(h.hour))}
							data={filteredHours.map((h) => h.average)}
							label="Average Visitors"
						/>
					</div>
				</section>
			{/if}

			<!-- Daily Summary Table -->
			{#if dailySummary.length > 0}
				<section class="card p-4 md:p-6">
					<h2 class="h3 mb-4">Daily Summary (Last 14 Days)</h2>
					<div class="table-container">
						<table class="table table-hover">
							<thead>
								<tr>
									<th>Date</th>
									<th class="text-right">Min</th>
									<th class="text-right">Max</th>
									<th class="text-right">Average</th>
									<th class="text-right">Readings</th>
								</tr>
							</thead>
							<tbody>
								{#each dailySummary.slice(0, 14) as day}
									<tr>
										<td>{new Date(day.date).toLocaleDateString('de-CH', { weekday: 'short', month: 'short', day: 'numeric' })}</td>
										<td class="text-right">{day.min_visitors}</td>
										<td class="text-right">{day.max_visitors}</td>
										<td class="text-right">{day.avg_visitors.toFixed(1)}</td>
										<td class="text-right">{day.total_readings}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</section>
			{/if}
		{:else}
			<div class="card p-8 text-center">
				<p class="text-lg opacity-75">No pools configured yet.</p>
			</div>
		{/if}
	</div>
{/if}
