'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/lib/stores/auth';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  Clock,
  BarChart3,
  Users,
  FolderOpen,
  Settings,
  Calendar,
  FileText,
  CheckSquare,
  AlertTriangle,
  Menu,
  LogOut,
  User,
} from 'lucide-react';

interface NavigationItem {
  name: string;
  href: string;
  icon: any;
  roles: string[];
  badge?: string;
}

const navigation: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: BarChart3,
    roles: ['employee', 'contractor', 'team_lead', 'manager', 'admin', 'client_admin', 'global_admin'],
  },
  {
    name: 'Time Tracker',
    href: '/timer',
    icon: Clock,
    roles: ['employee', 'contractor', 'team_lead', 'manager', 'admin'],
  },
  {
    name: 'Time Entries',
    href: '/time-entries',
    icon: Calendar,
    roles: ['employee', 'contractor', 'team_lead', 'manager', 'admin'],
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderOpen,
    roles: ['team_lead', 'manager', 'admin', 'client_admin'],
  },
  {
    name: 'Team Management',
    href: '/team',
    icon: Users,
    roles: ['team_lead', 'manager', 'admin'],
  },
  {
    name: 'Approvals',
    href: '/approvals',
    icon: CheckSquare,
    roles: ['team_lead', 'manager', 'admin'],
    badge: '3',
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    roles: ['manager', 'admin', 'client_admin'],
  },
  {
    name: 'Compliance',
    href: '/compliance',
    icon: AlertTriangle,
    roles: ['manager', 'admin', 'global_admin'],
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    roles: ['admin', 'global_admin'],
  },
];

interface MobileNavProps {
  className?: string;
}

export function MobileNav({ className }: MobileNavProps) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const [open, setOpen] = useState(false);

  if (!user) return null;

  const filteredNavigation = navigation.filter(item =>
    item.roles.includes(user.role)
  );

  const handleLogout = () => {
    logout();
    setOpen(false);
  };

  return (
    <div className={cn("md:hidden", className)}>
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="h-10 w-10"
          >
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle navigation menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-80 px-0">
          <SheetHeader className="px-6 pb-4 border-b">
            <SheetTitle className="flex items-center text-left">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center mr-3">
                <Clock className="w-4 h-4 text-primary-foreground" />
              </div>
              TimeTracker
            </SheetTitle>
            <SheetDescription className="text-left">
              Time tracking and project management
            </SheetDescription>
          </SheetHeader>

          {/* User Info */}
          <div className="p-4 border-b">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-gray-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user.role.replace('_', ' ').toUpperCase()}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {filteredNavigation.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "flex items-center justify-between px-4 py-3 rounded-lg text-base font-medium transition-colors touch-target",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-gray-700 hover:bg-gray-100"
                  )}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className="w-5 h-5 flex-shrink-0" />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <Badge variant="destructive" className="text-xs">
                      {item.badge}
                    </Badge>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t">
            <Button
              variant="ghost"
              onClick={handleLogout}
              className="w-full justify-start text-base py-3 px-4 touch-target"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Sign Out
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}