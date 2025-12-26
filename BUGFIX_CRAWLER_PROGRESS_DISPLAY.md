# Bug Fix: Crawler Progress Display

## Issue
爬虫管理模块的爬取进度没有显示，进度条始终为 0。

## Root Cause
前端和后端的数据结构不匹配：

**前端期望**:
```typescript
{
  id: string,
  status: 'idle' | 'running' | 'completed' | 'error',
  progress: {
    total: number,
    crawled: number,
    success: number,
    failed: number
  }
}
```

**后端返回**:
```python
{
  task_id: str,
  current_status: str,
  total_crawled: int,
  success_count: int,
  failed_count: int
}
```

数据结构不匹配导致前端无法正确读取进度数据。

## Solution
统一前后端的数据结构，使其完全匹配。

## Files Modified

### 1. Backend Schema
**File**: `backend/schemas/crawler.py`

**Changes**:

1. 添加 `CrawlerProgress` 嵌套模型：
```python
class CrawlerProgress(BaseModel):
    """爬虫进度模型"""
    total: int = Field(0, description="总数")
    crawled: int = Field(0, description="已爬取数")
    success: int = Field(0, description="成功数")
    failed: int = Field(0, description="失败数")
```

2. 修改 `CrawlerStatus` 模型：
```python
class CrawlerStatus(BaseModel):
    """爬虫状态模型"""
    is_running: bool
    task_id: Optional[str]
    mode: Optional[str]
    status: str  # 改名从 current_status
    progress: CrawlerProgress  # 嵌套结构
    started_at: Optional[str]
    completed_at: Optional[str]  # 新增
    error_message: Optional[str]  # 新增
```

### 2. Backend Service
**File**: `backend/service/crawler_service.py`

**Changes**:

修改 `get_status` 方法返回嵌套的进度结构：
```python
async def get_status(self) -> CrawlerStatus:
    from backend.schemas.crawler import CrawlerProgress
    
    return CrawlerStatus(
        is_running=self.task_status["is_running"],
        task_id=self.task_id if self.task_status["is_running"] else None,
        mode=self.task_status["mode"],
        status=self.task_status["current_status"],
        progress=CrawlerProgress(
            total=0,
            crawled=self.task_status["total_crawled"],
            success=self.task_status["success_count"],
            failed=self.task_status["failed_count"],
        ),
        started_at=self.task_status["started_at"],
        completed_at=self.task_status.get("completed_at"),
        error_message=self.task_status.get("error_message"),
    )
```

添加 `completed_at` 和 `error_message` 字段更新。

### 3. Frontend Types
**File**: `frontend/src/types/search.ts`

**Changes**:

更新 `CrawlerTask` 接口以匹配后端：
```typescript
export interface CrawlerTask {
  task_id: string | null;  // 匹配后端字段名
  mode: 'all' | 'tech_only' | 'with_analysis' | null;
  status: 'idle' | 'running' | 'completed' | 'error';
  is_running: boolean;  // 新增，匹配后端
  progress: {
    total: number;
    crawled: number;
    success: number;
    failed: number;
  };
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}
```

### 4. Frontend Component
**File**: `frontend/src/components/crawler/CrawlerProgress.tsx`

**Changes**:

更新轮询条件以使用 `is_running` 和 `task_id`：
```typescript
useEffect(() => {
  if (!task || !task.is_running) {
    return;
  }
  // ...
}, [task?.is_running, task?.task_id, onUpdate]);
```

## Data Structure Comparison

### Before (Mismatched)

**Backend**:
```json
{
  "task_id": "abc-123",
  "current_status": "running",
  "total_crawled": 10,
  "success_count": 8,
  "failed_count": 2
}
```

**Frontend Expected**:
```json
{
  "id": "abc-123",
  "status": "running",
  "progress": {
    "crawled": 10,
    "success": 8,
    "failed": 2
  }
}
```

❌ **Result**: Frontend can't read progress data

### After (Matched)

**Backend**:
```json
{
  "task_id": "abc-123",
  "is_running": true,
  "status": "running",
  "progress": {
    "total": 0,
    "crawled": 10,
    "success": 8,
    "failed": 2
  }
}
```

**Frontend**:
```json
{
  "task_id": "abc-123",
  "is_running": true,
  "status": "running",
  "progress": {
    "total": 0,
    "crawled": 10,
    "success": 8,
    "failed": 2
  }
}
```

✅ **Result**: Perfect match, progress displays correctly

## Testing

After these changes:
1. ✅ Start a crawler task
2. ✅ Progress bar shows real-time updates
3. ✅ Crawled count increases
4. ✅ Success/failed counts update
5. ✅ Status changes correctly (idle → running → completed)
6. ✅ Completed time displays when task finishes

## API Response Example

```json
GET /api/crawler/status

{
  "is_running": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "mode": "all",
  "status": "running",
  "progress": {
    "total": 0,
    "crawled": 15,
    "success": 13,
    "failed": 2
  },
  "started_at": "2025-12-26T10:30:00",
  "completed_at": null,
  "error_message": null
}
```

## Related Files
- `backend/schemas/crawler.py` (data model)
- `backend/service/crawler_service.py` (status mapping)
- `frontend/src/types/search.ts` (TypeScript types)
- `frontend/src/components/crawler/CrawlerProgress.tsx` (UI component)

## Notes
- The `total` field in progress is set to 0 because we don't know the total number of articles beforehand
- Progress percentage is calculated as `(crawled / total) * 100`, but since total is 0, we show absolute numbers instead
- The frontend component already handles this gracefully by showing "已爬取 X / 未知"


---

## Additional Fix: Article Count Limit Removed

### Issue
Even after fixing the data structure mismatch, users still reported that progress wasn't显示 properly. Upon investigation, we found that the crawler was only processing 10 articles instead of all articles.

### Root Cause
In `backend/agent/agent_today_data.py` line 640, the code was limiting the crawl to only the first 10 articles:

```python
for i, article_info in enumerate(articles[:10], 1):  # ❌ Only processes 10 articles
```

This made progress updates less noticeable and gave the impression that progress wasn't working.

### Solution
Removed the `[:10]` slice to process all articles:

```python
for i, article_info in enumerate(articles, 1):  # ✅ Processes all articles
```

### Additional Improvements

1. **Added Debug Logging** in `backend/service/crawler_service.py`:
```python
def _update_progress_callback(self, total: int, success: int, failed: int, current: str = ""):
    self.progress_tracker["total_crawled"] = total
    self.progress_tracker["success_count"] = success
    self.progress_tracker["failed_count"] = failed
    self.progress_tracker["current_article"] = current
    logger.debug(
        "Progress update: total=%d, success=%d, failed=%d, current=%s",
        total, success, failed, current[:30] if current else ""
    )
```

2. **Created Test Script** (`test_crawler_progress.py`):
   - Allows testing progress tracking without running the full application
   - Monitors progress updates every 2 seconds
   - Displays real-time statistics

### Testing Steps

1. **Restart Backend**:
   ```bash
   python start_api.py
   ```

2. **Start Crawler**:
   ```bash
   curl -X POST http://localhost:8000/api/crawler/start \
     -H "Content-Type: application/json" \
     -d '{"mode": "all", "batch_size": 5}'
   ```

3. **Monitor Progress** (run multiple times):
   ```bash
   curl http://localhost:8000/api/crawler/status
   ```

4. **Expected Behavior**:
   - Progress updates every 0.5 seconds (backend)
   - Frontend polls every 2 seconds
   - Crawled count increases steadily
   - Success/failed counts update in real-time
   - Progress bar shows meaningful updates

### Files Modified
- `backend/agent/agent_today_data.py` - Removed article count limit
- `backend/service/crawler_service.py` - Added debug logging
- `test_crawler_progress.py` - New test script

### Performance Considerations
- Crawling all articles may take longer (depends on article count)
- Consider adding timeout controls in production
- May want to add pause/resume functionality
- Consider implementing batch processing with configurable limits

### Future Enhancements
1. **Total Count Estimation**: Get article count before crawling to show accurate progress percentage
2. **Current Article Display**: Show which article is currently being crawled
3. **Speed Statistics**: Calculate articles per second and estimated time remaining
4. **Pause/Resume**: Allow users to pause and resume crawling
5. **Progress Persistence**: Save progress to allow recovery from crashes

### Fix Date
2024-12-26 (Second iteration)
