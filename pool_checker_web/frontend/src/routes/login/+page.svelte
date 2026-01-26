<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth, isAuthenticated } from '$lib/stores/auth';

	let username = '';
	let password = '';
	let loading = false;

	$: if ($isAuthenticated) {
		goto('/');
	}

	async function handleSubmit() {
		loading = true;
		auth.clearError();
		const success = await auth.login(username, password);
		if (success) {
			goto('/');
		}
		loading = false;
	}
</script>

<svelte:head>
	<title>Login - Pool Visitor Tracker</title>
</svelte:head>

<div class="flex items-center justify-center min-h-[60vh]">
	<div class="card p-8 w-full max-w-md space-y-6">
		<h1 class="h2 text-center">Login</h1>

		{#if $auth.error}
			<aside class="alert variant-filled-error">
				<div class="alert-message">
					<p>{$auth.error}</p>
				</div>
				<button class="btn btn-sm" on:click={() => auth.clearError()}>Dismiss</button>
			</aside>
		{/if}

		<form on:submit|preventDefault={handleSubmit} class="space-y-4">
			<label class="label">
				<span>Username</span>
				<input
					class="input"
					type="text"
					placeholder="Enter your username"
					bind:value={username}
					required
					disabled={loading}
				/>
			</label>

			<label class="label">
				<span>Password</span>
				<input
					class="input"
					type="password"
					placeholder="Enter your password"
					bind:value={password}
					required
					disabled={loading}
				/>
			</label>

			<button type="submit" class="btn variant-filled-primary w-full" disabled={loading}>
				{#if loading}
					<span class="animate-spin">⏳</span>
				{:else}
					Login
				{/if}
			</button>
		</form>

	</div>
</div>
