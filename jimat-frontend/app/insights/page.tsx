'use client';

import { useEffect, useState } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Zap, TrendingUp, TrendingDown, AlertCircle, Loader } from "lucide-react";
import { useExpenseContext } from '@/contexts/ExpenseContext';
import { useSpendingSummary, usePatternDetection } from '@/hooks/useAI';
import { ExpenseData } from '@/lib/aiApi';

export default function InsightsPage() {
  const { expenses, expensesLoading, fetchExpenses, categories } = useExpenseContext();
  const { getSummaryData, loading: summaryLoading } = useSpendingSummary();
  const { detectSpendingPatterns, loading: patternsLoading } = usePatternDetection();

  const [mounted, setMounted] = useState(false);
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly' | 'yearly'>('monthly');
  const [summary, setSummary] = useState<any>(null);
  const [patterns, setPatterns] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
    fetchExpenses();
  }, []);

  useEffect(() => {
    if (expenses.length === 0) return;

    const loadInsights = async () => {
      try {
        setError(null);

        const expenseData: ExpenseData[] = expenses.map((exp) => {
          // Match category_id to get category name
          const category = categories.find(c => c.id === exp.category_id);
          return {
            amount: exp.amount,
            date: exp.date,
            category: category?.name || 'Unknown',
            description: exp.description,
          };
        });

        // Get summary
        const summaryResult = await getSummaryData({
          expenses: expenseData,
          period,
        });
        setSummary(summaryResult);

        // Get patterns
        const patternsResult = await detectSpendingPatterns({
          expenses: expenseData,
          baseline_days: period === 'daily' ? 7 : 30,
        });
        setPatterns(patternsResult);
      } catch (err: any) {
        setError(err.message || 'Failed to load insights');
      }
    };

    loadInsights();
  }, [expenses, period, getSummaryData, detectSpendingPatterns]);

  if (!mounted) return null;

  const isLoading = expensesLoading || summaryLoading || patternsLoading;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6 sm:space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">AI Insights</h1>
          <p className="text-slate-600 mt-1">Analyze spending patterns and trends</p>
        </div>

        <div className="w-full sm:w-48">
          <Select value={period} onValueChange={(value: any) => setPeriod(value)}>
            <SelectTrigger>
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
              <SelectItem value="yearly">Yearly</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {error && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex gap-3 items-start">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900">Error Loading Insights</p>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </Card>
      )}

      {expenses.length === 0 ? (
        <Card className="p-8 text-center bg-slate-50 border-dashed">
          <Zap className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-600 font-semibold">No expenses yet</p>
          <p className="text-gray-500 text-sm mt-1">Add expenses to see AI insights</p>
        </Card>
      ) : isLoading ? (
        <Card className="p-8">
          <div className="flex flex-col items-center justify-center gap-3">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
            <p className="text-slate-600">Analyzing your spending...</p>
          </div>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Summary Statistics */}
          {summary && (
            <Card className="p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                <Zap className="w-6 h-6 text-blue-600" />
                Summary ({period})
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Total Spending</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    ${summary.total_spending.toFixed(2)}
                  </p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Transactions</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {summary.transaction_count}
                  </p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Average Transaction</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    ${summary.average_transaction.toFixed(2)}
                  </p>
                </div>
                <div className="bg-orange-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Biggest Transaction</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    ${summary.biggest_transaction.toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Category Breakdown */}
              <div className="mt-8">
                <h3 className="font-semibold text-gray-900 mb-4">Category Breakdown</h3>
                <div className="space-y-3">
                  {summary.category_breakdown && summary.category_breakdown.length > 0 ? (
                    summary.category_breakdown.map((category: any, idx: number) => (
                      <div key={idx}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-700">{category.category}</span>
                          <div className="text-right">
                            <p className="font-bold text-gray-900">
                              ${category.total.toFixed(2)}
                            </p>
                            <p className="text-xs text-gray-600">
                              {category.percentage.toFixed(0)}%
                            </p>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-blue-600"
                            style={{ width: `${category.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-600 text-sm">No categories to display</p>
                  )}
                </div>
              </div>
            </Card>
          )}

          {/* Spending Patterns */}
          {patterns && patterns.patterns.length > 0 && (
            <Card className="p-6">
              <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-amber-600" />
                Detected Spending Patterns ({patterns.patterns_detected})
              </h2>

              <div className="space-y-4">
                {patterns.patterns.map((pattern: any, idx: number) => (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg border-l-4 ${
                      pattern.severity > 0.7
                        ? 'border-l-red-500 bg-red-50'
                        : pattern.severity > 0.4
                        ? 'border-l-amber-500 bg-amber-50'
                        : 'border-l-green-500 bg-green-50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {pattern.severity > 0.7 ? (
                            <TrendingUp className="w-5 h-5 text-red-600" />
                          ) : (
                            <TrendingDown className="w-5 h-5 text-amber-600" />
                          )}
                          <p className="font-semibold text-gray-900 capitalize">
                            {pattern.pattern_type}
                          </p>
                        </div>
                        <p className="text-gray-700">{pattern.description}</p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="text-xs font-semibold text-gray-600 mb-1">
                          Confidence
                        </p>
                        <p className="text-lg font-bold text-gray-900">
                          {(pattern.confidence * 100).toFixed(0)}%
                        </p>
                        <p className="text-xs font-semibold text-gray-600 mt-1">
                          Severity: {(pattern.severity * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {patterns.patterns.length === 0 && (
                <p className="text-center text-gray-600 py-4">
                  No unusual patterns detected in your spending!
                </p>
              )}
            </Card>
          )}

          {/* No patterns detected */}
          {patterns && patterns.patterns.length === 0 && (
            <Card className="p-6 bg-green-50 border-green-200">
              <div className="flex gap-3 items-start">
                <div className="bg-green-100 rounded-lg p-3">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <p className="font-semibold text-green-900">Great spending habits!</p>
                  <p className="text-sm text-green-700 mt-1">
                    No unusual patterns detected in your {period} spending. Keep it up!
                  </p>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
