'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { BarChart3, Wallet, Tag, Sparkles, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const navItems = [
  {
    label: 'Dashboard',
    href: '/',
    icon: BarChart3,
  },
  {
    label: 'Expenses',
    href: '/expenses',
    icon: Wallet,
  },
  {
    label: 'Categories',
    href: '/categories',
    icon: Tag,
  },
  {
    label: 'AI Insights',
    href: '/insights',
    icon: Sparkles,
  },
];

interface SidebarProps {
  onQuickAddClick?: () => void;
}

export function Sidebar({ onQuickAddClick }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col h-screen border-r border-slate-700">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-2xl font-bold">Jimat</h1>
        <p className="text-xs text-slate-400 mt-1">Expense Tracker</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link key={item.href} href={item.href}>
              <button
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-left',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-800'
                )}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </button>
            </Link>
          );
        })}
      </nav>

      {/* Quick Add Button */}
      <div className="p-4 border-t border-slate-700">
        <Button
          onClick={onQuickAddClick}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white gap-2"
          size="lg"
        >
          <Plus className="w-5 h-5" />
          Quick Add
        </Button>
      </div>
    </aside>
  );
}
