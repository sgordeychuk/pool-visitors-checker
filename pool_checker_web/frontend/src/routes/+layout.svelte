<script lang="ts">
	import '../app.postcss';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import {
		AppShell,
		LightSwitch,
		getDrawerStore,
		initializeStores,
		Drawer,
		Toast
	} from '@skeletonlabs/skeleton';
	import { auth, isAuthenticated, currentUser, isAdmin } from '$lib/stores/auth';
	import { Badge } from '$clearlane';

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

	function isActive(path: string): string {
		return $page.url.pathname === path ? 'bg-white/15' : '';
	}
</script>

<Toast />
<Drawer>
	<nav class="p-4 space-y-2 bg-cl-bg-surface h-full">
		<div class="flex items-center gap-2 mb-6 pb-4 border-b border-cl-border">
			<svg class="w-8 h-8 text-cl-primary" viewBox="0 0 32 32" fill="currentColor">
				<circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" stroke-width="2" />
				<path d="M8 18 Q16 10, 24 18" stroke="currentColor" stroke-width="2" fill="none" />
				<path d="M8 22 Q16 14, 24 22" stroke="currentColor" stroke-width="2" fill="none" />
			</svg>
			<span class="font-bold text-lg text-cl-text-primary">ClearLane</span>
		</div>
		<a
			href="/"
			class="block px-4 py-2.5 rounded-lg text-cl-text-primary hover:bg-cl-bg-muted transition-colors {$page.url.pathname === '/' ? 'bg-cl-primary/10 text-cl-primary font-medium' : ''}"
		>
			Dashboard
		</a>
		<a
			href="/analytics"
			class="block px-4 py-2.5 rounded-lg text-cl-text-primary hover:bg-cl-bg-muted transition-colors {$page.url.pathname === '/analytics' ? 'bg-cl-primary/10 text-cl-primary font-medium' : ''}"
		>
			Analytics
		</a>
		<a
			href="/data"
			class="block px-4 py-2.5 rounded-lg text-cl-text-primary hover:bg-cl-bg-muted transition-colors {$page.url.pathname === '/data' ? 'bg-cl-primary/10 text-cl-primary font-medium' : ''}"
		>
			Raw Data
		</a>
		{#if $isAdmin}
			<a
				href="/pools"
				class="block px-4 py-2.5 rounded-lg text-cl-text-primary hover:bg-cl-bg-muted transition-colors {$page.url.pathname === '/pools' ? 'bg-cl-primary/10 text-cl-primary font-medium' : ''}"
			>
				Manage Pools
			</a>
		{/if}
	</nav>
</Drawer>

<AppShell>
	<svelte:fragment slot="header">
		<header class="bg-cl-primary text-white px-4 py-3 shadow-cl-card">
			<div class="container mx-auto flex items-center justify-between">
				<div class="flex items-center gap-3">
					<button
						class="lg:hidden p-2 hover:bg-white/10 rounded-cl-md transition-colors"
						on:click={() => drawerStore.open()}
					>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
						</svg>
					</button>
					<a href="/" class="flex items-center gap-2">
						<svg class="w-8 h-8" viewBox="0 0 32 32" fill="currentColor">
							<circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" stroke-width="2" />
							<path d="M8 18 Q16 10, 24 18" stroke="currentColor" stroke-width="2" fill="none" />
							<path d="M8 22 Q16 14, 24 22" stroke="currentColor" stroke-width="2" fill="none" />
						</svg>
						<span class="font-bold text-xl hidden sm:inline">ClearLane</span>
					</a>
				</div>

				{#if $isAuthenticated}
					<nav class="hidden lg:flex items-center gap-1">
						<a
							href="/"
							class="px-4 py-2 rounded-cl-md hover:bg-white/10 transition-colors text-sm font-medium {isActive('/')}"
						>
							Dashboard
						</a>
						<a
							href="/analytics"
							class="px-4 py-2 rounded-cl-md hover:bg-white/10 transition-colors text-sm font-medium {isActive('/analytics')}"
						>
							Analytics
						</a>
						<a
							href="/data"
							class="px-4 py-2 rounded-cl-md hover:bg-white/10 transition-colors text-sm font-medium {isActive('/data')}"
						>
							Data
						</a>
						{#if $isAdmin}
							<a
								href="/pools"
								class="px-4 py-2 rounded-cl-md hover:bg-white/10 transition-colors text-sm font-medium {isActive('/pools')}"
							>
								Pools
							</a>
						{/if}
					</nav>
				{/if}

				<div class="flex items-center gap-3">
					{#if $isAuthenticated}
						<span class="hidden md:inline text-sm opacity-90">
							{$currentUser?.username}
							{#if $isAdmin}
								<Badge variant="primary" size="sm" class="ml-1 bg-white/20 text-white">Admin</Badge>
							{/if}
						</span>
						<button
							class="px-3 py-1.5 text-sm rounded-cl-md hover:bg-white/10 transition-colors"
							on:click={handleLogout}
						>
							Logout
						</button>
					{/if}
					<LightSwitch />
				</div>
			</div>
		</header>
	</svelte:fragment>

	<main class="bg-cl-bg-base min-h-screen">
		<div class="container mx-auto p-4 md:p-8">
			{#if $auth.loading}
				<div class="flex justify-center items-center h-64">
					<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cl-primary"></div>
				</div>
			{:else}
				<slot />
			{/if}
		</div>
	</main>
</AppShell>
