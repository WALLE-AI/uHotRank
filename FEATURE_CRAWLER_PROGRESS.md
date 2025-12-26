# Feature: Crawler Progress Tracking

## Issue
爬虫管理模块的爬取进度没有显示实时进度，进度条始终为 0。

## Root Cause
`CrawlerService` 中的爬虫任务在线程池中同步执行，没有机制来实时更新进度状态。爬虫函数 `scrape_all_articles_to_es` 也没有提供进度回调接口。

## Solution
实现了一个进度跟踪机制：

1. **共享进度跟踪器**：在 `CrawlerService` 中添加类级别的 `progress_tracker` 字典
2. **进度回调函数**：添加 `_update_progress_callback` 方法供爬虫函数调用
3. **异步进度更新**：创建后台任务定期从 `progress_tracker` 更新状态
4. **爬虫函数修改**：添加 `progress_callback` 参数并在处理每篇文章时调用

## Files Modified

### 1. CrawlerService
**File**: `backend/service/crawler_service.py`

**Changes**:

1. 添加共享进度跟踪器：
```python
class CrawlerService:
    # 共享的进度跟踪器（可以被爬虫函数访问）
    progress_tracker: Dict[str, Any] = {
        "total_crawled": 0,
        "success_count": 0,
        "failed_count": 0,
        "current_article": "",
    }
```

2. 添加进度回调方法：
```python
def _update_progress_callback(self, total: int, success: int, failed: int, current: str = ""):
    """进度回调函数（由爬虫函数调用）"""
    self.progress_tracker["total_crawled"] = total
    self.progress_tracker["success_count"] = success
    self.progress_tracker["failed_count"] = failed
    self.progress_tracker["current_article"] = current
```

3. 修改 `_run_crawler_task` 方法：
```python
async def _run_crawler_task(self, mode: str, batch_size: int):
    # 重置进度跟踪器
    self.progress_tracker = {
        "total_crawled": 0,
        "success_count": 0,
        "failed_count": 0,
        "current_article": "",
    }
    
    # 创建异步任务定期更新状态
    async def update_progress():
        while self.task_status["is_running"]:
            self.task_status["total_crawled"] = self.progress_tracker["total_crawled"]
            self.task_status["success_count"] = self.progress_tracker["success_count"]
            self.task_status["failed_count"] = self.progress_tracker["failed_count"]
            await asyncio.sleep(0.5)  # 每0.5秒更新一次
    
    progress_task = asyncio.create_task(update_progress())
    
    # 运行爬虫并传递回调
    def run_crawler():
        return scrape_all_articles_to_es(
            es_index_name="tophub_articles",
            batch_size=batch_size,
            check_duplicate=True,
            skip_duplicate=True,
            enable_analysis=enable_analysis,
            progress_callback=self._update_progress_callback,
        )
    
    result = await loop.run_in_executor(None, run_crawler)
    
    # 停止进度更新任务
    progress_task.cancel()
```

### 2. Crawler Function
**File**: `backend/agent/agent_today_data.py`

**Changes**:

1. 添加 `progress_callback` 参数：
```python
def scrape_all_articles_to_es(
    es_index_name: str = "tophub_articles",
    batch_size: int = 10,
    check_duplicate: bool = True,
    skip_duplicate: bool = True,
    enable_analysis: bool = True,
    progress_callback=None  # 新增
):
```

2. 在处理每篇文章时调用回调：
```python
for i, article_info in enumerate(articles[:5], 1):
    print(f"[{i}/{len(articles)}] 正在爬取: {article_info['title']}")
    
    # 调用进度回调
    if progress_callback:
        progress_callback(
            total=success_count + failed_count + duplicate_count,
            success=success_count,
            failed=failed_count,
            current=article_info['title']
        )
    
    article_content = gentle_scrape_content(article_info)
    # ...
```

## How It Works

### Data Flow

1. **前端轮询状态**
   - 前端每秒调用 `GET /api/crawler/status`

2. **后台进度更新**
   - `update_progress()` 任务每 0.5 秒从 `progress_tracker` 更新 `task_status`

3. **爬虫函数回调**
   - 爬虫处理每篇文章时调用 `progress_callback()`
   - 回调更新 `progress_tracker` 中的计数

4. **状态同步**
   ```
   爬虫函数 → progress_callback() → progress_tracker
                                           ↓
   前端 ← API ← task_status ← update_progress()
   ```

### Progress Update Cycle

```
Time 0.0s: 爬虫开始，progress_tracker = {total: 0, success: 0, failed: 0}
Time 0.5s: update_progress() 更新 task_status
Time 1.0s: 前端轮询，获取 task_status
Time 1.5s: 爬虫处理第1篇文章，调用 progress_callback(total=1, success=1, ...)
Time 2.0s: update_progress() 更新 task_status (total=1, success=1)
Time 2.5s: 前端轮询，看到进度更新 ✅
...
```

## Benefits

- ✅ 实时进度显示
- ✅ 显示当前正在处理的文章
- ✅ 显示成功/失败计数
- ✅ 不阻塞异步事件循环
- ✅ 线程安全（通过共享字典）
- ✅ 最小化性能影响（0.5秒更新间隔）

## Testing

启动爬虫后，前端应该能看到：
- ✅ 总爬取数实时增加
- ✅ 成功/失败计数更新
- ✅ 进度条移动
- ✅ 当前文章标题显示（如果前端实现）

## Notes

- 进度更新间隔为 0.5 秒，平衡了实时性和性能
- `progress_tracker` 是类级别变量，在单例模式下全局共享
- 爬虫函数在线程池中运行，回调是线程安全的（Python GIL）
- 如果不传递 `progress_callback`，爬虫函数仍然正常工作（向后兼容）

## Related Files

- `backend/service/crawler_service.py` (进度跟踪和更新)
- `backend/agent/agent_today_data.py` (进度回调)
- `frontend/src/components/crawler/CrawlerProgress.tsx` (前端显示)
