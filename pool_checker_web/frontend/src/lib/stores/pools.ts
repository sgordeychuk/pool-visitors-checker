import { writable, derived } from 'svelte/store';
import { api, type Pool, type LatestVisitor } from '$lib/api';

interface PoolsState {
	pools: Pool[];
	latestVisitors: LatestVisitor[];
	selectedPoolId: number | null;
	loading: boolean;
	error: string | null;
}

function createPoolsStore() {
	const { subscribe, set, update } = writable<PoolsState>({
		pools: [],
		latestVisitors: [],
		selectedPoolId: null,
		loading: false,
		error: null
	});

	return {
		subscribe,

		async loadPools() {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const pools = await api.getPools();
				update((state) => ({
					...state,
					pools,
					loading: false,
					selectedPoolId: state.selectedPoolId ?? (pools.length > 0 ? pools[0].id : null)
				}));
			} catch (error) {
				update((state) => ({
					...state,
					loading: false,
					error: error instanceof Error ? error.message : 'Failed to load pools'
				}));
			}
		},

		async loadLatestVisitors() {
			try {
				const latestVisitors = await api.getLatestVisitors();
				update((state) => ({ ...state, latestVisitors }));
			} catch (error) {
				console.error('Failed to load latest visitors:', error);
			}
		},

		selectPool(poolId: number) {
			update((state) => ({ ...state, selectedPoolId: poolId }));
		},

		async createPool(pool: Omit<Pool, 'id' | 'created_at' | 'latest_visitor_count' | 'latest_reading_time' | 'total_records'>) {
			try {
				const newPool = await api.createPool(pool);
				update((state) => ({
					...state,
					pools: [...state.pools, { ...newPool, total_records: 0 }]
				}));
				return newPool;
			} catch (error) {
				throw error;
			}
		},

		async updatePool(id: number, pool: Partial<Pool>) {
			try {
				const updatedPool = await api.updatePool(id, pool);
				update((state) => ({
					...state,
					pools: state.pools.map((p) => (p.id === id ? { ...p, ...updatedPool } : p))
				}));
				return updatedPool;
			} catch (error) {
				throw error;
			}
		},

		async deletePool(id: number) {
			try {
				await api.deletePool(id);
				update((state) => ({
					...state,
					pools: state.pools.filter((p) => p.id !== id),
					selectedPoolId: state.selectedPoolId === id ? (state.pools[0]?.id ?? null) : state.selectedPoolId
				}));
			} catch (error) {
				throw error;
			}
		},

		async triggerScrape(poolId: number) {
			try {
				return await api.triggerScrape(poolId);
			} catch (error) {
				throw error;
			}
		}
	};
}

export const pools = createPoolsStore();
export const selectedPool = derived(pools, ($pools) =>
	$pools.pools.find((p) => p.id === $pools.selectedPoolId) ?? null
);
