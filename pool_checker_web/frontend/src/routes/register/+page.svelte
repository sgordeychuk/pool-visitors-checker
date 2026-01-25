<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth, isAuthenticated } from '$lib/stores/auth';

	let email = '';
	let username = '';
	let password = '';
	let confirmPassword = '';
	let loading = false;
	let validationError = '';

	$: if ($isAuthenticated) {
		goto('/');
	}

	async function handleSubmit() {
		validationError = '';

		if (password !== confirmPassword) {
			validationError = 'Passwords do not match';
			return;
		}

		if (password.length < 8) {
			validationError = 'Password must be at least 8 characters';
			return;
		}

		loading = true;
		auth.clearError();
		const success = await auth.register(email, username, password);
		if (success) {
			goto('/');
		}
		loading = false;
	}
</script>

<svelte:head>
	<title>Register - Pool Visitor Tracker</title>
</svelte:head>

<div class="flex items-center justify-center min-h-[60vh]">
	<div class="card p-8 w-full max-w-md space-y-6">
		<h1 class="h2 text-center">Register</h1>

		{#if $auth.error || validationError}
			<aside class="alert variant-filled-error">
				<div class="alert-message">
					<p>{$auth.error || validationError}</p>
				</div>
				<button
					class="btn btn-sm"
					on:click={() => {
						auth.clearError();
						validationError = '';
					}}>Dismiss</button
				>
			</aside>
		{/if}

		<form on:submit|preventDefault={handleSubmit} class="space-y-4">
			<label class="label">
				<span>Email</span>
				<input
					class="input"
					type="email"
					placeholder="Enter your email"
					bind:value={email}
					required
					disabled={loading}
				/>
			</label>

			<label class="label">
				<span>Username</span>
				<input
					class="input"
					type="text"
					placeholder="Choose a username"
					bind:value={username}
					required
					minlength="3"
					disabled={loading}
				/>
			</label>

			<label class="label">
				<span>Password</span>
				<input
					class="input"
					type="password"
					placeholder="Choose a password"
					bind:value={password}
					required
					minlength="8"
					disabled={loading}
				/>
			</label>

			<label class="label">
				<span>Confirm Password</span>
				<input
					class="input"
					type="password"
					placeholder="Confirm your password"
					bind:value={confirmPassword}
					required
					disabled={loading}
				/>
			</label>

			<button type="submit" class="btn variant-filled-primary w-full" disabled={loading}>
				{#if loading}
					<span class="animate-spin">⏳</span>
				{:else}
					Register
				{/if}
			</button>
		</form>

		<p class="text-center text-sm opacity-75">
			Already have an account?
			<a href="/login" class="anchor">Login</a>
		</p>
	</div>
</div>
