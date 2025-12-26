# Bug Fix: Article Content Undefined Error

## Issue
Frontend error: `Cannot read properties of undefined (reading 'length')` at ArticleCard.tsx:43

## Root Cause
The `article.content` field was being accessed without checking if it exists. In some cases, articles from Elasticsearch might not have content, causing the error when trying to call `.length` on undefined.

## Files Modified

### 1. Frontend Type Definition
**File**: `frontend/src/types/article.ts`

**Change**: Made `content` field optional
```typescript
export interface Article {
  // ... other fields
  content?: string; // Changed from required to optional
  // ... other fields
}
```

### 2. ArticleCard Component
**File**: `frontend/src/components/article/ArticleCard.tsx`

**Changes**:
1. Updated `truncateContent` function to handle undefined content:
```typescript
const truncateContent = (content: string | undefined, maxLength: number = 150) => {
  if (!content) return '';
  if (content.length <= maxLength) return content;
  return content.slice(0, maxLength) + '...';
};
```

2. Added fallback text when displaying content:
```typescript
{article.content ? truncateContent(article.content) : '暂无内容'}
```

### 3. ArticleDetail Component
**File**: `frontend/src/components/article/ArticleDetail.tsx`

**Change**: Added fallback for missing content:
```typescript
<p className="whitespace-pre-wrap leading-relaxed text-sm sm:text-base">
  {article.content || '暂无内容'}
</p>
```

### 4. Backend Schema
**File**: `backend/schemas/article.py`

**Change**: Made `content` field optional in ArticleBase model:
```python
class ArticleBase(BaseModel):
    # ... other fields
    content: Optional[str] = Field(None, description="文章内容")
    # ... other fields
```

### 5. Backend Service
**File**: `backend/service/article_service.py`

**Change**: Updated article mapping to use None instead of empty string:
```python
article = ArticleDetail(
    # ... other fields
    content=doc.get("content") or None,  # Use None instead of empty string
    # ... other fields
)
```

## Testing
After these changes:
- ✅ ArticleCard renders without errors when content is missing
- ✅ ArticleDetail shows "暂无内容" when content is missing
- ✅ No TypeScript errors in frontend
- ✅ Backend schema properly handles optional content

## Prevention
To prevent similar issues in the future:
1. Always check for undefined/null before accessing properties
2. Use optional chaining (`?.`) when accessing nested properties
3. Provide fallback values for optional fields
4. Keep frontend types in sync with backend schemas
5. Make fields optional in schemas if they might not always be present in the data source

## Related Files
- `frontend/src/components/article/ArticleCard.tsx`
- `frontend/src/components/article/ArticleDetail.tsx`
- `frontend/src/types/article.ts`
- `backend/schemas/article.py`
- `backend/service/article_service.py`
