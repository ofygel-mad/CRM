import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';

type Role = 'owner' | 'admin' | 'manager' | 'viewer';

export function useRole() {
  const { data } = useQuery({
    queryKey: ['me'],
    queryFn: () => api.get('/users/me/'),
    staleTime: 5 * 60 * 1000,
  });

  const role: Role = (data as any)?.role ?? 'viewer';

  const isOwner = role === 'owner';
  const isAdmin = role === 'owner' || role === 'admin';
  const isManager = isAdmin || role === 'manager';

  return { role, isOwner, isAdmin, isManager };
}
