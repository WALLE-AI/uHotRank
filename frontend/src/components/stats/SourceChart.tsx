import ReactECharts from 'echarts-for-react';
import { Card } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '@/stores/searchStore';

interface SourceChartProps {
  data: Record<string, number>;
  loading?: boolean;
}

export function SourceChart({ data, loading }: SourceChartProps) {
  const navigate = useNavigate();
  const updateSearchParams = useSearchStore((state) => state.updateSearchParams);

  const handleSourceClick = (source: string) => {
    updateSearchParams({ sources: [source], page: 1 });
    navigate('/search');
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">文章来源分布</h3>
        <div className="h-[400px] flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">加载中...</div>
        </div>
      </Card>
    );
  }

  if (!data || Object.keys(data).length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">文章来源分布</h3>
        <div className="h-[400px] flex items-center justify-center text-muted-foreground">
          暂无来源数据
        </div>
      </Card>
    );
  }

  // Sort by value and take top 10
  const sortedData = Object.entries(data)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
    },
    yAxis: {
      type: 'category',
      data: sortedData.map(([name]) => name),
      axisLabel: {
        interval: 0,
        formatter: (value: string) => {
          return value.length > 15 ? value.substring(0, 15) + '...' : value;
        },
      },
    },
    series: [
      {
        name: '文章数量',
        type: 'bar',
        data: sortedData.map(([, value]) => value),
        label: {
          show: true,
          position: 'right',
        },
        itemStyle: {
          color: '#5470c6',
        },
      },
    ],
  };

  const onEvents = {
    click: (params: { name: string }) => {
      handleSourceClick(params.name);
    },
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">文章来源分布（Top 10）</h3>
      <ReactECharts
        option={option}
        style={{ height: '400px' }}
        onEvents={onEvents}
        opts={{ renderer: 'canvas' }}
      />
    </Card>
  );
}

export default SourceChart;
