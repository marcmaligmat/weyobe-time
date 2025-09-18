// User and Authentication Types
export type UserRole =
  | 'employee'
  | 'contractor'
  | 'team_lead'
  | 'manager'
  | 'admin'
  | 'client_admin'
  | 'global_admin';

export interface Permission {
  id: string;
  name: string;
  codename: string;
  description?: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  timezone: string;
  settings: OrganizationSettings;
  created_at: string;
  updated_at: string;
}

export interface OrganizationSettings {
  work_hours_per_day: number;
  work_days_per_week: number;
  overtime_threshold: number;
  break_duration_minutes: number;
  lunch_duration_minutes: number;
  allow_manual_time_entry: boolean;
  require_project_time_allocation: boolean;
  enable_compliance_monitoring: boolean;
}

export interface Department {
  id: string;
  name: string;
  description?: string;
  parent_id?: string;
  organization_id: string;
  manager_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  department_id: string;
  client_id?: string;
  billable: boolean;
  hourly_rate?: number;
  budget_hours?: number;
  status: 'active' | 'on_hold' | 'completed' | 'cancelled';
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  organization_id: string;
  department_id?: string;
  permissions: Permission[];
  is_active: boolean;
  timezone: string;
  hourly_rate?: number;
  employee_id?: string;
  hire_date?: string;
  compliance_settings: ComplianceConfig;
  created_at: string;
  updated_at: string;
}

export interface ComplianceConfig {
  max_hours_per_day: number;
  max_hours_per_week: number;
  require_breaks: boolean;
  break_after_hours: number;
  require_lunch: boolean;
  lunch_after_hours: number;
  overtime_rate_multiplier: number;
  night_shift_differential: number;
}

// Time Tracking Types
export type TimeEntryStatus = 'draft' | 'submitted' | 'approved' | 'rejected';
export type BreakType = 'short_break' | 'lunch' | 'personal';

export interface TimeEntry {
  id: string;
  user_id: string;
  organization_id: string;
  date: string;
  clock_in: string;
  clock_out?: string;
  break_entries: BreakEntry[];
  project_id?: string;
  department_id?: string;
  description?: string;
  billable: boolean;
  status: TimeEntryStatus;
  regular_hours: number;
  overtime_hours: number;
  total_hours: number;
  approval_notes?: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface BreakEntry {
  id: string;
  time_entry_id: string;
  break_type: BreakType;
  start_time: string;
  end_time?: string;
  paid: boolean;
  notes?: string;
}

export interface TimeModificationRequest {
  id: string;
  time_entry_id: string;
  requested_by: string;
  requested_changes: Partial<TimeEntry>;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  reviewed_by?: string;
  reviewed_at?: string;
  review_notes?: string;
  created_at: string;
}

// Dashboard and Analytics Types
export interface TimeSummary {
  today: {
    regular_hours: number;
    overtime_hours: number;
    break_hours: number;
    total_hours: number;
    status: 'not_started' | 'active' | 'on_break' | 'completed';
  };
  week: {
    regular_hours: number;
    overtime_hours: number;
    total_hours: number;
    days_worked: number;
  };
  month: {
    regular_hours: number;
    overtime_hours: number;
    total_hours: number;
    billable_hours: number;
    days_worked: number;
  };
}

export interface ComplianceAlert {
  id: string;
  type: 'overtime' | 'missed_break' | 'long_shift' | 'consecutive_days';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  user_id: string;
  time_entry_id?: string;
  created_at: string;
  acknowledged: boolean;
}

export interface ProjectTimeAllocation {
  project_id: string;
  project_name: string;
  department_name: string;
  hours: number;
  billable_hours: number;
  percentage: number;
}

// UI State Types
export interface TimerState {
  isActive: boolean;
  isPaused: boolean;
  startTime?: string;
  pausedTime?: string;
  currentProject?: Project;
  currentBreakType?: BreakType;
  elapsedTime: number;
}

export interface AppState {
  user: User | null;
  organization: Organization | null;
  timer: TimerState;
  isLoading: boolean;
  error: string | null;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface TimeEntryForm {
  project_id?: string;
  description?: string;
  billable: boolean;
  manual_entry?: {
    date: string;
    start_time: string;
    end_time: string;
    break_duration: number;
  };
}

export interface ApprovalAction {
  action: 'approve' | 'reject';
  notes?: string;
  time_entry_ids: string[];
}

// Chart and Analytics Types
export interface ChartDataPoint {
  date: string;
  hours: number;
  overtime_hours?: number;
  billable_hours?: number;
}

export interface ProductivityMetrics {
  efficiency_score: number;
  billable_ratio: number;
  overtime_frequency: number;
  break_compliance: number;
  average_daily_hours: number;
}

// Filter and Search Types
export interface TimeEntryFilters {
  date_from?: string;
  date_to?: string;
  user_id?: string;
  project_id?: string;
  department_id?: string;
  status?: TimeEntryStatus[];
  billable?: boolean;
}

export interface ReportFilters extends TimeEntryFilters {
  group_by?: 'day' | 'week' | 'month' | 'project' | 'user';
  include_breaks?: boolean;
  export_format?: 'csv' | 'pdf' | 'excel';
}