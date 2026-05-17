'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card } from "@/components/ui/card";
import { ArrowUpRight, TrendingUp, DollarSign, Calendar } from "lucide-react";
import { useExpenseContext } from '@/contexts/ExpenseContext';
import { AIInsightsPanel } from '@/components/ai';
import { 
  calculateDashboardStats, 
  getTopCategories, 
  getRecentExpenses 
} from '@/lib/dashboardUtils';

const CATEGORY_COLORS: { [key: string]: string } = {
  Food: '#FF5733',
  Transport: '#3366FF',
  Work: '#33FF66',
  Entertainment: '#FFFF33',
  Healthcare: '#FF33FF',
  Other: '#999999',
};

function getCategoryColor(categoryId: number, categories: any[]): string {
  const category = categories.find(c => c.id === categoryId);
  if (!category) return '#6366F1';
  return category.color || CATEGORY_COLORS[category.name] || '#6366F1';
}

export default function Dashboard() {
  const { 
    expenses, 
    expensesLoading, 
    expensesError, 
    fetchExpenses,
    categories, 
    categoriesLoading, 
    categoriesError, 
    fetchCategories 
  } = useExpenseContext();
  
  const [mounted, setMounted] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    setMounted(true);
    fetchExpenses();
    fetchCategories();
  }, []);

  if (!mounted) return null;

  // Calculate statistics
  const stats = calculateDashboardStats(expenses);
  const topCategories = getTopCategories(expenses, categories, 4);
  const recentExpenses = getRecentExpenses(expenses, 4);

  // Format currency
  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;
  
  // Format date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8">
      {/* Error Messages */}
      {(expensesError || categoriesError) && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">
            {expensesError || categoriesError}
          </p>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <Card className="p-4 sm:p-6 bg-white">
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="text-xs sm:text-sm text-slate-600">Total Spent</p>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1 sm:mt-2">
                {expensesLoading ? '...' : formatCurrency(stats.totalSpent)}
              </p>
              <p className="text-xs text-slate-500 mt-1 sm:mt-2">All time</p>
            </div>
            <div className="bg-blue-100 p-2 sm:p-3 rounded-lg flex-shrink-0">
              <DollarSign className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4 sm:p-6 bg-white">
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="text-xs sm:text-sm text-slate-600">This Month</p>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1 sm:mt-2">
                {expensesLoading ? '...' : formatCurrency(stats.thisMonthSpent)}
              </p>
              <p className="text-xs text-green-600 mt-1 sm:mt-2 flex items-center gap-1 flex-wrap">
                <ArrowUpRight className="w-4 h-4 flex-shrink-0" />
                <span>Tracked</span>
              </p>
            </div>
            <div className="bg-green-100 p-2 sm:p-3 rounded-lg flex-shrink-0">
              <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4 sm:p-6 bg-white">
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="text-xs sm:text-sm text-slate-600">This Week</p>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1 sm:mt-2">
                {expensesLoading ? '...' : formatCurrency(stats.thisWeekSpent)}
              </p>
              <p className="text-xs text-slate-500 mt-1 sm:mt-2">7 days</p>
            </div>
            <div className="bg-purple-100 p-2 sm:p-3 rounded-lg flex-shrink-0">
              <Calendar className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4 sm:p-6 bg-white">
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0 flex-1">
              <p className="text-xs sm:text-sm text-slate-600">Budget Used</p>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1 sm:mt-2">
                {expensesLoading ? '...' : `${stats.budgetPercentage}%`}
              </p>
              <p className="text-xs text-orange-600 mt-1 sm:mt-2">$1,500 budget</p>
            </div>
            <div className="bg-orange-100 p-2 sm:p-3 rounded-lg flex-shrink-0">
              <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* AI Insights Section */}
      {expenses.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-slate-900 mb-4">AI Insights</h2>
          <AIInsightsPanel expenses={expenses} categories={categories} period="monthly" />
        </div>
      )}

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        {/* Charts Placeholder */}
        <Card className="lg:col-span-2 p-6 bg-white">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">
            Monthly Spending Trend
          </h3>
          <div className="h-64 bg-gradient-to-b from-slate-50 to-slate-100 rounded-lg flex items-center justify-center">
            <p className="text-slate-500">Chart will be displayed here</p>
          </div>
        </Card>

        {/* Category Breakdown */}
        <Card className="p-6 bg-white">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">
            Top Categories
          </h3>
          {categoriesLoading || expensesLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-slate-200 rounded w-3/4 mb-2"></div>
                  <div className="h-2 bg-slate-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : topCategories.length > 0 ? (
            <div className="space-y-4">
              {topCategories.map((category) => (
                <div key={category.categoryId}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-slate-700">
                      {category.categoryName}
                    </span>
                    <span className="text-sm font-semibold text-slate-900">
                      {formatCurrency(category.total)}
                    </span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${category.percentage}%`,
                        backgroundColor: getCategoryColor(category.categoryId, categories),
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm">No expenses yet</p>
          )}
        </Card>
      </div>

      {/* Recent Expenses */}
      <Card className="p-6 bg-white">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">
          Recent Expenses
        </h3>
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
              </tr>
            </thead>
            <tbody>
              {expensesLoading ? (
                <tr>
                  <td colSpan={4} className="py-4 px-4 text-center text-slate-500">
                    Loading expenses...
                  </td>
                </tr>
              ) : recentExpenses.length > 0 ? (
                recentExpenses.map((expense) => {
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
                        -{formatCurrency(typeof expense.amount === 'string' ? parseFloat(expense.amount) : expense.amount)}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={4} className="py-4 px-4 text-center text-slate-500">
                    No expenses yet
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="mt-4">
          <Link href="/expenses" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            View All Expenses →
          </Link>
        </div>
      </Card>
    </div>
  );
}
