interface BadgeProps {
  children: React.ReactNode;
  color?: string;
  bg?: string;
}

export function Badge({ children, color='var(--color-text-secondary)', bg='var(--color-bg-muted)' }: BadgeProps) {
  return (
    <span style={{
      display:'inline-flex', alignItems:'center',
      padding:'2px 8px', borderRadius:'var(--radius-full)',
      fontSize:11, fontWeight:500, color, background:bg,
      whiteSpace:'nowrap',
    }}>
      {children}
    </span>
  );
}
