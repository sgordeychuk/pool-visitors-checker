<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { pools, selectedPool } from '$lib/stores/pools';
	import { isAuthenticated } from '$lib/stores/auth';
	import { api, type VisitorRecord, type WeekdayAverageUpToNow } from '$lib/api';
	import VisitorCard from '$lib/components/ui/VisitorCard.svelte';
	import TrendChart from '$lib/components/charts/TrendChart.svelte';

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
		// Refresh data every 60 seconds
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

	// Calculate comparison between today's current average and historical weekday average
	$: todayCurrentAvg = todayData.length > 0
		? Math.round(todayData.reduce((sum, d) => sum + d.visitor_count, 0) / todayData.length)
		: 0;
	$: comparison = weekdayAverage && todayCurrentAvg > 0
		? todayCurrentAvg - weekdayAverage.average_visitors
		: 0;
</script>

<svelte:head>
	<title>Dashboard - Pool Visitor Tracker</title>
</svelte:head>

{#if !$isAuthenticated}
	<div class="flex flex-col items-center justify-center h-64 space-y-4">
		<h1 class="h1">Welcome to Pool Visitor Tracker</h1>
		<p class="text-lg opacity-75">Please log in to view pool visitor data.</p>
		<a href="/login" class="btn variant-filled-primary">Log In</a>
	</div>
{:else if loading}
	<div class="flex justify-center items-center h-64">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
	</div>
{:else}
	<div class="space-y-8">
		<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
			<div>
				<h1 class="h1">Dashboard</h1>
				<p class="opacity-75">{formatDate(new Date().toISOString())}</p>
			</div>
			{#if $pools.pools.length > 1}
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

		<!-- Latest Visitors Cards -->
		<section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
		</section>

		<!-- Today's Trend Chart -->
		{#if $selectedPool && todayData.length > 0}
			<section class="card p-4 md:p-6">
				<h2 class="h3 mb-4">Today's Trend - {$selectedPool.name}</h2>
				<div class="h-64 md:h-80">
					<TrendChart
						labels={todayData.map((d) => formatTime(d.timestamp))}
						data={todayData.map((d) => d.visitor_count)}
						label="Visitors"
					/>
				</div>
			</section>
		{:else if $selectedPool}
			<section class="card p-6">
				<h2 class="h3 mb-4">Today's Trend - {$selectedPool.name}</h2>
				<p class="opacity-75">No data available for today yet.</p>
			</section>
		{/if}

		<!-- Quick Stats -->
		{#if $selectedPool}
			<section class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
				<div class="card p-4 text-center">
					<p class="text-sm opacity-75">Today's Min</p>
					<p class="text-2xl font-bold">
						{todayData.length > 0 ? Math.min(...todayData.map((d) => d.visitor_count)) : '-'}
					</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-sm opacity-75">Today's Max</p>
					<p class="text-2xl font-bold">
						{todayData.length > 0 ? Math.max(...todayData.map((d) => d.visitor_count)) : '-'}
					</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-sm opacity-75">Today's Avg</p>
					<p class="text-2xl font-bold">
						{todayCurrentAvg > 0 ? todayCurrentAvg : '-'}
					</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-sm opacity-75">{weekdayAverage?.weekday || 'Weekday'} Avg</p>
					<p class="text-2xl font-bold">
						{weekdayAverage ? Math.round(weekdayAverage.average_visitors) : '-'}
					</p>
					<p class="text-xs opacity-60">up to {weekdayAverage?.current_time || 'now'}</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-sm opacity-75">vs. Typical</p>
					<p class="text-2xl font-bold {comparison > 0 ? 'text-error-500' : comparison < 0 ? 'text-success-500' : ''}">
						{#if comparison !== 0}
							{comparison > 0 ? '+' : ''}{Math.round(comparison)}
						{:else}
							-
						{/if}
					</p>
					<p class="text-xs opacity-60">{comparison > 0 ? 'busier' : comparison < 0 ? 'quieter' : ''}</p>
				</div>
				<div class="card p-4 text-center">
					<p class="text-sm opacity-75">Total Records</p>
					<p class="text-2xl font-bold">{$selectedPool.total_records.toLocaleString()}</p>
				</div>
			</section>
		{/if}
	</div>
{/if}
