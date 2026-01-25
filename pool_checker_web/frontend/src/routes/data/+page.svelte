<script lang="ts">
	import { onMount } from 'svelte';
	import { pools, selectedPool } from '$lib/stores/pools';
	import { isAuthenticated } from '$lib/stores/auth';
	import { api, type VisitorRecord, type PaginatedVisitorResponse } from '$lib/api';

	let data: PaginatedVisitorResponse | null = null;
	let loading = true;
	let currentPage = 1;
	let pageSize = 50;

	$: if ($isAuthenticated) {
		loadData();
	}

	$: totalPages = data ? Math.ceil(data.total / pageSize) : 0;

	async function loadData() {
		loading = true;
		await pools.loadPools();
		await fetchRecords();
		loading = false;
	}

	async function fetchRecords() {
		const offset = (currentPage - 1) * pageSize;
		data = await api.getVisitorsPaginated({
			pool_id: $pools.selectedPoolId || undefined,
			limit: pageSize,
			offset
		});
	}

	async function handlePoolChange(e: Event) {
		const target = e.currentTarget as HTMLSelectElement;
		pools.selectPool(Number(target.value));
		currentPage = 1;
		await fetchRecords();
	}

	async function goToPage(page: number) {
		if (page < 1 || page > totalPages) return;
		currentPage = page;
		await fetchRecords();
	}

	function formatDateTime(timestamp: string): string {
		return new Date(timestamp).toLocaleString('de-CH', {
			year: 'numeric',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit'
		});
	}

	function formatDate(timestamp: string): string {
		return new Date(timestamp).toLocaleDateString('de-CH', {
			weekday: 'long',
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	// Generate page numbers to display
	$: pageNumbers = (() => {
		const pages: (number | string)[] = [];
		const maxVisible = 7;

		if (totalPages <= maxVisible) {
			for (let i = 1; i <= totalPages; i++) pages.push(i);
		} else {
			pages.push(1);
			if (currentPage > 3) pages.push('...');

			const start = Math.max(2, currentPage - 1);
			const end = Math.min(totalPages - 1, currentPage + 1);

			for (let i = start; i <= end; i++) pages.push(i);

			if (currentPage < totalPages - 2) pages.push('...');
			pages.push(totalPages);
		}
		return pages;
	})();
</script>

<svelte:head>
	<title>Raw Data - Pool Visitor Tracker</title>
</svelte:head>

{#if !$isAuthenticated}
	<div class="flex flex-col items-center justify-center h-64 space-y-4">
		<h1 class="h1">Raw Data</h1>
		<p class="text-lg opacity-75">Please log in to view pool visitor data.</p>
		<a href="/login" class="btn variant-filled-primary">Log In</a>
	</div>
{:else if loading}
	<div class="flex justify-center items-center h-64">
		<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
	</div>
{:else}
	<div class="space-y-6">
		<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
			<div>
				<h1 class="h1">Raw Data</h1>
				<p class="opacity-75">{formatDate(new Date().toISOString())}</p>
			</div>
			<div class="flex gap-4 items-center">
				{#if $pools.pools.length > 0}
					<select
						class="select w-full md:w-64"
						value={$pools.selectedPoolId}
						on:change={handlePoolChange}
					>
						<option value={0}>All Pools</option>
						{#each $pools.pools as pool}
							<option value={pool.id}>{pool.name}</option>
						{/each}
					</select>
				{/if}
			</div>
		</header>

		<!-- Summary -->
		{#if data}
			<div class="card p-4">
				<p class="text-sm opacity-75">
					Showing {data.offset + 1} - {data.offset + data.records.length} of {data.total.toLocaleString()} records
				</p>
			</div>
		{/if}

		<!-- Data Table -->
		<div class="card">
			<div class="table-container">
				<table class="table table-hover">
					<thead>
						<tr>
							<th>Date & Time</th>
							<th>Weekday</th>
							<th class="text-right">Visitors</th>
							<th>Pool</th>
						</tr>
					</thead>
					<tbody>
						{#if data && data.records.length > 0}
							{#each data.records as record}
								<tr>
									<td>{formatDateTime(record.timestamp)}</td>
									<td>{record.weekday}</td>
									<td class="text-right font-mono">{record.visitor_count}</td>
									<td class="opacity-75">
										{$pools.pools.find(p => p.id === record.pool_id)?.name || `Pool ${record.pool_id}`}
									</td>
								</tr>
							{/each}
						{:else}
							<tr>
								<td colspan="4" class="text-center opacity-75">No data available</td>
							</tr>
						{/if}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Pagination -->
		{#if data && totalPages > 1}
			<nav class="flex justify-center items-center gap-2">
				<button
					class="btn btn-sm variant-ghost-surface"
					disabled={currentPage === 1}
					on:click={() => goToPage(currentPage - 1)}
				>
					Previous
				</button>

				{#each pageNumbers as page}
					{#if page === '...'}
						<span class="px-2 opacity-50">...</span>
					{:else}
						<button
							class="btn btn-sm {currentPage === page ? 'variant-filled-primary' : 'variant-ghost-surface'}"
							on:click={() => goToPage(Number(page))}
						>
							{page}
						</button>
					{/if}
				{/each}

				<button
					class="btn btn-sm variant-ghost-surface"
					disabled={currentPage === totalPages}
					on:click={() => goToPage(currentPage + 1)}
				>
					Next
				</button>
			</nav>
		{/if}
	</div>
{/if}
