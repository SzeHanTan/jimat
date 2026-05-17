/**
 * AI Features Hooks
 * 
 * Custom React hooks for AI functionality
 */

'use client';

import { useState, useCallback } from 'react';
import {
  DocumentAnalyzeRequest,
  DocumentAnalyzeResponse,
  CategorizationRequest,
  CategorizationResponse,
  SummaryRequest,
  SummaryResponse,
  PatternsRequest,
  PatternsResponse,
  analyzeDocument,
  categorizeExpense,
  getSummary,
  detectPatterns,
  checkAIHealth,
} from '@/lib/aiApi';

/**
 * Hook for document analysis
 */
export function useDocumentAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = useCallback(async (request: DocumentAnalyzeRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeDocument(request);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to analyze document';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { analyze, loading, error };
}

/**
 * Hook for expense categorization
 */
export function useCategorization() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const categorize = useCallback(async (request: CategorizationRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await categorizeExpense(request);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to categorize expense';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { categorize, loading, error };
}

/**
 * Hook for getting spending summary
 */
export function useSpendingSummary() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getSummaryData = useCallback(async (request: SummaryRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getSummary(request);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate summary';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { getSummaryData, loading, error };
}

/**
 * Hook for pattern detection
 */
export function usePatternDetection() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const detectSpendingPatterns = useCallback(async (request: PatternsRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await detectPatterns(request);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to detect patterns';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { detectSpendingPatterns, loading, error };
}

/**
 * Hook for checking AI service health
 */
export function useAIHealth() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);

  const check = useCallback(async () => {
    setLoading(true);
    try {
      const healthy = await checkAIHealth();
      setIsHealthy(healthy);
      return healthy;
    } finally {
      setLoading(false);
    }
  }, []);

  return { isHealthy, loading, check };
}
