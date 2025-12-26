# Search Components

This directory contains the search and filter components for the UHotRank application.

## Components

### SearchBar

A search input component with the following features:
- Keyword search with debouncing (300ms)
- Search history management
- Keyboard shortcut support (Ctrl/Cmd + K)
- Search suggestions dropdown

**Usage:**

```tsx
import { SearchBar } from '@/components/search';

function MyComponent() {
  return (
    <SearchBar
      onSearch={(keyword) => console.log('Searching:', keyword)}
      placeholder="搜索文章..."
    />
  );
}
```

**Props:**
- `onSearch?: (keyword: string) => void` - Callback when search is triggered
- `placeholder?: string` - Input placeholder text
- `className?: string` - Additional CSS classes

### FilterPanel

A comprehensive filter panel with multiple filter options:
- Tech categories (multi-select checkboxes)
- Article sources (multi-select checkboxes)
- Sentiment analysis (single-select dropdown)
- Date range picker
- Clear filters button

**Usage:**

```tsx
import { FilterPanel } from '@/components/search';

function MyComponent() {
  return (
    <FilterPanel
      onFilterChange={() => console.log('Filters changed')}
    />
  );
}
```

**Props:**
- `onFilterChange?: () => void` - Callback when filters are applied
- `className?: string` - Additional CSS classes

### SearchResults

Displays search results with the following features:
- Results count display
- Sort options (relevance, time, popularity)
- Keyword highlighting in titles
- Aggregations summary (categories, sources, sentiments)
- Empty state handling
- Loading state

**Usage:**

```tsx
import { SearchResults } from '@/components/search';

function MyComponent() {
  return <SearchResults />;
}
```

**Props:**
- `className?: string` - Additional CSS classes

## Complete Example

See `frontend/src/pages/SearchPage.tsx` for a complete example of how to use all three components together.

```tsx
import { SearchBar, FilterPanel, SearchResults } from '@/components/search';

function SearchPage() {
  return (
    <div>
      <SearchBar />
      <div className="grid grid-cols-4 gap-6">
        <aside className="col-span-1">
          <FilterPanel />
        </aside>
        <main className="col-span-3">
          <SearchResults />
        </main>
      </div>
    </div>
  );
}
```

## State Management

All components use the `useSearchStore` from Zustand for state management. The store handles:
- Search parameters
- Search results
- Search history
- Loading and error states

## Keyboard Shortcuts

- **Ctrl/Cmd + K**: Focus search input
- **ESC**: Close search suggestions/history dropdown
- **Enter**: Submit search

## Features

### Search History
- Automatically saves search keywords
- Displays up to 10 recent searches
- Persisted to localStorage
- Can remove individual items or clear all

### Debouncing
- Search suggestions are debounced by 300ms
- Prevents excessive API calls while typing

### Keyword Highlighting
- Search keywords are highlighted in article titles
- Uses `<mark>` element with custom styling

### Responsive Design
- Filter panel is collapsible on mobile devices
- Adapts layout for different screen sizes
- Touch-friendly interactions
