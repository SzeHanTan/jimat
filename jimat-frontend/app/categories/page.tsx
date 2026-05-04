'use client';

import { useEffect, useState } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Edit2, Trash2 } from "lucide-react";
import { useCategories } from '@/hooks/useCategories';
import { useExpenses } from '@/hooks/useExpenses';
import { AddCategoryModal } from '@/components/modals/AddCategoryModal';
import { EditCategoryModal } from '@/components/modals/EditCategoryModal';
import { DeleteConfirmDialog } from '@/components/modals/DeleteConfirmDialog';
import { Category, CategoryCreate, CategoryUpdate } from '@/types';

export default function CategoriesPage() {
  const { categories, loading: categoriesLoading, error: categoriesError, fetchCategories, createCategory, updateCategory, deleteCategory } = useCategories();
  const { expenses, fetchExpenses } = useExpenses();
  
  const [mounted, setMounted] = useState(false);
  
  // Modal state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);

  // Fetch data on mount
  useEffect(() => {
    setMounted(true);
    fetchCategories();
    fetchExpenses();
  }, []);

  // Count expenses per category
  const getExpenseCount = (categoryId: number) => {
    return expenses.filter(e => e.category_id === categoryId).length;
  };

  const handleAddCategory = async (data: CategoryCreate) => {
    setIsModalLoading(true);
    try {
      await createCategory(data);
      await fetchCategories();
      setIsAddModalOpen(false);
    } finally {
      setIsModalLoading(false);
    }
  };

  const handleEditCategory = async (data: CategoryUpdate) => {
    if (!selectedCategory) return;
    setIsModalLoading(true);
    try {
      await updateCategory(selectedCategory.id, data);
      await fetchCategories();
      setIsEditModalOpen(false);
      setSelectedCategory(null);
    } finally {
      setIsModalLoading(false);
    }
  };

  const handleDeleteCategory = async () => {
    if (!selectedCategory) return;
    setIsModalLoading(true);
    try {
      await deleteCategory(selectedCategory.id);
      await fetchCategories();
      setIsDeleteModalOpen(false);
      setSelectedCategory(null);
    } finally {
      setIsModalLoading(false);
    }
  };

  const openEditModal = (category: Category) => {
    setSelectedCategory(category);
    setIsEditModalOpen(true);
  };

  const openDeleteModal = (category: Category) => {
    setSelectedCategory(category);
    setIsDeleteModalOpen(true);
  };

  if (!mounted) return null;

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Categories</h1>
        <Button 
          className="bg-blue-600 hover:bg-blue-700 text-white gap-2"
          onClick={() => setIsAddModalOpen(true)}
        >
          <Plus className="w-5 h-5" />
          New Category
        </Button>
      </div>

      {/* Error Messages */}
      {categoriesError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{categoriesError}</p>
        </div>
      )}

      {/* Categories Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {categoriesLoading ? (
          // Loading skeleton
          [...Array(3)].map((_, i) => (
            <Card key={i} className="p-6 bg-white animate-pulse">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3 w-full">
                  <div className="w-12 h-12 rounded-lg bg-slate-200"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-slate-200 rounded w-24 mb-2"></div>
                    <div className="h-3 bg-slate-200 rounded w-32"></div>
                  </div>
                </div>
              </div>
            </Card>
          ))
        ) : categories.length > 0 ? (
          categories.map((category: Category) => {
            const expenseCount = getExpenseCount(category.id);
            return (
              <Card
                key={category.id}
                className="p-4 sm:p-6 bg-white hover:shadow-lg transition cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg flex-shrink-0"
                      style={{ backgroundColor: category.color }}
                    ></div>
                    <div className="min-w-0">
                      <h3 className="font-semibold text-slate-900 text-sm sm:text-base truncate">
                        {category.name}
                      </h3>
                      <p className="text-xs sm:text-sm text-slate-500">
                        {expenseCount} {expenseCount === 1 ? 'expense' : 'expenses'}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-1 flex-shrink-0">
                    <button 
                      onClick={() => openEditModal(category)}
                      className="p-2 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-lg transition"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => openDeleteModal(category)}
                      className="p-2 text-slate-500 hover:text-red-600 hover:bg-slate-100 rounded-lg transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="text-xs text-slate-500">
                  Created: {new Date(category.created_at).toLocaleDateString()}
                </div>
              </Card>
            );
          })
        ) : (
          <div className="col-span-full text-center py-12">
            <p className="text-slate-500">No categories yet. Create one to get started!</p>
          </div>
        )}
      </div>

      {/* Modals */}
      <AddCategoryModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={handleAddCategory}
        isLoading={isModalLoading}
      />

      <EditCategoryModal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedCategory(null);
        }}
        category={selectedCategory}
        onSubmit={handleEditCategory}
        isLoading={isModalLoading}
      />

      <DeleteConfirmDialog
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setSelectedCategory(null);
        }}
        title="Delete Category"
        description="Are you sure you want to delete this category?"
        itemName={selectedCategory ? selectedCategory.name : ''}
        onConfirm={handleDeleteCategory}
        isLoading={isModalLoading}
      />
    </div>
  );
}
