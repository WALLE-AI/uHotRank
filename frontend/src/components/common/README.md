# Common Components

This directory contains reusable common components used throughout the application.

## Components

### LoadingSpinner

A loading spinner component with customizable size and optional text.

**Props:**
- `size?: 'sm' | 'md' | 'lg'` - Size of the spinner (default: 'md')
- `className?: string` - Additional CSS classes
- `text?: string` - Optional loading text to display below spinner

**Usage:**
```tsx
import { LoadingSpinner } from '@/components/common';

// Basic usage
<LoadingSpinner />

// With text
<LoadingSpinner text="加载中..." />

// Custom size
<LoadingSpinner size="lg" text="正在处理..." />
```

### EmptyState

A component to display when there's no data or content to show.

**Props:**
- `icon?: LucideIcon` - Optional icon to display
- `title: string` - Title text (required)
- `description?: string` - Optional description text
- `action?: { label: string; onClick: () => void }` - Optional action button
- `className?: string` - Additional CSS classes

**Usage:**
```tsx
import { EmptyState } from '@/components/common';
import { FileText } from 'lucide-react';

<EmptyState
  icon={FileText}
  title="没有文章"
  description="暂时没有找到任何文章，请尝试调整筛选条件"
  action={{
    label: "清除筛选",
    onClick: () => clearFilters()
  }}
/>
```

### ErrorBoundary

A React error boundary component that catches JavaScript errors in child components.

**Props:**
- `children: ReactNode` - Child components to wrap
- `fallback?: ReactNode` - Optional custom fallback UI
- `onError?: (error: Error, errorInfo: ErrorInfo) => void` - Optional error handler

**Usage:**
```tsx
import { ErrorBoundary } from '@/components/common';

// Basic usage
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>

// With custom fallback
<ErrorBoundary fallback={<div>Something went wrong</div>}>
  <YourComponent />
</ErrorBoundary>

// With error handler
<ErrorBoundary onError={(error, errorInfo) => {
  console.error('Error caught:', error, errorInfo);
  // Send to error tracking service
}}>
  <YourComponent />
</ErrorBoundary>
```

## Toast Notifications

Toast notifications are already implemented using shadcn/ui. Use the `useToast` hook:

**Usage:**
```tsx
import { useToast } from '@/hooks/use-toast';

function MyComponent() {
  const { toast } = useToast();

  const showSuccess = () => {
    toast({
      title: "成功",
      description: "操作已完成",
    });
  };

  const showError = () => {
    toast({
      variant: "destructive",
      title: "错误",
      description: "操作失败，请重试",
    });
  };

  return (
    <div>
      <button onClick={showSuccess}>Show Success</button>
      <button onClick={showError}>Show Error</button>
    </div>
  );
}
```

## Requirements Validation

These components satisfy the following requirements:

- **Requirement 7.1**: LoadingSpinner provides loading animation during data loading
- **Requirement 7.2**: ErrorBoundary displays clear error messages when operations fail
- **Requirement 7.3**: Toast system provides success feedback for operations
