// ClearLane Design System - Chart.js Color Utilities

/**
 * ClearLane color constants for use in Chart.js
 */
export const clearLaneColors = {
	// Primary
	primary: '#006994',
	primaryHover: '#005577',
	primaryLight: '#0089c2',
	primaryDark: '#004d6d',

	// Crowd/Traffic Light Colors
	crowdLow: '#4CD964',
	crowdModerate: '#5AC8FA',
	crowdHigh: '#FF9500',
	crowdFull: '#FF3B30',

	// Background
	bgBase: '#F5F7FA',
	bgSurface: '#FFFFFF',
	bgMuted: '#EDF0F4',

	// Text
	textPrimary: '#2C3E50',
	textSecondary: '#5A6978',
	textMuted: '#8A96A3',

	// Border/Grid
	border: '#E2E8F0',
	gridLine: 'rgba(226, 232, 240, 0.5)'
} as const;

/**
 * Crowd level type
 */
export type CrowdLevel = 'low' | 'moderate' | 'high' | 'full';

/**
 * Returns the appropriate traffic light color based on a normalized value (0-1)
 * @param normalized - Value between 0 and 1 representing crowd density
 * @returns Hex color string
 */
export function getCrowdColor(normalized: number): string {
	if (normalized < 0.25) return clearLaneColors.crowdLow;
	if (normalized < 0.5) return clearLaneColors.crowdModerate;
	if (normalized < 0.75) return clearLaneColors.crowdHigh;
	return clearLaneColors.crowdFull;
}

/**
 * Returns the crowd level category based on a normalized value (0-1)
 * @param normalized - Value between 0 and 1 representing crowd density
 * @returns Crowd level string
 */
export function getCrowdLevel(normalized: number): CrowdLevel {
	if (normalized < 0.25) return 'low';
	if (normalized < 0.5) return 'moderate';
	if (normalized < 0.75) return 'high';
	return 'full';
}

/**
 * Returns crowd color based on actual visitor count and a maximum
 * @param count - Current visitor count
 * @param max - Maximum expected visitors (defaults to 100)
 * @returns Hex color string
 */
export function getCrowdColorFromCount(count: number, max = 100): string {
	const normalized = Math.min(count / max, 1);
	return getCrowdColor(normalized);
}

/**
 * Creates a vertical gradient for area charts
 * @param ctx - Canvas 2D rendering context
 * @param chartArea - Chart.js chart area object
 * @param colorStart - Starting color (top)
 * @param colorEnd - Ending color (bottom)
 * @returns CanvasGradient
 */
export function createAreaGradient(
	ctx: CanvasRenderingContext2D,
	chartArea: { top: number; bottom: number },
	colorStart: string = clearLaneColors.primary,
	colorEnd: string = 'rgba(0, 105, 148, 0.05)'
): CanvasGradient {
	const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
	gradient.addColorStop(0, colorStart);
	gradient.addColorStop(1, colorEnd);
	return gradient;
}

/**
 * Creates a crowd-level gradient based on data values
 * @param ctx - Canvas 2D rendering context
 * @param chartArea - Chart.js chart area object
 * @param normalized - Normalized crowd value (0-1)
 * @returns CanvasGradient
 */
export function createCrowdGradient(
	ctx: CanvasRenderingContext2D,
	chartArea: { top: number; bottom: number },
	normalized: number
): CanvasGradient {
	const color = getCrowdColor(normalized);
	const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
	gradient.addColorStop(0, color);
	gradient.addColorStop(1, `${color}10`);
	return gradient;
}

/**
 * Default Chart.js options styled with ClearLane design system
 */
export const clearLaneChartDefaults = {
	responsive: true,
	maintainAspectRatio: false,
	plugins: {
		legend: {
			display: true,
			position: 'top' as const,
			labels: {
				color: clearLaneColors.textSecondary,
				font: {
					family: 'Inter, sans-serif',
					size: 12
				},
				padding: 16,
				usePointStyle: true,
				pointStyle: 'circle'
			}
		},
		tooltip: {
			backgroundColor: clearLaneColors.bgSurface,
			titleColor: clearLaneColors.textPrimary,
			bodyColor: clearLaneColors.textSecondary,
			borderColor: clearLaneColors.border,
			borderWidth: 1,
			cornerRadius: 8,
			padding: 12,
			titleFont: {
				family: 'Inter, sans-serif',
				size: 14,
				weight: 600
			},
			bodyFont: {
				family: 'Inter, sans-serif',
				size: 13
			},
			displayColors: true,
			boxPadding: 4
		}
	},
	scales: {
		x: {
			grid: {
				color: clearLaneColors.gridLine,
				drawBorder: false
			},
			ticks: {
				color: clearLaneColors.textMuted,
				font: {
					family: 'Inter, sans-serif',
					size: 11
				}
			}
		},
		y: {
			grid: {
				color: clearLaneColors.gridLine,
				drawBorder: false
			},
			ticks: {
				color: clearLaneColors.textMuted,
				font: {
					family: 'Inter, sans-serif',
					size: 11
				}
			}
		}
	},
	elements: {
		line: {
			tension: 0.4, // Smooth curves as per design system
			borderWidth: 2
		},
		point: {
			radius: 0,
			hoverRadius: 6,
			hoverBorderWidth: 2
		}
	}
};

/**
 * Line chart specific defaults (smooth area charts)
 */
export const clearLaneLineChartDefaults = {
	...clearLaneChartDefaults,
	elements: {
		...clearLaneChartDefaults.elements,
		line: {
			tension: 0.4,
			borderWidth: 2,
			fill: true
		}
	}
};

/**
 * Bar chart specific defaults
 */
export const clearLaneBarChartDefaults = {
	...clearLaneChartDefaults,
	elements: {
		...clearLaneChartDefaults.elements,
		bar: {
			borderRadius: 4
		}
	}
};

/**
 * Heatmap cell colors array for use in custom heatmap implementations
 */
export const heatmapColors = [
	clearLaneColors.crowdLow,
	clearLaneColors.crowdModerate,
	clearLaneColors.crowdHigh,
	clearLaneColors.crowdFull
] as const;
