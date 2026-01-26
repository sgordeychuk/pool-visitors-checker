<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { pools, selectedPool } from '$lib/stores/pools';
	import { isAuthenticated } from '$lib/stores/auth';
	import { api, type VisitorRecord, type WeekdayAverageUpToNow } from '$lib/api';
	import VisitorCard from '$lib/components/ui/VisitorCard.svelte';
	import TrendChart from '$lib/components/charts/TrendChart.svelte';
	import { Card, Button, Badge, Select, PredictionCard } from '$clearlane';
	import { getCrowdLevel, getCrowdColor } from '$styles/chart-colors';

	let todayData: VisitorRecord[] = [];
	let weekdayAverage: WeekdayAverageUpToNow | null = null;
	let loading = true;
	let refreshInterval: ReturnType<typeof setInterval>;

	$: if ($isAuthenticated) {
		loadData();
	}

	async function loadData() {
		loading = true;
		await pools.loadPools();
		await pools.loadLatestVisitors();
		if ($selectedPool) {
			todayData = await api.getTodayVisitors($selectedPool.id);
			weekdayAverage = await api.getWeekdayAverageUpToNow($selectedPool.id);
		}
		loading = false;
	}

	async function refreshData() {
		await pools.loadLatestVisitors();
		if ($selectedPool) {
			todayData = await api.getTodayVisitors($selectedPool.id);
			weekdayAverage = await api.getWeekdayAverageUpToNow($selectedPool.id);
		}
	}

	onMount(() => {
		refreshInterval = setInterval(refreshData, 60000);
	});

	onDestroy(() => {
		if (refreshInterval) clearInterval(refreshInterval);
	});

	function formatTime(timestamp: string): string {
		return new Date(timestamp).toLocaleTimeString('de-CH', { hour: '2-digit', minute: '2-digit' });
	}

	function formatDate(timestamp: string): string {
		return new Date(timestamp).toLocaleDateString('de-CH', {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	$: todayCurrentAvg = todayData.length > 0
		? Math.round(todayData.reduce((sum, d) => sum + d.visitor_count, 0) / todayData.length)
		: 0;
	$: comparison = weekdayAverage && todayCurrentAvg > 0
		? todayCurrentAvg - weekdayAverage.average_visitors
		: 0;

	// Get current visitor status
	$: latestVisitor = $pools.latestVisitors.find(v => v.pool_id === $pools.selectedPoolId);
	$: currentCount = latestVisitor?.visitor_count ?? 0;
	$: normalizedCrowd = Math.min(currentCount / 150, 1);
	$: currentCrowdLevel = getCrowdLevel(normalizedCrowd);

	// Generate recommendation text
	$: recommendationText = currentCrowdLevel === 'low' ? 'Great time to swim!' :
		currentCrowdLevel === 'moderate' ? 'Good conditions' :
		currentCrowdLevel === 'high' ? 'Expect some crowds' : 'Very busy right now';

	// Generate trend text
	$: trendText = comparison > 5 ? `${Math.round(comparison)} more than usual` :
		comparison < -5 ? `${Math.round(Math.abs(comparison))} fewer than usual` :
		'About average';

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
	<title>Dashboard - ClearLane</title>
</svelte:head>

{#if !$isAuthenticated}
	<div class="flex flex-col items-center justify-center h-64 space-y-4">
		<h1 class="text-cl-h1 text-cl-text-primary">Welcome to ClearLane</h1>
		<p class="text-cl-body text-cl-text-secondary">Track pool visitors and find the best time to swim.</p>
		<a href="/login">
			<Button variant="primary" size="lg">Log In</Button>
		</a>
	</div>
{:else if loading}
	<div class="flex justify-center items-center h-64">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cl-primary"></div>
	</div>
{:else}
	<div class="space-y-6">
		<!-- Header with Pool Selector -->
		<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
			<div>
				<h1 class="text-cl-h1 text-cl-text-primary">Dashboard</h1>
				<p class="text-cl-small text-cl-text-muted">{formatDate(new Date().toISOString())}</p>
			</div>
			{#if $pools.pools.length > 1}
				<div class="w-full md:w-64">
					<Select
						options={poolOptions}
						value={selectedPoolValue}
						on:change={handlePoolChange}
					/>
				</div>
			{/if}
		</header>

		<!-- Hero Prediction Card -->
		{#if $selectedPool && latestVisitor}
			<PredictionCard
				title="Current Status"
				recommendation={recommendationText}
				crowdLevel={currentCrowdLevel}
				subtitle="{currentCount} visitors at {$selectedPool.name}"
				trendText={trendText}
			/>
		{/if}

		<!-- Latest Visitors Cards -->
		<section>
			<h2 class="text-cl-h2 text-cl-text-primary mb-4">Pool Overview</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each $pools.latestVisitors as visitor}
					<VisitorCard
						poolName={visitor.pool_name}
						visitorCount={visitor.visitor_count}
						timestamp={visitor.timestamp}
						weekday={visitor.weekday}
						isSelected={visitor.pool_id === $pools.selectedPoolId}
						on:click={() => pools.selectPool(visitor.pool_id)}
					/>
				{/each}
			</div>
		</section>

		<!-- Today's Trend Chart -->
		{#if $selectedPool && todayData.length > 0}
			<Card padding="lg">
				<h2 class="text-cl-h2 text-cl-text-primary mb-4">Today's Trend - {$selectedPool.name}</h2>
				<div class="h-64 md:h-80">
					<TrendChart
						labels={todayData.map((d) => formatTime(d.timestamp))}
						data={todayData.map((d) => d.visitor_count)}
						label="Visitors"
					/>
				</div>
			</Card>
		{:else if $selectedPool}
			<Card padding="lg">
				<h2 class="text-cl-h2 text-cl-text-primary mb-4">Today's Trend - {$selectedPool.name}</h2>
				<p class="text-cl-body text-cl-text-muted">No data available for today yet.</p>
			</Card>
		{/if}

		<!-- Quick Stats -->
		{#if $selectedPool}
			<section>
				<h2 class="text-cl-h2 text-cl-text-primary mb-4">Quick Stats</h2>
				<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
					<Card padding="md">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-1">Today's Min</p>
							<p class="text-2xl font-bold text-cl-crowd-low">
								{todayData.length > 0 ? Math.min(...todayData.map((d) => d.visitor_count)) : '-'}
							</p>
						</div>
					</Card>
					<Card padding="md">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-1">Today's Max</p>
							<p class="text-2xl font-bold text-cl-crowd-high">
								{todayData.length > 0 ? Math.max(...todayData.map((d) => d.visitor_count)) : '-'}
							</p>
						</div>
					</Card>
					<Card padding="md">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-1">Today's Avg</p>
							<p class="text-2xl font-bold text-cl-primary">
								{todayCurrentAvg > 0 ? todayCurrentAvg : '-'}
							</p>
						</div>
					</Card>
					<Card padding="md">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-1">{weekdayAverage?.weekday || 'Weekday'} Avg</p>
							<p class="text-2xl font-bold text-cl-text-primary">
								{weekdayAverage ? Math.round(weekdayAverage.average_visitors) : '-'}
							</p>
							<p class="text-[10px] text-cl-text-muted">up to {weekdayAverage?.current_time || 'now'}</p>
						</div>
					</Card>
					<Card padding="md">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-1">vs. Typical</p>
							<p class="text-2xl font-bold {comparison > 0 ? 'text-cl-crowd-high' : comparison < 0 ? 'text-cl-crowd-low' : 'text-cl-text-primary'}">
								{#if comparison !== 0}
									{comparison > 0 ? '+' : ''}{Math.round(comparison)}
								{:else}
									-
								{/if}
							</p>
							<p class="text-[10px] text-cl-text-muted">{comparison > 0 ? 'busier' : comparison < 0 ? 'quieter' : ''}</p>
						</div>
					</Card>
					<Card padding="md">
						<div class="text-center">
							<p class="text-cl-label text-cl-text-muted mb-1">Total Records</p>
							<p class="text-2xl font-bold text-cl-text-primary">{$selectedPool.total_records.toLocaleString()}</p>
						</div>
					</Card>
				</div>
			</section>
		{/if}
	</div>
{/if}
