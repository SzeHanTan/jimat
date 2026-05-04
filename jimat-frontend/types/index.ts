/**
 * TypeScript type definitions matching the FastAPI backend schemas
 */

export interface Category {
  id: number;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  color?: string;
}

export interface CategoryUpdate {
  name?: string;
  color?: string;
}

export interface Expense {
  id: number;
  amount: number | string;
  description: string;
  date: string;
  category_id: number;
  created_at: string;
  updated_at: string;
}

export interface ExpenseCreate {
  amount: number | string;
  description: string;
  date: string;
  category_id: number;
}

export interface ExpenseUpdate {
  amount?: number | string;
  description?: string;
  date?: string;
  category_id?: number;
}

export interface ApiError {
  detail: string;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface DateRangeParams {
  start_date: string;
  end_date: string;
}
