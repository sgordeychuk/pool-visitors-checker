<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { pools } from '$lib/stores/pools';
	import { isAdmin } from '$lib/stores/auth';
	import { getModalStore, getToastStore, type ModalSettings } from '@skeletonlabs/skeleton';
	import PoolForm from '$lib/components/ui/PoolForm.svelte';
	import type { Pool } from '$lib/api';

	const modalStore = getModalStore();
	const toastStore = getToastStore();

	let editingPool: Pool | null = null;
	let showForm = false;

	$: if (!$isAdmin) {
		goto('/');
	}

	onMount(async () => {
		await pools.loadPools();
	});

	function handleCreateNew() {
		editingPool = null;
		showForm = true;
	}

	function handleEdit(pool: Pool) {
		editingPool = pool;
		showForm = true;
	}

	async function handleSave(event: CustomEvent<Partial<Pool>>) {
		const poolData = event.detail;
		try {
			if (editingPool) {
				await pools.updatePool(editingPool.id, poolData);
				toastStore.trigger({ message: 'Pool updated successfully', background: 'variant-filled-success' });
			} else {
				await pools.createPool(poolData as any);
				toastStore.trigger({ message: 'Pool created successfully', background: 'variant-filled-success' });
			}
			showForm = false;
			editingPool = null;
		} catch (error) {
			toastStore.trigger({
				message: error instanceof Error ? error.message : 'Failed to save pool',
				background: 'variant-filled-error'
			});
		}
	}

	function handleCancel() {
		showForm = false;
		editingPool = null;
	}

	async function handleDelete(pool: Pool) {
		const modal: ModalSettings = {
			type: 'confirm',
			title: 'Delete Pool',
			body: `Are you sure you want to delete "${pool.name}"? This will also delete all associated visitor data.`,
			response: async (confirmed: boolean) => {
				if (confirmed) {
					try {
						await pools.deletePool(pool.id);
						toastStore.trigger({ message: 'Pool deleted successfully', background: 'variant-filled-success' });
					} catch (error) {
						toastStore.trigger({
							message: error instanceof Error ? error.message : 'Failed to delete pool',
							background: 'variant-filled-error'
						});
					}
				}
			}
		};
		modalStore.trigger(modal);
	}

	async function handleTriggerScrape(pool: Pool) {
		try {
			const result = await pools.triggerScrape(pool.id);
			toastStore.trigger({
				message: `Scrape task queued (Task ID: ${result.task_id.slice(0, 8)}...)`,
				background: 'variant-filled-success'
			});
		} catch (error) {
			toastStore.trigger({
				message: error instanceof Error ? error.message : 'Failed to trigger scrape',
				background: 'variant-filled-error'
			});
		}
	}

	function formatDateTime(timestamp: string | undefined): string {
		if (!timestamp) return 'Never';
		return new Date(timestamp).toLocaleString('de-CH');
	}
</script>

<svelte:head>
	<title>Manage Pools - Pool Visitor Tracker</title>
</svelte:head>

<div class="space-y-8">
	<header class="flex flex-col md:flex-row md:items-center justify-between gap-4">
		<h1 class="h1">Manage Pools</h1>
		<button class="btn variant-filled-primary" on:click={handleCreateNew}>
			+ Add Pool
		</button>
	</header>

	{#if showForm}
		<div class="card p-6">
			<h2 class="h3 mb-4">{editingPool ? 'Edit Pool' : 'Create New Pool'}</h2>
			<PoolForm pool={editingPool} on:save={handleSave} on:cancel={handleCancel} />
		</div>
	{/if}

	{#if $pools.loading}
		<div class="flex justify-center items-center h-32">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
		</div>
	{:else if $pools.pools.length === 0}
		<div class="card p-8 text-center">
			<p class="text-lg opacity-75">No pools configured yet.</p>
			<button class="btn variant-filled-primary mt-4" on:click={handleCreateNew}>
				Create Your First Pool
			</button>
		</div>
	{:else}
		<div class="space-y-4">
			{#each $pools.pools as pool}
				<div class="card p-4 md:p-6">
					<div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
						<div class="flex-1 space-y-2">
							<div class="flex items-center gap-2">
								<h3 class="h4">{pool.name}</h3>
								<span class="badge" class:variant-filled-success={pool.is_active} class:variant-filled-error={!pool.is_active}>
									{pool.is_active ? 'Active' : 'Inactive'}
								</span>
							</div>
							<p class="text-sm opacity-75 break-all">{pool.url}</p>
							<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
								<div>
									<span class="opacity-75">Element ID:</span>
									<span class="font-mono">{pool.element_id}</span>
								</div>
								<div>
									<span class="opacity-75">Scrape Hours:</span>
									<span>{pool.scrape_start_time} - {pool.scrape_end_time}</span>
								</div>
								<div>
									<span class="opacity-75">Interval:</span>
									<span>{pool.scrape_interval_minutes} min</span>
								</div>
								<div>
									<span class="opacity-75">Total Records:</span>
									<span>{pool.total_records.toLocaleString()}</span>
								</div>
							</div>
							{#if pool.latest_reading_time}
								<p class="text-sm">
									<span class="opacity-75">Last reading:</span>
									{pool.latest_visitor_count} visitors at {formatDateTime(pool.latest_reading_time)}
								</p>
							{/if}
						</div>
						<div class="flex flex-wrap gap-2">
							<button class="btn btn-sm variant-ghost-surface" on:click={() => handleTriggerScrape(pool)}>
								Scrape Now
							</button>
							<button class="btn btn-sm variant-ghost-surface" on:click={() => handleEdit(pool)}>
								Edit
							</button>
							<button class="btn btn-sm variant-ghost-error" on:click={() => handleDelete(pool)}>
								Delete
							</button>
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
