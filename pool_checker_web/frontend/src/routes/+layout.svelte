<script lang="ts">
	import '../app.postcss';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import {
		AppShell,
		AppBar,
		LightSwitch,
		getDrawerStore,
		initializeStores,
		Drawer,
		Toast,
		getToastStore
	} from '@skeletonlabs/skeleton';
	import { auth, isAuthenticated, currentUser, isAdmin } from '$lib/stores/auth';

	initializeStores();
	const drawerStore = getDrawerStore();

	onMount(async () => {
		await auth.init();
	});

	function handleLogout() {
		auth.logout();
		goto('/login');
	}

	$: publicRoutes = ['/login', '/register'];
	$: isPublicRoute = publicRoutes.includes($page.url.pathname);

	$: if (!$auth.loading && !$isAuthenticated && !isPublicRoute) {
		goto('/login');
	}
</script>

<Toast />
<Drawer>
	<nav class="p-4 space-y-2">
		<a href="/" class="btn variant-ghost-surface w-full justify-start">Dashboard</a>
		<a href="/analytics" class="btn variant-ghost-surface w-full justify-start">Analytics</a>
		<a href="/data" class="btn variant-ghost-surface w-full justify-start">Raw Data</a>
		{#if $isAdmin}
			<a href="/pools" class="btn variant-ghost-surface w-full justify-start">Manage Pools</a>
		{/if}
	</nav>
</Drawer>

<AppShell>
	<svelte:fragment slot="header">
		<AppBar>
			<svelte:fragment slot="lead">
				<button class="lg:hidden btn btn-sm variant-ghost-surface" on:click={() => drawerStore.open()}>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				<a href="/" class="font-bold text-xl">Pool Visitor Tracker</a>
			</svelte:fragment>
			<svelte:fragment slot="trail">
				{#if $isAuthenticated}
					<nav class="hidden lg:flex items-center space-x-4">
						<a href="/" class="btn btn-sm variant-ghost-surface">Dashboard</a>
						<a href="/analytics" class="btn btn-sm variant-ghost-surface">Analytics</a>
						<a href="/data" class="btn btn-sm variant-ghost-surface">Data</a>
						{#if $isAdmin}
							<a href="/pools" class="btn btn-sm variant-ghost-surface">Pools</a>
						{/if}
					</nav>
					<span class="hidden md:inline text-sm opacity-75">
						{$currentUser?.username}
						{#if $isAdmin}<span class="badge variant-soft-primary ml-1">Admin</span>{/if}
					</span>
					<button class="btn btn-sm variant-ghost-surface" on:click={handleLogout}>Logout</button>
				{/if}
				<LightSwitch />
			</svelte:fragment>
		</AppBar>
	</svelte:fragment>
	<main class="container mx-auto p-4 md:p-8">
		{#if $auth.loading}
			<div class="flex justify-center items-center h-64">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
			</div>
		{:else}
			<slot />
		{/if}
	</main>
</AppShell>
