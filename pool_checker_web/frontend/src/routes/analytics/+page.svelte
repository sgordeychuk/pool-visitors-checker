<script lang="ts">
	import { onMount } from 'svelte';
	import { pools, selectedPool } from '$lib/stores/pools';
	import { isAuthenticated } from '$lib/stores/auth';
	import { api, type HeatmapData, type TrendData, type DailySummary, type WeekdayAverage } from '$lib/api';
	import TrendChart from '$lib/components/charts/TrendChart.svelte';
	import HeatmapChart from '$lib/components/charts/HeatmapChart.svelte';
	import WeekdayComparisonChart from '$lib/components/charts/WeekdayComparisonChart.svelte';
	import { Card, Button, Badge, Select, PredictionCard } from '$clearlane';
	import { getCrowdLevel } from '$styles/chart-colors';

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

	// Find best time to swim
	$: bestDay = weekdayAverages.length > 0
		? weekdayAverages.reduce((best, current) =>
			current.average_visitors < best.average_visitors ? current : best
		)
		: null;

	$: bestTimeRecommendation = bestDay && peakHours && peakHours.quietest_hour !== null
		? `${bestDay.weekday}s at ${formatHour(peakHours.quietest_hour)}`
		: 'Analyzing patterns...';

	$: poolOptions = $pools.pools.map(p => ({ value: String(p.id), label: p.name }));

	let selectedPoolValue = '';
	$: selectedPoolValue = String($pools.selectedPoolId);

	function handlePoolChange(e: Event) {
		const target = e.target as HTMLSelectElement;
		if (target) {
			pools.selectPool(Number(target.value));
		}
	}
</script>

<svelte:head>
	<title>Analytics - ClearLane</title>
</svelte:head>

{#if loading}
	<div class="flex justify-center items-center h-64">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cl-primary"></div>
	</div>
{:else}
	<div class="space-y-6">
		<!-- Header -->
		<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
			<h1 class="text-cl-h1 text-cl-text-primary">Analytics</h1>
			{#if $pools.pools.length > 0}
				<div class="w-full md:w-64">
					<Select
						options={poolOptions}
						value={selectedPoolValue}
						on:change={handlePoolChange}
					/>
				</div>
			{/if}
		</header>

		{#if $selectedPool}
			<!-- Best Time to Swim Prediction -->
			<PredictionCard
				title="Best Time to Swim"
				recommendation={bestTimeRecommendation}
				crowdLevel="low"
				subtitle="Based on historical patterns"
				trendText={peakHours && peakHours.peak_hour !== null ? `Peak: ${formatHour(peakHours.peak_hour)}` : undefined}
			/>

			<!-- Peak Hours Summary -->
			{#if peakHours}
				<section class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<Card padding="lg">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-2">Peak Hour</p>
							<p class="text-4xl font-bold text-cl-crowd-full">
								{peakHours.peak_hour !== null ? formatHour(peakHours.peak_hour) : '-'}
							</p>
							<p class="text-cl-small text-cl-text-muted mt-2">Busiest time on average</p>
						</div>
					</Card>
					<Card padding="lg">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-2">Quietest Hour</p>
							<p class="text-4xl font-bold text-cl-crowd-low">
								{peakHours.quietest_hour !== null ? formatHour(peakHours.quietest_hour) : '-'}
							</p>
							<p class="text-cl-small text-cl-text-muted mt-2">Best time to visit</p>
						</div>
					</Card>
				</section>
			{/if}

			<!-- Heatmap -->
			{#if heatmapData && heatmapData.data.length > 0}
				<Card padding="lg">
					<h2 class="text-cl-h2 text-cl-text-primary mb-2">Weekly Crowd Density</h2>
					<p class="text-cl-small text-cl-text-muted mb-4">Average visitors by day and hour (6 AM - 10 PM)</p>
					<HeatmapChart data={heatmapData} />
				</Card>
			{/if}

			<!-- Weekday Comparison Chart -->
			{#if weekdayAverages.length > 0}
				<Card padding="lg">
					<h2 class="text-cl-h2 text-cl-text-primary mb-2">Best Time to Visit</h2>
					<p class="text-cl-small text-cl-text-muted mb-4">Compare hourly averages by weekday - toggle days to find the best time</p>
					<WeekdayComparisonChart data={weekdayAverages} />
				</Card>
			{/if}

			<!-- Trend Chart -->
			{#if trendData && trendData.data.length > 0}
				<Card padding="lg">
					<div class="flex flex-col md:flex-row md:items-center justify-between mb-4 gap-4">
						<h2 class="text-cl-h2 text-cl-text-primary">Visitor Trends</h2>
						<div class="flex gap-2">
							<Button
								variant={trendPeriod === 'weekly' ? 'primary' : 'secondary'}
								size="sm"
								on:click={() => changeTrendPeriod('weekly')}
							>
								Weekly
							</Button>
							<Button
								variant={trendPeriod === 'monthly' ? 'primary' : 'secondary'}
								size="sm"
								on:click={() => changeTrendPeriod('monthly')}
							>
								Monthly
							</Button>
						</div>
					</div>
					<div class="h-64 md:h-80">
						<TrendChart
							labels={trendData.data.map((d) => d.period)}
							data={trendData.data.map((d) => d.average_visitors)}
							label="Average Visitors"
						/>
					</div>
				</Card>
			{/if}

			<!-- Hourly Distribution -->
			{#if peakHours && peakHours.by_hour.length > 0}
				{@const filteredHours = peakHours.by_hour.filter((h) => h.hour >= 6 && h.hour <= 22)}
				<Card padding="lg">
					<h2 class="text-cl-h2 text-cl-text-primary mb-2">Average Daily Flow</h2>
					<p class="text-cl-small text-cl-text-muted mb-4">Overall average visitors by hour (all days combined)</p>
					<div class="h-64 md:h-80">
						<TrendChart
							labels={filteredHours.map((h) => formatHour(h.hour))}
							data={filteredHours.map((h) => h.average)}
							label="Average Visitors"
						/>
					</div>
				</Card>
			{/if}

			<!-- Daily Summary Table -->
			{#if dailySummary.length > 0}
				<Card padding="lg">
					<h2 class="text-cl-h2 text-cl-text-primary mb-4">Daily Summary (Last 14 Days)</h2>
					<div class="overflow-x-auto">
						<table class="w-full text-left">
							<thead>
								<tr class="border-b border-cl-border">
									<th class="pb-3 text-cl-label text-cl-text-muted font-medium">Date</th>
									<th class="pb-3 text-cl-label text-cl-text-muted font-medium text-right">Min</th>
									<th class="pb-3 text-cl-label text-cl-text-muted font-medium text-right">Max</th>
									<th class="pb-3 text-cl-label text-cl-text-muted font-medium text-right">Average</th>
									<th class="pb-3 text-cl-label text-cl-text-muted font-medium text-right">Readings</th>
								</tr>
							</thead>
							<tbody>
								{#each dailySummary.slice(0, 14) as day, i}
									{@const avgNormalized = day.avg_visitors / 150}
									{@const crowdLevel = getCrowdLevel(avgNormalized)}
									<tr class="border-b border-cl-border-subtle hover:bg-cl-bg-muted transition-colors">
										<td class="py-3 text-cl-body text-cl-text-primary">
											{new Date(day.date).toLocaleDateString('de-CH', { weekday: 'short', month: 'short', day: 'numeric' })}
										</td>
										<td class="py-3 text-cl-body text-cl-crowd-low text-right">{day.min_visitors}</td>
										<td class="py-3 text-cl-body text-cl-crowd-high text-right">{day.max_visitors}</td>
										<td class="py-3 text-right">
											<Badge variant={crowdLevel} size="sm">
												{day.avg_visitors.toFixed(0)}
											</Badge>
										</td>
										<td class="py-3 text-cl-body text-cl-text-muted text-right">{day.total_readings}</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</Card>
			{/if}
		{:else}
			<Card padding="lg">
				<div class="text-center py-8">
					<p class="text-cl-body text-cl-text-muted">No pools configured yet.</p>
				</div>
			</Card>
		{/if}
	</div>
{/if}
