'use client';

import { useState, useEffect } from 'react';
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
import { Calendar, Clock, FolderOpen, Edit } from 'lucide-react';
import { TimeEntry } from '@/types';
import { getProjectsForForm } from '@/lib/data/projects';

interface EditEntryFormData {
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

interface EditEntryFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  entry: TimeEntry | null;
  onSubmit: (id: string, data: Partial<TimeEntry>) => Promise<void>;
}

export function EditEntryForm({
  open,
  onOpenChange,
  entry,
  onSubmit,
}: EditEntryFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const projects = getProjectsForForm();

  const form = useForm<EditEntryFormData>({
    defaultValues: {
      date: '',
      startTime: '',
      endTime: '',
      projectId: '',
      description: '',
      billable: false,
    },
  });

  // Update form when entry changes
  useEffect(() => {
    if (entry && open) {
      // Parse clock_in and clock_out times
      const clockInDate = new Date(entry.clock_in);
      const clockOutDate = entry.clock_out ? new Date(entry.clock_out) : new Date();

      form.reset({
        date: entry.date,
        startTime: clockInDate.toTimeString().slice(0, 5), // HH:MM format
        endTime: clockOutDate.toTimeString().slice(0, 5), // HH:MM format
        projectId: entry.project_id || '',
        description: entry.description || '',
        billable: entry.billable,
      });
    }
  }, [entry, open, form]);

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

  const handleSubmit = async (data: EditEntryFormData) => {
    if (!entry) return;

    try {
      setIsLoading(true);

      // Convert form data to API format
      const updateData: Partial<TimeEntry> = {
        project_id: data.projectId,
        description: data.description,
        billable: data.billable,
        date: data.date,
        clock_in: `${data.date}T${data.startTime}:00.000Z`,
        clock_out: `${data.date}T${data.endTime}:00.000Z`,
      };

      // Calculate total hours
      const startDateTime = new Date(`${data.date}T${data.startTime}:00`);
      const endDateTime = new Date(`${data.date}T${data.endTime}:00`);
      const diffMs = endDateTime.getTime() - startDateTime.getTime();
      const totalHours = diffMs / (1000 * 60 * 60);

      updateData.total_hours = Number(totalHours.toFixed(2));
      updateData.regular_hours = Math.min(totalHours, 8);
      updateData.overtime_hours = Math.max(0, totalHours - 8);

      await onSubmit(entry.id, updateData);
      onOpenChange(false);
    } catch (error) {
      console.error('Failed to update time entry:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateHours = () => {
    const startTime = form.watch('startTime');
    const endTime = form.watch('endTime');
    const date = form.watch('date');

    if (startTime && endTime && date) {
      const start = new Date(`${date}T${startTime}:00`);
      const end = new Date(`${date}T${endTime}:00`);

      if (end > start) {
        const diffMs = end.getTime() - start.getTime();
        const hours = diffMs / (1000 * 60 * 60);
        return hours.toFixed(2);
      }
    }

    return '0.00';
  };

  if (!entry) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md mx-auto max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Edit className="w-5 h-5 mr-2" />
            Edit Time Entry
          </DialogTitle>
          <DialogDescription>
            Update the details of this time entry.
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
                    value={field.value}
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

            {/* Billable Status */}
            <FormField
              control={form.control}
              name="billable"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <input
                      type="checkbox"
                      checked={field.value}
                      onChange={(e) => field.onChange(e.target.checked)}
                      className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary focus:ring-2"
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>
                      Billable time
                    </FormLabel>
                    <p className="text-xs text-gray-500">
                      This time entry will be marked as billable to the client
                    </p>
                  </div>
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
                {isLoading ? 'Updating...' : 'Update Entry'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}