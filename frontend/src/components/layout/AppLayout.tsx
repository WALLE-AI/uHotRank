import { Outlet } from 'react-router-dom';
import { Navigation } from './Navigation';
import { cn } from '@/lib/utils';

export function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <Navigation />

      {/* Main Content */}
      <main
        className={cn(
          'transition-all duration-300 ease-in-out',
          'pt-[calc(4rem+1px)]', // Space for fixed navigation (64px + 1px border)
          'min-h-[calc(100vh-4rem)]',
          // Mobile: single column with padding
          'px-4 pb-4 sm:px-6 sm:pb-6',
          // Tablet: increased padding
          'md:px-8 md:pb-6',
          // Desktop: max width container
          'lg:px-8 lg:pb-8'
        )}
      >
        <div className="mx-auto max-w-7xl w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
