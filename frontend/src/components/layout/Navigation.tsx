import { Link, useLocation } from 'react-router-dom';
import { useUIStore } from '@/stores/uiStore';
import { Button } from '@/components/ui/button';
import { Menu, X, Home, BarChart3, Settings, PlayCircle, Moon, Sun, Monitor } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useEffect } from 'react';

const navigationItems = [
  {
    name: '文章列表',
    href: '/',
    icon: Home,
  },
  {
    name: '统计分析',
    href: '/statistics',
    icon: BarChart3,
  },
  {
    name: '任务管理',
    href: '/crawler',
    icon: PlayCircle,
  },
  {
    name: '设置',
    href: '/settings',
    icon: Settings,
  },
];

export function Navigation() {
  const location = useLocation();
  const { theme, toggleTheme, sidebarOpen, toggleSidebar, setSidebarOpen } = useUIStore();

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname, setSidebarOpen]);

  // Close sidebar on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && sidebarOpen) {
        setSidebarOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [sidebarOpen, setSidebarOpen]);

  // Prevent body scroll when sidebar is open on mobile
  useEffect(() => {
    if (sidebarOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [sidebarOpen]);

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun className="h-5 w-5" />;
      case 'dark':
        return <Moon className="h-5 w-5" />;
      default:
        return <Monitor className="h-5 w-5" />;
    }
  };

  return (
    <>
      {/* Top Navigation Bar */}
      <nav className="fixed top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Left: Logo and Mobile Menu Toggle */}
            <div className="flex items-center gap-3 sm:gap-4">
              {/* Mobile Menu Toggle - Hamburger Menu */}
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden touch-manipulation active:scale-95 transition-transform"
                onClick={toggleSidebar}
                aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
                aria-expanded={sidebarOpen}
              >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>

              {/* Logo */}
              <Link to="/" className="flex items-center gap-2 touch-manipulation">
                {/* <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <span className="text-lg font-bold">U</span>
                </div> */}
                <span className="hidden text-xl font-bold sm:inline-block">UHotRank</span>
              </Link>
            </div>

            {/* Center: Desktop Navigation Links */}
            <div className="hidden lg:flex lg:items-center lg:gap-1">
              {navigationItems.map((item) => {
                const isActive = location.pathname === item.href;
                const Icon = item.icon;

                return (
                  <Link
                    key={item.href}
                    to={item.href}
                    className={cn(
                      'flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>

            {/* Right: Theme Toggle */}
            <div className="flex items-center gap-2">
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={toggleTheme} 
                aria-label="Toggle theme"
                className="touch-manipulation active:scale-95 transition-transform"
              >
                {getThemeIcon()}
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Sidebar - Slide-in Menu */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 w-64 transform border-r bg-background transition-transform duration-300 ease-in-out lg:hidden',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
        aria-hidden={!sidebarOpen}
      >
        <div className="flex h-full flex-col pt-20 pb-4">
          {/* Mobile Navigation Links */}
          <nav className="flex-1 space-y-1 px-3 overflow-y-auto">
            {navigationItems.map((item) => {
              const isActive = location.pathname === item.href;
              const Icon = item.icon;

              return (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    'flex items-center gap-3 rounded-md px-4 py-3 text-base font-medium transition-colors',
                    'touch-manipulation active:scale-98 transition-transform',
                    // Larger touch targets for mobile
                    'min-h-[48px]',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Mobile Sidebar Footer */}
          <div className="border-t px-3 pt-4">
            <div className="text-xs text-muted-foreground px-4">
              UHotRank v1.0
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}
    </>
  );
}
