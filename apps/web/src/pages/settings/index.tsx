import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Users, GitBranch, Shield } from 'lucide-react';
import { api } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/PageHeader';
import { Button } from '../../shared/ui/Button';
import { Badge } from '../../shared/ui/Badge';
import { Skeleton } from '../../shared/ui/Skeleton';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';

const SECTIONS = [
  { key: 'organization', label: 'Организация', icon: <Building2 size={16}/> },
  { key: 'team', label: 'Команда', icon: <Users size={16}/> },
  { key: 'pipelines', label: 'Воронки', icon: <GitBranch size={16}/> },
  { key: 'mode', label: 'Режим CRM', icon: <Shield size={16}/> },
];

const MODE_LABELS: Record<string, string> = {
  basic: 'Базовый', advanced: 'Продвинутый', industrial: 'Промышленный',
};
const MODE_COLORS: Record<string, string> = {
  basic: '#3B82F6', advanced: '#D97706', industrial: '#8B5CF6',
};

interface OrgData { id: string; name: string; mode: string; industry: string; company_size: string; timezone: string; currency: string; }
interface UserItem { id: string; full_name: string; email: string; status: string; }

function OrgSection() {
  const qc = useQueryClient();
  const { data: org } = useQuery<OrgData>({ queryKey: ['organization'], queryFn: () => api.get('/organization/') });
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<Partial<OrgData>>();
  const mutation = useMutation({
    mutationFn: (d: Partial<OrgData>) => api.patch('/organization/', d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['organization'] }); toast.success('Сохранено'); },
  });
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {['name', 'timezone', 'currency'].map(field => (
        <div key={field} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <label style={{ fontSize: 12, fontWeight: 500, color: 'var(--color-text-secondary)', textTransform: 'capitalize' }}>{field}</label>
          <input {...register(field as keyof OrgData)} defaultValue={(org as any)?.[field] ?? ''} className="crm-input"/>
        </div>
      ))}
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button loading={isSubmitting} onClick={handleSubmit(d => mutation.mutate(d))}>Сохранить</Button>
      </div>
    </div>
  );
}

function TeamSection() {
  const { data, isLoading } = useQuery<{ results: UserItem[] }>({ queryKey: ['users'], queryFn: () => api.get('/users/') });
  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-end' }}>
        <Button size="sm">+ Пригласить</Button>
      </div>
      <div style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        {isLoading ? [1, 2, 3].map(i => <div key={i} style={{ padding: '12px 16px', borderBottom: '1px solid var(--color-border)' }}><Skeleton height={14} width="50%"/></div>)
          : (data?.results ?? []).map(user => (
            <div key={user.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', borderBottom: '1px solid var(--color-border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 32, height: 32, borderRadius: 'var(--radius-full)', background: 'var(--color-amber-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, color: 'var(--color-amber)' }}>
                  {user.full_name.charAt(0)}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 500 }}>{user.full_name}</div>
                  <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>{user.email}</div>
                </div>
              </div>
              <Badge bg={user.status === 'active' ? '#D1FAE5' : '#F3F4F6'} color={user.status === 'active' ? '#065F46' : '#6B7280'}>
                {user.status === 'active' ? 'Активен' : 'Неактивен'}
              </Badge>
            </div>
          ))
        }
      </div>
    </div>
  );
}

function ModeSection() {
  const { data: org } = useQuery<OrgData>({ queryKey: ['organization'], queryFn: () => api.get('/organization/') });
  const qc = useQueryClient();
  const mutation = useMutation({
    mutationFn: (mode: string) => api.patch('/organization/mode/', { mode }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['organization'] }); toast.success('Режим изменён'); },
  });
  const modes = ['basic', 'advanced', 'industrial'] as const;
  return (
    <div>
      <p style={{ fontSize: 13, color: 'var(--color-text-secondary)', marginBottom: 16 }}>
        Режим определяет набор доступных функций и сложность интерфейса.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {modes.map(m => (
          <motion.button
            key={m}
            whileHover={{ scale: 1.01 }}
            onClick={() => mutation.mutate(m)}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '14px 18px', borderRadius: 'var(--radius-md)', cursor: 'pointer',
              border: `2px solid ${org?.mode === m ? MODE_COLORS[m] : 'var(--color-border)'}`,
              background: org?.mode === m ? `${MODE_COLORS[m]}08` : 'var(--color-bg-elevated)',
              fontFamily: 'var(--font-body)', transition: 'all var(--transition-fast)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 8, height: 8, borderRadius: 'var(--radius-full)', background: MODE_COLORS[m] }}/>
              <span style={{ fontSize: 13, fontWeight: 600 }}>{MODE_LABELS[m]}</span>
            </div>
            {org?.mode === m && <span style={{ fontSize: 11, color: MODE_COLORS[m], fontWeight: 600 }}>Текущий</span>}
          </motion.button>
        ))}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState('organization');

  return (
    <div style={{ maxWidth: 860 }}>
      <PageHeader title="Настройки" subtitle="Управление организацией и системой" />

      <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: 20 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {SECTIONS.map(sec => (
            <button
              key={sec.key}
              onClick={() => setActiveSection(sec.key)}
              style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '9px 12px', borderRadius: 'var(--radius-md)',
                border: 'none', cursor: 'pointer', textAlign: 'left',
                fontFamily: 'var(--font-body)', fontSize: 13, fontWeight: 500,
                background: activeSection === sec.key ? 'var(--color-amber-subtle)' : 'transparent',
                color: activeSection === sec.key ? 'var(--color-amber-dark)' : 'var(--color-text-secondary)',
                transition: 'all var(--transition-fast)',
              }}
            >
              <span style={{ color: activeSection === sec.key ? 'var(--color-amber)' : 'var(--color-text-muted)' }}>{sec.icon}</span>
              {sec.label}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '24px' }}
          >
            {activeSection === 'organization' && <OrgSection />}
            {activeSection === 'team' && <TeamSection />}
            {activeSection === 'mode' && <ModeSection />}
            {activeSection === 'pipelines' && (
              <div style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
                Управление воронками будет добавлено в следующем обновлении.
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
