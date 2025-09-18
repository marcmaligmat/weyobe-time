'use client';

import { AlertTriangle, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface ValidationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  validationErrors: string[];
  onContinue?: () => void;
}

export function ValidationModal({
  open,
  onOpenChange,
  validationErrors,
  onContinue
}: ValidationModalProps) {
  const handleClose = () => {
    onOpenChange(false);
  };

  const handleContinue = () => {
    onContinue?.();
    handleClose();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="flex flex-row items-center gap-3 space-y-0 pb-4">
          <div className="flex items-center justify-center w-10 h-10 bg-amber-100 rounded-full flex-shrink-0">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
          </div>
          <div className="flex-1">
            <DialogTitle className="text-left text-lg font-semibold text-gray-900">
              Required fields missing
            </DialogTitle>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 text-gray-400 hover:text-gray-600"
            onClick={handleClose}
          >
            <X className="w-4 h-4" />
          </Button>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Please complete the following required fields before stopping the timer:
          </p>

          <div className="space-y-2">
            {validationErrors.map((error, index) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-gray-700">{error}</span>
              </div>
            ))}
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              className="flex-1"
              onClick={handleClose}
            >
              OK, I'll complete them
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}