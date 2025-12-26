import { Card } from '@/components/ui/card';
import { TrendingUp, TrendingDown, FileText, Code, Calendar } from 'lucide-react';
import type { Statistics } from '@/types/search';

interface StatsOverviewProps {
  statistics: Statistics | null;
  loading?: boolean;
}

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  trend?: number;
  trendLabel?: string;
}

function StatCard({ title, value, icon, trend, trendLabel }: StatCardProps) {
  const hasTrend = trend !== undefined;
  const isPositive = trend && trend > 0;
  const isNegative = trend && trend < 0;

  return (
    <Card className="p-4 sm:p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs sm:text-sm font-medium text-muted-foreground truncate">{title}</p>
          <h3 className="text-xl sm:text-2xl font-bold mt-1 sm:mt-2">{value.toLocaleString()}</h3>
          {hasTrend && (
            <div className="flex items-center mt-1 sm:mt-2 text-xs sm:text-sm">
              {isPositive && (
                <>
                  <TrendingUp className="w-3 h-3 sm:w-4 sm:h-4 text-green-500 mr-1" />
                  <span className="text-green-500">+{trend}%</span>
                </>
              )}
              {isNegative && (
                <>
                  <TrendingDown className="w-3 h-3 sm:w-4 sm:h-4 text-red-500 mr-1" />
                  <span className="text-red-500">{trend}%</span>
                </>
              )}
              {!isPositive && !isNegative && trend === 0 && (
                <span className="text-muted-foreground">0%</span>
              )}
              {trendLabel && <span className="text-muted-foreground ml-1 truncate">{trendLabel}</span>}
            </div>
          )}
        </div>
        <div className="ml-3 sm:ml-4 p-2 sm:p-3 bg-primary/10 rounded-lg flex-shrink-0">{icon}</div>
      </div>
    </Card>
  );
}

export function StatsOverview({ statistics, loading }: StatsOverviewProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4 sm:p-6">
            <div className="animate-pulse">
              <div className="h-4 bg-muted rounded w-1/2 mb-4"></div>
              <div className="h-8 bg-muted rounded w-3/4"></div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (!statistics) {
    return <div className="text-center py-8 text-muted-foreground">暂无统计数据</div>;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
      <StatCard
        title="文章总数"
        value={statistics.total_articles}
        icon={<FileText className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />}
      />
      <StatCard
        title="技术文章"
        value={statistics.tech_articles}
        icon={<Code className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />}
      />
      <StatCard
        title="今日新增"
        value={statistics.today_new}
        icon={<Calendar className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />}
      />
    </div>
  );
}
