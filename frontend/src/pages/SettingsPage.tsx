import { useState, useEffect } from 'react';
import { useSettingsStore, validateElasticsearchSettings, validateDisplaySettings } from '@/stores/settingsStore';
import { useTheme } from '@/components/theme-provider';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { toast } from '@/hooks/use-toast';
import { Loader2, CheckCircle2, XCircle, Save, RotateCcw, TestTube2 } from 'lucide-react';

export function SettingsPage() {
  const {
    settings,
    updateElasticsearch,
    updateDisplay,
    updateTheme,
    testConnection,
    testingConnection,
    connectionStatus,
    resetSettings,
    error,
    clearError,
  } = useSettingsStore();

  const { setTheme } = useTheme();

  // Local form state
  const [esHost, setEsHost] = useState(settings.elasticsearch.host);
  const [esUsername, setEsUsername] = useState(settings.elasticsearch.username);
  const [esPassword, setEsPassword] = useState(settings.elasticsearch.password);
  const [articlesPerPage, setArticlesPerPage] = useState(settings.display.articlesPerPage);
  const [defaultSort, setDefaultSort] = useState(settings.display.defaultSort);
  const [showTechBadge, setShowTechBadge] = useState(settings.display.showTechBadge);
  const [showSentiment, setShowSentiment] = useState(settings.display.showSentiment);
  const [themeMode, setThemeMode] = useState(settings.theme.mode);
  const [hasChanges, setHasChanges] = useState(false);

  // Validation errors
  const [esErrors, setEsErrors] = useState<string[]>([]);
  const [displayErrors, setDisplayErrors] = useState<string[]>([]);

  // Track changes
  useEffect(() => {
    const changed =
      esHost !== settings.elasticsearch.host ||
      esUsername !== settings.elasticsearch.username ||
      esPassword !== settings.elasticsearch.password ||
      articlesPerPage !== settings.display.articlesPerPage ||
      defaultSort !== settings.display.defaultSort ||
      showTechBadge !== settings.display.showTechBadge ||
      showSentiment !== settings.display.showSentiment ||
      themeMode !== settings.theme.mode;

    setHasChanges(changed);
  }, [
    esHost,
    esUsername,
    esPassword,
    articlesPerPage,
    defaultSort,
    showTechBadge,
    showSentiment,
    themeMode,
    settings,
  ]);

  // Handle test connection
  const handleTestConnection = async () => {
    // Validate before testing
    const validation = validateElasticsearchSettings({
      host: esHost,
      username: esUsername,
      password: esPassword,
    });

    if (!validation.valid) {
      setEsErrors(validation.errors);
      toast({
        title: '验证失败',
        description: validation.errors.join(', '),
        variant: 'destructive',
      });
      return;
    }

    setEsErrors([]);

    // Update settings temporarily for test
    updateElasticsearch({
      host: esHost,
      username: esUsername,
      password: esPassword,
    });

    const success = await testConnection();

    if (success) {
      toast({
        title: '连接成功',
        description: 'Elasticsearch 连接测试成功',
      });
    } else {
      toast({
        title: '连接失败',
        description: error || 'Elasticsearch 连接测试失败',
        variant: 'destructive',
      });
    }
  };

  // Handle save settings
  const handleSaveSettings = () => {
    // Validate Elasticsearch settings
    const esValidation = validateElasticsearchSettings({
      host: esHost,
      username: esUsername,
      password: esPassword,
    });

    if (!esValidation.valid) {
      setEsErrors(esValidation.errors);
      toast({
        title: '验证失败',
        description: '请检查 Elasticsearch 配置',
        variant: 'destructive',
      });
      return;
    }

    // Validate display settings
    const displayValidation = validateDisplaySettings({
      articlesPerPage,
      defaultSort,
      showTechBadge,
      showSentiment,
    });

    if (!displayValidation.valid) {
      setDisplayErrors(displayValidation.errors);
      toast({
        title: '验证失败',
        description: '请检查显示偏好配置',
        variant: 'destructive',
      });
      return;
    }

    // Clear errors
    setEsErrors([]);
    setDisplayErrors([]);
    clearError();

    // Update all settings
    updateElasticsearch({
      host: esHost,
      username: esUsername,
      password: esPassword,
    });

    updateDisplay({
      articlesPerPage,
      defaultSort,
      showTechBadge,
      showSentiment,
    });

    updateTheme({
      mode: themeMode,
    });

    // Apply theme change
    setTheme(themeMode);

    setHasChanges(false);

    toast({
      title: '保存成功',
      description: '设置已保存',
    });
  };

  // Handle reset settings
  const handleResetSettings = () => {
    resetSettings();
    // Reset local form state
    setEsHost(settings.elasticsearch.host);
    setEsUsername(settings.elasticsearch.username);
    setEsPassword(settings.elasticsearch.password);
    setArticlesPerPage(settings.display.articlesPerPage);
    setDefaultSort(settings.display.defaultSort);
    setShowTechBadge(settings.display.showTechBadge);
    setShowSentiment(settings.display.showSentiment);
    setThemeMode(settings.theme.mode);
    setEsErrors([]);
    setDisplayErrors([]);
    setHasChanges(false);

    toast({
      title: '重置成功',
      description: '设置已重置为默认值',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header - 紧凑布局，增强视觉归属 */}
      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">设置</h1>
            <p className="text-sm text-muted-foreground mt-1">配置系统参数和个性化选项</p>
          </div>
          <div className="flex gap-2 sm:pt-1">
            <Button variant="outline" onClick={handleResetSettings} className="touch-manipulation">
              <RotateCcw className="mr-2 h-4 w-4" />
              重置
            </Button>
            <Button onClick={handleSaveSettings} disabled={!hasChanges} className="touch-manipulation">
              <Save className="mr-2 h-4 w-4" />
              保存设置
            </Button>
          </div>
        </div>
      </div>

      {/* Elasticsearch Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>Elasticsearch 连接配置</CardTitle>
          <CardDescription>配置 Elasticsearch 数据库连接参数</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="es-host">主机地址 *</Label>
            <Input
              id="es-host"
              type="text"
              placeholder="http://localhost:9200"
              value={esHost}
              onChange={(e) => setEsHost(e.target.value)}
              className={esErrors.length > 0 ? 'border-destructive' : ''}
            />
            {esErrors.length > 0 && (
              <p className="text-sm text-destructive">{esErrors.join(', ')}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="es-username">用户名</Label>
              <Input
                id="es-username"
                type="text"
                placeholder="elastic"
                value={esUsername}
                onChange={(e) => setEsUsername(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="es-password">密码</Label>
              <Input
                id="es-password"
                type="password"
                placeholder="••••••••"
                value={esPassword}
                onChange={(e) => setEsPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <Button
              variant="outline"
              onClick={handleTestConnection}
              disabled={testingConnection}
            >
              {testingConnection ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  测试中...
                </>
              ) : (
                <>
                  <TestTube2 className="mr-2 h-4 w-4" />
                  测试连接
                </>
              )}
            </Button>

            {connectionStatus === 'success' && (
              <div className="flex items-center text-sm text-green-600 dark:text-green-400">
                <CheckCircle2 className="mr-1 h-4 w-4" />
                连接成功
              </div>
            )}

            {connectionStatus === 'error' && (
              <div className="flex items-center text-sm text-destructive">
                <XCircle className="mr-1 h-4 w-4" />
                连接失败
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Display Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>显示偏好</CardTitle>
          <CardDescription>配置文章列表和内容显示选项</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="articles-per-page">每页文章数量</Label>
              <Input
                id="articles-per-page"
                type="number"
                min="1"
                max="100"
                value={articlesPerPage}
                onChange={(e) => setArticlesPerPage(parseInt(e.target.value) || 20)}
                className={displayErrors.length > 0 ? 'border-destructive' : ''}
              />
              {displayErrors.length > 0 && (
                <p className="text-sm text-destructive">{displayErrors.join(', ')}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="default-sort">默认排序方式</Label>
              <Select value={defaultSort} onValueChange={(value: any) => setDefaultSort(value)}>
                <SelectTrigger id="default-sort">
                  <SelectValue placeholder="选择排序方式" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="time">时间</SelectItem>
                  <SelectItem value="relevance">相关度</SelectItem>
                  <SelectItem value="popularity">热度</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="show-tech-badge"
                checked={showTechBadge}
                onCheckedChange={(checked) => setShowTechBadge(checked as boolean)}
              />
              <Label
                htmlFor="show-tech-badge"
                className="text-sm font-normal cursor-pointer"
              >
                显示技术文章标识
              </Label>
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="show-sentiment"
                checked={showSentiment}
                onCheckedChange={(checked) => setShowSentiment(checked as boolean)}
              />
              <Label
                htmlFor="show-sentiment"
                className="text-sm font-normal cursor-pointer"
              >
                显示情感分析结果
              </Label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Theme Configuration */}
      <Card>
        <CardHeader>
          <CardTitle>主题配置</CardTitle>
          <CardDescription>配置应用外观和主题</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="theme-mode">主题模式</Label>
            <Select value={themeMode} onValueChange={(value: any) => setThemeMode(value)}>
              <SelectTrigger id="theme-mode">
                <SelectValue placeholder="选择主题模式" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">亮色</SelectItem>
                <SelectItem value="dark">暗色</SelectItem>
                <SelectItem value="system">跟随系统</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              选择"跟随系统"将根据您的操作系统设置自动切换主题
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Save reminder */}
      {hasChanges && (
        <div className="rounded-lg border border-yellow-500 bg-yellow-50 dark:bg-yellow-950 p-4">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            您有未保存的更改。请点击"保存设置"按钮保存您的更改。
          </p>
        </div>
      )}
    </div>
  );
}

export default SettingsPage;
