<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import Chart from 'chart.js/auto';

	export let labels: string[] = [];
	export let data: number[] = [];
	export let label: string = 'Visitors';

	let canvas: HTMLCanvasElement;
	let chart: Chart | null = null;

	$: if (browser && canvas && labels.length > 0) {
		updateChart();
	}

	function updateChart() {
		if (chart) {
			chart.data.labels = labels;
			chart.data.datasets[0].data = data;
			chart.update();
		} else if (canvas) {
			createChart();
		}
	}

	function createChart() {
		const ctx = canvas.getContext('2d');
		if (!ctx) return;

		chart = new Chart(ctx, {
			type: 'line',
			data: {
				labels,
				datasets: [
					{
						label,
						data,
						borderColor: 'rgb(59, 130, 246)',
						backgroundColor: 'rgba(59, 130, 246, 0.1)',
						fill: true,
						tension: 0.4,
						pointRadius: 2,
						pointHoverRadius: 6
					}
				]
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
						grid: {
							color: 'rgba(128, 128, 128, 0.1)'
						}
					},
					x: {
						grid: {
							display: false
						},
						ticks: {
							maxTicksLimit: 12
						}
					}
				},
				plugins: {
					legend: {
						display: false
					},
					tooltip: {
						backgroundColor: 'rgba(0, 0, 0, 0.8)',
						padding: 12,
						displayColors: false
					}
				}
			}
		});
	}

	onMount(() => {
		if (labels.length > 0) {
			createChart();
		}
	});

	onDestroy(() => {
		if (chart) {
			chart.destroy();
		}
	});
</script>

<canvas bind:this={canvas}></canvas>
