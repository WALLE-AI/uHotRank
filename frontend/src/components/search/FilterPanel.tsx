import React, { useState } from 'react';
import { Filter, X, Calendar } from 'lucide-react';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Checkbox } from '../ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useSearchStore } from '../../stores/searchStore';
import { cn } from '../../lib/utils';

interface FilterPanelProps {
  onFilterChange?: () => void;
  className?: string;
}

// Common tech categories
const TECH_CATEGORIES = [
  'AI/机器学习',
  '前端开发',
  '后端开发',
  '移动开发',
  '云计算',
  '数据库',
  '网络安全',
  '区块链',
  'DevOps',
  '大数据',
];

// Common sources (these should ideally come from API)
const SOURCES = [
  '知乎热榜',
  '微博热搜',
  'V2EX',
  '掘金',
  'GitHub Trending',
  'Hacker News',
  '少数派',
  'InfoQ',
];

// Sentiment options
const SENTIMENTS = [
  { value: '', label: '全部' },
  { value: 'positive', label: '正面' },
  { value: 'neutral', label: '中性' },
  { value: 'negative', label: '负面' },
];

export const FilterPanel: React.FC<FilterPanelProps> = ({ onFilterChange, className }) => {
  const { searchParams, updateSearchParams, clearFilters, search } = useSearchStore();

  const [localFilters, setLocalFilters] = useState({
    tech_categories: searchParams.tech_categories || [],
    sources: searchParams.sources || [],
    sentiment: searchParams.sentiment || '',
    date_from: searchParams.date_from || '',
    date_to: searchParams.date_to || '',
  });

  const handleTechCategoryToggle = (category: string) => {
    setLocalFilters((prev) => {
      const categories = prev.tech_categories.includes(category)
        ? prev.tech_categories.filter((c) => c !== category)
        : [...prev.tech_categories, category];
      return { ...prev, tech_categories: categories };
    });
  };

  const handleSourceToggle = (source: string) => {
    setLocalFilters((prev) => {
      const sources = prev.sources.includes(source)
        ? prev.sources.filter((s) => s !== source)
        : [...prev.sources, source];
      return { ...prev, sources };
    });
  };

  const handleSentimentChange = (value: string) => {
    setLocalFilters((prev) => ({ ...prev, sentiment: value }));
  };

  const handleDateFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalFilters((prev) => ({ ...prev, date_from: e.target.value }));
  };

  const handleDateToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalFilters((prev) => ({ ...prev, date_to: e.target.value }));
  };

  const handleApplyFilters = () => {
    const filters = {
      ...searchParams,
      tech_categories:
        localFilters.tech_categories.length > 0 ? localFilters.tech_categories : undefined,
      sources: localFilters.sources.length > 0 ? localFilters.sources : undefined,
      sentiment: localFilters.sentiment || undefined,
      date_from: localFilters.date_from || undefined,
      date_to: localFilters.date_to || undefined,
      page: 1, // Reset to first page when filters change
    };

    updateSearchParams(filters);
    search(filters);
    onFilterChange?.();
  };

  const handleClearFilters = () => {
    setLocalFilters({
      tech_categories: [],
      sources: [],
      sentiment: '',
      date_from: '',
      date_to: '',
    });
    clearFilters();
    onFilterChange?.();
  };

  const hasActiveFilters =
    localFilters.tech_categories.length > 0 ||
    localFilters.sources.length > 0 ||
    localFilters.sentiment ||
    localFilters.date_from ||
    localFilters.date_to;

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Filter className="h-4 w-4" />
            筛选条件
          </CardTitle>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearFilters}
              className="h-8 px-2 text-xs"
            >
              <X className="mr-1 h-3 w-3" />
              清除
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Tech Categories */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">技术分类</Label>
          <div className="grid grid-cols-2 gap-2">
            {TECH_CATEGORIES.map((category) => (
              <div key={category} className="flex items-center space-x-2">
                <Checkbox
                  id={`tech-${category}`}
                  checked={localFilters.tech_categories.includes(category)}
                  onCheckedChange={() => handleTechCategoryToggle(category)}
                />
                <label htmlFor={`tech-${category}`} className="text-sm cursor-pointer select-none">
                  {category}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Sources */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">文章来源</Label>
          <div className="grid grid-cols-2 gap-2">
            {SOURCES.map((source) => (
              <div key={source} className="flex items-center space-x-2">
                <Checkbox
                  id={`source-${source}`}
                  checked={localFilters.sources.includes(source)}
                  onCheckedChange={() => handleSourceToggle(source)}
                />
                <label htmlFor={`source-${source}`} className="text-sm cursor-pointer select-none">
                  {source}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Sentiment */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">情感分析</Label>
          <Select value={localFilters.sentiment} onValueChange={handleSentimentChange}>
            <SelectTrigger>
              <SelectValue placeholder="选择情感类型" />
            </SelectTrigger>
            <SelectContent>
              {SENTIMENTS.map((sentiment) => (
                <SelectItem key={sentiment.value} value={sentiment.value}>
                  {sentiment.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Date Range */}
        <div className="space-y-2">
          <Label className="text-sm font-medium flex items-center gap-2">
            <Calendar className="h-3.5 w-3.5" />
            日期范围
          </Label>
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <Label htmlFor="date-from" className="text-xs text-muted-foreground">
                开始日期
              </Label>
              <Input
                id="date-from"
                type="date"
                value={localFilters.date_from}
                onChange={handleDateFromChange}
                max={localFilters.date_to || undefined}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="date-to" className="text-xs text-muted-foreground">
                结束日期
              </Label>
              <Input
                id="date-to"
                type="date"
                value={localFilters.date_to}
                onChange={handleDateToChange}
                min={localFilters.date_from || undefined}
              />
            </div>
          </div>
        </div>

        {/* Apply Button */}
        <Button onClick={handleApplyFilters} className="w-full">
          应用筛选
        </Button>
      </CardContent>
    </Card>
  );
};
