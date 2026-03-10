import type { ReactNode } from 'react';

interface Props {
  icon?:     ReactNode;
  title:     string;
  subtitle?: string;
  action?:   ReactNode;
}

export function EmptyState({ icon, title, subtitle, action }: Props) {
  return (
    <div style={{
      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
      padding:'60px 20px', textAlign:'center', gap:12,
    }}>
      {icon && (
        <div style={{
          width:56, height:56,
          background:'var(--color-bg-muted)',
          borderRadius:'var(--radius-xl)',
          display:'flex', alignItems:'center', justifyContent:'center',
          color:'var(--color-text-muted)',
        }}>{icon}</div>
      )}
      <h3 style={{ fontSize:15, fontWeight:600, margin:0 }}>{title}</h3>
      {subtitle && <p style={{ fontSize:13, color:'var(--color-text-muted)', margin:0, maxWidth:280 }}>{subtitle}</p>}
      {action}
    </div>
  );
}
