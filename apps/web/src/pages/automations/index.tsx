import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Zap, Plus, Play, Pause } from 'lucide-react';
import { api } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/PageHeader';
import { Button } from '../../shared/ui/Button';
import { Badge } from '../../shared/ui/Badge';
import { EmptyState } from '../../shared/ui/EmptyState';
import { Skeleton } from '../../shared/ui/Skeleton';
import { toast } from 'sonner';
import { useCapabilities } from '../../shared/hooks/useCapabilities';

interface AutomationRule {
  id: string; name: string; description: string;
  trigger_type: string; status: string;
  is_template_based: boolean;
  created_at: string;
}

interface Template {
  code: string; name: string; description: string; trigger_type: string;
}

const TRIGGER_LABELS: Record<string, string> = {
  'customer.created': 'Новый клиент',
  'deal.created': 'Новая сделка',
  'deal.stage_changed': 'Смена этапа',
  'task.completed': 'Задача выполнена',
  'task.created': 'Новая задача',
};

const STATUS_MAP: Record<string, { bg: string; color: string; label: string }> = {
  active: { bg: '#D1FAE5', color: '#065F46', label: 'Активна' },
  paused: { bg: '#FEF3C7', color: '#92400E', label: 'Пауза' },
  draft: { bg: '#F3F4F6', color: '#6B7280', label: 'Черновик' },
  archived: { bg: '#F3F4F6', color: '#9CA3AF', label: 'Архив' },
};

const BUILT_IN_TEMPLATES: Template[] = [
  { code: 'new_lead_task', name: 'Задача при новом лиде', description: 'Создать задачу менеджеру при появлении нового клиента', trigger_type: 'customer.created' },
  { code: 'deal_stage_notify', name: 'Уведомление при смене этапа', description: 'Уведомить ответственного при переходе сделки на новый этап', trigger_type: 'deal.stage_changed' },
  { code: 'overdue_reminder', name: 'Напоминание о просроченной', description: 'Создать задачу если сделка без активности 3 дня', trigger_type: 'deal.created' },
  { code: 'won_deal_note', name: 'Заметка при выигрыше сделки', description: 'Автоматически добавить заметку при переводе в "Выиграно"', trigger_type: 'deal.stage_changed' },
];

export default function AutomationsPage() {
  const { can } = useCapabilities();
  const qc = useQueryClient();
  const [showTemplates, setShowTemplates] = useState(false);

  const { data, isLoading } = useQuery<{ results: AutomationRule[] }>({
    queryKey: ['automations'],
    queryFn: () => api.get('/automations/'),
  });

  const toggleMutation = useMutation({
    mutationFn: (id: string) => api.post(`/automations/${id}/toggle/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['automations'] }); toast.success('Статус изменён'); },
  });

  const createFromTemplate = useMutation({
    mutationFn: (template: Template) => api.post('/automations/', {
      name: template.name,
      description: template.description,
      trigger_type: template.trigger_type,
      is_template_based: true,
      template_code: template.code,
      status: 'active',
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['automations'] });
      toast.success('Автоматизация создана');
      setShowTemplates(false);
    },
  });

  if (!can('automations.manage')) {
    return (
      <EmptyState
        icon={<Zap size={22}/>}
        title="Автоматизации недоступны"
        subtitle="Обновите режим CRM до Продвинутого или Промышленного"
        action={<Button size="sm" onClick={() => {}}>Обновить режим</Button>}
      />
    );
  }

  return (
    <div style={{ maxWidth: 900 }}>
      <PageHeader
        title="Автоматизации"
        subtitle="Правила для автоматической обработки событий"
        actions={
          <div style={{ display: 'flex', gap: 8 }}>
            <Button variant="secondary" size="sm" onClick={() => setShowTemplates(true)}>
              Из шаблона
            </Button>
            <Button size="sm" icon={<Plus size={13}/>}>Создать правило</Button>
          </div>
        }
      />

      {showTemplates && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ background: 'var(--color-amber-subtle)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: '20px', marginBottom: 20 }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600 }}>Готовые шаблоны</h3>
            <button onClick={() => setShowTemplates(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)', fontFamily: 'var(--font-body)' }}>✕</button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
            {BUILT_IN_TEMPLATES.map(tpl => (
              <motion.div key={tpl.code} whileHover={{ scale: 1.01 }}
                style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 3 }}>{tpl.name}</div>
                  <div style={{ fontSize: 12, color: 'var(--color-text-secondary)' }}>{tpl.description}</div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 11, color: 'var(--color-amber)', fontWeight: 500, background: 'var(--color-amber-light)', padding: '2px 8px', borderRadius: 'var(--radius-full)' }}>
                    {TRIGGER_LABELS[tpl.trigger_type] ?? tpl.trigger_type}
                  </span>
                  <Button size="xs" loading={createFromTemplate.isPending} onClick={() => createFromTemplate.mutate(tpl)}>
                    Добавить
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      <div style={{ background: 'var(--color-bg-elevated)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        {isLoading
          ? [1,2,3].map(i => <div key={i} style={{ padding: '14px 18px', borderBottom: '1px solid var(--color-border)' }}><Skeleton height={14} width="50%"/></div>)
          : (data?.results ?? []).length === 0
            ? <EmptyState icon={<Zap size={20}/>} title="Автоматизаций нет" subtitle="Создайте из шаблона или настройте своё правило"
                action={<Button size="sm" onClick={() => setShowTemplates(true)}>Из шаблона</Button>} />
            : (data?.results ?? []).map((rule, idx) => {
                const sm = STATUS_MAP[rule.status] ?? STATUS_MAP.draft;
                return (
                  <motion.div key={rule.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.05 }}
                    style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px', borderBottom: '1px solid var(--color-border)' }}>
                    <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: rule.status === 'active' ? '#D1FAE5' : 'var(--color-bg-muted)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Zap size={16} color={rule.status === 'active' ? '#10B981' : 'var(--color-text-muted)'}/>
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 500 }}>{rule.name}</div>
                      <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>
                        Триггер: {TRIGGER_LABELS[rule.trigger_type] ?? rule.trigger_type}
                      </div>
                    </div>
                    <Badge bg={sm.bg} color={sm.color}>{sm.label}</Badge>
                    <Button
                      variant="ghost" size="xs"
                      icon={rule.status === 'active' ? <Pause size={13}/> : <Play size={13}/>}
                      onClick={() => toggleMutation.mutate(rule.id)}
                    >
                      {rule.status === 'active' ? 'Стоп' : 'Старт'}
                    </Button>
                  </motion.div>
                );
              })
        }
      </div>
    </div>
  );
}
