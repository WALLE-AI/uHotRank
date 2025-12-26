import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';
import { useTheme } from '@/components/theme-provider';
import { Moon, Sun } from 'lucide-react';

export function UIDemo() {
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();

  return (
    <div className="container mx-auto p-8 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">shadcn/ui 组件演示</h1>
        <Button
          variant="outline"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>按钮组件</CardTitle>
          <CardDescription>不同变体和尺寸的按钮</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          <Button>默认按钮</Button>
          <Button variant="secondary">次要按钮</Button>
          <Button variant="destructive">危险按钮</Button>
          <Button variant="outline">轮廓按钮</Button>
          <Button variant="ghost">幽灵按钮</Button>
          <Button variant="link">链接按钮</Button>
          <Button size="sm">小按钮</Button>
          <Button size="lg">大按钮</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>输入组件</CardTitle>
          <CardDescription>文本输入框</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="请输入文本..." />
          <Input type="email" placeholder="请输入邮箱..." />
          <Input type="password" placeholder="请输入密码..." />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>选择组件</CardTitle>
          <CardDescription>下拉选择框</CardDescription>
        </CardHeader>
        <CardContent>
          <Select>
            <SelectTrigger className="w-[280px]">
              <SelectValue placeholder="选择一个选项" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="option1">选项 1</SelectItem>
              <SelectItem value="option2">选项 2</SelectItem>
              <SelectItem value="option3">选项 3</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>对话框和提示</CardTitle>
          <CardDescription>模态对话框和 Toast 通知</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline">打开对话框</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>对话框标题</DialogTitle>
                <DialogDescription>这是一个对话框的描述文本。</DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <Input placeholder="在这里输入..." />
              </div>
              <DialogFooter>
                <Button variant="outline">取消</Button>
                <Button>确认</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Button
            onClick={() => {
              toast({
                title: '成功提示',
                description: '这是一个成功的 Toast 通知！',
              });
            }}
          >
            显示 Toast
          </Button>

          <Button
            variant="destructive"
            onClick={() => {
              toast({
                variant: 'destructive',
                title: '错误提示',
                description: '这是一个错误的 Toast 通知！',
              });
            }}
          >
            显示错误 Toast
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>卡片组件</CardTitle>
          <CardDescription>这是一个完整的卡片示例</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">卡片内容区域可以包含任何内容。</p>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline">取消</Button>
          <Button>保存</Button>
        </CardFooter>
      </Card>
    </div>
  );
}
