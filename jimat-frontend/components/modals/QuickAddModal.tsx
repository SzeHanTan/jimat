/**
 * Quick Add Expense Modal Component
 * Simplified form for quickly adding expenses from anywhere in the app
 */

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ExpenseCreate, Category } from '@/types';

interface QuickAddModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: Category[];
  onSubmit: (data: ExpenseCreate) => Promise<void>;
  isLoading?: boolean;
}

export function QuickAddModal({ isOpen, onClose, categories, onSubmit, isLoading = false }: QuickAddModalProps) {
  const [formData, setFormData] = useState<ExpenseCreate>({
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    category_id: 0,
  });
  const [error, setError] = useState('');

  // Reset form when modal opens
  useEffect(() => {
    if (isOpen) {
      setFormData({
        amount: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        category_id: 0,
      });
      setError('');
    }
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.description.trim()) {
      setError('Description is required');
      return;
    }
    if (!formData.amount || parseFloat(String(formData.amount)) <= 0) {
      setError('Amount must be greater than 0');
      return;
    }
    if (formData.category_id === 0) {
      setError('Please select a category');
      return;
    }

    try {
      await onSubmit(formData);
      setFormData({
        amount: '',
        description: '',
        date: new Date().toISOString().split('T')[0],
        category_id: 0,
      });
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create expense');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle>Quick Add Expense</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded p-3">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Description
            </label>
            <Input
              type="text"
              placeholder="What did you spend on?"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              autoFocus
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Amount
              </label>
              <Input
                type="number"
                placeholder="0.00"
                min="0"
                step="0.01"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Category
              </label>
              <Select
                value={String(formData.category_id || 0)}
                onValueChange={(value) => {
                  const id = value ? parseInt(value) : 0;
                  setFormData({ ...formData, category_id: id });
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Pick one" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={String(cat.id)}>
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-2 justify-end pt-2">
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} className="bg-blue-600 hover:bg-blue-700">
              {isLoading ? 'Adding...' : 'Add'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
