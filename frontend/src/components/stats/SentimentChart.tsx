import ReactECharts from 'echarts-for-react';
import { Card } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '@/stores/searchStore';

interface SentimentChartProps {
  data: Record<string, number>;
  loading?: boolean;
}

const sentimentLabels: Record<string, string> = {
  positive: '积极',
  neutral: '中性',
  negative: '消极',
};

const sentimentColors: Record<string, string> = {
  positive: '#52c41a',
  neutral: '#1890ff',
  negative: '#f5222d',
};

export function SentimentChart({ data, loading }: SentimentChartProps) {
  const navigate = useNavigate();
  const updateSearchParams = useSearchStore((state) => state.updateSearchParams);

  const handleSentimentClick = (sentiment: string) => {
    updateSearchParams({ sentiment, page: 1 });
    navigate('/search');
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">情感分析分布</h3>
        <div className="h-[400px] flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">加载中...</div>
        </div>
      </Card>
    );
  }

  if (!data || Object.keys(data).length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">情感分析分布</h3>
        <div className="h-[400px] flex items-center justify-center text-muted-foreground">
          暂无情感数据
        </div>
      </Card>
    );
  }

  const chartData = Object.entries(data).map(([name, value]) => ({
    name: sentimentLabels[name] || name,
    value,
    itemStyle: {
      color: sentimentColors[name] || '#8c8c8c',
    },
  }));

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: Array<{ name: string; value: number }>) => {
        const item = params[0];
        const total = chartData.reduce((sum, d) => sum + d.value, 0);
        const percentage = ((item.value / total) * 100).toFixed(1);
        return `${item.name}: ${item.value} (${percentage}%)`;
      },
    },
    xAxis: {
      type: 'category',
      data: chartData.map((item) => item.name),
      axisLabel: {
        interval: 0,
        rotate: 0,
      },
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '数量',
        type: 'bar',
        data: chartData,
        barWidth: '60%',
        label: {
          show: true,
          position: 'top',
        },
      },
    ],
  };

  const onEvents = {
    click: (params: { name: string }) => {
      const sentiment = Object.keys(sentimentLabels).find(
        (key) => sentimentLabels[key] === params.name
      );
      if (sentiment) {
        handleSentimentClick(sentiment);
      }
    },
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">情感分析分布</h3>
      <ReactECharts
        option={option}
        style={{ height: '400px' }}
        onEvents={onEvents}
        opts={{ renderer: 'canvas' }}
      />
    </Card>
  );
}

export default SentimentChart;
