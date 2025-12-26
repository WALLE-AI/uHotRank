# Export Components

This directory contains components for exporting article data to various formats.

## Components

### ExportDialog

A dialog component that allows users to export articles in different formats (JSON, CSV, Excel) with customizable field selection.

**Props:**
- `open: boolean` - Controls dialog visibility
- `onOpenChange: (open: boolean) => void` - Callback when dialog open state changes
- `filters: SearchParams` - Current search/filter parameters to display in the dialog
- `onExport: (format, fields) => Promise<void>` - Callback to handle the export action

**Features:**
- Format selection (JSON, CSV, Excel)
- Field selection with checkboxes
- Select all / Deselect all functionality
- Export progress indicator
- Current filter summary display

**Usage:**

```tsx
import { ExportDialog } from '@/components/export';
import { downloadAsJSON, downloadAsCSV, downloadAsExcel } from '@/utils/export';

function MyComponent() {
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const { searchParams } = useSearchStore();
  const articles = [...]; // Your articles data

  const handleExport = async (format: 'json' | 'csv' | 'excel', fields: string[]) => {
    try {
      switch (format) {
        case 'json':
          downloadAsJSON(articles, fields);
          break;
        case 'csv':
          downloadAsCSV(articles, fields);
          break;
        case 'excel':
          downloadAsExcel(articles, fields);
          break;
      }
      toast({ title: '导出成功' });
    } catch (error) {
      toast({ title: '导出失败', variant: 'destructive' });
    }
  };

  return (
    <>
      <Button onClick={() => setExportDialogOpen(true)}>
        导出
      </Button>
      
      <ExportDialog
        open={exportDialogOpen}
        onOpenChange={setExportDialogOpen}
        filters={searchParams}
        onExport={handleExport}
      />
    </>
  );
}
```

## Export Utilities

The export utilities are located in `@/utils/export.ts` and provide functions for:

- Converting articles to JSON, CSV, and Excel formats
- Triggering file downloads in the browser
- Handling field filtering and data transformation

See `@/utils/export.ts` for detailed documentation.

## Available Fields

The following fields can be selected for export:

- **title** - 标题 (default)
- **url** - 原文链接 (default)
- **category** - 分类 (default)
- **published_time** - 发布时间 (default)
- **content** - 正文内容
- **tech_detection** - 技术检测结果
- **content_analysis** - 内容分析结果
- **created_at** - 创建时间

## Requirements Validation

This component validates the following requirements:

- **需求 9.1**: Provides JSON, CSV, and Excel format options
- **需求 9.3**: Displays export progress indicator
- **需求 9.4**: Supports field selection for export

The export utilities validate:

- **需求 9.2**: Exports articles matching current filter conditions
- **需求 9.5**: Automatically triggers file download when export completes
