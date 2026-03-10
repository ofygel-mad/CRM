import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Plus, User } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../shared/api/client';
import type { Customer } from '../../entities/customer/model/types';
import { STATUS_LABELS, STATUS_COLORS } from '../../entities/customer/model/types';
import { PageHeader } from '../../shared/ui/PageHeader';
import { Button } from '../../shared/ui/Button';
import { SearchInput } from '../../shared/ui/SearchInput';
import { Badge } from '../../shared/ui/Badge';
import { Skeleton } from '../../shared/ui/Skeleton';
import { Drawer } from '../../shared/ui/Drawer';
import { EmptyState } from '../../shared/ui/EmptyState';
import { useDebounce } from '../../shared/hooks/useDebounce';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';

function Field({ label, children }: { label:string; children:React.ReactNode }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
      <label style={{ fontSize:12, fontWeight:500, color:'var(--color-text-secondary)' }}>{label}</label>
      {children}
    </div>
  );
}

function Input({ ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      style={{
        height:36, padding:'0 12px',
        border:'1px solid var(--color-border)',
        borderRadius:'var(--radius-md)',
        background:'var(--color-bg-elevated)',
        fontSize:13, color:'var(--color-text-primary)',
        fontFamily:'var(--font-body)', outline:'none',
        ...props.style,
      }}
    />
  );
}

export default function CustomersPage() {
  const navigate = useNavigate();
  const qc       = useQueryClient();
  const [search, setSearch]     = useState('');
  const [drawerOpen, setDrawer] = useState(false);
  const debouncedSearch         = useDebounce(search, 300);

  const { data, isLoading } = useQuery<{ results:Customer[]; count:number }>({
    queryKey: ['customers', debouncedSearch],
    queryFn:  () => api.get('/customers/', { search:debouncedSearch }),
  });

  const { register, handleSubmit, reset, formState:{ isSubmitting } } = useForm<{
    full_name:string; phone?:string; email?:string; company_name?:string; source?:string;
  }>();

  const createMutation = useMutation({
    mutationFn: (data: object) => api.post('/customers/', data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey:['customers'] });
      toast.success('Клиент создан');
      setDrawer(false);
      reset();
    },
    onError: () => toast.error('Ошибка при создании'),
  });

  return (
    <div>
      <PageHeader
        title="Клиенты"
        subtitle={data ? `${data.count} всего` : undefined}
        actions={<Button icon={<Plus size={15}/>} onClick={()=>setDrawer(true)}>Добавить клиента</Button>}
      />

      <div style={{ marginBottom:16 }}>
        <SearchInput value={search} onChange={setSearch} placeholder="Поиск по имени, телефону, email..." />
      </div>

      {/* Table */}
      <div style={{ background:'var(--color-bg-elevated)', border:'1px solid var(--color-border)', borderRadius:'var(--radius-lg)', overflow:'hidden' }}>
        {/* Head */}
        <div style={{
          display:'grid', gridTemplateColumns:'2fr 1.5fr 1.5fr 1fr 1fr',
          padding:'10px 16px', borderBottom:'1px solid var(--color-border)',
          fontSize:11, fontWeight:600, color:'var(--color-text-muted)',
          textTransform:'uppercase', letterSpacing:'0.05em',
          background:'var(--color-bg-muted)',
        }}>
          <span>Имя</span><span>Телефон</span><span>Email</span><span>Статус</span><span>Добавлен</span>
        </div>

        {isLoading
          ? [1,2,3,4,5,6].map(i => (
              <div key={i} style={{ display:'grid', gridTemplateColumns:'2fr 1.5fr 1.5fr 1fr 1fr', padding:'13px 16px', borderBottom:'1px solid var(--color-border)', gap:12 }}>
                <Skeleton height={14} width="70%" /><Skeleton height={14} width="60%" /><Skeleton height={14} width="80%" /><Skeleton height={16} width={60} radius="var(--radius-full)" /><Skeleton height={14} width={60} />
              </div>
            ))
          : data?.results.length === 0
            ? <EmptyState icon={<User size={22}/>} title="Клиентов пока нет" subtitle="Добавьте первого клиента или импортируйте из Excel" action={<Button size="sm" icon={<Plus size={14}/>} onClick={()=>setDrawer(true)}>Добавить</Button>} />
            : data?.results.map((c, idx) => {
                const sc = STATUS_COLORS[c.status];
                return (
                  <motion.div
                    key={c.id}
                    initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:idx*0.03 }}
                    onClick={() => navigate(`/customers/${c.id}`)}
                    whileHover={{ backgroundColor:'var(--color-bg-muted)' }}
                    style={{
                      display:'grid', gridTemplateColumns:'2fr 1.5fr 1.5fr 1fr 1fr',
                      padding:'12px 16px', borderBottom:'1px solid var(--color-border)',
                      cursor:'pointer', fontSize:13, alignItems:'center',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight:500 }}>{c.full_name}</div>
                      {c.company_name && <div style={{ fontSize:11, color:'var(--color-text-muted)' }}>{c.company_name}</div>}
                    </div>
                    <span style={{ color:'var(--color-text-secondary)' }}>{c.phone || '—'}</span>
                    <span style={{ color:'var(--color-text-secondary)' }}>{c.email || '—'}</span>
                    <Badge bg={sc.bg} color={sc.color}>{STATUS_LABELS[c.status]}</Badge>
                    <span style={{ color:'var(--color-text-muted)', fontSize:12 }}>
                      {new Date(c.created_at).toLocaleDateString('ru-RU')}
                    </span>
                  </motion.div>
                );
              })
        }
      </div>

      {/* Create Drawer */}
      <Drawer
        open={drawerOpen}
        onClose={() => { setDrawer(false); reset(); }}
        title="Новый клиент"
        subtitle="Заполните основные данные"
        footer={
          <div style={{ display:'flex', gap:8, justifyContent:'flex-end' }}>
            <Button variant="secondary" onClick={() => { setDrawer(false); reset(); }}>Отмена</Button>
            <Button loading={isSubmitting} onClick={handleSubmit(d => createMutation.mutate(d))}>Создать</Button>
          </div>
        }
      >
        <form onSubmit={handleSubmit(d => createMutation.mutate(d))} style={{ display:'flex', flexDirection:'column', gap:16 }}>
          <Field label="Имя *">
            <Input {...register('full_name', { required:true })} placeholder="Иван Иванов" />
          </Field>
          <Field label="Телефон">
            <Input {...register('phone')} placeholder="+7 700 000 00 00" />
          </Field>
          <Field label="Email">
            <Input {...register('email')} type="email" placeholder="ivan@company.kz" />
          </Field>
          <Field label="Компания">
            <Input {...register('company_name')} placeholder="ТОО Компания" />
          </Field>
          <Field label="Источник">
            <Input {...register('source')} placeholder="Instagram, Referral..." />
          </Field>
        </form>
      </Drawer>
    </div>
  );
}
