# shadcn/ui 配置文档

本文档记录了 shadcn/ui 组件库的配置和使用方法。

## 已安装的组件

以下 shadcn/ui 组件已成功安装并配置：

### 1. Button（按钮）
- 位置：`src/components/ui/button.tsx`
- 变体：default, secondary, destructive, outline, ghost, link
- 尺寸：default, sm, lg, icon

### 2. Card（卡片）
- 位置：`src/components/ui/card.tsx`
- 子组件：Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter

### 3. Input（输入框）
- 位置：`src/components/ui/input.tsx`
- 支持所有标准 HTML input 类型

### 4. Select（选择器）
- 位置：`src/components/ui/select.tsx`
- 基于 Radix UI Select
- 子组件：Select, SelectTrigger, SelectValue, SelectContent, SelectItem, SelectGroup, SelectLabel

### 5. Dialog（对话框）
- 位置：`src/components/ui/dialog.tsx`
- 基于 Radix UI Dialog
- 子组件：Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter

### 6. Toast（提示通知）
- 位置：`src/components/ui/toast.tsx`, `src/components/ui/toaster.tsx`
- Hook：`src/hooks/use-toast.ts`
- 基于 Radix UI Toast
- 变体：default, destructive

## 主题系统

### ThemeProvider
- 位置：`src/components/theme-provider.tsx`
- 功能：管理亮色/暗色模式切换
- 支持：light, dark, system（跟随系统）
- 持久化：使用 localStorage 保存用户偏好

### 使用方法

```tsx
import { ThemeProvider, useTheme } from '@/components/theme-provider';

// 在应用根组件中包裹
function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="uhotrank-ui-theme">
      {/* 你的应用 */}
    </ThemeProvider>
  );
}

// 在组件中使用
function MyComponent() {
  const { theme, setTheme } = useTheme();
  
  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      切换主题
    </button>
  );
}
```

## 全局样式

### CSS 变量
位置：`src/index.css`

所有主题颜色都通过 CSS 变量定义，支持亮色和暗色模式：

- `--background`: 背景色
- `--foreground`: 前景色（文本）
- `--primary`: 主色调
- `--secondary`: 次要色
- `--muted`: 柔和色
- `--accent`: 强调色
- `--destructive`: 危险/删除色
- `--border`: 边框色
- `--input`: 输入框边框色
- `--ring`: 焦点环颜色
- `--radius`: 圆角半径

### Tailwind 配置
位置：`frontend/tailwind.config.js`

已配置：
- 暗色模式：class 策略
- 容器：居中，带内边距
- 颜色扩展：所有 shadcn/ui 颜色变量
- 圆角扩展：基于 `--radius` 变量

## 路径别名

已配置以下路径别名：

```typescript
{
  "@/*": ["./src/*"]
}
```

使用示例：
```typescript
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
```

## 工具函数

### cn 函数
位置：`src/lib/utils.ts`

用于合并 Tailwind CSS 类名：

```typescript
import { cn } from '@/lib/utils';

<div className={cn('base-class', condition && 'conditional-class', className)} />
```

## Toast 使用示例

```typescript
import { useToast } from '@/hooks/use-toast';

function MyComponent() {
  const { toast } = useToast();
  
  const showToast = () => {
    toast({
      title: '成功',
      description: '操作已完成',
    });
  };
  
  const showError = () => {
    toast({
      variant: 'destructive',
      title: '错误',
      description: '操作失败',
    });
  };
  
  return (
    <>
      <button onClick={showToast}>显示成功提示</button>
      <button onClick={showError}>显示错误提示</button>
    </>
  );
}

// 别忘了在根组件添加 Toaster
import { Toaster } from '@/components/ui/toaster';

function App() {
  return (
    <>
      {/* 你的应用 */}
      <Toaster />
    </>
  );
}
```

## 组件演示

位置：`src/components/ui-demo.tsx`

包含所有已安装组件的演示页面，展示：
- 所有按钮变体
- 输入框
- 选择器
- 对话框
- Toast 通知
- 卡片组件
- 主题切换

## 添加新组件

如需添加更多 shadcn/ui 组件，可以：

1. 访问 [shadcn/ui 文档](https://ui.shadcn.com/)
2. 选择需要的组件
3. 复制组件代码到 `src/components/ui/` 目录
4. 确保依赖的 Radix UI 包已安装（查看 package.json）

## 验证安装

运行以下命令验证配置：

```bash
# 类型检查
npm run type-check

# 构建
npm run build

# 开发服务器
npm run dev
```

访问 http://localhost:5173 查看组件演示页面。
