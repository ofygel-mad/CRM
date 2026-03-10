import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Users, Briefcase, CheckSquare, TrendingUp, Plus, ArrowRight, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../shared/api/client';
import { useAuthStore } from '../../shared/stores/auth';
import { Button } from '../../shared/ui/Button';
import { Skeleton } from '../../shared/ui/Skeleton';
import { Badge } from '../../shared/ui/Badge';

interface DashboardData {
  customers_count:    number;
  customers_delta:    number;
  active_deals_count: number;
  revenue_month:      number;
  tasks_today:        number;
  overdue_tasks:      number;
  recent_customers:   Array<{ id:string; full_name:string; company_name:string; status:string; created_at:string }>;
}

const STATUS_COLORS: Record<string, { bg: string; color: string }> = {
  new:      { bg:'#DBEAFE', color:'#1D4ED8' },
  active:   { bg:'#D1FAE5', color:'#065F46' },
  inactive: { bg:'#F3F4F6', color:'#6B7280' },
  archived: { bg:'#F3F4F6', color:'#9CA3AF' },
};

const STATUS_LABELS: Record<string, string> = {
  new:'Новый', active:'Активный', inactive:'Неактивный', archived:'Архив',
};

const stagger = { hidden:{}, show:{ transition:{ staggerChildren:0.06 } } };
const item    = { hidden:{ opacity:0, y:10 }, show:{ opacity:1, y:0, transition:{ type:'spring', stiffness:500, damping:35 } } };

function StatCard({ label, value, delta, icon, colorAccent, format='number', loading }: {
  label:string; value:number; delta?:number; icon:React.ReactNode;
  colorAccent:string; format?:'number'|'currency'; loading?:boolean;
}) {
  const fmt = (n: number) =>
    format === 'currency'
      ? new Intl.NumberFormat('ru-RU', { style:'currency', currency:'RUB', maximumFractionDigits:0 }).format(n)
      : n.toLocaleString('ru-RU');

  return (
    <div style={{
      background:'var(--color-bg-elevated)',
      border:'1px solid var(--color-border)',
      borderRadius:'var(--radius-lg)',
      padding:'20px',
      display:'flex',
      flexDirection:'column',
      gap:12,
    }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
        <div style={{
          width:36, height:36,
          background:`${colorAccent}15`,
          borderRadius:'var(--radius-md)',
          display:'flex', alignItems:'center', justifyContent:'center',
          color:colorAccent,
        }}>
          {icon}
        </div>
        {delta !== undefined && delta !== 0 && (
          <span style={{ fontSize:12, color:delta>0?'#10B981':'#EF4444', fontWeight:500 }}>
            {delta>0?'+':''}{delta}
          </span>
        )}
      </div>
      {loading ? <Skeleton height={28} width={80} /> : (
        <div style={{ fontSize:24, fontWeight:700, fontFamily:'var(--font-display)' }}>{fmt(value)}</div>
      )}
      <div style={{ fontSize:12, color:'var(--color-text-muted)' }}>{label}</div>
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const user     = useAuthStore(s => s.user);
  const hour     = new Date().getHours();
  const greeting = hour<12?'Доброе утро':hour<18?'Добрый день':'Добрый вечер';

  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard-summary'],
    queryFn:  () => api.get('/reports/dashboard'),
  });

  return (
    <div style={{ maxWidth:1100 }}>
      {/* Header */}
      <div style={{ display:'flex', alignItems:'flex-start', justifyContent:'space-between', marginBottom:28 }}>
        <div>
          <p style={{ fontSize:13, color:'var(--color-text-muted)', margin:0 }}>{greeting},</p>
          <h1 style={{ fontSize:26, fontWeight:700, fontFamily:'var(--font-display)', margin:'4px 0 0' }}>
            {user?.full_name?.split(' ')[0] ?? 'пользователь'} 👋
          </h1>
        </div>
        <div style={{ display:'flex', gap:8 }}>
          <Button variant="secondary" size="sm" icon={<Plus size={14} />} onClick={() => navigate('/customers')}>
            Клиент
          </Button>
          <Button size="sm" icon={<Plus size={14} />} onClick={() => navigate('/deals')}>
            Сделка
          </Button>
        </div>
      </div>

      {/* Stats */}
      <motion.div
        variants={stagger} initial="hidden" animate="show"
        style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:12, marginBottom:24 }}
      >
        {[
          { label:'Клиентов всего',    value:data?.customers_count??0,    delta:data?.customers_delta,  icon:<Users size={17}/>,       colorAccent:'#3B82F6' },
          { label:'Активных сделок',   value:data?.active_deals_count??0, icon:<Briefcase size={17}/>,  colorAccent:'#D97706' },
          { label:'Задач сегодня',     value:data?.tasks_today??0,        icon:<CheckSquare size={17}/>, colorAccent:'#10B981' },
          { label:'Выручка месяца',    value:data?.revenue_month??0,      icon:<TrendingUp size={17}/>, colorAccent:'#8B5CF6', format:'currency' as const },
        ].map(stat => (
          <motion.div key={stat.label} variants={item}>
            <StatCard {...stat} loading={isLoading} />
          </motion.div>
        ))}
      </motion.div>

      {/* Overdue warning */}
      {(data?.overdue_tasks ?? 0) > 0 && (
        <motion.div
          initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }}
          style={{
            display:'flex', alignItems:'center', gap:10,
            padding:'12px 16px', marginBottom:20,
            background:'#FEF3C7', borderRadius:'var(--radius-md)',
            border:'1px solid #FDE68A',
          }}
        >
          <AlertTriangle size={16} color="#D97706" />
          <span style={{ fontSize:13, color:'#92400E', fontWeight:500 }}>
            У вас {data!.overdue_tasks} просроченных задач
          </span>
          <button
            onClick={() => navigate('/tasks')}
            style={{ marginLeft:'auto', fontSize:12, color:'#D97706', fontWeight:600, background:'none', border:'none', cursor:'pointer' }}
          >
            Посмотреть →
          </button>
        </motion.div>
      )}

      {/* Bottom grid */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:16 }}>
        {/* Recent customers */}
        <div style={{
          background:'var(--color-bg-elevated)', border:'1px solid var(--color-border)',
          borderRadius:'var(--radius-lg)', padding:'0',
          overflow:'hidden',
        }}>
          <div style={{
            display:'flex', alignItems:'center', justifyContent:'space-between',
            padding:'16px 20px', borderBottom:'1px solid var(--color-border)',
          }}>
            <span style={{ fontSize:14, fontWeight:600 }}>Последние клиенты</span>
            <button
              onClick={() => navigate('/customers')}
              style={{ fontSize:12, color:'var(--color-amber)', fontWeight:500, background:'none', border:'none', cursor:'pointer', display:'flex', alignItems:'center', gap:4 }}
            >
              Все <ArrowRight size={12} />
            </button>
          </div>
          <div>
            {isLoading
              ? [1,2,3,4,5].map(i => (
                  <div key={i} style={{ padding:'12px 20px', borderBottom:'1px solid var(--color-border)' }}>
                    <Skeleton height={14} width="60%" />
                  </div>
                ))
              : (data?.recent_customers ?? []).map((c, idx) => {
                  const sc = STATUS_COLORS[c.status] ?? STATUS_COLORS.new;
                  return (
                    <motion.div
                      key={c.id}
                      initial={{ opacity:0, x:-6 }} animate={{ opacity:1, x:0 }}
                      transition={{ delay: idx * 0.04 }}
                      onClick={() => navigate(`/customers/${c.id}`)}
                      style={{
                        display:'flex', alignItems:'center', justifyContent:'space-between',
                        padding:'11px 20px',
                        borderBottom:'1px solid var(--color-border)',
                        cursor:'pointer',
                        transition:'background var(--transition-fast)',
                      }}
                      whileHover={{ backgroundColor:'var(--color-bg-muted)' }}
                    >
                      <div>
                        <div style={{ fontSize:13, fontWeight:500 }}>{c.full_name}</div>
                        {c.company_name && <div style={{ fontSize:11, color:'var(--color-text-muted)' }}>{c.company_name}</div>}
                      </div>
                      <Badge bg={sc.bg} color={sc.color}>{STATUS_LABELS[c.status] ?? c.status}</Badge>
                    </motion.div>
                  );
                })
            }
          </div>
        </div>

        {/* Quick actions */}
        <div style={{
          background:'var(--color-bg-elevated)', border:'1px solid var(--color-border)',
          borderRadius:'var(--radius-lg)', padding:'16px 20px',
        }}>
          <p style={{ fontSize:14, fontWeight:600, marginBottom:16 }}>Быстрые действия</p>
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {[
              { label:'Добавить клиента',  path:'/customers',   icon:<Users size={15}/> },
              { label:'Создать сделку',    path:'/deals',       icon:<Briefcase size={15}/> },
              { label:'Новая задача',      path:'/tasks',       icon:<CheckSquare size={15}/> },
              { label:'Импорт клиентов',   path:'/imports',     icon:<TrendingUp size={15}/> },
            ].map(action => (
              <motion.button
                key={action.path}
                whileHover={{ x:3 }}
                whileTap={{ scale:0.98 }}
                onClick={() => navigate(action.path)}
                style={{
                  display:'flex', alignItems:'center', gap:10,
                  padding:'10px 14px',
                  background:'var(--color-bg-muted)',
                  border:'1px solid var(--color-border)',
                  borderRadius:'var(--radius-md)',
                  cursor:'pointer', fontSize:13, fontWeight:500,
                  color:'var(--color-text-primary)',
                  fontFamily:'var(--font-body)',
                  textAlign:'left',
                  transition:'border-color var(--transition-fast)',
                }}
              >
                <span style={{ color:'var(--color-amber)' }}>{action.icon}</span>
                {action.label}
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
