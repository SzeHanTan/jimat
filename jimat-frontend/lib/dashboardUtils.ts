/**
 * Dashboard utility functions
 * Handles calculations for expense statistics
 */

import { Expense } from '@/types';

export interface DashboardStats {
  totalSpent: number;
  thisMonthSpent: number;
  thisWeekSpent: number;
  budgetUsed: number;
  budgetPercentage: number;
}

export interface CategoryStats {
  categoryId: number;
  categoryName: string;
  total: number;
  percentage: number;
}

const MONTHLY_BUDGET = 1500; // Default budget - can be made configurable

/**
 * Get current month's first day and today
 */
function getCurrentMonthRange() {
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  return { firstDay, today };
}

/**
 * Get this week's first day (Monday) and today
 */
function getThisWeekRange() {
  const today = new Date();
  const dayOfWeek = today.getDay();
  const daysToMonday = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
  const monday = new Date(today);
  monday.setDate(today.getDate() - daysToMonday);
  return { monday, today };
}

/**
 * Format date for comparison (YYYY-MM-DD)
 */
function formatDateString(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Calculate all dashboard statistics
 */
export function calculateDashboardStats(expenses: Expense[]): DashboardStats {
  const { firstDay, today } = getCurrentMonthRange();
  const { monday } = getThisWeekRange();

  const thisMonthStr = firstDay.getFullYear() + '-' + String(firstDay.getMonth() + 1).padStart(2, '0');
  const thisWeekStart = formatDateString(monday);
  const thisWeekEnd = formatDateString(today);

  let totalSpent = 0;
  let thisMonthSpent = 0;
  let thisWeekSpent = 0;

  expenses.forEach((expense) => {
    const amount = typeof expense.amount === 'string' ? parseFloat(expense.amount) : expense.amount;
    
    // Total spent (all time, or you could limit to a period)
    totalSpent += amount;

    // This month
    if (expense.date.startsWith(thisMonthStr)) {
      thisMonthSpent += amount;
    }

    // This week
    if (expense.date >= thisWeekStart && expense.date <= thisWeekEnd) {
      thisWeekSpent += amount;
    }
  });

  const budgetUsed = thisMonthSpent;
  const budgetPercentage = Math.round((budgetUsed / MONTHLY_BUDGET) * 100);

  return {
    totalSpent: Math.round(totalSpent * 100) / 100,
    thisMonthSpent: Math.round(thisMonthSpent * 100) / 100,
    thisWeekSpent: Math.round(thisWeekSpent * 100) / 100,
    budgetUsed: Math.round(budgetUsed * 100) / 100,
    budgetPercentage: Math.min(budgetPercentage, 100),
  };
}

/**
 * Get top categories by total spending
 */
export function getTopCategories(
  expenses: Expense[],
  categories: any[],
  limit: number = 4
): CategoryStats[] {
  // Sum spending by category
  const categoryTotals: { [key: number]: number } = {};
  
  expenses.forEach((expense) => {
    const amount = typeof expense.amount === 'string' ? parseFloat(expense.amount) : expense.amount;
    categoryTotals[expense.category_id] = (categoryTotals[expense.category_id] || 0) + amount;
  });

  // Calculate total and percentages
  const totalSpent = Object.values(categoryTotals).reduce((sum, amount) => sum + amount, 0);

  // Convert to array and map with category names
  const stats = Object.entries(categoryTotals)
    .map(([categoryId, amount]) => {
      const category = categories.find((c) => c.id === parseInt(categoryId));
      return {
        categoryId: parseInt(categoryId),
        categoryName: category?.name || 'Unknown',
        total: Math.round(amount * 100) / 100,
        percentage: totalSpent > 0 ? Math.round((amount / totalSpent) * 100) : 0,
      };
    })
    .sort((a, b) => b.total - a.total)
    .slice(0, limit);

  return stats;
}

/**
 * Get recent expenses (sorted by date, most recent first)
 */
export function getRecentExpenses(expenses: Expense[], limit: number = 4): Expense[] {
  return [...expenses]
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, limit);
}
