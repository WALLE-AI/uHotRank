import ReactECharts from 'echarts-for-react';
import { Card } from '@/components/ui/card';

interface TrendChartProps {
  data: Array<{ date: string; count: number }>;
  loading?: boolean;
}

export function TrendChart({ data, loading }: TrendChartProps) {
  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">文章发布趋势</h3>
        <div className="h-[400px] flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">加载中...</div>
        </div>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">文章发布趋势</h3>
        <div className="h-[400px] flex items-center justify-center text-muted-foreground">
          暂无趋势数据
        </div>
      </Card>
    );
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: Array<{ axisValue: string; value: number }>) => {
        const item = params[0];
        return `${item.axisValue}<br/>文章数: ${item.value}`;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.map((item) => item.date),
      axisLabel: {
        rotate: 45,
        interval: 'auto',
      },
    },
    yAxis: {
      type: 'value',
      name: '文章数量',
    },
    series: [
      {
        name: '文章数量',
        type: 'line',
        smooth: true,
        data: data.map((item) => item.count),
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(84, 112, 198, 0.5)',
              },
              {
                offset: 1,
                color: 'rgba(84, 112, 198, 0.1)',
              },
            ],
          },
        },
        lineStyle: {
          color: '#5470c6',
          width: 2,
        },
        itemStyle: {
          color: '#5470c6',
        },
      },
    ],
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">文章发布趋势</h3>
      <ReactECharts option={option} style={{ height: '400px' }} opts={{ renderer: 'canvas' }} />
    </Card>
  );
}

export default TrendChart;
