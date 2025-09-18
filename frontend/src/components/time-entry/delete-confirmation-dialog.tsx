'use client';

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { AlertTriangle, Trash2 } from 'lucide-react';
import { TimeEntry } from '@/types';
import { getProjectName } from '@/lib/data/projects';
import { formatTime, formatDate } from '@/lib/utils';

interface DeleteConfirmationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  entry: TimeEntry | null;
  onConfirm: (id: string) => Promise<void>;
  isLoading?: boolean;
}

export function DeleteConfirmationDialog({
  open,
  onOpenChange,
  entry,
  onConfirm,
  isLoading = false,
}: DeleteConfirmationDialogProps) {
  const handleConfirm = async () => {
    if (!entry) return;

    try {
      await onConfirm(entry.id);
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to delete entry:', error);
      // Keep dialog open on error to show user can retry
    }
  };

  if (!entry) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md mx-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center text-red-600">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Delete Time Entry
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to delete this time entry? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>

        {/* Entry Details */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900">Project:</span>
            <span className="text-sm text-gray-700">
              {getProjectName(entry.project_id)}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900">Date:</span>
            <span className="text-sm text-gray-700">
              {formatDate(entry.date, 'short')}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900">Duration:</span>
            <span className="text-sm text-gray-700 font-mono">
              {formatTime((entry.total_hours || 0) * 3600)}
            </span>
          </div>

          {entry.description && (
            <div className="pt-2 border-t border-gray-200">
              <span className="text-sm font-medium text-gray-900">Description:</span>
              <p className="text-sm text-gray-700 mt-1">
                {entry.description}
              </p>
            </div>
          )}
        </div>

        <DialogFooter className="flex flex-col sm:flex-row gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="w-full sm:w-auto"
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={isLoading}
            className="w-full sm:w-auto"
          >
            {isLoading ? (
              <>
                <Trash2 className="w-4 h-4 mr-2 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Entry
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}