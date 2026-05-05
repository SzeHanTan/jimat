'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useExpenses } from '@/hooks/useExpenses';
import { useCategories } from '@/hooks/useCategories';
import { Category, Expense } from '@/types';

interface ExpenseContextType {
  // Expenses
  expenses: Expense[];
  expensesLoading: boolean;
  expensesError: string | null;
  fetchExpenses: () => Promise<void>;
  fetchExpensesByDateRange: (params: any) => Promise<void>;
  fetchExpensesByCategory: (categoryId: number) => Promise<void>;
  createExpense: (data: any) => Promise<Expense>;
  updateExpense: (id: number, data: any) => Promise<Expense>;
  deleteExpense: (id: number) => Promise<void>;
  
  // Categories
  categories: Category[];
  categoriesLoading: boolean;
  categoriesError: string | null;
  fetchCategories: () => Promise<void>;
  createCategory: (data: any) => Promise<Category>;
  updateCategory: (id: number, data: any) => Promise<Category>;
  deleteCategory: (id: number) => Promise<void>;
}

const ExpenseContext = createContext<ExpenseContextType | undefined>(undefined);

export function ExpenseProvider({ children }: { children: ReactNode }) {
  const expenses = useExpenses();
  const categories = useCategories();

  const value: ExpenseContextType = {
    // Expenses
    expenses: expenses.expenses,
    expensesLoading: expenses.loading,
    expensesError: expenses.error,
    fetchExpenses: expenses.fetchExpenses,
    fetchExpensesByDateRange: expenses.fetchExpensesByDateRange,
    fetchExpensesByCategory: expenses.fetchExpensesByCategory,
    createExpense: expenses.createExpense,
    updateExpense: expenses.updateExpense,
    deleteExpense: expenses.deleteExpense,
    
    // Categories
    categories: categories.categories,
    categoriesLoading: categories.loading,
    categoriesError: categories.error,
    fetchCategories: categories.fetchCategories,
    createCategory: categories.createCategory,
    updateCategory: categories.updateCategory,
    deleteCategory: categories.deleteCategory,
  };

  return (
    <ExpenseContext.Provider value={value}>
      {children}
    </ExpenseContext.Provider>
  );
}

export function useExpenseContext() {
  const context = useContext(ExpenseContext);
  if (!context) {
    throw new Error('useExpenseContext must be used within ExpenseProvider');
  }
  return context;
}
