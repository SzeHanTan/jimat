'use client';

import { useEffect, useState, useCallback } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useExpenseContext } from '@/contexts/ExpenseContext';
import { AddExpenseModal } from '@/components/modals/AddExpenseModal';
import { EditExpenseModal } from '@/components/modals/EditExpenseModal';
import { DeleteConfirmDialog } from '@/components/modals/DeleteConfirmDialog';
import { Expense, ExpenseCreate, ExpenseUpdate } from '@/types';

function getCategoryColor(categoryId: number, categories: any[]): string {
  const category = categories.find(c => c.id === categoryId);
  return category?.color || '#6366F1';
}

export default function ExpensesPage() {
  const { expenses, expensesLoading, expensesError, fetchExpenses, fetchExpensesByDateRange, createExpense, updateExpense, deleteExpense, categories, categoriesLoading, fetchCategories } = useExpenseContext();
  
  const [mounted, setMounted] = useState(false);
  const [filteredExpenses, setFilteredExpenses] = useState<Expense[]>([]);
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Modal state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    setMounted(true);
    fetchExpenses();
    fetchCategories();
  }, []);

  // Apply filters whenever expenses, filters change
  useEffect(() => {
    let filtered = expenses;

    // Filter by date range
    if (fromDate || toDate) {
      filtered = filtered.filter(expense => {
        const expenseDate = new Date(expense.date);
        if (fromDate && expenseDate < new Date(fromDate)) return false;
        if (toDate && expenseDate > new Date(toDate)) return false;
        return true;
      });
    }

    // Filter by category
    if (selectedCategory && selectedCategory !== '') {
      filtered = filtered.filter(expense => expense.category_id === parseInt(selectedCategory));
    }

    // Filter by search term (description)
    if (searchTerm) {
      filtered = filtered.filter(expense =>
        expense.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredExpenses(filtered);
  }, [expenses, fromDate, toDate, selectedCategory, searchTerm]);

  const handleFilterByDate = useCallback(async () => {
    if (fromDate && toDate) {
      await fetchExpensesByDateRange({
        start_date: fromDate,
        end_date: toDate,
      });
    } else if (fromDate || toDate) {
      // If only one date is provided, fetch all and filter client-side
      fetchExpenses();
    }
  }, [fromDate, toDate, fetchExpensesByDateRange, fetchExpenses]);

  const handleClearFilters = useCallback(() => {
    setFromDate('');
    setToDate('');
    setSelectedCategory('');
    setSearchTerm('');
    fetchExpenses();
  }, [fetchExpenses]);

  const handleAddExpense = async (data: ExpenseCreate) => {
    setIsModalLoading(true);
    try {
      await createExpense(data);
      await fetchExpenses();
      setIsAddModalOpen(false);
    } finally {
      setIsModalLoading(false);
    }
  };

  const handleEditExpense = async (data: ExpenseUpdate) => {
    if (!selectedExpense) return;
    setIsModalLoading(true);
    try {
      await updateExpense(selectedExpense.id, data);
      await fetchExpenses();
      setIsEditModalOpen(false);
      setSelectedExpense(null);
    } finally {
      setIsModalLoading(false);
    }
  };

  const handleDeleteExpense = async () => {
    if (!selectedExpense) return;
    setIsModalLoading(true);
    try {
      await deleteExpense(selectedExpense.id);
      await fetchExpenses();
      setIsDeleteModalOpen(false);
      setSelectedExpense(null);
    } finally {
      setIsModalLoading(false);
    }
  };

  const openEditModal = (expense: Expense) => {
    setSelectedExpense(expense);
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (expense: Expense) => {
    setSelectedExpense(expense);
    setIsDeleteModalOpen(true);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatCurrency = (value: number | string) => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return `$${num.toFixed(2)}`;
  };

  if (!mounted) return null;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Expenses</h1>
        <Button 
          className="bg-blue-600 hover:bg-blue-700 text-white gap-2"
          onClick={() => setIsAddModalOpen(true)}
        >
          <Plus className="w-5 h-5" />
          Add Expense
        </Button>
      </div>

      {/* Error Messages */}
      {expensesError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{expensesError}</p>
        </div>
      )}

      {/* Filters */}
      <Card className="p-4 sm:p-6 bg-white">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              From Date
            </label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              To Date
            </label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Search
            </label>
            <input
              type="text"
              placeholder="Search expenses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button
            onClick={handleFilterByDate}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
          >
            Apply Filters
          </button>
          <button
            onClick={handleClearFilters}
            className="px-4 py-2 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 text-sm font-medium"
          >
            Clear Filters
          </button>
        </div>
      </Card>

      {/* Expenses Table */}
      <Card className="p-4 sm:p-6 bg-white">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">
          {expensesLoading ? 'Loading...' : `All Expenses (${filteredExpenses.length})`}
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 px-4 font-semibold text-slate-900">
                  Date
                </th>
                <th className="text-left py-3 px-4 font-semibold text-slate-900">
                  Category
                </th>
                <th className="text-left py-3 px-4 font-semibold text-slate-900">
                  Description
                </th>
                <th className="text-right py-3 px-4 font-semibold text-slate-900">
                  Amount
                </th>
                <th className="text-center py-3 px-4 font-semibold text-slate-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {expensesLoading ? (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-slate-500">
                    Loading expenses...
                  </td>
                </tr>
              ) : filteredExpenses.length > 0 ? (
                filteredExpenses
                  .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                  .map((expense) => {
                    const category = categories.find(c => c.id === expense.category_id);
                    return (
                      <tr
                        key={expense.id}
                        className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition"
                      >
                        <td className="py-3 px-4 text-slate-600">{formatDate(expense.date)}</td>
                        <td className="py-3 px-4">
                          <span
                            className="inline-block px-3 py-1 rounded-full text-xs font-medium text-white"
                            style={{ backgroundColor: getCategoryColor(expense.category_id, categories) }}
                          >
                            {category?.name || 'Unknown'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-900">{expense.description}</td>
                        <td className="py-3 px-4 text-right font-semibold text-slate-900">
                          {formatCurrency(expense.amount)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <button 
                            onClick={() => openEditModal(expense)}
                            className="text-blue-600 hover:text-blue-700 text-xs font-medium mr-3"
                          >
                            Edit
                          </button>
                          <button 
                            onClick={() => openDeleteModal(expense)}
                            className="text-red-600 hover:text-red-700 text-xs font-medium"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })
              ) : (
                <tr>
                  <td colSpan={5} className="py-4 px-4 text-center text-slate-500">
                    No expenses found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Modals */}
      <AddExpenseModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        categories={categories}
        onSubmit={handleAddExpense}
        isLoading={isModalLoading}
      />

      <EditExpenseModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedExpense(null);
        }}
        expense={selectedExpense}
        categories={categories}
        onSubmit={handleEditExpense}
        isLoading={isModalLoading}
      />

      <DeleteConfirmDialog
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setSelectedExpense(null);
        }}
        title="Delete Expense"
        description="Are you sure you want to delete this expense?"
        itemName={selectedExpense ? selectedExpense.description : ''}
        onConfirm={handleDeleteExpense}
        isLoading={isModalLoading}
      />
    </div>
  );
}
