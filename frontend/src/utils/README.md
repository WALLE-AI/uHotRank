# Utility Functions

This directory contains reusable utility functions used throughout the application.

## Format Utilities (`format.ts`)

### Date Formatting

#### `formatRelativeTime(date: string | Date): string`

Formats a date as relative time (e.g., "刚刚", "5分钟前", "2小时前").

**Usage:**
```typescript
import { formatRelativeTime } from '@/utils';

const relativeTime = formatRelativeTime('2024-01-01T10:00:00Z');
// Returns: "2小时前" (depending on current time)
```

#### `formatDateTime(date: string | Date): string`

Formats a date as standard datetime string (YYYY-MM-DD HH:mm:ss).

**Usage:**
```typescript
import { formatDateTime } from '@/utils';

const datetime = formatDateTime(new Date());
// Returns: "2024-01-01 10:30:45"
```

#### `formatDate(date: string | Date): string`

Formats a date as date string (YYYY-MM-DD).

**Usage:**
```typescript
import { formatDate } from '@/utils';

const date = formatDate(new Date());
// Returns: "2024-01-01"
```

#### `formatTime(date: string | Date): string`

Formats a date as time string (HH:mm:ss).

**Usage:**
```typescript
import { formatTime } from '@/utils';

const time = formatTime(new Date());
// Returns: "10:30:45"
```

### Text Truncation

#### `truncateText(text: string, maxLength: number, ellipsis = '...'): string`

Truncates text to specified length and adds ellipsis.

**Usage:**
```typescript
import { truncateText } from '@/utils';

const truncated = truncateText('This is a very long text', 10);
// Returns: "This is..."
```

#### `truncateTextByWord(text: string, maxLength: number, ellipsis = '...'): string`

Truncates text at word boundaries to avoid cutting words in half.

**Usage:**
```typescript
import { truncateTextByWord } from '@/utils';

const truncated = truncateTextByWord('This is a very long text', 15);
// Returns: "This is a..."
```

#### `truncateTextByLines(text: string, maxLines: number, ellipsis = '...'): string`

Truncates text to specified number of lines.

**Usage:**
```typescript
import { truncateTextByLines } from '@/utils';

const multilineText = 'Line 1\nLine 2\nLine 3\nLine 4';
const truncated = truncateTextByLines(multilineText, 2);
// Returns: "Line 1\nLine 2..."
```

## Debounce and Throttle Utilities (`debounce.ts`)

### `debounce<T>(func: T, delay: number): T`

Delays function execution until after a specified delay has elapsed since the last call.

**Usage:**
```typescript
import { debounce } from '@/utils';

const handleSearch = debounce((query: string) => {
  console.log('Searching for:', query);
}, 300);

// Call multiple times rapidly
handleSearch('a');
handleSearch('ab');
handleSearch('abc');
// Only the last call executes after 300ms
```

### `throttle<T>(func: T, limit: number): T`

Limits function execution to at most once per specified time period.

**Usage:**
```typescript
import { throttle } from '@/utils';

const handleScroll = throttle(() => {
  console.log('Scroll event');
}, 100);

window.addEventListener('scroll', handleScroll);
// Executes at most once every 100ms
```

### `debounceImmediate<T>(func: T, delay: number, immediate = true): T`

Debounce with option to execute immediately on first call.

**Usage:**
```typescript
import { debounceImmediate } from '@/utils';

const handleClick = debounceImmediate(() => {
  console.log('Clicked');
}, 1000, true);

// First click executes immediately
// Subsequent clicks within 1s are ignored
```

### `throttleAdvanced<T>(func: T, limit: number, options): T`

Advanced throttle with leading and trailing edge options.

**Usage:**
```typescript
import { throttleAdvanced } from '@/utils';

const handleResize = throttleAdvanced(
  () => console.log('Resized'),
  200,
  { leading: true, trailing: true }
);

window.addEventListener('resize', handleResize);
```

## Export Utilities (`export.ts`)

Functions for exporting data to various formats (JSON, CSV, Excel).

See the export component documentation for usage examples.

## Requirements Validation

These utilities satisfy the following requirements:

- **Requirement 1.2**: Date formatting and text truncation for article card display
- **Requirement 3.1**: Debounce for search input to improve performance
- **Requirement 7.5**: Utility functions support keyboard shortcuts and user interactions
