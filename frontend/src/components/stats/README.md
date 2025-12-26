# Statistics Components

This directory contains all statistics and visualization components for the UHotRank application.

## Components

### StatsOverview
Displays overview statistics cards showing:
- Total articles count
- Tech articles count
- Today's new articles count

### KeywordCloud
Interactive word cloud visualization using ECharts:
- Displays top keywords with size based on frequency
- Click on keywords to search for related articles
- Uses echarts-wordcloud plugin

### CategoryChart
Pie chart showing technology category distribution:
- Interactive donut chart
- Click on categories to filter articles
- Shows percentage distribution

### SentimentChart
Bar chart showing sentiment analysis distribution:
- Displays positive, neutral, and negative sentiment counts
- Color-coded bars (green for positive, blue for neutral, red for negative)
- Click to filter by sentiment

### SourceChart
Horizontal bar chart showing article source distribution:
- Displays top 10 sources
- Click on sources to filter articles
- Sorted by article count

### TrendChart
Line chart showing article publishing trends over time:
- Area chart with smooth curves
- Shows article count over time
- Responsive to date range filters

## Usage

```tsx
import {
  StatsOverview,
  KeywordCloud,
  CategoryChart,
  SentimentChart,
  SourceChart,
  TrendChart,
} from '@/components/stats';

// In your component
<StatsOverview statistics={statistics} loading={loading} />
<KeywordCloud keywords={keywords} loading={loading} />
<CategoryChart data={categoryData} loading={loading} />
<SentimentChart data={sentimentData} loading={loading} />
<SourceChart data={sourceData} loading={loading} />
<TrendChart data={trendData} loading={loading} />
```

## Dependencies

- echarts: ^6.0.0
- echarts-for-react: ^3.0.5
- echarts-wordcloud: ^2.1.0 (installed with --legacy-peer-deps)

## Features

- All charts are interactive and clickable
- Clicking on chart elements navigates to search page with appropriate filters
- Loading states with skeleton screens
- Empty states with helpful messages
- Responsive design
- Theme-aware (works with light/dark mode)
