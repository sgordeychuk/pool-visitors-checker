import { browser } from '$app/environment';

const API_BASE = browser ? (import.meta.env.PUBLIC_API_URL || 'http://localhost:8000') : 'http://backend:8000';
const API_V1 = `${API_BASE}/api/v1`;

export interface User {
	id: number;
	email: string;
	username: string;
	is_active: boolean;
	is_superuser: boolean;
	created_at: string;
}

export interface Pool {
	id: number;
	name: string;
	url: string;
	element_id: string;
	timezone: string;
	scrape_start_time: string;
	scrape_end_time: string;
	scrape_interval_minutes: number;
	is_active: boolean;
	created_at: string;
	latest_visitor_count?: number;
	latest_reading_time?: string;
	total_records: number;
}

export interface VisitorRecord {
	id: number;
	pool_id: number;
	timestamp: string;
	weekday: string;
	visitor_count: number;
	week_number?: number;
	created_at: string;
}

export interface LatestVisitor {
	pool_id: number;
	pool_name: string;
	visitor_count: number;
	timestamp: string;
	weekday: string;
}

export interface WeekdayAverage {
	weekday: string;
	hour: number;
	average_visitors: number;
	sample_count: number;
}

export interface HeatmapCell {
	weekday: string;
	hour: number;
	value: number;
}

export interface HeatmapData {
	pool_id: number;
	pool_name: string;
	data: HeatmapCell[];
	min_value: number;
	max_value: number;
}

export interface DailySummary {
	date: string;
	pool_id: number;
	min_visitors: number;
	max_visitors: number;
	avg_visitors: number;
	total_readings: number;
}

export interface TrendDataPoint {
	period: string;
	average_visitors: number;
	peak_visitors: number;
	total_readings: number;
}

export interface TrendData {
	pool_id: number;
	pool_name: string;
	period_type: string;
	data: TrendDataPoint[];
}

export interface WeekdayAverageUpToNow {
	pool_id: number;
	pool_name: string;
	weekday: string;
	current_time: string;
	average_visitors: number;
	min_visitors: number;
	max_visitors: number;
	sample_count: number;
}

export interface PaginatedVisitorResponse {
	records: VisitorRecord[];
	total: number;
	limit: number;
	offset: number;
	has_more: boolean;
}

export interface Token {
	access_token: string;
	refresh_token: string;
	token_type: string;
}

class ApiClient {
	private getToken(): string | null {
		if (!browser) return null;
		return localStorage.getItem('access_token');
	}

	private getHeaders(): HeadersInit {
		const headers: HeadersInit = {
			'Content-Type': 'application/json'
		};
		const token = this.getToken();
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}
		return headers;
	}

	private async handleResponse<T>(response: Response): Promise<T> {
		if (!response.ok) {
			const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
			throw new Error(error.detail || `HTTP error: ${response.status}`);
		}
		return response.json();
	}

	// Auth
	async login(username: string, password: string): Promise<Token> {
		const formData = new URLSearchParams();
		formData.append('username', username);
		formData.append('password', password);

		const response = await fetch(`${API_V1}/auth/login`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: formData
		});
		return this.handleResponse<Token>(response);
	}

	async register(email: string, username: string, password: string): Promise<User> {
		const response = await fetch(`${API_V1}/auth/register`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, username, password })
		});
		return this.handleResponse<User>(response);
	}

	async getCurrentUser(): Promise<User> {
		const response = await fetch(`${API_V1}/auth/me`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<User>(response);
	}

	// Pools
	async getPools(): Promise<Pool[]> {
		const response = await fetch(`${API_V1}/pools`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<Pool[]>(response);
	}

	async getPool(id: number): Promise<Pool> {
		const response = await fetch(`${API_V1}/pools/${id}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<Pool>(response);
	}

	async createPool(pool: Omit<Pool, 'id' | 'created_at' | 'latest_visitor_count' | 'latest_reading_time' | 'total_records'>): Promise<Pool> {
		const response = await fetch(`${API_V1}/pools`, {
			method: 'POST',
			headers: this.getHeaders(),
			body: JSON.stringify(pool)
		});
		return this.handleResponse<Pool>(response);
	}

	async updatePool(id: number, pool: Partial<Pool>): Promise<Pool> {
		const response = await fetch(`${API_V1}/pools/${id}`, {
			method: 'PUT',
			headers: this.getHeaders(),
			body: JSON.stringify(pool)
		});
		return this.handleResponse<Pool>(response);
	}

	async deletePool(id: number): Promise<void> {
		const response = await fetch(`${API_V1}/pools/${id}`, {
			method: 'DELETE',
			headers: this.getHeaders()
		});
		if (!response.ok) {
			const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
			throw new Error(error.detail || `HTTP error: ${response.status}`);
		}
	}

	async triggerScrape(poolId: number): Promise<{ message: string; task_id: string }> {
		const response = await fetch(`${API_V1}/pools/${poolId}/scrape`, {
			method: 'POST',
			headers: this.getHeaders()
		});
		return this.handleResponse(response);
	}

	// Visitors
	async getVisitors(params?: {
		pool_id?: number;
		start_date?: string;
		end_date?: string;
		weekday?: string;
		limit?: number;
		offset?: number;
	}): Promise<VisitorRecord[]> {
		const searchParams = new URLSearchParams();
		if (params) {
			Object.entries(params).forEach(([key, value]) => {
				if (value !== undefined) searchParams.append(key, String(value));
			});
		}
		const response = await fetch(`${API_V1}/visitors?${searchParams}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<VisitorRecord[]>(response);
	}

	async getLatestVisitors(): Promise<LatestVisitor[]> {
		const response = await fetch(`${API_V1}/visitors/latest`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<LatestVisitor[]>(response);
	}

	async getTodayVisitors(poolId: number): Promise<VisitorRecord[]> {
		const response = await fetch(`${API_V1}/visitors/today/${poolId}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<VisitorRecord[]>(response);
	}

	// Analytics
	async getWeekdayAverages(poolId: number): Promise<WeekdayAverage[]> {
		const response = await fetch(`${API_V1}/analytics/weekday-averages?pool_id=${poolId}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<WeekdayAverage[]>(response);
	}

	async getHeatmapData(poolId: number): Promise<HeatmapData> {
		const response = await fetch(`${API_V1}/analytics/heatmap?pool_id=${poolId}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<HeatmapData>(response);
	}

	async getDailySummary(poolId: number, startDate?: string, endDate?: string): Promise<DailySummary[]> {
		const params = new URLSearchParams({ pool_id: String(poolId) });
		if (startDate) params.append('start_date', startDate);
		if (endDate) params.append('end_date', endDate);

		const response = await fetch(`${API_V1}/analytics/daily-summary?${params}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<DailySummary[]>(response);
	}

	async getTrends(poolId: number, period: 'weekly' | 'monthly' = 'weekly'): Promise<TrendData> {
		const response = await fetch(`${API_V1}/analytics/trends?pool_id=${poolId}&period=${period}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<TrendData>(response);
	}

	async getPeakHours(poolId: number, weekday?: string): Promise<{
		peak_hour: number | null;
		quietest_hour: number | null;
		by_hour: { hour: number; average: number; max: number }[];
	}> {
		const params = new URLSearchParams({ pool_id: String(poolId) });
		if (weekday) params.append('weekday', weekday);

		const response = await fetch(`${API_V1}/analytics/peak-hours?${params}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse(response);
	}

	async getWeekdayAverageUpToNow(poolId: number): Promise<WeekdayAverageUpToNow> {
		const response = await fetch(`${API_V1}/analytics/weekday-average-now?pool_id=${poolId}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<WeekdayAverageUpToNow>(response);
	}

	async getVisitorsPaginated(params?: {
		pool_id?: number;
		start_date?: string;
		end_date?: string;
		weekday?: string;
		limit?: number;
		offset?: number;
	}): Promise<PaginatedVisitorResponse> {
		const searchParams = new URLSearchParams();
		if (params) {
			Object.entries(params).forEach(([key, value]) => {
				if (value !== undefined) searchParams.append(key, String(value));
			});
		}
		const response = await fetch(`${API_V1}/visitors/paginated?${searchParams}`, {
			headers: this.getHeaders()
		});
		return this.handleResponse<PaginatedVisitorResponse>(response);
	}
}

export const api = new ApiClient();
