import { create } from 'zustand';
import { persist } from 'zustand/middleware';
type User = { id: string; full_name: string; email: string; avatar_url?: string };
type Org = { id: string; name: string; mode: 'basic' | 'advanced' | 'industrial'; slug: string };
export const useAuthStore = create<{ user: User | null; org: Org | null; token: string | null; capabilities: string[]; setAuth: (user: User, org: Org, token: string, caps: string[]) => void; clearAuth: () => void }>()(persist((set) => ({ user: null, org: null, token: null, capabilities: [], setAuth: (user, org, token, capabilities) => set({ user, org, token, capabilities }), clearAuth: () => set({ user: null, org: null, token: null, capabilities: [] }) }), { name: 'crm-auth' }));
