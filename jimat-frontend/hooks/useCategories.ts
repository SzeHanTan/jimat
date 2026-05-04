/**
 * Custom Hook: useCategories
 * 
 * Handles all category-related API calls and state management:
 * - Fetch all categories
 * - Fetch single category
 * - Create category
 * - Update category
 * - Delete category
 */

import { useState, useCallback } from 'react';
import apiClient from '@/lib/api';
import { Category, CategoryCreate, CategoryUpdate } from '@/types';

interface UseCategoriesReturn {
  // State
  categories: Category[];
  loading: boolean;
  error: string | null;
  
  // Methods
  fetchCategories: () => Promise<void>;
  fetchCategory: (id: number) => Promise<Category>;
  createCategory: (data: CategoryCreate) => Promise<Category>;
  updateCategory: (id: number, data: CategoryUpdate) => Promise<Category>;
  deleteCategory: (id: number) => Promise<void>;
}

export function useCategories(): UseCategoriesReturn {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/api/v1/categories');
      setCategories(response.data);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to fetch categories';
      setError(message);
      console.error('Error fetching categories:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchCategory = useCallback(async (id: number): Promise<Category> => {
    try {
      setError(null);
      const response = await apiClient.get(`/api/v1/categories/${id}`);
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to fetch category';
      setError(message);
      console.error('Error fetching category:', err);
      throw err;
    }
  }, []);

  const createCategory = useCallback(async (data: CategoryCreate): Promise<Category> => {
    try {
      setError(null);
      const response = await apiClient.post('/api/v1/categories', data);
      const newCategory = response.data;
      setCategories((prev) => [...prev, newCategory]);
      return newCategory;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to create category';
      setError(message);
      console.error('Error creating category:', err);
      throw err;
    }
  }, []);

  const updateCategory = useCallback(async (id: number, data: CategoryUpdate): Promise<Category> => {
    try {
      setError(null);
      const response = await apiClient.put(`/api/v1/categories/${id}`, data);
      const updatedCategory = response.data;
      setCategories((prev) =>
        prev.map((category) => (category.id === id ? updatedCategory : category))
      );
      return updatedCategory;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to update category';
      setError(message);
      console.error('Error updating category:', err);
      throw err;
    }
  }, []);

  const deleteCategory = useCallback(async (id: number) => {
    try {
      setError(null);
      await apiClient.delete(`/api/v1/categories/${id}`);
      setCategories((prev) => prev.filter((category) => category.id !== id));
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to delete category';
      setError(message);
      console.error('Error deleting category:', err);
      throw err;
    }
  }, []);

  return {
    categories,
    loading,
    error,
    fetchCategories,
    fetchCategory,
    createCategory,
    updateCategory,
    deleteCategory,
  };
}
