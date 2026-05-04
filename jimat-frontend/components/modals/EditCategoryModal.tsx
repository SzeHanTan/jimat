/**
 * Edit Category Modal Component
 * Allows users to update an existing category
 */

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Category, CategoryUpdate } from '@/types';

interface EditCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  category: Category | null;
  onSubmit: (data: CategoryUpdate) => Promise<void>;
  isLoading?: boolean;
}

export function EditCategoryModal({ isOpen, onClose, category, onSubmit, isLoading = false }: EditCategoryModalProps) {
  const [formData, setFormData] = useState<CategoryUpdate>({
    name: '',
    color: '#3b82f6',
  });
  const [error, setError] = useState('');

  // Initialize form when category changes
  useEffect(() => {
    if (category) {
      setFormData({
        name: category.name,
        color: category.color,
      });
      setError('');
    }
  }, [category, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.name?.trim()) {
      setError('Category name is required');
      return;
    }

    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update category');
    }
  };

  if (!category) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Category</DialogTitle>
          <DialogDescription>Update category details</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-3">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Category Name
            </label>
            <Input
              type="text"
              placeholder="e.g., Groceries"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Color
            </label>
            <div className="flex gap-3 items-center">
              <Input
                type="color"
                value={formData.color || '#3b82f6'}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-20 h-10 p-1 cursor-pointer"
              />
              <div
                className="w-10 h-10 rounded border border-slate-200"
                style={{ backgroundColor: formData.color || '#3b82f6' }}
              />
            </div>
          </div>

          <div className="flex gap-2 justify-end pt-4">
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Updating...' : 'Update Category'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
