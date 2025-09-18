import { Project } from '@/types';

// Mock projects data - centralized for consistent usage across the app
export const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Website Redesign',
    description: 'Complete redesign of the company website',
    department_id: 'dev-1',
    client_id: 'acme-corp',
    billable: true,
    hourly_rate: 75,
    budget_hours: 120,
    status: 'active',
    start_date: '2024-01-01',
    end_date: '2024-06-30',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    name: 'Mobile App',
    description: 'iOS and Android mobile application development',
    department_id: 'dev-1',
    client_id: 'tech-solutions',
    billable: true,
    hourly_rate: 85,
    budget_hours: 200,
    status: 'active',
    start_date: '2024-02-01',
    end_date: '2024-08-31',
    created_at: '2024-02-01T00:00:00Z',
    updated_at: '2024-02-01T00:00:00Z',
  },
  {
    id: '3',
    name: 'Internal Tools',
    description: 'Development of internal productivity tools',
    department_id: 'it-1',
    billable: false,
    status: 'active',
    start_date: '2024-01-15',
    created_at: '2024-01-15T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
  },
  {
    id: '4',
    name: 'Marketing Campaign',
    description: 'Digital marketing campaign implementation',
    department_id: 'marketing-1',
    client_id: 'creative-agency',
    billable: true,
    hourly_rate: 65,
    budget_hours: 80,
    status: 'active',
    start_date: '2024-03-01',
    end_date: '2024-05-31',
    created_at: '2024-03-01T00:00:00Z',
    updated_at: '2024-03-01T00:00:00Z',
  },
];

// Legacy format for timer widget compatibility
export const mockProjectsForTimer = mockProjects.map(project => ({
  id: project.id,
  name: project.name,
  color: getProjectColor(project.id),
  client: getClientName(project.client_id),
  billable: project.billable,
}));

// Helper functions
function getProjectColor(projectId: string): string {
  const colors = {
    '1': '#ef4444', // red
    '2': '#10b981', // green
    '3': '#6366f1', // indigo
    '4': '#f59e0b', // amber
  };
  return colors[projectId as keyof typeof colors] || '#6b7280'; // gray as default
}

function getClientName(clientId?: string): string | undefined {
  const clients = {
    'acme-corp': 'Acme Corp',
    'tech-solutions': 'Tech Solutions',
    'creative-agency': 'Creative Agency',
  };
  return clientId ? clients[clientId as keyof typeof clients] : undefined;
}

// Helper function to get project name by ID
export function getProjectName(projectId?: string): string {
  if (!projectId) return 'No Project';
  const project = mockProjects.find(p => p.id === projectId);
  return project?.name || `Project ${projectId}`;
}

// Helper function to get project by ID
export function getProjectById(projectId?: string): Project | undefined {
  if (!projectId) return undefined;
  return mockProjects.find(p => p.id === projectId);
}

// Helper function for manual entry form
export function getProjectsForForm() {
  return mockProjects.map(project => ({
    id: project.id,
    name: project.name,
    billable: project.billable,
    department: getDepartmentName(project.department_id),
  }));
}

function getDepartmentName(departmentId: string): string {
  const departments = {
    'dev-1': 'Development',
    'it-1': 'IT',
    'marketing-1': 'Marketing',
  };
  return departments[departmentId as keyof typeof departments] || 'Unknown';
}