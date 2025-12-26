import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Search, X, Clock, Command } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { useSearchStore } from '../../stores/searchStore';
import { cn } from '../../lib/utils';

interface SearchBarProps {
  onSearch?: (keyword: string) => void;
  placeholder?: string;
  className?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = '搜索文章标题或内容...',
  className,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [debouncedValue, setDebouncedValue] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Derive showSuggestions from debouncedValue instead of using state
  const showSuggestions = debouncedValue.length > 0;

  const {
    searchParams,
    searchHistory,
    search,
    updateSearchParams,
    removeFromHistory,
    clearHistory,
  } = useSearchStore();

  // Debounced search suggestions
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(inputValue);
    }, 300);

    return () => clearTimeout(timer);
  }, [inputValue]);

  // Keyboard shortcut (Ctrl/Cmd + K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }

      // ESC to close suggestions/history
      if (e.key === 'Escape') {
        setShowHistory(false);
        setInputValue('');
        inputRef.current?.blur();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Click outside to close suggestions/history
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowHistory(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = useCallback(
    (keyword: string) => {
      const trimmedKeyword = keyword.trim();
      if (trimmedKeyword) {
        updateSearchParams({ keyword: trimmedKeyword, page: 1 });
        search({ ...searchParams, keyword: trimmedKeyword, page: 1 });
        onSearch?.(trimmedKeyword);
        setShowHistory(false);
      }
    },
    [searchParams, search, updateSearchParams, onSearch]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(inputValue);
  };

  const handleClear = () => {
    setInputValue('');
    setShowHistory(false);
    inputRef.current?.focus();
  };

  const handleFocus = () => {
    if (searchHistory.length > 0 && !inputValue) {
      setShowHistory(true);
    }
  };

  const handleHistoryClick = (keyword: string) => {
    setInputValue(keyword);
    handleSearch(keyword);
  };

  const handleRemoveHistory = (e: React.MouseEvent, keyword: string) => {
    e.stopPropagation();
    removeFromHistory(keyword);
  };

  const handleClearHistory = (e: React.MouseEvent) => {
    e.stopPropagation();
    clearHistory();
    setShowHistory(false);
  };

  // Filter history based on input
  const filteredHistory = searchHistory.filter((keyword) =>
    keyword.toLowerCase().includes(inputValue.toLowerCase())
  );

  const showDropdown = (showSuggestions || showHistory) && (inputValue || searchHistory.length > 0);

  return (
    <div ref={containerRef} className={cn('relative w-full', className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <Search className="absolute left-3 h-4 w-4 text-muted-foreground" />
          <Input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onFocus={handleFocus}
            placeholder={placeholder}
            className="pl-10 pr-20"
          />
          <div className="absolute right-2 flex items-center gap-1">
            {inputValue && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleClear}
                className="h-7 w-7 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
            <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
              <Command className="h-3 w-3" />K
            </kbd>
          </div>
        </div>
      </form>

      {/* Suggestions/History Dropdown */}
      {showDropdown && (
        <div className="absolute z-50 mt-2 w-full rounded-md border bg-popover p-2 shadow-md">
          {showHistory && searchHistory.length > 0 && (
            <div>
              <div className="flex items-center justify-between px-2 py-1.5">
                <span className="text-xs font-medium text-muted-foreground">搜索历史</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearHistory}
                  className="h-6 px-2 text-xs"
                >
                  清除
                </Button>
              </div>
              <div className="space-y-1">
                {filteredHistory.map((keyword) => (
                  <div
                    key={keyword}
                    onClick={() => handleHistoryClick(keyword)}
                    className="flex items-center justify-between rounded-sm px-2 py-1.5 text-sm hover:bg-accent cursor-pointer group"
                  >
                    <div className="flex items-center gap-2">
                      <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                      <span>{keyword}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => handleRemoveHistory(e, keyword)}
                      className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {showSuggestions && inputValue && filteredHistory.length === 0 && (
            <div className="px-2 py-1.5 text-sm text-muted-foreground">
              按 Enter 搜索 "{inputValue}"
            </div>
          )}
        </div>
      )}
    </div>
  );
};
