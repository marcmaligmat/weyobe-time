import { create } from 'zustand';
import { TimeEntry, TimeEntryForm } from '@/types';

interface TimeEntriesStore {
  timeEntries: TimeEntry[];
  isLoading: boolean;
  error: string | null;

  // Actions
  addTimeEntry: (entry: TimeEntry) => void;
  updateTimeEntry: (id: string, updates: Partial<TimeEntry>) => void;
  removeTimeEntry: (id: string) => void;
  setTimeEntries: (entries: TimeEntry[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // API Actions
  fetchTimeEntries: (filters?: { date_from?: string; date_to?: string }) => Promise<void>;
  createManualEntry: (data: TimeEntryForm) => Promise<TimeEntry>;
  submitTimeEntry: (entry: TimeEntry) => Promise<TimeEntry>;
  editTimeEntry: (id: string, data: Partial<TimeEntry>) => Promise<TimeEntry>;
  deleteTimeEntry: (id: string) => Promise<void>;

  // Persistence Actions
  loadFromLocalStorage: () => void;
  syncWithLocalStorage: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const useTimeEntriesStore = create<TimeEntriesStore>((set, get) => ({
  timeEntries: [],
  isLoading: false,
  error: null,

  addTimeEntry: (entry) => {
    set((state) => {
      // Check if entry already exists to avoid duplicates
      const existingIndex = state.timeEntries.findIndex(e => e.id === entry.id);
      if (existingIndex !== -1) {
        // Update existing entry
        const updatedEntries = [...state.timeEntries];
        updatedEntries[existingIndex] = entry;
        return { timeEntries: updatedEntries };
      } else {
        // Add new entry at the beginning (most recent first)
        return { timeEntries: [entry, ...state.timeEntries] };
      }
    });
  },

  updateTimeEntry: (id, updates) => {
    set((state) => ({
      timeEntries: state.timeEntries.map((entry) =>
        entry.id === id ? { ...entry, ...updates } : entry
      ),
    }));
  },

  removeTimeEntry: (id) => {
    set((state) => ({
      timeEntries: state.timeEntries.filter((entry) => entry.id !== id),
    }));
  },

  setTimeEntries: (entries) => {
    set({ timeEntries: entries });
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error });
  },

  fetchTimeEntries: async (filters = {}) => {
    try {
      set({ isLoading: true, error: null });

      const params = new URLSearchParams();
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);

      const response = await fetch(`${API_BASE_URL}/time-tracking/entries/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch time entries: ${response.statusText}`);
      }

      const data = await response.json();
      set({ timeEntries: data.results || data });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to fetch time entries' });
    } finally {
      set({ isLoading: false });
    }
  },

  createManualEntry: async (data) => {
    try {
      set({ isLoading: true, error: null });

      // Convert form data to API format
      const entryData = {
        project_id: data.project_id,
        description: data.description,
        billable: data.billable,
        date: data.manual_entry?.date,
        clock_in: `${data.manual_entry?.date}T${data.manual_entry?.start_time}:00.000Z`,
        clock_out: `${data.manual_entry?.date}T${data.manual_entry?.end_time}:00.000Z`,
        status: 'submitted',
      };

      try {
        const response = await fetch(`${API_BASE_URL}/time-tracking/entries/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(entryData),
        });

        if (response.ok) {
          const newEntry = await response.json();

          // Add to the store
          get().addTimeEntry(newEntry);

          // Save to localStorage
          const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
          storedEntries.unshift(newEntry);
          localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries.slice(0, 100)));

          return newEntry;
        }
      } catch (apiError) {
        console.warn('API call failed, creating entry locally:', apiError);
      }

      // Fallback: Create entry locally if API fails
      const clockIn = new Date(`${data.manual_entry?.date}T${data.manual_entry?.start_time}:00`);
      const clockOut = new Date(`${data.manual_entry?.date}T${data.manual_entry?.end_time}:00`);
      const totalMs = clockOut.getTime() - clockIn.getTime();
      const totalHours = totalMs / (1000 * 60 * 60);

      const localEntry: TimeEntry = {
        id: `manual-${Date.now()}`,
        user_id: 'current-user',
        organization_id: 'current-org',
        date: data.manual_entry?.date || new Date().toISOString().split('T')[0],
        clock_in: entryData.clock_in,
        clock_out: entryData.clock_out,
        break_entries: [],
        project_id: data.project_id,
        description: data.description,
        billable: data.billable,
        status: 'submitted',
        regular_hours: Math.min(totalHours, 8),
        overtime_hours: Math.max(0, totalHours - 8),
        total_hours: Number(totalHours.toFixed(2)),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      // Add to the store
      get().addTimeEntry(localEntry);

      // Save to localStorage
      const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
      storedEntries.unshift(localEntry);
      localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries.slice(0, 100)));

      return localEntry;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create time entry';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  submitTimeEntry: async (entry) => {
    try {
      set({ isLoading: true, error: null });

      const response = await fetch(`${API_BASE_URL}/time-tracking/clock-out/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to clock out: ${response.statusText}`);
      }

      const updatedEntry = await response.json();

      // Update the store
      get().updateTimeEntry(entry.id, updatedEntry);
      get().addTimeEntry(updatedEntry);

      return updatedEntry;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit time entry';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  loadFromLocalStorage: () => {
    try {
      if (typeof window === 'undefined') return;

      const storedEntries = localStorage.getItem('completed-time-entries');
      if (storedEntries) {
        const parsedEntries = JSON.parse(storedEntries);
        // Merge with existing entries, avoiding duplicates
        const existingEntries = get().timeEntries;
        const mergedEntries = [...parsedEntries];

        // Add existing entries that aren't in localStorage
        existingEntries.forEach(entry => {
          if (!mergedEntries.find(e => e.id === entry.id)) {
            mergedEntries.push(entry);
          }
        });

        // Sort by created_at or date, most recent first
        mergedEntries.sort((a, b) => {
          const dateA = new Date(a.created_at || a.date);
          const dateB = new Date(b.created_at || b.date);
          return dateB.getTime() - dateA.getTime();
        });

        set({ timeEntries: mergedEntries });
      }
    } catch (error) {
      console.error('Error loading time entries from localStorage:', error);
    }
  },

  syncWithLocalStorage: () => {
    try {
      if (typeof window === 'undefined') return;

      const currentEntries = get().timeEntries;
      const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');

      // Merge current entries with stored ones
      const allEntries = [...currentEntries];
      storedEntries.forEach((stored: TimeEntry) => {
        if (!allEntries.find(entry => entry.id === stored.id)) {
          allEntries.push(stored);
        }
      });

      // Sort and limit to 100 entries
      allEntries.sort((a, b) => {
        const dateA = new Date(a.created_at || a.date);
        const dateB = new Date(b.created_at || b.date);
        return dateB.getTime() - dateA.getTime();
      });

      const limitedEntries = allEntries.slice(0, 100);

      // Update both store and localStorage
      set({ timeEntries: limitedEntries });
      localStorage.setItem('completed-time-entries', JSON.stringify(limitedEntries));
    } catch (error) {
      console.error('Error syncing with localStorage:', error);
    }
  },

  editTimeEntry: async (id, data) => {
    try {
      set({ isLoading: true, error: null });

      // Check if this is a temporary/local entry (starts with 'temp-' or is a mock entry)
      const isLocalEntry = id.startsWith('temp-') || ['1', '2', '3'].includes(id);

      if (isLocalEntry) {
        // Handle local entry update directly
        console.log('Updating local entry:', id, data);

        const currentEntries = get().timeEntries;
        const entryIndex = currentEntries.findIndex(entry => entry.id === id);

        if (entryIndex !== -1) {
          const updatedEntry = { ...currentEntries[entryIndex], ...data, updated_at: new Date().toISOString() };
          const updatedEntries = [...currentEntries];
          updatedEntries[entryIndex] = updatedEntry;

          set({ timeEntries: updatedEntries, isLoading: false });

          // Update localStorage
          const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
          const storedIndex = storedEntries.findIndex((entry: TimeEntry) => entry.id === id);
          if (storedIndex !== -1) {
            storedEntries[storedIndex] = updatedEntry;
            localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries));
          } else {
            // Add to localStorage if not found
            storedEntries.push(updatedEntry);
            localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries));
          }

          console.log('Local entry updated successfully');
          return updatedEntry;
        } else {
          set({ isLoading: false, error: 'Entry not found' });
          throw new Error('Entry not found');
        }
      }

      // Try API update for real entries
      try {
        const response = await fetch(`${API_BASE_URL}/time-tracking/entries/${id}/`, {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });

        if (!response.ok) {
          throw new Error(`API request failed: ${response.statusText}`);
        }

        const updatedEntry = await response.json();

        // Update the store
        get().updateTimeEntry(id, updatedEntry);

        // Update localStorage
        const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
        const storedIndex = storedEntries.findIndex((entry: TimeEntry) => entry.id === id);
        if (storedIndex !== -1) {
          storedEntries[storedIndex] = updatedEntry;
          localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries));
        }

        set({ isLoading: false });
        return updatedEntry;
      } catch (apiError) {
        console.log('API failed, falling back to local update:', apiError);

        // Fallback to local update
        const currentEntries = get().timeEntries;
        const entryIndex = currentEntries.findIndex(entry => entry.id === id);

        if (entryIndex !== -1) {
          const updatedEntry = { ...currentEntries[entryIndex], ...data, updated_at: new Date().toISOString() };
          const updatedEntries = [...currentEntries];
          updatedEntries[entryIndex] = updatedEntry;

          set({ timeEntries: updatedEntries, isLoading: false });

          // Update localStorage
          const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
          const storedIndex = storedEntries.findIndex((entry: TimeEntry) => entry.id === id);
          if (storedIndex !== -1) {
            storedEntries[storedIndex] = updatedEntry;
            localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries));
          }

          return updatedEntry;
        }
        throw new Error('Entry not found for fallback update');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to edit time entry';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  deleteTimeEntry: async (id) => {
    try {
      set({ isLoading: true, error: null });

      // Check if this is a temporary/local entry (starts with 'temp-' or is a mock entry)
      const isLocalEntry = id.startsWith('temp-') || ['1', '2', '3'].includes(id);

      if (isLocalEntry) {
        // Handle local entry deletion directly
        console.log('Deleting local entry:', id);

        // Remove from store
        get().removeTimeEntry(id);

        // Remove from localStorage
        const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
        const filteredEntries = storedEntries.filter((entry: TimeEntry) => entry.id !== id);
        localStorage.setItem('completed-time-entries', JSON.stringify(filteredEntries));

        console.log('Local entry deleted successfully');
        set({ isLoading: false });
        return;
      }

      // Try API deletion for real entries
      try {
        const response = await fetch(`${API_BASE_URL}/time-tracking/entries/${id}/`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`API delete failed: ${response.statusText}`);
        }
      } catch (apiError) {
        console.log('API delete failed, deleting locally anyway:', apiError);
      }

      // Remove from store (whether API succeeded or failed)
      get().removeTimeEntry(id);

      // Remove from localStorage
      const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
      const filteredEntries = storedEntries.filter((entry: TimeEntry) => entry.id !== id);
      localStorage.setItem('completed-time-entries', JSON.stringify(filteredEntries));

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete time entry';
      set({ error: errorMessage });
      console.error('Delete error:', error);
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },
}));