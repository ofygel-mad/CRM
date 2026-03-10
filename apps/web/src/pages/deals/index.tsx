import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DndContext, DragOverlay, closestCorners, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { motion } from 'framer-motion';
import { Plus, Briefcase } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/PageHeader';
import { Button } from '../../shared/ui/Button';
import { Skeleton } from '../../shared/ui/Skeleton';
import { EmptyState } from '../../shared/ui/EmptyState';
import { toast } from 'sonner';

interface DealCard {
  id:string; title:string; amount?:number; currency:string; status:string;
  customer:{ id:string; full_name:string; company_name?:string } | null;
  owner:{ id:string; full_name:string } | null;
  stage:{ id:string; name:string; color?:string };
  created_at:string;
}

interface Stage {
  id:string; name:string; type:'open'|'won'|'lost'; color:string;
  deals: DealCard[];
}

interface BoardData {
  pipeline: { id:string; name:string };
  stages: Stage[];
}

function DealCardItem({ deal, isDragging }: { deal:DealCard; isDragging?:boolean }) {
  const navigate = useNavigate();
  const fmt = (n:number) => new Intl.NumberFormat('ru-RU', { maximumFractionDigits:0 }).format(n);

  return (
    <motion.div
      layout
      onClick={() => !isDragging && navigate(`/deals/${deal.id}`)}
      style={{
        background:    'var(--color-bg-elevated)',
        border:        '1px solid var(--color-border)',
        borderRadius:  'var(--radius-md)',
        padding:       '12px',
        cursor:        'pointer',
        boxShadow:     isDragging ? 'var(--shadow-lg)' : 'var(--shadow-xs)',
        opacity:       isDragging ? 0.95 : 1,
        transform:     isDragging ? 'rotate(1.5deg)' : undefined,
      }}
    >
      <div style={{ fontSize:13, fontWeight:500, marginBottom:6 }}>{deal.title}</div>
      {deal.customer && (
        <div style={{ fontSize:12, color:'var(--color-text-muted)', marginBottom:6 }}>
          {deal.customer.full_name}
          {deal.customer.company_name && ` • ${deal.customer.company_name}`}
        </div>
      )}
      {deal.amount && (
        <div style={{ fontSize:14, fontWeight:700, color:'var(--color-amber)', fontFamily:'var(--font-display)' }}>
          {fmt(deal.amount)} {deal.currency === 'RUB' ? '₽' : deal.currency}
        </div>
      )}
    </motion.div>
  );
}

function SortableDealCard({ deal }: { deal:DealCard }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id:deal.id });
  return (
    <div ref={setNodeRef} style={{ transform:CSS.Transform.toString(transform), transition }} {...attributes} {...listeners}>
      <DealCardItem deal={deal} isDragging={isDragging} />
    </div>
  );
}

function KanbanColumn({ stage, isLoading }: { stage:Stage; isLoading?:boolean }) {
  const typeColors: Record<string, { header:string; dot:string }> = {
    open: { header:'var(--color-bg-muted)', dot:'#9CA3AF' },
    won:  { header:'#D1FAE5',              dot:'#10B981' },
    lost: { header:'#FEE2E2',              dot:'#EF4444' },
  };
  const tc = typeColors[stage.type] ?? typeColors.open;
  const total = stage.deals.reduce((sum, d) => sum + (d.amount ?? 0), 0);
  const fmt   = (n:number) => new Intl.NumberFormat('ru-RU', { maximumFractionDigits:0 }).format(n);

  return (
    <div style={{
      width: 272, flexShrink:0,
      display:'flex', flexDirection:'column',
      background:'var(--color-bg-muted)',
      borderRadius:'var(--radius-lg)',
      border:'1px solid var(--color-border)',
      overflow:'hidden',
      maxHeight:'calc(100vh - 160px)',
    }}>
      {/* Column header */}
      <div style={{
        padding:'12px 14px',
        background:tc.header,
        borderBottom:'1px solid var(--color-border)',
      }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:4 }}>
          <span style={{ width:8,height:8,borderRadius:'50%',background:tc.dot,display:'inline-block',flexShrink:0 }} />
          <span style={{ fontSize:13, fontWeight:600, flex:1 }}>{stage.name}</span>
          <span style={{ fontSize:12, color:'var(--color-text-muted)', background:'var(--color-bg-elevated)', padding:'1px 7px', borderRadius:'var(--radius-full)' }}>
            {stage.deals.length}
          </span>
        </div>
        {total > 0 && (
          <div style={{ fontSize:12, color:'var(--color-text-muted)', paddingLeft:16 }}>
            {fmt(total)} ₽
          </div>
        )}
      </div>

      {/* Cards */}
      <div style={{ flex:1, overflowY:'auto', padding:'10px', display:'flex', flexDirection:'column', gap:8 }}>
        <SortableContext items={stage.deals.map(d=>d.id)} strategy={verticalListSortingStrategy}>
          {isLoading
            ? [1,2,3].map(i => <div key={i} style={{ background:'var(--color-bg-elevated)', borderRadius:'var(--radius-md)', padding:12, border:'1px solid var(--color-border)' }}><Skeleton height={14} width="80%" style={{ marginBottom:8 }} /><Skeleton height={12} width="60%" /></div>)
            : stage.deals.length === 0
              ? <div style={{ textAlign:'center', padding:'20px 8px', color:'var(--color-text-muted)', fontSize:12 }}>Нет сделок</div>
              : stage.deals.map(deal => <SortableDealCard key={deal.id} deal={deal} />)
          }
        </SortableContext>
      </div>
    </div>
  );
}

export default function DealsPage() {
  const qc      = useQueryClient();
  const [activeId, setActiveId] = useState<string|null>(null);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint:{ distance:8 } }));

  const { data:board, isLoading } = useQuery<BoardData>({
    queryKey: ['deals-board'],
    queryFn:  () => api.get('/deals/board'),
  });

  const changeStage = useMutation({
    mutationFn: ({ dealId, stageId }:{ dealId:string; stageId:string }) =>
      api.post(`/deals/${dealId}/change_stage/`, { stage_id:stageId }),
    onSuccess: () => qc.invalidateQueries({ queryKey:['deals-board'] }),
    onError:   () => toast.error('Ошибка при перемещении'),
  });

  const activeDeal = board?.stages.flatMap(s=>s.deals).find(d=>d.id===activeId);

  function handleDragEnd(event: any) {
    const { active, over } = event;
    setActiveId(null);
    if (!over || active.id === over.id) return;
    // find which stage "over" is in
    const targetStage = board?.stages.find(s => s.id === over.id || s.deals.some(d=>d.id===over.id));
    if (!targetStage) return;
    changeStage.mutate({ dealId:active.id, stageId:targetStage.id });
  }

  const totalDeals = board?.stages.flatMap(s=>s.deals).length ?? 0;

  return (
    <div>
      <PageHeader
        title="Сделки"
        subtitle={board?.pipeline?.name ?? ''}
        actions={<Button icon={<Plus size={15}/>} onClick={()=>{}}>Новая сделка</Button>}
      />

      {!isLoading && totalDeals === 0 && (
        <EmptyState
          icon={<Briefcase size={22}/>}
          title="Сделок пока нет"
          subtitle="Создайте первую сделку из карточки клиента или нажмите Новая сделка"
        />
      )}

      <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={e=>setActiveId(e.active.id as string)} onDragEnd={handleDragEnd} onDragCancel={()=>setActiveId(null)}>
        <div style={{ display:'flex', gap:12, overflowX:'auto', paddingBottom:16, alignItems:'flex-start' }}>
          {(board?.stages ?? []).map(stage => (
            <KanbanColumn key={stage.id} stage={stage} isLoading={isLoading} />
          ))}
        </div>
        <DragOverlay>
          {activeDeal && <DealCardItem deal={activeDeal} isDragging />}
        </DragOverlay>
      </DndContext>
    </div>
  );
}
