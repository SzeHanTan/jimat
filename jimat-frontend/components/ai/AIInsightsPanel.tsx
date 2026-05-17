/**
 * AI Insights Panel Component
 * 
 * Displays AI-generated insights about spending patterns
 */

'use client';

import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { AlertCircle, TrendingDown, TrendingUp, Zap, Loader } from 'lucide-react';
import { useSpendingSummary, usePatternDetection } from '@/hooks/useAI';
import { ExpenseData, SummaryResponse, PatternsResponse } from '@/lib/aiApi';

interface AIInsightsPanelProps {
  expenses: any[];
  categories?: any[];
  period?: 'daily' | 'weekly' | 'monthly' | 'yearly';
}

export function AIInsightsPanel({ expenses, categories = [], period = 'monthly' }: AIInsightsPanelProps) {
  const { getSummaryData, loading: summaryLoading } = useSpendingSummary();
  const { detectSpendingPatterns, loading: patternsLoading } = usePatternDetection();

  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [patterns, setPatterns] = useState<PatternsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (expenses.length === 0) return;

    const loadInsights = async () => {
      try {
        setError(null);

        // Convert expenses to the format expected by AI API
        const expenseData: ExpenseData[] = expenses.map((exp) => ({
          amount: exp.amount,
          date: exp.date,
          category: exp.category?.name || 'Unknown',
          description: exp.description,
        }));

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

  if (expenses.length === 0) {
    return (
      <Card className="p-4 bg-gray-50 border-dashed">
        <p className="text-sm text-gray-600">Add expenses to see AI insights</p>
      </Card>
    );
  }

  const isLoading = summaryLoading || patternsLoading;

  // Calculate top category locally from expenses data
  const calculateTopCategory = () => {
    if (expenses.length === 0) return null;

    const categoryTotals: Record<string, { total: number; count: number }> = {};
    let grandTotal = 0;

    expenses.forEach((exp) => {
      // Match category_id to get category name
      const category = categories.find(c => c.id === exp.category_id);
      const categoryName = category?.name || 'Uncategorized';
      // Convert amount to number in case it's a string
      const amount = typeof exp.amount === 'string' ? parseFloat(exp.amount) : exp.amount;
      if (!categoryTotals[categoryName]) {
        categoryTotals[categoryName] = { total: 0, count: 0 };
      }
      categoryTotals[categoryName].total += amount;
      categoryTotals[categoryName].count += 1;
      grandTotal += amount;
    });

    // Find category with highest spending
    let topCategory = null;
    let maxSpending = 0;

    Object.entries(categoryTotals).forEach(([category, data]) => {
      if (data.total > maxSpending) {
        maxSpending = data.total;
        topCategory = {
          category,
          total: data.total,
          count: data.count,
          percentage: grandTotal > 0 ? (data.total / grandTotal) * 100 : 0,
        };
      }
    });

    return topCategory;
  };

  const topCategory = calculateTopCategory();

  return (
    <div className="space-y-4">
      {error && (
        <Card className="p-3 border-red-200 bg-red-50">
          <div className="flex gap-2 items-start">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </Card>
      )}

      {isLoading && (
        <Card className="p-6">
          <div className="flex items-center justify-center gap-2 text-blue-600">
            <Loader className="w-5 h-5 animate-spin" />
            <span className="text-sm">Loading AI insights...</span>
          </div>
        </Card>
      )}

      {summary && !isLoading && (
        <Card className="p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-600" />
            Spending Overview ({period})
          </h3>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <div>
              <p className="text-xs text-gray-600 mb-1">Total Spending</p>
              <p className="font-bold text-lg text-gray-900">
                ${summary.total_spending.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Transactions</p>
              <p className="font-bold text-lg text-gray-900">{summary.transaction_count}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Average</p>
              <p className="font-bold text-lg text-gray-900">
                ${summary.average_transaction.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Biggest</p>
              <p className="font-bold text-lg text-gray-900">
                ${summary.biggest_transaction.toFixed(2)}
              </p>
            </div>
          </div>

          {topCategory && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs font-semibold text-gray-700 mb-2">Top Category</p>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-gray-900">{topCategory.category}</p>
                  <p className="text-sm text-gray-600">
                    {topCategory.count} transactions
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-gray-900">
                    ${topCategory.total.toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-600">
                    {topCategory.percentage.toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}

      {patterns && !isLoading && patterns.patterns_detected > 0 && (
        <Card className="p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-amber-600" />
            Spending Patterns Detected ({patterns.patterns_detected})
          </h3>
          <div className="space-y-3">
            {patterns.patterns.slice(0, 3).map((pattern, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border-l-4 ${
                  pattern.severity > 0.7
                    ? 'border-l-red-500 bg-red-50'
                    : pattern.severity > 0.4
                    ? 'border-l-amber-500 bg-amber-50'
                    : 'border-l-green-500 bg-green-50'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900 capitalize">
                      {pattern.pattern_type}
                    </p>
                    <p className="text-sm text-gray-700 mt-1">{pattern.description}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-xs font-semibold text-gray-600 block">
                      {(pattern.confidence * 100).toFixed(0)}% sure
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {patterns.patterns_detected > 3 && (
            <p className="text-xs text-gray-600 mt-2 text-center">
              +{patterns.patterns_detected - 3} more patterns detected
            </p>
          )}
        </Card>
      )}
    </div>
  );
}
