'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, FolderOpen } from 'lucide-react';

interface ManualEntryFormData {
  date: string;
  startTime: string;
  endTime: string;
  projectId: string;
  description: string;
  billable: boolean;
}

interface Project {
  id: string;
  name: string;
  billable: boolean;
  department: string;
}

interface ManualEntryFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projects: Project[];
  onSubmit: (data: ManualEntryFormData) => Promise<void>;
}

export function ManualEntryForm({
  open,
  onOpenChange,
  projects,
  onSubmit,
}: ManualEntryFormProps) {
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<ManualEntryFormData>({
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
      startTime: '09:00',
      endTime: '17:00',
      projectId: '',
      description: '',
      billable: false,
    },
  });

  const selectedProject = projects.find(
    (p) => p.id === form.watch('projectId')
  );

  // Update billable status when project changes
  const handleProjectChange = (projectId: string) => {
    const project = projects.find((p) => p.id === projectId);
    if (project) {
      form.setValue('billable', project.billable);
    }
  };

  const handleSubmit = async (data: ManualEntryFormData) => {
    try {
      setIsLoading(true);
      await onSubmit(data);
      form.reset();
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to submit manual entry:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateHours = () => {
    const startTime = form.watch('startTime');
    const endTime = form.watch('endTime');

    if (startTime && endTime) {
      const start = new Date(`2000-01-01T${startTime}:00`);
      const end = new Date(`2000-01-01T${endTime}:00`);

      if (end > start) {
        const diffMs = end.getTime() - start.getTime();
        const hours = diffMs / (1000 * 60 * 60);
        return hours.toFixed(2);
      }
    }

    return '0.00';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md mx-auto max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Add Manual Time Entry
          </DialogTitle>
          <DialogDescription>
            Add a time entry for work completed outside of the timer.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            {/* Date */}
            <FormField
              control={form.control}
              name="date"
              rules={{ required: 'Date is required' }}
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="flex items-center">
                    <Calendar className="w-4 h-4 mr-1" />
                    Date
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="date"
                      {...field}
                      className="text-base md:text-sm"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Time Range */}
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="startTime"
                rules={{ required: 'Start time is required' }}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Start Time</FormLabel>
                    <FormControl>
                      <Input
                        type="time"
                        {...field}
                        className="text-base md:text-sm"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="endTime"
                rules={{ required: 'End time is required' }}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>End Time</FormLabel>
                    <FormControl>
                      <Input
                        type="time"
                        {...field}
                        className="text-base md:text-sm"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Duration Display */}
            <div className="bg-gray-50 p-3 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Duration:</span>
                <span className="font-medium text-lg">
                  {calculateHours()} hours
                </span>
              </div>
            </div>

            {/* Project Selection */}
            <FormField
              control={form.control}
              name="projectId"
              rules={{ required: 'Project is required' }}
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="flex items-center">
                    <FolderOpen className="w-4 h-4 mr-1" />
                    Project
                  </FormLabel>
                  <Select
                    onValueChange={(value) => {
                      field.onChange(value);
                      handleProjectChange(value);
                    }}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger className="text-base md:text-sm">
                        <SelectValue placeholder="Select a project" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {projects.map((project) => (
                        <SelectItem key={project.id} value={project.id}>
                          <div className="flex items-center justify-between w-full">
                            <div>
                              <div className="font-medium">{project.name}</div>
                              <div className="text-xs text-gray-500">
                                {project.department}
                              </div>
                            </div>
                            <Badge
                              variant={project.billable ? "default" : "secondary"}
                              className="ml-2 text-xs"
                            >
                              {project.billable ? 'Billable' : 'Non-billable'}
                            </Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Project Info Display */}
            {selectedProject && (
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm">{selectedProject.name}</p>
                    <p className="text-xs text-gray-600">{selectedProject.department}</p>
                  </div>
                  <Badge
                    variant={selectedProject.billable ? "default" : "secondary"}
                    className="text-xs"
                  >
                    {selectedProject.billable ? 'Billable' : 'Non-billable'}
                  </Badge>
                </div>
              </div>
            )}

            {/* Description */}
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe the work performed..."
                      className="resize-none text-base md:text-sm"
                      rows={3}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter className="flex flex-col sm:flex-row gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="w-full sm:w-auto"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full sm:w-auto"
              >
                {isLoading ? 'Adding...' : 'Add Entry'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}