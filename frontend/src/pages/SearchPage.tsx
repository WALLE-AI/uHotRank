import { useState } from 'react';
import { SearchBar } from '@/components/search/SearchBar';
import { FilterPanel } from '@/components/search/FilterPanel';
import { SearchResults } from '@/components/search/SearchResults';
import { Button } from '@/components/ui/button';
import { SlidersHorizontal, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export function SearchPage() {
  const [showFilters, setShowFilters] = useState(false);

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">搜索文章</h1>
        <p className="text-muted-foreground">搜索和筛选热门文章，发现感兴趣的内容</p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <SearchBar />
      </div>

      {/* Filter Toggle (Mobile) */}
      <div className="mb-4 lg:hidden">
        <Button variant="outline" onClick={() => setShowFilters(!showFilters)} className="w-full">
          {showFilters ? (
            <>
              <X className="mr-2 h-4 w-4" />
              隐藏筛选
            </>
          ) : (
            <>
              <SlidersHorizontal className="mr-2 h-4 w-4" />
              显示筛选
            </>
          )}
        </Button>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filter Panel - Sidebar on desktop, collapsible on mobile */}
        <aside className={cn('lg:col-span-1', showFilters ? 'block' : 'hidden lg:block')}>
          <div className="sticky top-4">
            <FilterPanel onFilterChange={() => setShowFilters(false)} />
          </div>
        </aside>

        {/* Search Results */}
        <main className="lg:col-span-3">
          <SearchResults />
        </main>
      </div>
    </div>
  );
}
