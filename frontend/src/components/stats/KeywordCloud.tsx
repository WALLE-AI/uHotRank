import ReactECharts from 'echarts-for-react';
import { Card } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '@/stores/searchStore';
import 'echarts-wordcloud';

interface KeywordCloudProps {
  keywords: Array<{ keyword: string; count: number }>;
  loading?: boolean;
}

export function KeywordCloud({ keywords, loading }: KeywordCloudProps) {
  const navigate = useNavigate();
  const updateSearchParams = useSearchStore((state) => state.updateSearchParams);

  const handleKeywordClick = (keyword: string) => {
    updateSearchParams({ keyword, page: 1 });
    navigate('/search');
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">热门关键词</h3>
        <div className="h-[400px] flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">加载中...</div>
        </div>
      </Card>
    );
  }

  if (!keywords || keywords.length === 0) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">热门关键词</h3>
        <div className="h-[400px] flex items-center justify-center text-muted-foreground">
          暂无关键词数据
        </div>
      </Card>
    );
  }

  const option = {
    tooltip: {
      show: true,
      formatter: (params: { name: string; value: number }) => {
        return `${params.name}: ${params.value}`;
      },
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '100%',
        height: '100%',
        right: null,
        bottom: null,
        sizeRange: [12, 60],
        rotationRange: [-90, 90],
        rotationStep: 45,
        gridSize: 8,
        drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          color: () => {
            const colors = [
              '#5470c6',
              '#91cc75',
              '#fac858',
              '#ee6666',
              '#73c0de',
              '#3ba272',
              '#fc8452',
              '#9a60b4',
              '#ea7ccc',
            ];
            return colors[Math.floor(Math.random() * colors.length)];
          },
        },
        emphasis: {
          focus: 'self',
          textStyle: {
            textShadowBlur: 10,
            textShadowColor: '#333',
          },
        },
        data: keywords.map((item) => ({
          name: item.keyword,
          value: item.count,
        })),
      },
    ],
  };

  const onEvents = {
    click: (params: { name: string }) => {
      handleKeywordClick(params.name);
    },
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">热门关键词</h3>
      <ReactECharts
        option={option}
        style={{ height: '400px' }}
        onEvents={onEvents}
        opts={{ renderer: 'canvas' }}
      />
    </Card>
  );
}

export default KeywordCloud;
