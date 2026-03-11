import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Search, Users, Briefcase, CheckSquare, Settings, Loader2 } from 'lucide-react';
import { useCommandPalette } from '../../shared/stores/commandPalette';
import { api } from '../../shared/api/client';
import { useDebounce } from '../../shared/hooks/useDebounce';
import styles from './CommandPalette.module.css';

interface SearchResult {
  id: string;
  type: 'customer' | 'deal' | 'task';
  label: string;
  sublabel?: string;
  path: string;
}

const STATIC_COMMANDS = [
  { id: 'go-customers', label: 'Клиенты', icon: Users, path: '/customers' },
  { id: 'go-deals', label: 'Сделки', icon: Briefcase, path: '/deals' },
  { id: 'go-tasks', label: 'Задачи', icon: CheckSquare, path: '/tasks' },
  { id: 'go-settings', label: 'Настройки', icon: Settings, path: '/settings' },
];

const TYPE_ICON: Record<string, typeof Users> = {
  customer: Users,
  deal: Briefcase,
  task: CheckSquare,
};

export function CommandPalette() {
  const { close } = useCommandPalette();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debouncedQuery = useDebounce(query, 250);

  useEffect(() => { inputRef.current?.focus(); }, []);

  useEffect(() => {
    if (debouncedQuery.trim().length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    Promise.all([
      api.get<{ results: any[] }>('/customers/', { search: debouncedQuery, page_size: 4 }).catch(() => ({ results: [] })),
      api.get<{ results: any[] }>('/deals/', { search: debouncedQuery, page_size: 4 }).catch(() => ({ results: [] })),
      api.get<{ results: any[] }>('/tasks/', { search: debouncedQuery, page_size: 3 }).catch(() => ({ results: [] })),
    ]).then(([customers, deals, tasks]) => {
      const mapped: SearchResult[] = [
        ...(customers.results ?? []).map((c: any) => ({
          id: `customer-${c.id}`,
          type: 'customer' as const,
          label: c.full_name,
          sublabel: c.company_name,
          path: `/customers/${c.id}`,
        })),
        ...(deals.results ?? []).map((d: any) => ({
          id: `deal-${d.id}`,
          type: 'deal' as const,
          label: d.title,
          sublabel: d.customer?.full_name,
          path: `/deals/${d.id}`,
        })),
        ...(tasks.results ?? []).map((t: any) => ({
          id: `task-${t.id}`,
          type: 'task' as const,
          label: t.title,
          sublabel: t.customer?.full_name,
          path: '/tasks',
        })),
      ];
      setResults(mapped);
    }).finally(() => setLoading(false));
  }, [debouncedQuery]);

  const staticFiltered = query.trim().length < 2
    ? STATIC_COMMANDS
    : STATIC_COMMANDS.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()));

  return (
    <>
      <motion.div
        className={styles.backdrop}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={close}
      />
      <motion.div
        className={styles.palette}
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.96 }}
      >
        <div className={styles.inputWrap}>
          {loading ? <Loader2 size={16} style={{ animation: 'spin 0.6s linear infinite' }} /> : <Search size={16} />}
          <input
            ref={inputRef}
            className={styles.input}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск клиентов, сделок, задач..."
          />
        </div>

        {results.length > 0 && (
          <>
            <div className={styles.sectionLabel}>Результаты</div>
            {results.map((r) => {
              const Icon = TYPE_ICON[r.type] ?? Search;
              return (
                <button
                  key={r.id}
                  className={styles.resultItem}
                  onClick={() => {
                    navigate(r.path);
                    close();
                  }}
                >
                  <Icon size={14} />
                  <span style={{ flex: 1 }}>
                    {r.label}
                    {r.sublabel && (
                      <span style={{ marginLeft: 6, fontSize: 11, opacity: 0.5 }}>{r.sublabel}</span>
                    )}
                  </span>
                </button>
              );
            })}
            <div className={styles.divider} />
          </>
        )}

        <div className={styles.sectionLabel}>Навигация</div>
        {staticFiltered.map((cmd) => (
          <button
            key={cmd.id}
            className={styles.resultItem}
            onClick={() => {
              navigate(cmd.path);
              close();
            }}
          >
            <cmd.icon size={14} />
            <span>{cmd.label}</span>
          </button>
        ))}
      </motion.div>
    </>
  );
}
