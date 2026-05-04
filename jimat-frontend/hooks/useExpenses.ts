/**
 * Custom Hook: useExpenses
 * 
 * Handles all expense-related API calls and state management:
 * - Fetch expenses (with pagination)
 * - Fetch expenses by date range
 * - Fetch expenses by category
 * - Create expense
 * - Update expense
 * - Delete expense
 */

import { useState, useCallback } from 'react';
import apiClient from '@/lib/api';
import { Expense, ExpenseCreate, ExpenseUpdate, DateRangeParams, PaginationParams } from '@/types';

interface UseExpensesReturn {
  // State
  expenses: Expense[];
  loading: boolean;
  error: string | null;
  
  // Methods
  fetchExpenses: (params?: PaginationParams) => Promise<void>;
  fetchExpensesByDateRange: (params: DateRangeParams) => Promise<void>;
  fetchExpensesByCategory: (categoryId: number) => Promise<void>;
  createExpense: (data: ExpenseCreate) => Promise<Expense>;
  updateExpense: (id: number, data: ExpenseUpdate) => Promise<Expense>;
  deleteExpense: (id: number) => Promise<void>;
}

export function useExpenses(): UseExpensesReturn {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExpenses = useCallback(async (params?: PaginationParams) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/api/v1/expenses', { params });
      setExpenses(response.data);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to fetch expenses';
      setError(message);
      console.error('Error fetching expenses:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchExpensesByDateRange = useCallback(async (params: DateRangeParams) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/api/v1/expenses/date-range/search', {
        params: {
          start_date: params.start_date,
          end_date: params.end_date,
        },
      });
      setExpenses(response.data);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to fetch expenses by date range';
      setError(message);
      console.error('Error fetching expenses by date range:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchExpensesByCategory = useCallback(async (categoryId: number) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get(`/api/v1/expenses/category/${categoryId}`);
      setExpenses(response.data);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to fetch expenses by category';
      setError(message);
      console.error('Error fetching expenses by category:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const createExpense = useCallback(async (data: ExpenseCreate): Promise<Expense> => {
    try {
      setError(null);
      const response = await apiClient.post('/api/v1/expenses', data);
      const newExpense = response.data;
      setExpenses((prev) => [newExpense, ...prev]);
      return newExpense;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to create expense';
      setError(message);
      console.error('Error creating expense:', err);
      throw err;
    }
  }, []);

  const updateExpense = useCallback(async (id: number, data: ExpenseUpdate): Promise<Expense> => {
    try {
      setError(null);
      const response = await apiClient.put(`/api/v1/expenses/${id}`, data);
      const updatedExpense = response.data;
      setExpenses((prev) =>
        prev.map((expense) => (expense.id === id ? updatedExpense : expense))
      );
      return updatedExpense;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to update expense';
      setError(message);
      console.error('Error updating expense:', err);
      throw err;
    }
  }, []);

  const deleteExpense = useCallback(async (id: number) => {
    try {
      setError(null);
      await apiClient.delete(`/api/v1/expenses/${id}`);
      setExpenses((prev) => prev.filter((expense) => expense.id !== id));
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to delete expense';
      setError(message);
      console.error('Error deleting expense:', err);
      throw err;
    }
  }, []);

  return {
    expenses,
    loading,
    error,
    fetchExpenses,
    fetchExpensesByDateRange,
    fetchExpensesByCategory,
    createExpense,
    updateExpense,
    deleteExpense,
  };
}
