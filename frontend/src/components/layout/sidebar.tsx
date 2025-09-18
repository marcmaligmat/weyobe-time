'use client';

import { useAuthStore } from '@/lib/stores/auth';
import { cn } from '@/lib/utils';
import {
  ArrowRight,
  BarChart3,
  Calendar,
  Clock,
  FileText,
  FolderOpen,
  Menu,
  Settings,
  Users,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

interface NavigationItem {
  name: string;
  href: string;
  icon: any;
  roles: string[];
}

const navigation: NavigationItem[] = [
  {
    name: 'TIME TRACKER',
    href: '/timer',
    icon: Clock,
    roles: ['employee', 'contractor', 'team_lead', 'manager', 'admin'],
  },
  {
    name: 'CALENDAR',
    href: '/calendar',
    icon: Calendar,
    roles: ['employee', 'contractor', 'team_lead', 'manager', 'admin'],
  },
];

const analyzeSection: NavigationItem[] = [
  {
    name: 'DASHBOARD',
    href: '/dashboard',
    icon: BarChart3,
    roles: [
      'employee',
      'contractor',
      'team_lead',
      'manager',
      'admin',
      'client_admin',
      'global_admin',
    ],
  },
  {
    name: 'REPORTS',
    href: '/reports',
    icon: FileText,
    roles: ['manager', 'admin', 'client_admin'],
  },
];

const manageSection: NavigationItem[] = [
  {
    name: 'PROJECTS',
    href: '/projects',
    icon: FolderOpen,
    roles: ['team_lead', 'manager', 'admin', 'client_admin'],
  },
  {
    name: 'TEAM',
    href: '/team',
    icon: Users,
    roles: ['team_lead', 'manager', 'admin'],
  },
];

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!user) return null;

  const filterNavigation = (items: NavigationItem[]) =>
    items.filter((item) => item.roles.includes(user.role));

  const renderNavSection = (items: NavigationItem[], title?: string) => (
    <div>
      {title && (
        <div className="px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
          {title}
        </div>
      )}
      {items.map((item) => {
        const isActive =
          pathname === item.href || pathname.startsWith(item.href + '/');
        const Icon = item.icon;

        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors',
              isActive && 'bg-blue-50 text-primary border-r-2 border-primary'
            )}
          >
            <Icon className="w-4 h-4 mr-3 flex-shrink-0" />
            <span className="font-medium">{item.name}</span>
            {isActive && (
              <ArrowRight className="w-4 h-4 ml-auto text-primary" />
            )}
          </Link>
        );
      })}
    </div>
  );

  return (
    <div
      className={cn(
        'flex flex-col h-full bg-white border-r border-gray-200',
        className
      )}
      style={{ width: '240px' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
            <div className="w-3 h-3 bg-white rounded-sm"></div>
          </div>
          <span className="font-bold text-lg text-gray-900">WeYobeTime</span>
        </div>
        <button className="p-1 hover:bg-gray-100 rounded">
          <Menu className="w-4 h-4 text-gray-600" />
        </button>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-gray-200">
        <div className="text-sm text-gray-600">
          {user.first_name}'s workspace
        </div>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-gray-500">••••</span>
          <button className="px-2 py-1 bg-primary text-white text-xs rounded font-medium">
            UPGRADE
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-2 overflow-y-auto">
        {/* Main sections */}
        {renderNavSection(filterNavigation(navigation))}

        {/* Analyze section */}
        <div className="mt-6">
          {renderNavSection(filterNavigation(analyzeSection), 'ANALYZE')}
        </div>

        {/* Manage section */}
        <div className="mt-6">
          {renderNavSection(filterNavigation(manageSection), 'MANAGE')}
        </div>
      </nav>

      {/* Footer - Settings */}
      <div className="border-t border-gray-200 p-2">
        <Link
          href="/settings"
          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <Settings className="w-4 h-4 mr-3" />
          <span className="font-medium">SETTINGS</span>
        </Link>
      </div>
    </div>
  );
}
