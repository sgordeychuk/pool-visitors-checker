<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import Chart from 'chart.js/auto';
	import type { WeekdayAverage } from '$lib/api';

	export let data: WeekdayAverage[] = [];

	let canvas: HTMLCanvasElement;
	let chart: Chart | null = null;

	const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
	const weekdayColors: Record<string, { border: string; bg: string }> = {
		Monday: { border: 'rgb(59, 130, 246)', bg: 'rgba(59, 130, 246, 0.1)' },
		Tuesday: { border: 'rgb(168, 85, 247)', bg: 'rgba(168, 85, 247, 0.1)' },
		Wednesday: { border: 'rgb(34, 197, 94)', bg: 'rgba(34, 197, 94, 0.1)' },
		Thursday: { border: 'rgb(249, 115, 22)', bg: 'rgba(249, 115, 22, 0.1)' },
		Friday: { border: 'rgb(236, 72, 153)', bg: 'rgba(236, 72, 153, 0.1)' },
		Saturday: { border: 'rgb(234, 179, 8)', bg: 'rgba(234, 179, 8, 0.1)' },
		Sunday: { border: 'rgb(239, 68, 68)', bg: 'rgba(239, 68, 68, 0.1)' }
	};

	// Track enabled weekdays
	let enabledDays: Record<string, boolean> = {
		Monday: true,
		Tuesday: true,
		Wednesday: true,
		Thursday: true,
		Friday: true,
		Saturday: true,
		Sunday: true
	};

	// Hours from 6 AM to 10 PM (pool hours)
	const hours = Array.from({ length: 17 }, (_, i) => i + 6);

	function formatHour(hour: number): string {
		return `${hour.toString().padStart(2, '0')}:00`;
	}

	function getDataForWeekday(weekday: string): (number | null)[] {
		return hours.map((hour) => {
			const entry = data.find((d) => d.weekday === weekday && d.hour === hour);
			return entry ? entry.average_visitors : null;
		});
	}

	function toggleDay(day: string) {
		enabledDays[day] = !enabledDays[day];
		updateChart();
	}

	function updateChart() {
		if (!chart) return;

		const datasets = weekdays
			.filter((day) => enabledDays[day])
			.map((weekday) => ({
				label: weekday,
				data: getDataForWeekday(weekday),
				borderColor: weekdayColors[weekday].border,
				backgroundColor: weekdayColors[weekday].bg,
				fill: false,
				tension: 0.4,
				pointRadius: 3,
				pointHoverRadius: 6,
				spanGaps: true
			}));

		chart.data.datasets = datasets;
		chart.update();
	}

	function createChart() {
		const ctx = canvas.getContext('2d');
		if (!ctx) return;

		const datasets = weekdays
			.filter((day) => enabledDays[day])
			.map((weekday) => ({
				label: weekday,
				data: getDataForWeekday(weekday),
				borderColor: weekdayColors[weekday].border,
				backgroundColor: weekdayColors[weekday].bg,
				fill: false,
				tension: 0.4,
				pointRadius: 3,
				pointHoverRadius: 6,
				spanGaps: true
			}));

		chart = new Chart(ctx, {
			type: 'line',
			data: {
				labels: hours.map(formatHour),
				datasets
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				interaction: {
					intersect: false,
					mode: 'index'
				},
				scales: {
					y: {
						beginAtZero: true,
						title: {
							display: true,
							text: 'Average Visitors'
						},
						grid: {
							color: 'rgba(128, 128, 128, 0.1)'
						}
					},
					x: {
						title: {
							display: true,
							text: 'Hour'
						},
						grid: {
							display: false
						}
					}
				},
				plugins: {
					legend: {
						display: false
					},
					tooltip: {
						backgroundColor: 'rgba(0, 0, 0, 0.8)',
						padding: 12
					}
				}
			}
		});
	}

	$: if (browser && canvas && data.length > 0) {
		if (chart) {
			updateChart();
		} else {
			createChart();
		}
	}

	onMount(() => {
		if (data.length > 0) {
			createChart();
		}
	});

	onDestroy(() => {
		if (chart) {
			chart.destroy();
		}
	});

	// Find best time to visit (lowest average across all days)
	$: bestTimes = (() => {
		const hourlyAverages: { hour: number; avg: number; days: number }[] = [];

		for (const hour of hours) {
			const enabledData = data.filter(
				(d) => d.hour === hour && enabledDays[d.weekday]
			);
			if (enabledData.length > 0) {
				const avg = enabledData.reduce((sum, d) => sum + d.average_visitors, 0) / enabledData.length;
				hourlyAverages.push({ hour, avg, days: enabledData.length });
			}
		}

		return hourlyAverages.sort((a, b) => a.avg - b.avg).slice(0, 3);
	})();
</script>

<div class="space-y-4">
	<!-- Day Toggles -->
	<div class="flex flex-wrap gap-2 justify-center">
		{#each weekdays as day}
			<button
				class="btn btn-sm {enabledDays[day] ? '' : 'opacity-40'}"
				style="background-color: {enabledDays[day] ? weekdayColors[day].border : 'transparent'};
					   color: {enabledDays[day] ? 'white' : weekdayColors[day].border};
					   border: 2px solid {weekdayColors[day].border};"
				on:click={() => toggleDay(day)}
			>
				{day.slice(0, 3)}
			</button>
		{/each}
	</div>

	<!-- Chart -->
	<div class="h-64 md:h-80">
		<canvas bind:this={canvas}></canvas>
	</div>

	<!-- Best Times Summary -->
	{#if bestTimes.length > 0}
		<div class="flex flex-wrap justify-center gap-4 pt-4 border-t border-surface-500/20">
			<p class="text-sm opacity-75 w-full text-center mb-2">Best times to visit (for selected days):</p>
			{#each bestTimes as time, i}
				<div class="text-center">
					<span class="badge {i === 0 ? 'variant-filled-success' : 'variant-soft-success'}">
						{formatHour(time.hour)} - Avg: {Math.round(time.avg)}
					</span>
				</div>
			{/each}
		</div>
	{/if}
</div>
