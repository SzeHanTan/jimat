/**
 * AI Category Suggestion Component
 * 
 * Shows AI-powered category suggestions with confidence scores
 */

'use client';

import React, { useState } from 'react';
import { Sparkles, Check, X, Loader } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCategorization } from '@/hooks/useAI';

interface AICategorySuggestionProps {
  description: string;
  amount?: number;
  date?: string;
  onSelectCategory: (category: string) => void;
  disabled?: boolean;
}

export function AICategorySuggestion({
  description,
  amount,
  date,
  onSelectCategory,
  disabled = false,
}: AICategorySuggestionProps) {
  const { categorize, loading, error } = useCategorization();
  const [suggestion, setSuggestion] = useState<any>(null);
  const [expanded, setExpanded] = useState(false);

  const handleGetSuggestion = async () => {
    try {
      const result = await categorize({
        description,
        amount,
        date,
      });
      setSuggestion(result);
      setExpanded(true);
    } catch (err) {
      // Error is handled in hook
    }
  };

  if (!description.trim() || disabled) return null;

  return (
    <div className="space-y-2">
      {!suggestion ? (
        <Button
          onClick={handleGetSuggestion}
          disabled={loading}
          size="sm"
          variant="outline"
          className="w-full gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Getting AI suggestion...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Get AI Category Suggestion
            </>
          )}
        </Button>
      ) : (
        <div className="border rounded-lg p-3 bg-blue-50">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-4 h-4 text-blue-600" />
                <span className="font-semibold text-blue-900">{suggestion.category}</span>
                <span className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">
                  {(suggestion.confidence * 100).toFixed(0)}% confident
                </span>
              </div>
              {expanded && (
                <>
                  <p className="text-sm text-gray-700 mb-2">{suggestion.explanation}</p>
                  {suggestion.alternatives && suggestion.alternatives.length > 0 && (
                    <div className="text-xs text-gray-600">
                      <span className="font-semibold">Other options: </span>
                      {suggestion.alternatives.slice(0, 2).join(', ')}
                    </div>
                  )}
                </>
              )}
            </div>
            <div className="flex gap-1">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onSelectCategory(suggestion.category)}
                className="text-green-600 hover:text-green-700 hover:bg-green-50"
                title="Accept"
              >
                <Check className="w-4 h-4" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setSuggestion(null)}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                title="Reject"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
      {error && (
        <p className="text-sm text-red-600">
          Error getting suggestion: {error}
        </p>
      )}
    </div>
  );
}
