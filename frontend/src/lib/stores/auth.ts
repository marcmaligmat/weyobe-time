import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, Organization } from '@/types';

interface AuthState {
  user: User | null;
  organization: Organization | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  setUser: (user: User | null) => void;
  setOrganization: (organization: Organization | null) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      organization: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => {
        set({
          user,
          isAuthenticated: !!user
        });
      },

      setOrganization: (organization) => {
        set({ organization });
      },

      login: async (email: string, password: string) => {
        set({ isLoading: true });

        try {
          // Mock login - replace with actual API call
          await new Promise(resolve => setTimeout(resolve, 1000));

          // Mock user data
          const mockUser: User = {
            id: '1',
            email,
            first_name: 'John',
            last_name: 'Doe',
            role: 'employee',
            organization_id: 'org-1',
            department_id: 'dept-1',
            permissions: [],
            is_active: true,
            timezone: 'America/New_York',
            hourly_rate: 25.00,
            employee_id: 'EMP001',
            hire_date: '2023-01-15',
            compliance_settings: {
              max_hours_per_day: 8,
              max_hours_per_week: 40,
              require_breaks: true,
              break_after_hours: 4,
              require_lunch: true,
              lunch_after_hours: 6,
              overtime_rate_multiplier: 1.5,
              night_shift_differential: 0.1,
            },
            created_at: '2023-01-15T00:00:00Z',
            updated_at: '2023-01-15T00:00:00Z',
          };

          const mockOrganization: Organization = {
            id: 'org-1',
            name: 'TechCorp Inc.',
            slug: 'techcorp',
            timezone: 'America/New_York',
            settings: {
              work_hours_per_day: 8,
              work_days_per_week: 5,
              overtime_threshold: 40,
              break_duration_minutes: 15,
              lunch_duration_minutes: 60,
              allow_manual_time_entry: true,
              require_project_time_allocation: true,
              enable_compliance_monitoring: true,
            },
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z',
          };

          set({
            user: mockUser,
            organization: mockOrganization,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          organization: null,
          isAuthenticated: false,
        });
      },

      checkAuth: async () => {
        const { user } = get();
        if (!user) return;

        set({ isLoading: true });

        try {
          // Mock auth check - replace with actual API call
          await new Promise(resolve => setTimeout(resolve, 500));
          // For now, assume auth is still valid
          set({ isLoading: false });
        } catch (error) {
          set({
            user: null,
            organization: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        organization: state.organization,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);