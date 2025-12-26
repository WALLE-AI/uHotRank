import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Download, FileJson, FileSpreadsheet, FileText } from 'lucide-react';
import type { SearchParams } from '@/types/search';

interface ExportDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  filters: SearchParams;
  onExport: (format: 'json' | 'csv' | 'excel', fields: string[]) => Promise<void>;
}

// Available fields for export
const AVAILABLE_FIELDS = [
  { id: 'title', label: '标题', default: true },
  { id: 'url', label: '原文链接', default: true },
  { id: 'category', label: '分类', default: true },
  { id: 'published_time', label: '发布时间', default: true },
  { id: 'content', label: '正文内容', default: false },
  { id: 'tech_detection', label: '技术检测结果', default: false },
  { id: 'content_analysis', label: '内容分析结果', default: false },
  { id: 'created_at', label: '创建时间', default: false },
];

export const ExportDialog: React.FC<ExportDialogProps> = ({
  open,
  onOpenChange,
  filters,
  onExport,
}) => {
  const [format, setFormat] = useState<'json' | 'csv' | 'excel'>('json');
  const [selectedFields, setSelectedFields] = useState<string[]>(
    AVAILABLE_FIELDS.filter((f) => f.default).map((f) => f.id)
  );
  const [isExporting, setIsExporting] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFieldToggle = (fieldId: string) => {
    setSelectedFields((prev) =>
      prev.includes(fieldId) ? prev.filter((id) => id !== fieldId) : [...prev, fieldId]
    );
  };

  const handleSelectAll = () => {
    setSelectedFields(AVAILABLE_FIELDS.map((f) => f.id));
  };

  const handleDeselectAll = () => {
    setSelectedFields([]);
  };

  const handleExport = async () => {
    if (selectedFields.length === 0) {
      return;
    }

    setIsExporting(true);
    setProgress(0);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      await onExport(format, selectedFields);

      clearInterval(progressInterval);
      setProgress(100);

      // Close dialog after successful export
      setTimeout(() => {
        onOpenChange(false);
        setIsExporting(false);
        setProgress(0);
      }, 500);
    } catch (error) {
      setIsExporting(false);
      setProgress(0);
      console.error('Export failed:', error);
    }
  };

  const getFormatIcon = (fmt: string) => {
    switch (fmt) {
      case 'json':
        return <FileJson className="h-4 w-4" />;
      case 'csv':
        return <FileText className="h-4 w-4" />;
      case 'excel':
        return <FileSpreadsheet className="h-4 w-4" />;
      default:
        return <Download className="h-4 w-4" />;
    }
  };

  const getFilterSummary = () => {
    const parts: string[] = [];
    if (filters.keyword) parts.push(`关键词: ${filters.keyword}`);
    if (filters.tech_categories?.length) parts.push(`技术分类: ${filters.tech_categories.length}个`);
    if (filters.sources?.length) parts.push(`来源: ${filters.sources.length}个`);
    if (filters.sentiment) parts.push(`情感: ${filters.sentiment}`);
    if (filters.date_from || filters.date_to) parts.push('日期范围已设置');
    return parts.length > 0 ? parts.join(', ') : '无筛选条件';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>导出文章数据</DialogTitle>
          <DialogDescription>选择导出格式和要包含的字段</DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Current filters summary */}
          <div className="rounded-lg border p-3 bg-muted/50">
            <p className="text-sm font-medium mb-1">当前筛选条件</p>
            <p className="text-xs text-muted-foreground">{getFilterSummary()}</p>
          </div>

          {/* Format selection */}
          <div className="space-y-2">
            <Label htmlFor="format">导出格式</Label>
            <Select value={format} onValueChange={(value: any) => setFormat(value)}>
              <SelectTrigger id="format">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="json">
                  <div className="flex items-center gap-2">
                    <FileJson className="h-4 w-4" />
                    <span>JSON</span>
                  </div>
                </SelectItem>
                <SelectItem value="csv">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    <span>CSV</span>
                  </div>
                </SelectItem>
                <SelectItem value="excel">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="h-4 w-4" />
                    <span>Excel</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Field selection */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>选择字段</Label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleSelectAll}
                  className="h-7 text-xs"
                >
                  全选
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleDeselectAll}
                  className="h-7 text-xs"
                >
                  清空
                </Button>
              </div>
            </div>

            <div className="space-y-2 max-h-[200px] overflow-y-auto border rounded-md p-3">
              {AVAILABLE_FIELDS.map((field) => (
                <div key={field.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={field.id}
                    checked={selectedFields.includes(field.id)}
                    onCheckedChange={() => handleFieldToggle(field.id)}
                  />
                  <Label
                    htmlFor={field.id}
                    className="text-sm font-normal cursor-pointer flex-1"
                  >
                    {field.label}
                  </Label>
                </div>
              ))}
            </div>

            <p className="text-xs text-muted-foreground">
              已选择 {selectedFields.length} 个字段
            </p>
          </div>

          {/* Export progress */}
          {isExporting && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>导出进度</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} />
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isExporting}
          >
            取消
          </Button>
          <Button
            type="button"
            onClick={handleExport}
            disabled={isExporting || selectedFields.length === 0}
          >
            {isExporting ? (
              <>
                <Download className="mr-2 h-4 w-4 animate-spin" />
                导出中...
              </>
            ) : (
              <>
                {getFormatIcon(format)}
                <span className="ml-2">导出</span>
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
