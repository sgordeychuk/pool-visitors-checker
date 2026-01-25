import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { api, type User } from '$lib/api';

interface AuthState {
	user: User | null;
	loading: boolean;
	error: string | null;
}

function createAuthStore() {
	const { subscribe, set, update } = writable<AuthState>({
		user: null,
		loading: true,
		error: null
	});

	return {
		subscribe,

		async init() {
			if (!browser) {
				update((state) => ({ ...state, loading: false }));
				return;
			}

			const token = localStorage.getItem('access_token');
			if (!token) {
				update((state) => ({ ...state, loading: false }));
				return;
			}

			try {
				const user = await api.getCurrentUser();
				set({ user, loading: false, error: null });
			} catch (error) {
				localStorage.removeItem('access_token');
				localStorage.removeItem('refresh_token');
				set({ user: null, loading: false, error: null });
			}
		},

		async login(username: string, password: string) {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				const tokens = await api.login(username, password);
				localStorage.setItem('access_token', tokens.access_token);
				localStorage.setItem('refresh_token', tokens.refresh_token);

				const user = await api.getCurrentUser();
				set({ user, loading: false, error: null });
				return true;
			} catch (error) {
				set({ user: null, loading: false, error: error instanceof Error ? error.message : 'Login failed' });
				return false;
			}
		},

		async register(email: string, username: string, password: string) {
			update((state) => ({ ...state, loading: true, error: null }));
			try {
				await api.register(email, username, password);
				// After registration, log in automatically
				return await this.login(username, password);
			} catch (error) {
				set({ user: null, loading: false, error: error instanceof Error ? error.message : 'Registration failed' });
				return false;
			}
		},

		logout() {
			if (browser) {
				localStorage.removeItem('access_token');
				localStorage.removeItem('refresh_token');
			}
			set({ user: null, loading: false, error: null });
		},

		clearError() {
			update((state) => ({ ...state, error: null }));
		}
	};
}

export const auth = createAuthStore();
export const isAuthenticated = derived(auth, ($auth) => $auth.user !== null);
export const isAdmin = derived(auth, ($auth) => $auth.user?.is_superuser ?? false);
export const currentUser = derived(auth, ($auth) => $auth.user);
