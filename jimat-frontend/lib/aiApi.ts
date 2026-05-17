/**
 * AI API Client
 * 
 * Interfaces with jimat-ai service endpoints for:
 * - Document analysis (OCR, text extraction)
 * - Expense categorization with confidence scoring
 * - Insights and analytics
 */

import axios from 'axios';

// Get AI API base URL from environment or default to localhost:8001
const AI_API_BASE_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8001';

const aiClient = axios.create({
  baseURL: AI_API_BASE_URL,
  timeout: 60000, // Longer timeout for AI processing (60 seconds)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling interceptor
aiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (process.env.NODE_ENV === 'development') {
      console.error('AI API Error:', error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Document Analysis
 */

export interface DocumentAnalyzeRequest {
  content_type: 'image' | 'text';
  content: string; // base64 for image, plain text for text
  metadata?: Record<string, any>;
}

export interface DocumentAnalyzeResponse {
  success: boolean;
  extracted_text: string;
  document_type: string;
  confidence: number;
  processing_time_ms: number;
  timestamp: string;
}

export async function analyzeDocument(
  request: DocumentAnalyzeRequest
): Promise<DocumentAnalyzeResponse> {
  const response = await aiClient.post('/api/v1/documents/analyze', request);
  return response.data;
}

/**
 * Expense Categorization
 */

export interface CategorizationRequest {
  description: string;
  amount?: number;
  date?: string;
  user_id?: string;
}

export interface CategorizationResponse {
  success: boolean;
  category: string;
  confidence: number;
  explanation: string;
  alternatives: string[];
  metadata: Record<string, any>;
  processing_time_ms: number;
  timestamp: string;
}

export async function categorizeExpense(
  request: CategorizationRequest
): Promise<CategorizationResponse> {
  const response = await aiClient.post('/api/v1/categorization/categorize', request);
  return response.data;
}

/**
 * Insights - Summary
 */

export interface ExpenseData {
  amount: number;
  date: string; // YYYY-MM-DD
  category?: string;
  description?: string;
}

export interface CategoryBreakdown {
  category: string;
  total: number;
  percentage: number;
  count: number;
  average: number;
  min: number;
  max: number;
}

export interface SummaryRequest {
  expenses: ExpenseData[];
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
}

export interface SummaryResponse {
  success: boolean;
  period: string;
  total_spending: number;
  transaction_count: number;
  average_transaction: number;
  biggest_transaction: number;
  smallest_transaction: number;
  biggest_category?: CategoryBreakdown;
  category_breakdown: CategoryBreakdown[];
  processing_time_ms: number;
  timestamp: string;
}

export async function getSummary(request: SummaryRequest): Promise<SummaryResponse> {
  const response = await aiClient.post('/api/v1/insights/summary', request);
  return response.data;
}

/**
 * Insights - Patterns
 */

export interface SpendingPattern {
  pattern_type: string;
  description: string;
  severity: number;
  confidence: number;
}

export interface PatternsRequest {
  expenses: ExpenseData[];
  baseline_days?: number;
}

export interface PatternsResponse {
  success: boolean;
  patterns_detected: number;
  patterns: SpendingPattern[];
  processing_time_ms: number;
  timestamp: string;
}

export async function detectPatterns(
  request: PatternsRequest
): Promise<PatternsResponse> {
  const response = await aiClient.post('/api/v1/insights/patterns', request);
  return response.data;
}

/**
 * Health check
 */
export async function checkAIHealth(): Promise<boolean> {
  try {
    const response = await aiClient.get('/health');
    return response.status === 200;
  } catch (error) {
    return false;
  }
}
