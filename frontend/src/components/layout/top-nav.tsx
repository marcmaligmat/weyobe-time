'use client';

import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/auth';
import { MobileNav } from './mobile-nav';
import { Button } from '@/components/ui/button';
import { Clock, LogOut, User } from 'lucide-react';

interface TopNavProps {
  className?: string;
}

export function TopNav({ className }: TopNavProps) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  if (!user) return null;

  const getPageTitle = () => {
    switch (pathname) {
      case '/dashboard':
        return 'Dashboard';
      case '/timer':
        return 'Time Tracker';
      case '/time-entries':
        return 'Time Entries';
      case '/projects':
        return 'Projects';
      case '/team':
        return 'Team Management';
      case '/approvals':
        return 'Approvals';
      case '/reports':
        return 'Reports';
      case '/compliance':
        return 'Compliance';
      case '/settings':
        return 'Settings';
      default:
        return 'TimeTracker';
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center justify-between px-4">
        {/* Mobile Navigation and Logo */}
        <div className="flex items-center">
          <MobileNav />

          {/* Desktop Logo (hidden on mobile) */}
          <div className="hidden md:flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Clock className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-bold text-lg">TimeTracker</span>
          </div>

          {/* Mobile Page Title */}
          <div className="md:hidden ml-4">
            <h1 className="text-lg font-semibold">{getPageTitle()}</h1>
          </div>
        </div>

        {/* User Info and Actions */}
        <div className="flex items-center space-x-3">
          {/* User Avatar */}
          <div className="hidden sm:flex items-center space-x-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-gray-600" />
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-medium text-gray-900">
                {user.first_name} {user.last_name}
              </p>
              <p className="text-xs text-gray-500">
                {user.role.replace('_', ' ').toUpperCase()}
              </p>
            </div>
          </div>

          {/* Desktop Logout (hidden on mobile) */}
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className="hidden md:flex h-8 w-8"
          >
            <LogOut className="w-4 h-4" />
            <span className="sr-only">Sign Out</span>
          </Button>

          {/* Mobile User Avatar */}
          <div className="sm:hidden w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-600" />
          </div>
        </div>
      </div>
    </header>
  );
}