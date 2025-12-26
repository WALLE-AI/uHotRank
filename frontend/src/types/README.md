# Type Definitions

This directory contains all TypeScript type definitions for the UHotRank frontend application.

## Files

### article.ts
Contains article-related type definitions:
- `Entity` - Entity information (name, type)
- `ContentAnalysis` - LLM-generated content analysis results
- `TechDetection` - Technical content detection results
- `Article` - Main article data structure

### search.ts
Contains search and statistics-related type definitions:
- `SearchParams` - Search and filter parameters
- `SearchResult` - Search results with aggregations
- `Statistics` - System statistics and metrics
- `CrawlerTask` - Crawler task configuration and status

### api.ts
Contains API-related type definitions:
- `ApiResponse<T>` - Generic API response wrapper
- `ApiError` - API error structure
- `PaginationParams` - Pagination parameters
- `PaginatedResponse<T>` - Paginated response structure

### index.ts
Central export file that re-exports all types for easy importing.

## Usage

Import types from the central index file:

```typescript
import type {
  Article,
  TechDetection,
  ContentAnalysis,
  SearchParams,
  SearchResult,
  Statistics,
  CrawlerTask,
  ApiResponse,
  ApiError,
} from '@/types';
```

## Type Definitions Overview

### Article Types

**Article**: Main article data structure
- `id`: Unique identifier
- `url`: Original article URL
- `title`: Article title
- `category`: Article category
- `published_time`: Publication timestamp
- `content`: Article content
- `tech_detection?`: Optional technical detection results
- `content_analysis?`: Optional content analysis results
- `created_at`: Creation timestamp

**TechDetection**: Technical content detection results
- `is_tech_related`: Boolean flag for tech content
- `categories`: Array of technical categories
- `confidence`: Confidence score (0-1)
- `matched_keywords`: Array of matched technical keywords

**ContentAnalysis**: LLM-generated content analysis
- `keywords`: Extracted keywords
- `topics`: Identified topics
- `summary`: Content summary
- `sentiment`: Sentiment analysis ('positive' | 'neutral' | 'negative')
- `category`: Content category
- `entities`: Array of identified entities

**Entity**: Named entity information
- `name`: Entity name
- `type`: Entity type

### Search Types

**SearchParams**: Search and filter parameters
- `keyword?`: Search keyword
- `tech_categories?`: Filter by technical categories
- `sources?`: Filter by article sources
- `sentiment?`: Filter by sentiment
- `date_from?`: Start date for date range filter
- `date_to?`: End date for date range filter
- `page`: Current page number
- `size`: Page size
- `sort_by?`: Sort order ('relevance' | 'time' | 'popularity')

**SearchResult**: Search results with aggregations
- `total`: Total number of results
- `articles`: Array of article results
- `aggregations?`: Optional aggregation data
  - `categories`: Category distribution
  - `sources`: Source distribution
  - `sentiments`: Sentiment distribution

**Statistics**: System statistics and metrics
- `total_articles`: Total article count
- `tech_articles`: Technical article count
- `today_new`: New articles today
- `top_keywords`: Top keywords with counts
- `category_distribution`: Category distribution
- `sentiment_distribution`: Sentiment distribution
- `source_distribution`: Source distribution
- `time_series`: Time series data

**CrawlerTask**: Crawler task configuration and status
- `id`: Task identifier
- `mode`: Crawl mode ('all' | 'tech_only' | 'with_analysis')
- `status`: Task status ('idle' | 'running' | 'completed' | 'error')
- `progress`: Progress information
  - `total`: Total items to crawl
  - `crawled`: Items crawled so far
  - `success`: Successful crawls
  - `failed`: Failed crawls
- `started_at?`: Task start timestamp
- `completed_at?`: Task completion timestamp
- `error_message?`: Error message if failed

### API Types

**ApiResponse<T>**: Generic API response wrapper
- `data`: Response data of type T
- `message?`: Optional message
- `success`: Success flag

**ApiError**: API error structure
- `message`: Error message
- `code?`: Optional error code
- `details?`: Optional error details

**PaginationParams**: Pagination parameters
- `page`: Page number
- `size`: Page size

**PaginatedResponse<T>**: Paginated response structure
- `items`: Array of items of type T
- `total`: Total item count
- `page`: Current page
- `size`: Page size
- `total_pages`: Total number of pages

## Validation

All type definitions have been validated using TypeScript's type checker. Run `npm run type-check` to verify type correctness.

## Testing

Type definitions are tested in `__tests__/types.test.ts` to ensure:
- All types are properly exported
- All required fields are present
- Optional fields work correctly
- Type constraints are enforced
