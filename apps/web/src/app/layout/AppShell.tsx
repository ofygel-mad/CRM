import { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { CommandPalette } from '../../widgets/command-palette/CommandPalette';
import { useCommandPalette } from '../../shared/stores/commandPalette';
import { Toaster } from 'sonner';
export function AppShell() { const [sidebarCollapsed, setSidebarCollapsed] = useState(false); const { isOpen, toggle } = useCommandPalette(); const location = useLocation(); useEffect(() => { const onDown = (e: KeyboardEvent) => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); toggle(); } }; document.addEventListener('keydown', onDown); return () => document.removeEventListener('keydown', onDown); }, [toggle]); return <div className="app-shell"><Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed((p) => !p)} /><div className="app-main" style={{ marginLeft: sidebarCollapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)', transition: 'margin-left var(--transition-base)' }}><Topbar /><main className="app-content"><AnimatePresence mode="wait"><motion.div key={location.pathname} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }}><Outlet /></motion.div></AnimatePresence></main></div><AnimatePresence>{isOpen && <CommandPalette />}</AnimatePresence><Toaster position="bottom-right" /></div>; }
