'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { TimerWidget } from '@/components/timer/timer-widget';
import { ManualEntryForm } from '@/components/time-entry/manual-entry-form';
import { EditEntryForm } from '@/components/time-entry/edit-entry-form';
import { DeleteConfirmationDialog } from '@/components/time-entry/delete-confirmation-dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useTimerStore } from '@/lib/stores/timer';
import { useTimeEntriesStore } from '@/lib/stores/time-entries';
import { formatTime, formatDate } from '@/lib/utils';
import { TimeEntryForm, TimeEntry } from '@/types';
import {
  Calendar,
  Clock,
  FolderOpen,
  Plus,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Search,
  Loader2,
} from 'lucide-react';
import { getProjectName, getProjectsForForm } from '@/lib/data/projects';

// Mock data for recent time entries
const mockTimeEntries = [
  {
    id: '1',
    date: new Date().toISOString(),
    clockIn: '09:00:00',
    clockOut: '17:30:00',
    projectName: 'Website Redesign',
    description: 'Frontend development work',
    status: 'approved',
    totalHours: 8.5,
    overtimeHours: 0.5,
    billable: true,
  },
  {
    id: '2',
    date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    clockIn: '08:30:00',
    clockOut: '17:00:00',
    projectName: 'Mobile App',
    description: 'Bug fixes and testing',
    status: 'pending',
    totalHours: 8.5,
    overtimeHours: 0.5,
    billable: true,
  },
  {
    id: '3',
    date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    clockIn: '09:15:00',
    clockOut: '17:45:00',
    projectName: 'Internal Tools',
    description: 'Dashboard improvements',
    status: 'submitted',
    totalHours: 8.5,
    overtimeHours: 0.5,
    billable: false,
  },
];


export default function TimerPage() {
  const { currentProject, setCurrentProject, isActive, elapsedTime, description } = useTimerStore();
  const {
    timeEntries,
    isLoading: entriesLoading,
    fetchTimeEntries,
    createManualEntry,
    addTimeEntry,
    loadFromLocalStorage,
    syncWithLocalStorage,
    editTimeEntry,
    deleteTimeEntry
  } = useTimeEntriesStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [showManualEntryForm, setShowManualEntryForm] = useState(false);
  const [editingEntry, setEditingEntry] = useState<TimeEntry | null>(null);
  const [deletingEntry, setDeletingEntry] = useState<TimeEntry | null>(null);

  // Load from localStorage and fetch time entries on mount
  useEffect(() => {
    loadFromLocalStorage();
    fetchTimeEntries();
  }, [fetchTimeEntries, loadFromLocalStorage]);

  // Listen for new time entries from clock out
  useEffect(() => {
    const handleTimeEntrySubmitted = (event: CustomEvent) => {
      console.log('Timer page received time entry submitted event:', event.detail);
      addTimeEntry(event.detail);
      syncWithLocalStorage(); // Sync with localStorage when new entry is added
      // Also refresh the entries to ensure we have the latest data
      fetchTimeEntries();
    };

    window.addEventListener('timeEntrySubmitted', handleTimeEntrySubmitted as EventListener);
    return () => {
      window.removeEventListener('timeEntrySubmitted', handleTimeEntrySubmitted as EventListener);
    };
  }, [addTimeEntry, fetchTimeEntries, syncWithLocalStorage]);

  const allProjects = getProjectsForForm();
  const filteredProjects = allProjects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.department.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'submitted': return 'bg-blue-100 text-blue-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'tracking': return 'bg-emerald-100 text-emerald-800 animate-pulse';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleManualEntrySubmit = async (data: {
    date: string;
    startTime: string;
    endTime: string;
    projectId: string;
    description: string;
    billable: boolean;
  }) => {
    const formData: TimeEntryForm = {
      project_id: data.projectId,
      description: data.description,
      billable: data.billable,
      manual_entry: {
        date: data.date,
        start_time: data.startTime,
        end_time: data.endTime,
        break_duration: 0,
      },
    };

    await createManualEntry(formData);
  };

  const handleEditEntry = async (id: string, data: Partial<TimeEntry>) => {
    await editTimeEntry(id, data);
    setEditingEntry(null);
  };

  const handleDeleteEntry = async (id: string) => {
    await deleteTimeEntry(id);
    setDeletingEntry(null);
  };

  const handleEditClick = (entry: any) => {
    console.log('handleEditClick called with entry:', entry);
    try {
      // Convert display entry to TimeEntry format if needed
      const timeEntry: TimeEntry = {
        id: entry.id,
        user_id: entry.user_id || 'current-user',
        organization_id: entry.organization_id || 'current-org',
        date: entry.date,
        clock_in: entry.clock_in || `${entry.date}T${entry.clockIn}:00.000Z`,
        clock_out: entry.clock_out || (entry.clockOut !== 'Active' ? `${entry.date}T${entry.clockOut}:00.000Z` : undefined),
        break_entries: entry.break_entries || [],
        project_id: entry.project_id,
        department_id: entry.department_id,
        description: entry.description,
        billable: entry.billable,
        status: entry.status,
        regular_hours: entry.regular_hours || 0,
        overtime_hours: entry.overtime_hours || 0,
        total_hours: entry.total_hours || entry.totalHours || 0,
        approval_notes: entry.approval_notes,
        approved_by: entry.approved_by,
        approved_at: entry.approved_at,
        created_at: entry.created_at || new Date().toISOString(),
        updated_at: entry.updated_at || new Date().toISOString(),
      };
      console.log('Setting editing entry:', timeEntry);
      setEditingEntry(timeEntry);
    } catch (error) {
      console.error('Error in handleEditClick:', error);
    }
  };

  const handleDeleteClick = (entry: any) => {
    console.log('handleDeleteClick called with entry:', entry);
    try {
      // Convert display entry to TimeEntry format if needed
      const timeEntry: TimeEntry = {
        id: entry.id,
        user_id: entry.user_id || 'current-user',
        organization_id: entry.organization_id || 'current-org',
        date: entry.date,
        clock_in: entry.clock_in || `${entry.date}T${entry.clockIn}:00.000Z`,
        clock_out: entry.clock_out || (entry.clockOut !== 'Active' ? `${entry.date}T${entry.clockOut}:00.000Z` : undefined),
        break_entries: entry.break_entries || [],
        project_id: entry.project_id,
        department_id: entry.department_id,
        description: entry.description,
        billable: entry.billable,
        status: entry.status,
        regular_hours: entry.regular_hours || 0,
        overtime_hours: entry.overtime_hours || 0,
        total_hours: entry.total_hours || entry.totalHours || 0,
        approval_notes: entry.approval_notes,
        approved_by: entry.approved_by,
        approved_at: entry.approved_at,
        created_at: entry.created_at || new Date().toISOString(),
        updated_at: entry.updated_at || new Date().toISOString(),
      };
      console.log('Setting deleting entry:', timeEntry);
      setDeletingEntry(timeEntry);
    } catch (error) {
      console.error('Error in handleDeleteClick:', error);
    }
  };

  // Use real time entries if available, fallback to mock data
  const displayTimeEntries = timeEntries.length > 0 ? timeEntries : mockTimeEntries;

  // Create a virtual entry for the current active timer if running
  const currentTimerEntry = isActive ? {
    id: 'current-timer',
    date: new Date().toISOString(),
    clockIn: new Date(Date.now() - elapsedTime * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
    clockOut: 'Active',
    projectName: getProjectName(currentProject?.id),
    project_id: currentProject?.id,
    description: description || 'Currently tracking...',
    status: 'tracking',
    totalHours: elapsedTime / 3600,
    total_hours: elapsedTime / 3600,
    overtimeHours: 0,
    billable: currentProject?.billable || false,
  } : null;

  // Combine current timer with historical entries
  const allEntries = currentTimerEntry ? [currentTimerEntry, ...displayTimeEntries] : displayTimeEntries;

  // Calculate total weekly hours
  const calculateWeeklyTotal = () => {
    const now = new Date();
    const startOfWeek = new Date(now.setDate(now.getDate() - now.getDay()));
    const endOfWeek = new Date(now.setDate(now.getDate() - now.getDay() + 6));

    return displayTimeEntries
      .filter(entry => {
        const entryDate = new Date(entry.date);
        return entryDate >= startOfWeek && entryDate <= endOfWeek;
      })
      .reduce((total, entry) => {
        return total + ((entry as any).totalHours || (entry as any).total_hours || 0);
      }, 0);
  };

  const weeklyTotalHours = calculateWeeklyTotal();

  // Add current active timer to the total
  const currentActiveHours = isActive ? elapsedTime / 3600 : 0;
  const totalHoursWithActive = weeklyTotalHours + currentActiveHours;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Main Timer Widget */}
        <div className="w-full">
          <TimerWidget />
        </div>

        {/* Time Entries List */}
        <div className="bg-white border border-gray-200 rounded-lg">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">This week</h3>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">Total: <strong>{formatTime(totalHoursWithActive * 3600)}</strong></span>
              <Button
                size="sm"
                onClick={() => setShowManualEntryForm(true)}
                className="text-xs font-medium"
              >
                <Plus className="w-4 h-4 mr-1" />
                ADD TIME
              </Button>
            </div>
          </div>

          {/* Table Header - Desktop */}
          <div className="hidden md:grid grid-cols-12 gap-4 px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100">
            <div className="col-span-5">PROJECT</div>
            <div className="col-span-3">DESCRIPTION</div>
            <div className="col-span-2">TIME</div>
            <div className="col-span-2">STATUS</div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-gray-100">
            {entriesLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin mr-2" />
                <span>Loading time entries...</span>
              </div>
            ) : allEntries.length > 0 ? (
              allEntries.map((entry) => (
                <div key={entry.id} className="hover:bg-gray-50 transition-colors">
                  {/* Desktop View */}
                  <div className="hidden md:grid grid-cols-12 gap-4 px-4 py-3">
                    {/* Project */}
                    <div className="col-span-5 flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${entry.status === 'tracking' ? 'bg-emerald-500 animate-pulse' : 'bg-blue-500'}`}></div>
                      <div>
                        <div className="font-medium text-sm text-gray-900">
                          {(entry as any).projectName || getProjectName((entry as any).project_id) || 'No Project'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatDate(entry.date, 'short')}
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="col-span-3">
                      <div className="text-sm text-gray-700">
                        {entry.description || 'No description'}
                      </div>
                    </div>

                    {/* Time */}
                    <div className="col-span-2">
                      <div className="text-sm font-mono text-gray-900">
                        {formatTime(((entry as any).totalHours || (entry as any).total_hours || 0) * 3600)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {(entry as any).clockIn || new Date((entry as any).clock_in).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - {(entry as any).clockOut || ((entry as any).clock_out ? new Date((entry as any).clock_out).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'Active')}
                      </div>
                    </div>

                    {/* Status */}
                    <div className="col-span-2 flex items-center justify-between">
                      <Badge className={`text-xs ${getStatusColor(entry.status)}`}>
                        {entry.status}
                      </Badge>
                      <div className="flex items-center space-x-1">
                        {entry.status !== 'tracking' && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('Edit clicked for entry:', entry.id);
                                handleEditClick(entry);
                              }}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 hover:text-red-600"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('Delete clicked for entry:', entry.id);
                                handleDeleteClick(entry);
                              }}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Mobile View */}
                  <div className="md:hidden px-4 py-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        <div className={`w-3 h-3 rounded-full mt-1 ${entry.status === 'tracking' ? 'bg-emerald-500 animate-pulse' : 'bg-blue-500'}`}></div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-sm text-gray-900">
                            {(entry as any).projectName || getProjectName((entry as any).project_id) || 'No Project'}
                          </div>
                          <div className="text-sm text-gray-700 mt-1">
                            {entry.description || 'No description'}
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span>{formatDate(entry.date, 'short')}</span>
                            <span className="font-mono">
                              {formatTime(((entry as any).totalHours || (entry as any).total_hours || 0) * 3600)}
                            </span>
                            <Badge className={`text-xs ${getStatusColor(entry.status)}`}>
                              {entry.status}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1 ml-2">
                        {entry.status !== 'tracking' && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('Edit clicked for entry (mobile):', entry.id);
                                handleEditClick(entry);
                              }}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0 hover:text-red-600"
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log('Delete clicked for entry (mobile):', entry.id);
                                handleDeleteClick(entry);
                              }}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Let's start tracking!</h3>
                <p className="text-gray-500 mb-4">
                  Install Clockify and track time anywhere.
                </p>
                <div className="flex justify-center gap-2">
                  <Button variant="outline" size="sm">
                    Enable timesheet mode
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Manual Entry Form */}
      <ManualEntryForm
        open={showManualEntryForm}
        onOpenChange={setShowManualEntryForm}
        projects={allProjects}
        onSubmit={handleManualEntrySubmit}
      />

      {/* Edit Entry Form */}
      <EditEntryForm
        open={!!editingEntry}
        onOpenChange={(open) => !open && setEditingEntry(null)}
        entry={editingEntry}
        onSubmit={handleEditEntry}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmationDialog
        open={!!deletingEntry}
        onOpenChange={(open) => !open && setDeletingEntry(null)}
        entry={deletingEntry}
        onConfirm={handleDeleteEntry}
        isLoading={entriesLoading}
      />
    </DashboardLayout>
  );
}