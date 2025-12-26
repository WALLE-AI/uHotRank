import ReactECharts from 'echarts-for-react';
import { Card } from '@/components/ui/card';
import { useNavigate } from 'react-router-dom';
import { useSearchStore } from '@/stores/searchStore';

interface CategoryChartProps {
  data: Record<string, number>;
  loading?: boolean;
}

export function CategoryChart({ data, loading }: CategoryChartProps) {
  const navigate = useNavigate();
  const updateSearchParams = useSearchStore((state) => state.updateSearchParams);

  const handleCategoryClick = (category: string) => {
    updateSearchParams({ tech_categories: [category], page: 1 });
    navigate('/search');
  };

  if (loading) {
    return (
      <Card className="p-4 sm:p-6">
        <h3 className="text-base sm:text-lg font-semibold mb-4">技术分类分布</h3>
        <div className="h-[300px] flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">加载中...</div>
        </div>
      </Card>
    );
  }

  if (!data || Object.keys(data).length === 0) {
    return (
      <Card className="p-4 sm:p-6">
        <h3 className="text-base sm:text-lg font-semibold mb-4">技术分类分布</h3>
        <div className="h-[300px] flex items-center justify-center text-muted-foreground">
          暂无分类数据
        </div>
      </Card>
    );
  }

  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value,
  }));

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center',
      // Hide legend on mobile
      show: window.innerWidth >= 768,
    },
    series: [
      {
        name: '技术分类',
        type: 'pie',
        radius: ['40%', '70%'],
        center: window.innerWidth >= 768 ? ['60%', '50%'] : ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: window.innerWidth >= 768 ? 20 : 16,
            fontWeight: 'bold',
          },
        },
        labelLine: {
          show: false,
        },
        data: chartData,
      },
    ],
  };

  const onEvents = {
    click: (params: { name: string }) => {
      handleCategoryClick(params.name);
    },
  };

  return (
    <Card className="p-4 sm:p-6">
      <h3 className="text-base sm:text-lg font-semibold mb-4">技术分类分布</h3>
      <ReactECharts
        option={option}
        style={{ height: '300px', minHeight: '300px' }}
        onEvents={onEvents}
        opts={{ renderer: 'canvas' }}
      />
    </Card>
  );
}

export default CategoryChart;
