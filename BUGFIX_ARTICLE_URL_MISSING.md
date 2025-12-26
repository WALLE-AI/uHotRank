# Bug Fix: Article URL Missing in List Response

## Issue
点击文章卡片无法跳转到原始文章地址。

## Root Cause
后端的 `ArticleListItem` 模型中缺少 `url` 字段，导致前端收到的文章列表数据中没有 URL 信息。

## Files Modified

### 1. Backend Schema
**File**: `backend/schemas/article.py`

**Change**: 在 `ArticleListItem` 模型中添加 `url` 字段
```python
class ArticleListItem(BaseModel):
    """文章列表项模型（简化版）"""
    id: str = Field(..., description="文章ID")
    url: str = Field(..., description="文章URL")  # 新增
    title: str = Field(..., description="文章标题")
    category: str = Field(..., description="文章分类")
    published_time: Optional[str] = Field(None, description="发布时间")
    summary: Optional[str] = Field(None, description="内容摘要")
    sentiment: Optional[str] = Field(None, description="情感倾向")
```

### 2. Backend Service
**File**: `backend/service/article_service.py`

**Changes**: 在两个地方添加 URL 字段到 ArticleListItem 实例

**位置 1 - get_articles 方法**:
```python
article = ArticleListItem(
    id=hit["_id"],
    url=source.get("original_url", "") or source.get("tophub_url", ""),  # 新增
    title=source.get("title", ""),
    category=source.get("category", ""),
    published_time=source.get("publish_date", ""),
    summary=source.get("content_analysis", {}).get("summary"),
    sentiment=source.get("content_analysis", {}).get("sentiment"),
)
```

**位置 2 - search_articles 方法**:
```python
article = ArticleListItem(
    id=hit["_id"],
    url=source.get("original_url", "") or source.get("tophub_url", ""),  # 新增
    title=source.get("title", ""),
    category=source.get("category", ""),
    published_time=source.get("publish_date", ""),
    summary=source.get("content_analysis", {}).get("summary"),
    sentiment=source.get("content_analysis", {}).get("sentiment"),
)
```

### 3. Frontend Component
**File**: `frontend/src/components/article/ArticleCard.tsx`

**Change**: 添加调试日志和 URL 验证
```typescript
const handleClick = () => {
  // Check if URL exists and is valid
  if (!article.url) {
    console.error('Article URL is missing:', article);
    return;
  }
  
  // Log for debugging
  console.log('Opening article URL:', article.url);
  
  // Open the original article URL directly in a new tab
  window.open(article.url, '_blank', 'noopener,noreferrer');
};
```

## Data Flow

### Before (Broken)
1. Backend returns ArticleListItem without `url` field
2. Frontend receives: `{ id, title, category, ... }` (no url)
3. User clicks card
4. `article.url` is undefined
5. `window.open(undefined, ...)` does nothing

### After (Fixed)
1. Backend returns ArticleListItem with `url` field
2. Frontend receives: `{ id, url, title, category, ... }`
3. User clicks card
4. `article.url` contains the original article URL
5. `window.open(url, '_blank', ...)` opens the article in new tab ✅

## URL Priority
The service tries to get the URL in this order:
1. `original_url` (preferred - the actual article URL)
2. `tophub_url` (fallback - the TopHub listing URL)

This ensures we always have a URL to open.

## Testing
After these changes:
- ✅ Article list API returns URL field
- ✅ Frontend receives URL in article data
- ✅ Clicking article card opens original URL in new tab
- ✅ Console logs show URL being opened (for debugging)
- ✅ Error logged if URL is missing (for debugging)

## Related Files
- `backend/schemas/article.py` (added url field)
- `backend/service/article_service.py` (populate url field)
- `frontend/src/components/article/ArticleCard.tsx` (added validation)

## Notes
- The URL field is required in the schema to ensure data consistency
- The service uses fallback logic to handle both `original_url` and `tophub_url`
- Debug logging helps identify issues during development
- The fix applies to both article list and search results
