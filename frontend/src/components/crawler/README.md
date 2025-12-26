# Crawler Components

This directory contains components for managing and monitoring crawler tasks.

## Components

### CrawlerControl

Control panel for starting and stopping crawler tasks.

**Features:**
- Start crawler with different modes (all, tech_only, with_analysis)
- Stop running crawler tasks
- Display current task status
- Show error messages when tasks fail

**Props:**
- `currentTask`: Current crawler task state
- `onTaskUpdate`: Callback when task is updated

### CrawlerProgress

Real-time progress display for running crawler tasks.

**Features:**
- Progress bar showing completion percentage
- Statistics display (crawled, success, failed)
- Success rate calculation
- Elapsed time tracking
- Auto-polling every 2 seconds when task is running

**Props:**
- `task`: Current crawler task
- `onUpdate`: Callback when task status updates

### CrawlerHistory

Display historical crawler task records.

**Features:**
- List of past crawler tasks
- Expandable task details
- Task statistics (total, success, failed)
- Duration calculation
- Success rate display

**Props:**
- `refreshTrigger`: Number that triggers history refresh when changed

## Usage Example

```tsx
import { CrawlerControl, CrawlerProgress, CrawlerHistory } from '@/components/crawler';

function CrawlerPage() {
  const [currentTask, setCurrentTask] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  return (
    <div>
      <CrawlerControl 
        currentTask={currentTask}
        onTaskUpdate={() => setRefreshTrigger(prev => prev + 1)}
      />
      <CrawlerProgress 
        task={currentTask}
        onUpdate={setCurrentTask}
      />
      <CrawlerHistory refreshTrigger={refreshTrigger} />
    </div>
  );
}
```

## API Integration

These components integrate with the crawler service API:

- `POST /api/crawler/start` - Start a new crawler task
- `POST /api/crawler/stop` - Stop running crawler
- `GET /api/crawler/status` - Get current task status
- `GET /api/crawler/history` - Get task history

## Requirements Validation

This implementation satisfies the following requirements:

- **5.1**: Display current crawler task status
- **5.2**: Start crawler with mode selection
- **5.3**: Real-time progress display with statistics
- **5.4**: Mode selection (all/tech_only/with_analysis)
- **5.5**: Historical task records
- **5.6**: Stop running crawler tasks
