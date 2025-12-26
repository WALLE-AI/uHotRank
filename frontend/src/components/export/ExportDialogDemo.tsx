/**
 * Demo component showing how to use the ExportDialog
 * This file is for documentation purposes and can be removed in production
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Download } from 'lucide-react';
import { ExportDialog } from './ExportDialog';
import { downloadAsJSON, downloadAsCSV, downloadAsExcel } from '@/utils/export';
import { useToast } from '@/hooks/use-toast';
import type { Article } from '@/types/article';
import type { SearchParams } from '@/types/search';

// Sample data for demo
const sampleArticles: Article[] = [
  {
    id: '1',
    url: 'https://example.com/article1',
    title: '示例文章 1',
    category: '技术',
    published_time: '2024-12-26T00:00:00Z',
    content: '这是示例文章的内容...',
    tech_detection: {
      is_tech_related: true,
      categories: ['AI', 'Machine Learning'],
      confidence: 0.95,
      matched_keywords: ['人工智能', '机器学习'],
    },
    content_analysis: {
      keywords: ['AI', '技术', '创新'],
      topics: ['人工智能', '技术发展'],
      summary: '这是一篇关于人工智能的文章',
      sentiment: 'positive',
      category: '技术',
      entities: [
        { name: 'OpenAI', type: 'Organization' },
        { name: 'GPT', type: 'Technology' },
      ],
    },
    created_at: '2024-12-26T00:00:00Z',
  },
  {
    id: '2',
    url: 'https://example.com/article2',
    title: '示例文章 2',
    category: '新闻',
    published_time: '2024-12-25T00:00:00Z',
    content: '这是另一篇示例文章的内容...',
    created_at: '2024-12-25T00:00:00Z',
  },
];

const sampleFilters: SearchParams = {
  keyword: 'AI',
  tech_categories: ['Machine Learning'],
  page: 1,
  size: 20,
  sort_by: 'time',
};

export function ExportDialogDemo() {
  const [open, setOpen] = useState(false);
  const { toast } = useToast();

  const handleExport = async (format: 'json' | 'csv' | 'excel', fields: string[]) => {
    try {
      switch (format) {
        case 'json':
          downloadAsJSON(sampleArticles, fields);
          break;
        case 'csv':
          downloadAsCSV(sampleArticles, fields);
          break;
        case 'excel':
          downloadAsExcel(sampleArticles, fields);
          break;
      }

      toast({
        title: '导出成功',
        description: `已导出 ${sampleArticles.length} 篇文章为 ${format.toUpperCase()} 格式`,
      });
    } catch (error) {
      console.error('Export error:', error);
      toast({
        title: '导出失败',
        description: '导出过程中发生错误，请重试',
        variant: 'destructive',
      });
    }
  };

  return (
    <div className="p-8 space-y-4">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold">导出功能演示</h2>
        <p className="text-muted-foreground">
          点击下面的按钮打开导出对话框，体验数据导出功能
        </p>
      </div>

      <div className="space-y-4">
        <div className="p-4 border rounded-lg bg-muted/50">
          <h3 className="font-semibold mb-2">示例数据</h3>
          <ul className="text-sm space-y-1 text-muted-foreground">
            <li>• 文章数量: {sampleArticles.length}</li>
            <li>• 包含技术检测结果: 1 篇</li>
            <li>• 包含内容分析结果: 1 篇</li>
          </ul>
        </div>

        <Button onClick={() => setOpen(true)}>
          <Download className="mr-2 h-4 w-4" />
          打开导出对话框
        </Button>
      </div>

      <ExportDialog
        open={open}
        onOpenChange={setOpen}
        filters={sampleFilters}
        onExport={handleExport}
      />

      <div className="mt-8 p-4 border rounded-lg">
        <h3 className="font-semibold mb-2">使用说明</h3>
        <ol className="text-sm space-y-2 text-muted-foreground list-decimal list-inside">
          <li>点击"打开导出对话框"按钮</li>
          <li>选择导出格式（JSON、CSV 或 Excel）</li>
          <li>选择要导出的字段（可以使用"全选"或"清空"按钮）</li>
          <li>点击"导出"按钮</li>
          <li>文件将自动下载到您的计算机</li>
        </ol>
      </div>

      <div className="mt-4 p-4 border rounded-lg bg-blue-50 dark:bg-blue-950">
        <h3 className="font-semibold mb-2 text-blue-900 dark:text-blue-100">提示</h3>
        <ul className="text-sm space-y-1 text-blue-800 dark:text-blue-200">
          <li>• JSON 格式适合程序处理和数据交换</li>
          <li>• CSV 格式适合在 Excel 或其他表格软件中打开</li>
          <li>• Excel 格式包含 UTF-8 BOM，确保中文正确显示</li>
          <li>• 可以选择性导出字段，减少文件大小</li>
        </ul>
      </div>
    </div>
  );
}
