import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { TrendingUp, Users, Briefcase, CheckSquare, Calendar } from 'lucide-react';
import { api } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/PageHeader';
import { Skeleton } from '../../shared/ui/Skeleton';
import { Button } from '../../shared/ui/Button';

interface ReportData {
  customers_count: number; customers_delta: number;
  active_deals_count: number; revenue_month: number; revenue_delta: number;
  tasks_today: number; overdue_tasks: number;
  deals_by_stage: Array<{ stage: string; count: number; amount: number }>;
  customers_by_source: Array<{ source: string; count: number }>;
  recent_activity_count: number;
}

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 500, damping: 35 } } };

function MetricCard({ label, value, delta, icon, color, format: fmt = 'number' }: {
  label: string; value: number; delta?: number; icon: React.ReactNode; color: string; format?: 'number' | 'currency';
}) {
  const formatted = fmt === 'currency'
    ? new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(value)
    : value.toLocaleString('ru-RU');

  return (
    <div style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '20px', boxShadow: 'var(--shadow-xs)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ width: 38, height: 38, borderRadius: 'var(--radius-md)', background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center', color }}>{icon}</div>
        {delta !== undefined && delta !== 0 && (
          <span style={{ fontSize: 12, color: delta > 0 ? '#10B981' : '#EF4444', fontWeight: 600, background: delta > 0 ? '#D1FAE5' : '#FEE2E2', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
            {delta > 0 ? '+' : ''}{delta}%
          </span>
        )}
      </div>
      <div style={{ fontSize: 26, fontWeight: 800, fontFamily: 'var(--font-display)', marginBottom: 4 }}>{formatted}</div>
      <div style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>{label}</div>
    </div>
  );
}

function BarRow({ label, value, maxValue, color }: { label: string; value: number; maxValue: number; color: string }) {
  const pct = maxValue > 0 ? (value / maxValue) * 100 : 0;
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
      <div style={{ width: 110, fontSize: 12, color: 'var(--color-text-secondary)', flexShrink: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{label || 'Не указан'}</div>
      <div style={{ flex: 1, height: 8, background: 'var(--color-bg-muted)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
        <motion.div initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 0.7, ease: 'easeOut' }}
          style={{ height: '100%', background: color, borderRadius: 'var(--radius-full)' }} />
      </div>
      <div style={{ width: 32, fontSize: 12, fontWeight: 600, textAlign: 'right', flexShrink: 0 }}>{value}</div>
    </div>
  );
}

export default function ReportsPage() {
  const { data, isLoading } = useQuery<ReportData>({
    queryKey: ['reports-full'],
    queryFn: () => api.get('/reports/dashboard'),
  });

  const maxDealsAmount = Math.max(...(data?.deals_by_stage.map(d => d.amount) ?? [1]));
  const maxSourceCount = Math.max(...(data?.customers_by_source.map(s => s.count) ?? [1]));

  return (
    <div style={{ maxWidth: 1100 }}>
      <PageHeader
        title="Отчёты"
        subtitle="Аналитика вашего бизнеса"
        actions={<Button variant="secondary" size="sm" icon={<Calendar size={13}/>}>Период: Месяц</Button>}
      />

      <motion.div variants={stagger} initial="hidden" animate="show"
        style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 24 }}>
        {[
          { label: 'Клиентов', value: data?.customers_count ?? 0, delta: data?.customers_delta, icon: <Users size={17}/>, color: '#3B82F6' },
          { label: 'Активных сделок', value: data?.active_deals_count ?? 0, icon: <Briefcase size={17}/>, color: '#D97706' },
          { label: 'Задач сегодня', value: data?.tasks_today ?? 0, icon: <CheckSquare size={17}/>, color: '#10B981' },
          { label: 'Выручка, мес.', value: data?.revenue_month ?? 0, delta: data?.revenue_delta, icon: <TrendingUp size={17}/>, color: '#8B5CF6', format: 'currency' as const },
        ].map(stat => (
          <motion.div key={stat.label} variants={item}>
            {isLoading ? <div style={{ height: 100, background: 'var(--color-bg-elevated)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}><Skeleton height="100%" /></div>
              : <MetricCard {...stat} />}
          </motion.div>
        ))}
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '20px' }}>
          <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Briefcase size={15} color="var(--color-amber)"/> Сделки по этапам
          </div>
          {isLoading
            ? [1,2,3,4].map(i => <Skeleton key={i} height={16} style={{ marginBottom: 12 }}/>)
            : (data?.deals_by_stage ?? []).map(stage => (
                <BarRow key={stage.stage} label={stage.stage} value={stage.amount} maxValue={maxDealsAmount} color="var(--color-amber)" />
              ))
          }
        </div>

        <div style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '20px' }}>
          <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Users size={15} color="#3B82F6"/> Клиенты по источникам
          </div>
          {isLoading
            ? [1,2,3,4].map(i => <Skeleton key={i} height={16} style={{ marginBottom: 12 }}/>)
            : (data?.customers_by_source ?? []).map(src => (
                <BarRow key={src.source} label={src.source} value={src.count} maxValue={maxSourceCount} color="#3B82F6" />
              ))
          }
        </div>
      </div>
    </div>
  );
}
