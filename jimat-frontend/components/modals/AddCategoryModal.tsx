/**
 * Add Category Modal Component
 * Allows users to create a new expense category
 */

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { CategoryCreate } from '@/types';

interface AddCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CategoryCreate) => Promise<void>;
  isLoading?: boolean;
}

export function AddCategoryModal({ isOpen, onClose, onSubmit, isLoading = false }: AddCategoryModalProps) {
  const [formData, setFormData] = useState<CategoryCreate>({
    name: '',
    color: '#3b82f6',
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.name.trim()) {
      setError('Category name is required');
      return;
    }

    try {
      await onSubmit(formData);
      setFormData({
        name: '',
        color: '#3b82f6',
      });
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create category');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Category</DialogTitle>
          <DialogDescription>Create a new expense category</DialogDescription>
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
              value={formData.name}
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
                value={formData.color}
                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                className="w-20 h-10 p-1 cursor-pointer"
              />
              <div
                className="w-10 h-10 rounded border border-slate-200"
                style={{ backgroundColor: formData.color }}
              />
            </div>
          </div>

          <div className="flex gap-2 justify-end pt-4">
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Category'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
