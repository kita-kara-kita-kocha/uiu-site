import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { AnalyticsData } from '../types';
import './AnalyticsPage.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const AnalyticsPage: React.FC = () => {
  const [globalData, setGlobalData] = useState<AnalyticsData | null>(null);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    const loadDataAsync = async () => {
      try {
        const response = await fetch(`/youtube_analyzed.json?v=${Date.now()}`);
        const data: AnalyticsData = await response.json();
        setGlobalData(data);
        setInitialDateRange(data);
        renderChart(data);
      } catch (error) {
        console.error('Error loading analytics data:', error);
      }
    };

    loadDataAsync();
  }, []);

  const loadData = async () => {
    try {
      const response = await fetch(`/youtube_analyzed.json?v=${Date.now()}`);
      const data: AnalyticsData = await response.json();
      setGlobalData(data);
      setInitialDateRange(data);
      renderChart(data);
    } catch (error) {
      console.error('Error loading analytics data:', error);
    }
  };

  const setInitialDateRange = (data: AnalyticsData) => {
    let minDate: Date | null = null;
    let maxDate: Date | null = null;
    
    data.each_video.forEach(video => {
      video.views.forEach(view => {
        const date = new Date(view.v_datetime);
        if (!minDate || date < minDate) minDate = date;
        if (!maxDate || date > maxDate) maxDate = date;
      });
    });
    
    if (minDate && maxDate) {
      const jstMinDate = new Date((minDate as Date).getTime() + 9 * 60 * 60 * 1000);
      const jstMaxDate = new Date((maxDate as Date).getTime() + 9 * 60 * 60 * 1000);
      
      setStartDate(jstMinDate.toISOString().slice(0, 16));
      setEndDate(jstMaxDate.toISOString().slice(0, 16));
    }
  };

  const applyDateFilter = () => {
    if (!startDate || !endDate || !globalData) {
      alert('開始日と終了日を両方指定してください。');
      return;
    }
    
    const startDateUTC = new Date(startDate).getTime() - 9 * 60 * 60 * 1000;
    const endDateUTC = new Date(endDate).getTime() - 9 * 60 * 60 * 1000;
    
    renderChart(globalData, new Date(startDateUTC), new Date(endDateUTC));
  };

  const resetFilter = () => {
    if (globalData) {
      setInitialDateRange(globalData);
      renderChart(globalData);
    }
  };

  const renderChart = (data: AnalyticsData, startDate?: Date, endDate?: Date) => {
    const filteredData = {
      each_video: data.each_video.map(video => ({
        ...video,
        views: video.views.filter(view => {
          const viewDate = new Date(view.v_datetime);
          if (startDate && viewDate < startDate) return false;
          if (endDate && viewDate > endDate) return false;
          return true;
        })
      })).filter(video => video.views.length > 0)
    };

    const allTimePoints = new Set<string>();
    filteredData.each_video.forEach(video => {
      video.views.forEach(view => {
        const jstDate = new Date(new Date(view.v_datetime).getTime() + 9 * 60 * 60 * 1000);
        const hour = jstDate.toISOString().slice(0, 13);
        allTimePoints.add(hour);
      });
    });

    const sortedTimePoints = Array.from(allTimePoints).sort();
    const labels = sortedTimePoints.map(hour => formatHourDisplay(hour));

    const datasets = filteredData.each_video.map(video => {
      const hourlyAverages = calculateHourlyAverages(video.views);
      
      const alignedData = sortedTimePoints.map(timePoint => {
        const found = hourlyAverages.find(item => item.hourKey === timePoint);
        return found ? found.average : null;
      });

      return {
        label: video.title,
        data: alignedData,
        borderColor: getRandomColor(),
        backgroundColor: 'rgba(0, 0, 0, 0)',
        borderWidth: 1,
        tension: 0.1,
        spanGaps: true
      };
    });

    setChartData({
      labels,
      datasets
    });
  };

  const calculateHourlyAverages = (views: any[]) => {
    const hourlyData: { [key: string]: { sum: number; count: number } } = {};

    views.forEach((view, index) => {
      const jstDate = new Date(new Date(view.v_datetime).getTime() + 9 * 60 * 60 * 1000);
      const hour = jstDate.toISOString().slice(0, 13);
      let increment = 0;

      if (index > 0) {
        const currentTime = new Date(view.v_datetime).getTime();
        const previousTime = new Date(views[index - 1].v_datetime).getTime();
        const timeDifferenceInHours = (currentTime - previousTime) / (1000 * 60 * 60);
        increment = (view.view_count - views[index - 1].view_count) / timeDifferenceInHours;
      }

      if (!hourlyData[hour]) {
        hourlyData[hour] = { sum: 0, count: 0 };
      }
      hourlyData[hour].sum += increment;
      hourlyData[hour].count += 1;
    });

    return Object.keys(hourlyData)
      .sort()
      .filter((_, index) => index > 0)
      .map(hour => ({
        hourKey: hour,
        hour: formatHourDisplay(hour),
        average: Math.floor(hourlyData[hour].sum / hourlyData[hour].count)
      }));
  };

  const formatHourDisplay = (hour: string) => {
    const date = new Date(hour + ':00:00.000Z');
    const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
    const day = date.getUTCDate().toString().padStart(2, '0');
    const hourStr = date.getUTCHours().toString().padStart(2, '0');
    return `${month}/${day} ${hourStr}:00`;
  };

  const getRandomColor = () => {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, 1)`;
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        callbacks: {
          label: function (context: any) {
            return `${context.dataset.label}: ${context.raw}`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: '日時'
        }
      },
      y: {
        title: {
          display: true,
          text: '1時間の平均視聴回数増加分'
        },
        beginAtZero: true
      }
    }
  };

  return (
    <div className="analytics-container">
      <header>
        <h1>YouTube Analytics</h1>
        <Link to="/" className="back-button">&larr; 戻る</Link>
      </header>
      <main>
        <div className="controls">
          <label htmlFor="startDate">開始日:</label>
          <input 
            type="datetime-local" 
            id="startDate"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <label htmlFor="endDate">終了日:</label>
          <input 
            type="datetime-local" 
            id="endDate"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <button onClick={applyDateFilter}>期間を適用</button>
          <button onClick={resetFilter}>リセット</button>
        </div>
        {chartData && (
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
        )}
      </main>
    </div>
  );
};

export default AnalyticsPage;
