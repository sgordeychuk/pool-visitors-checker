<script lang="ts">
	import Badge from './Badge.svelte';
	import Card from './Card.svelte';

	type CrowdLevel = 'low' | 'moderate' | 'high' | 'full';

	export let title: string = 'Best Time to Swim';
	export let recommendation: string;
	export let crowdLevel: CrowdLevel = 'low';
	export let subtitle: string | undefined = undefined;
	export let trendText: string | undefined = undefined;
	export let trendIcon: string | undefined = undefined;

	const crowdLevelLabels: Record<CrowdLevel, string> = {
		low: 'Low Crowd',
		moderate: 'Moderate',
		high: 'Busy',
		full: 'Very Busy'
	};
</script>

<Card variant="prediction" padding="lg" class="relative overflow-hidden">
	<!-- Decorative background element -->
	<div
		class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none"
		aria-hidden="true"
	/>

	<div class="relative z-10 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
		<div class="flex-1 min-w-0">
			<!-- Label -->
			<div class="flex items-center gap-2 mb-3">
				<Badge variant={crowdLevel} size="sm" pill>
					{crowdLevelLabels[crowdLevel]}
				</Badge>
				<span class="text-xs uppercase tracking-wide text-white/80">{title}</span>
			</div>

			<!-- Main recommendation -->
			<h2 class="text-2xl font-bold text-white mb-2">
				{recommendation}
			</h2>

			{#if subtitle}
				<p class="text-white/70 text-sm">{subtitle}</p>
			{/if}
		</div>

		<!-- Trend indicator -->
		{#if trendText}
			<div
				class="flex-shrink-0 bg-white/15 backdrop-blur-sm rounded-lg px-4 py-3 text-center min-w-[120px]"
			>
				<div class="text-xs uppercase tracking-wide text-white/60 mb-1">Current Trend</div>
				{#if trendIcon}
					<div class="text-lg mb-0.5">{trendIcon}</div>
				{/if}
				<div class="text-sm text-white font-medium">{trendText}</div>
			</div>
		{/if}
	</div>

	<!-- Clock icon decoration - moved to bottom right to avoid overlap -->
	<div class="absolute bottom-2 right-4 opacity-10 pointer-events-none" aria-hidden="true">
		<svg class="w-12 h-12" fill="currentColor" viewBox="0 0 24 24">
			<path
				d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"
			/>
		</svg>
	</div>
</Card>
