'use client';

import { Settings, User } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function Header() {
  return (
    <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">
          Expense Management
        </h2>
        <p className="text-sm text-slate-500">
          Track and manage your expenses efficiently
        </p>
      </div>

      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="text-slate-600 hover:text-slate-900"
        >
          <Settings className="w-5 h-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="text-slate-600 hover:text-slate-900"
        >
          <User className="w-5 h-5" />
        </Button>
      </div>
    </header>
  );
}
