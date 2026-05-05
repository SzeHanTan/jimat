/**
 * Add Expense Modal Component
 * Allows users to create a new expense
 */

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ExpenseCreate, Category } from '@/types';

interface AddExpenseModalProps {
  isOpen: boolean;
  onClose: () => void;
  categories: Category[];
  onSubmit: (data: ExpenseCreate) => Promise<void>;
  isLoading?: boolean;
}

export function AddExpenseModal({ isOpen, onClose, categories, onSubmit, isLoading = false }: AddExpenseModalProps) {
  const [formData, setFormData] = useState<ExpenseCreate>({
    amount: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    category_id: 0,
  });
  const [error, setError] = useState('');

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
    if (!formData.date) {
      setError('Date is required');
      return;
    }

    try {
      // Convert amount to number for submission
      const submitData: ExpenseCreate = {
        amount: parseFloat(String(formData.amount)),
        description: formData.description,
        date: formData.date,
        category_id: formData.category_id,
      };
      await onSubmit(submitData);
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
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add New Expense</DialogTitle>
          <DialogDescription>Create a new expense record</DialogDescription>
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
            <Textarea
              placeholder="e.g., Lunch at restaurant"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="resize-none"
            />
          </div>

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
                <SelectValue placeholder="Select a category" />
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

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Date
            </label>
            <Input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
            />
          </div>

          <div className="flex gap-2 justify-end pt-4">
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Expense'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
