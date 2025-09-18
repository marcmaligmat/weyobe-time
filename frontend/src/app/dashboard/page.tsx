'use client';

import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { TimerWidget } from '@/components/timer/timer-widget';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/lib/stores/auth';
import { formatHours, formatDate, getRoleDisplayName } from '@/lib/utils';
import {
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Users,
  FolderOpen,
  Calendar,
  DollarSign,
  BarChart3,
  Target,
  Award,
  Activity,
} from 'lucide-react';

// Mock dashboard data
const mockDashboardData = {
  employee: {
    todayHours: 6.5,
    weekHours: 32.5,
    monthHours: 168.5,
    overtimeHours: 2.5,
    billableHours: 28.5,
    projectsActive: 3,
    pendingApprovals: 2,
    complianceAlerts: 1,
  },
  manager: {
    teamSize: 12,
    teamHoursToday: 78.5,
    teamHoursWeek: 384.5,
    pendingApprovals: 8,
    overtimeAlerts: 3,
    complianceIssues: 2,
    activeProjects: 15,
    budgetUtilization: 85.2,
  },
  admin: {
    totalUsers: 45,
    activeUsers: 42,
    totalHoursToday: 325.5,
    complianceAlerts: 5,
    systemAlerts: 2,
    billableRevenue: 125000,
    organizationEfficiency: 92.5,
    integrationStatus: 'healthy',
  },
};

const mockRecentActivities = [
  {
    id: '1',
    type: 'clock_in',
    user: 'John Doe',
    time: '09:00 AM',
    project: 'Website Redesign',
  },
  {
    id: '2',
    type: 'approval',
    user: 'Jane Smith',
    time: '08:45 AM',
    project: 'Mobile App',
  },
  {
    id: '3',
    type: 'overtime',
    user: 'Mike Johnson',
    time: '06:30 PM',
    project: 'Backend API',
  },
  {
    id: '4',
    type: 'break',
    user: 'Sarah Wilson',
    time: '12:00 PM',
    project: 'Database Migration',
  },
];

const mockComplianceAlerts = [
  {
    id: '1',
    type: 'overtime',
    message: 'You have exceeded 8 hours today',
    severity: 'warning',
    time: '6:30 PM',
  },
  {
    id: '2',
    type: 'break',
    message: 'Break reminder: Take a 15-minute break',
    severity: 'info',
    time: '2:45 PM',
  },
];

export default function DashboardPage() {
  const { user } = useAuthStore();

  if (!user) return null;

  const data = mockDashboardData[user.role as keyof typeof mockDashboardData] || mockDashboardData.employee;

  const renderEmployeeDashboard = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Timer Widget */}
      <div className="lg:col-span-1">
        <TimerWidget />
      </div>

      {/* Quick Stats */}
      <div className="lg:col-span-2 grid grid-cols-2 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Today</p>
                <p className="text-2xl font-bold">{formatHours((data as any).todayHours || 0)}</p>
              </div>
              <Clock className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">This Week</p>
                <p className="text-2xl font-bold">{formatHours((data as any).weekHours || 0)}</p>
              </div>
              <Calendar className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Billable</p>
                <p className="text-2xl font-bold">{formatHours((data as any).billableHours || 0)}</p>
              </div>
              <DollarSign className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Overtime</p>
                <p className="text-2xl font-bold text-red-600">{formatHours((data as any).overtimeHours || 0)}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderManagerDashboard = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Team Size</p>
              <p className="text-2xl font-bold">{(data as any).teamSize || 0}</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Team Hours Today</p>
              <p className="text-2xl font-bold">{formatHours((data as any).teamHoursToday || 0)}</p>
            </div>
            <Clock className="h-8 w-8 text-green-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Approvals</p>
              <p className="text-2xl font-bold">{(data as any).pendingApprovals || 0}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-yellow-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-bold">{(data as any).activeProjects || 0}</p>
            </div>
            <FolderOpen className="h-8 w-8 text-purple-600" />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderAdminDashboard = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold">{(data as any).totalUsers || 0}</p>
              <p className="text-xs text-gray-500">{(data as any).activeUsers || 0} active</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Revenue (MTD)</p>
              <p className="text-2xl font-bold">${((data as any).billableRevenue || 0).toLocaleString()}</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Efficiency</p>
              <p className="text-2xl font-bold">{(data as any).organizationEfficiency || 0}%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-600" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Compliance Alerts</p>
              <p className="text-2xl font-bold text-red-600">{(data as any).complianceAlerts || 0}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderRoleBasedContent = () => {
    switch (user.role) {
      case 'manager':
      case 'team_lead':
        return renderManagerDashboard();
      case 'admin':
      case 'global_admin':
        return renderAdminDashboard();
      default:
        return renderEmployeeDashboard();
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user.first_name}!
            </h1>
            <p className="text-gray-600">
              {getRoleDisplayName(user.role)} Dashboard • {formatDate(new Date().toISOString(), 'long')}
            </p>
          </div>
          <Badge variant="outline" className="text-sm">
            {getRoleDisplayName(user.role)}
          </Badge>
        </div>

        {/* Role-based Dashboard Content */}
        {renderRoleBasedContent()}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="w-5 h-5 mr-2" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockRecentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                      {activity.type === 'clock_in' && <Clock className="w-4 h-4 text-primary" />}
                      {activity.type === 'approval' && <CheckCircle className="w-4 h-4 text-green-600" />}
                      {activity.type === 'overtime' && <AlertTriangle className="w-4 h-4 text-red-600" />}
                      {activity.type === 'break' && <Clock className="w-4 h-4 text-yellow-600" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.user}</p>
                      <p className="text-xs text-gray-500">{activity.project}</p>
                    </div>
                    <span className="text-xs text-gray-400">{activity.time}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Compliance Alerts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Compliance Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockComplianceAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg border-l-4 ${
                      alert.severity === 'warning'
                        ? 'border-yellow-400 bg-yellow-50'
                        : 'border-blue-400 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{alert.message}</p>
                      <span className="text-xs text-gray-500">{alert.time}</span>
                    </div>
                  </div>
                ))}
                {mockComplianceAlerts.length === 0 && (
                  <div className="text-center py-6">
                    <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">All compliance requirements met!</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        {['employee', 'contractor'].includes(user.role) && (
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button variant="outline" className="h-20 flex-col space-y-2">
                  <Clock className="w-6 h-6" />
                  <span className="text-xs">Start Timer</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col space-y-2">
                  <Calendar className="w-6 h-6" />
                  <span className="text-xs">Manual Entry</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col space-y-2">
                  <BarChart3 className="w-6 h-6" />
                  <span className="text-xs">View Reports</span>
                </Button>
                <Button variant="outline" className="h-20 flex-col space-y-2">
                  <FolderOpen className="w-6 h-6" />
                  <span className="text-xs">Projects</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}