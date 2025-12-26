# Bug Fix: Article Card Direct URL Navigation

## Issue
The API was returning 404 errors when trying to fetch article details:
```
GET http://localhost:8000/api/articles/https://www.zhihu.com/question/1982019816844986360 404 (Not Found)
```

## User Requirement
Instead of navigating to an internal article detail page, clicking an article card should directly open the original article URL in a new tab.

## Solution
Modified ArticleCard to open the original article URL directly using `window.open()`.

### Files Modified

#### ArticleCard Component
**File**: `frontend/src/components/article/ArticleCard.tsx`

**Changes**:
1. Removed React Router navigation
2. Changed click handler to open URL directly in new tab
3. Removed unused `useNavigate` import

**Before**:
```typescript
import { useNavigate } from 'react-router-dom';

const navigate = useNavigate();
const handleClick = () => {
  const encodedId = encodeURIComponent(article.id);
  navigate(`/articles/${encodedId}`);
};
```

**After**:
```typescript
const handleClick = () => {
  // Open the original article URL directly in a new tab
  window.open(article.url, '_blank', 'noopener,noreferrer');
};
```

## Behavior

### Before
1. User clicks article card
2. App navigates to `/articles/:id`
3. ArticleDetailPage fetches article from API
4. User sees article detail page with "查看原文" link
5. User clicks "查看原文" to open original URL

### After
1. User clicks article card
2. Original article URL opens directly in new tab
3. User immediately sees the original article content

## Benefits
- ✅ Faster access to article content (one click instead of two)
- ✅ No API calls needed for article details
- ✅ Opens in new tab, preserving the article list
- ✅ More intuitive user experience
- ✅ No routing issues with URL-based IDs

## Security
The `window.open()` call includes security parameters:
- `'_blank'`: Opens in new tab
- `'noopener'`: Prevents new page from accessing `window.opener`
- `'noreferrer'`: Doesn't send referrer information

## Note
The ArticleDetailPage and ArticleDetail components are still available and functional, but are no longer accessed through article card clicks. They could be used for:
- Future features (e.g., showing analysis results)
- Admin/moderation interfaces
- Article preview before opening external link

## Related Files
- `frontend/src/components/article/ArticleCard.tsx` (modified)
- `frontend/src/pages/ArticleDetailPage.tsx` (no longer used by card clicks)
- `frontend/src/components/article/ArticleDetail.tsx` (no longer used by card clicks)
