import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { TimerState, BreakType, Project, TimeEntry } from '@/types';
import { getProjectById } from '@/lib/data/projects';

interface TimerStore extends TimerState {
  // Additional state
  currentTimeEntry: TimeEntry | null;
  breakStartTime?: string;
  description: string;

  // Actions
  startTimer: (projectId?: string) => void;
  stopTimer: () => Promise<{ success: boolean; errors?: string[] }>;
  pauseTimer: () => void;
  resumeTimer: () => void;
  startBreak: (breakType: BreakType) => void;
  endBreak: () => void;
  setCurrentProject: (project: Project | null) => void;
  setDescription: (description: string) => void;
  updateElapsedTime: () => void;
  resetTimer: () => void;
  validateTimerFields: () => string[];
}

export const useTimerStore = create<TimerStore>()(
  persist(
    (set, get) => ({
      // Initial state
      isActive: false,
      isPaused: false,
      startTime: undefined,
      pausedTime: undefined,
      currentProject: undefined,
      currentBreakType: undefined,
      elapsedTime: 0,
      currentTimeEntry: null,
      breakStartTime: undefined,
      description: '',

      startTimer: async (projectId) => {
        const now = new Date().toISOString();
        console.log('Timer store: Starting timer with project:', projectId);

        try {
          // Submit clock in to backend
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/time-tracking/clock-in/`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              project_id: projectId,
              description: '',
            }),
          });

          if (response.ok) {
            const timeEntry = await response.json();

            set({
              isActive: true,
              isPaused: false,
              startTime: now,
              pausedTime: undefined,
              elapsedTime: 0,
              currentTimeEntry: timeEntry,
              currentBreakType: undefined,
            });
          } else {
            // Fallback to local creation if API fails
            const newTimeEntry: TimeEntry = {
              id: `temp-${Date.now()}`,
              user_id: 'current-user',
              organization_id: 'current-org',
              date: now.split('T')[0],
              clock_in: now,
              break_entries: [],
              project_id: projectId,
              billable: false,
              status: 'draft',
              regular_hours: 0,
              overtime_hours: 0,
              total_hours: 0,
              created_at: now,
              updated_at: now,
            };

            set({
              isActive: true,
              isPaused: false,
              startTime: now,
              pausedTime: undefined,
              elapsedTime: 0,
              currentTimeEntry: newTimeEntry,
              currentBreakType: undefined,
            });
          }
        } catch (error) {
          console.error('Failed to clock in:', error);
          // Fallback to local creation
          const newTimeEntry: TimeEntry = {
            id: `temp-${Date.now()}`,
            user_id: 'current-user',
            organization_id: 'current-org',
            date: now.split('T')[0],
            clock_in: now,
            break_entries: [],
            project_id: projectId,
            billable: false,
            status: 'draft',
            regular_hours: 0,
            overtime_hours: 0,
            total_hours: 0,
            created_at: now,
            updated_at: now,
          };

          set({
            isActive: true,
            isPaused: false,
            startTime: now,
            pausedTime: undefined,
            elapsedTime: 0,
            currentTimeEntry: newTimeEntry,
            currentBreakType: undefined,
          });
        }
      },

      stopTimer: async () => {
        const state = get();

        // Validate required fields
        const validationErrors = state.validateTimerFields();
        if (validationErrors.length > 0) {
          return { success: false, errors: validationErrors };
        }

        if (!state.currentTimeEntry) {
          console.log('Timer store: No current time entry to stop');
          return { success: false, errors: ['No active timer to stop'] };
        }

        console.log('Timer store: Stopping timer for entry:', state.currentTimeEntry.id);

        try {
          // Submit to backend
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/time-tracking/clock-out/`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              description: state.description,
            }),
          });

          if (response.ok) {
            const submittedEntry = await response.json();

            // Update submitted entry with description
            const finalEntry = {
              ...submittedEntry,
              description: state.description,
            };

            // Save to localStorage for persistence
            const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
            storedEntries.unshift(finalEntry);
            localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries.slice(0, 100))); // Keep last 100 entries

            // Notify time entries store to refresh
            if (typeof window !== 'undefined') {
              console.log('Timer store dispatching timeEntrySubmitted event:', finalEntry);
              window.dispatchEvent(new CustomEvent('timeEntrySubmitted', {
                detail: finalEntry
              }));
            }

            set({
              isActive: false,
              isPaused: false,
              startTime: undefined,
              pausedTime: undefined,
              currentProject: undefined,
              currentBreakType: undefined,
              elapsedTime: 0,
              currentTimeEntry: null,
              description: '',
            });

            return { success: true };
          } else {
            // Fallback to local handling if API fails
            const now = new Date().toISOString();
            const updatedTimeEntry = {
              ...state.currentTimeEntry,
              clock_out: now,
              status: 'submitted' as const,
              updated_at: now,
              description: state.description,
            };

            // Calculate total hours
            const clockIn = new Date(state.currentTimeEntry.clock_in);
            const clockOut = new Date(now);
            const totalMs = clockOut.getTime() - clockIn.getTime();
            const totalHours = totalMs / (1000 * 60 * 60);

            updatedTimeEntry.total_hours = Number(totalHours.toFixed(2));
            updatedTimeEntry.regular_hours = Math.min(totalHours, 8);
            updatedTimeEntry.overtime_hours = Math.max(0, totalHours - 8);

            // Save to localStorage for persistence
            const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
            storedEntries.unshift(updatedTimeEntry);
            localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries.slice(0, 100)));

            set({
              isActive: false,
              isPaused: false,
              startTime: undefined,
              pausedTime: undefined,
              currentProject: undefined,
              currentBreakType: undefined,
              elapsedTime: 0,
              currentTimeEntry: null,
              description: '',
            });

            // Notify with local data
            if (typeof window !== 'undefined') {
              console.log('Timer store dispatching timeEntrySubmitted event (fallback):', updatedTimeEntry);
              window.dispatchEvent(new CustomEvent('timeEntrySubmitted', {
                detail: updatedTimeEntry
              }));
            }

            return { success: true };
          }
        } catch (error) {
          console.error('Failed to clock out:', error);
          // Handle error gracefully - still stop the timer locally and save to localStorage
          const now = new Date().toISOString();
          const fallbackEntry = {
            ...state.currentTimeEntry,
            clock_out: now,
            status: 'submitted' as const,
            updated_at: now,
            description: state.description,
          };

          // Calculate total hours
          const clockIn = new Date(state.currentTimeEntry.clock_in);
          const clockOut = new Date(now);
          const totalMs = clockOut.getTime() - clockIn.getTime();
          const totalHours = totalMs / (1000 * 60 * 60);

          fallbackEntry.total_hours = Number(totalHours.toFixed(2));
          fallbackEntry.regular_hours = Math.min(totalHours, 8);
          fallbackEntry.overtime_hours = Math.max(0, totalHours - 8);

          // Save to localStorage for persistence
          const storedEntries = JSON.parse(localStorage.getItem('completed-time-entries') || '[]');
          storedEntries.unshift(fallbackEntry);
          localStorage.setItem('completed-time-entries', JSON.stringify(storedEntries.slice(0, 100)));

          set({
            isActive: false,
            isPaused: false,
            startTime: undefined,
            pausedTime: undefined,
            currentProject: undefined,
            currentBreakType: undefined,
            elapsedTime: 0,
            currentTimeEntry: null,
            description: '',
          });

          // Notify with fallback data
          if (typeof window !== 'undefined') {
            console.log('Timer store dispatching timeEntrySubmitted event (error fallback):', fallbackEntry);
            window.dispatchEvent(new CustomEvent('timeEntrySubmitted', {
              detail: fallbackEntry
            }));
          }

          return { success: true }; // Consider it successful since we saved locally
        }
      },

      pauseTimer: () => {
        set({
          isPaused: true,
          pausedTime: new Date().toISOString(),
        });
      },

      resumeTimer: () => {
        const state = get();
        if (!state.pausedTime || !state.startTime) return;

        const pausedDuration = new Date().getTime() - new Date(state.pausedTime).getTime();
        const newStartTime = new Date(new Date(state.startTime).getTime() + pausedDuration).toISOString();

        set({
          isPaused: false,
          pausedTime: undefined,
          startTime: newStartTime,
        });
      },

      startBreak: (breakType) => {
        const now = new Date().toISOString();
        const state = get();

        if (state.currentTimeEntry) {
          const newBreakEntry = {
            id: `break-${Date.now()}`,
            time_entry_id: state.currentTimeEntry.id,
            break_type: breakType,
            start_time: now,
            paid: breakType === 'short_break',
            notes: undefined,
          };

          const updatedTimeEntry = {
            ...state.currentTimeEntry,
            break_entries: [...state.currentTimeEntry.break_entries, newBreakEntry],
          };

          set({
            currentBreakType: breakType,
            breakStartTime: now,
            currentTimeEntry: updatedTimeEntry,
          });
        }
      },

      endBreak: () => {
        const now = new Date().toISOString();
        const state = get();

        if (state.currentTimeEntry && state.breakStartTime) {
          const breakEntries = [...state.currentTimeEntry.break_entries];
          const lastBreakIndex = breakEntries.length - 1;

          if (lastBreakIndex >= 0) {
            breakEntries[lastBreakIndex] = {
              ...breakEntries[lastBreakIndex],
              end_time: now,
            };

            const updatedTimeEntry = {
              ...state.currentTimeEntry,
              break_entries: breakEntries,
            };

            set({
              currentBreakType: undefined,
              breakStartTime: undefined,
              currentTimeEntry: updatedTimeEntry,
            });
          }
        }
      },

      setCurrentProject: (project) => {
        const state = get();

        // If project is passed as object, use it; if string ID, look it up
        let actualProject: Project | undefined;
        if (typeof project === 'string') {
          actualProject = getProjectById(project);
        } else {
          actualProject = project || undefined;
        }

        set({
          currentProject: actualProject,
        });

        // Update current time entry if active
        if (state.currentTimeEntry) {
          set({
            currentTimeEntry: {
              ...state.currentTimeEntry,
              project_id: actualProject?.id,
              billable: actualProject?.billable || false,
            },
          });
        }
      },

      setDescription: (description) => {
        set({ description });
      },

      updateElapsedTime: () => {
        const state = get();
        if (!state.isActive || !state.startTime || state.isPaused) return;

        const now = new Date().getTime();
        const start = new Date(state.startTime).getTime();
        const elapsed = Math.floor((now - start) / 1000);

        set({ elapsedTime: elapsed });
      },

      resetTimer: () => {
        set({
          isActive: false,
          isPaused: false,
          startTime: undefined,
          pausedTime: undefined,
          currentProject: undefined,
          currentBreakType: undefined,
          elapsedTime: 0,
          currentTimeEntry: null,
          breakStartTime: undefined,
          description: '',
        });
      },

      validateTimerFields: () => {
        const state = get();
        const errors: string[] = [];

        // Check if project is selected
        if (!state.currentProject?.id && !state.currentTimeEntry?.project_id) {
          errors.push('Please select a project');
        }

        // Check if description is provided
        if (!state.description.trim()) {
          errors.push('Please describe what you\'re working on');
        }

        return errors;
      },
    }),
    {
      name: 'timer-storage',
      partialize: (state) => ({
        isActive: state.isActive,
        isPaused: state.isPaused,
        startTime: state.startTime,
        pausedTime: state.pausedTime,
        currentProject: state.currentProject,
        currentBreakType: state.currentBreakType,
        currentTimeEntry: state.currentTimeEntry,
        breakStartTime: state.breakStartTime,
        description: state.description,
      }),
    }
  )
);