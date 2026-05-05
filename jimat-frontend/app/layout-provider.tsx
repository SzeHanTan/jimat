/**
 * Root Layout Provider
 * Handles all client-side state and modals
 */

'use client';

import { useState, useEffect } from 'react';
import { Sidebar, Header } from "@/components/layouts";
import { QuickAddModal } from "@/components/modals/QuickAddModal";
import { ExpenseProvider, useExpenseContext } from "@/contexts/ExpenseContext";
import { ExpenseCreate } from '@/types';

interface RootLayoutProviderProps {
  children: React.ReactNode;
}

function RootLayoutContent({ children }: RootLayoutProviderProps) {
  const { createExpense, fetchExpenses, categories, fetchCategories } = useExpenseContext();
  const [mounted, setMounted] = useState(false);
  const [isQuickAddOpen, setIsQuickAddOpen] = useState(false);
  const [isModalLoading, setIsModalLoading] = useState(false);

  // Fetch categories on mount
  useEffect(() => {
    setMounted(true);
    fetchCategories();
  }, []);

  const handleQuickAdd = async (data: ExpenseCreate) => {
    setIsModalLoading(true);
    try {
      await createExpense(data);
      await fetchExpenses();
      setIsQuickAddOpen(false);
    } finally {
      setIsModalLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <>
      <Sidebar onQuickAddClick={() => setIsQuickAddOpen(true)} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
      
      <QuickAddModal
        isOpen={isQuickAddOpen}
        onClose={() => setIsQuickAddOpen(false)}
        categories={categories}
        onSubmit={handleQuickAdd}
        isLoading={isModalLoading}
      />
    </>
  );
}

export function RootLayoutProvider({ children }: RootLayoutProviderProps) {
  return (
    <ExpenseProvider>
      <RootLayoutContent>{children}</RootLayoutContent>
    </ExpenseProvider>
  );
}
