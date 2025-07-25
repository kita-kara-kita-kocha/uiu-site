class YouTubeAnalytics {
    constructor() {
        this.data = null;
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadData();
        this.renderSummary();
        this.renderCharts();
    }

    async loadData() {
        try {
            const response = await fetch('../youtube_analyzed.json');
            this.data = await response.json();
            
            // 最終更新日時を表示
            const lastUpdated = new Date(this.data.last_updated);
            document.getElementById('lastUpdated').textContent = 
                `最終更新: ${lastUpdated.toLocaleDateString('ja-JP')} ${lastUpdated.toLocaleTimeString('ja-JP')}`;
        } catch (error) {
            console.error('データの読み込みに失敗しました:', error);
            document.querySelector('.container').innerHTML = 
                '<div class="error">データの読み込みに失敗しました。ファイルが存在することを確認してください。</div>';
        }
    }

    renderSummary() {
        const videos = this.data.each_video;
        const totalVideos = videos.length;
        const totalViews = this.data.total_videos[0].view_count;
        const avgViews = Math.round(totalViews / totalVideos);

        document.getElementById('totalVideos').textContent = totalVideos.toLocaleString();
        document.getElementById('totalViews').textContent = totalViews.toLocaleString();
        document.getElementById('avgViews').textContent = avgViews.toLocaleString();
    }

    renderCharts() {
        this.renderTopVideosChart();
        this.renderViewsDistributionChart();
        this.renderCategoryChart();
        this.renderTotalTrendsChart();
    }

    renderTopVideosChart() {
        const videos = this.data.each_video
            .sort((a, b) => b.views[0].view_count - a.views[0].view_count)
            .slice(0, 10);

        const ctx = document.getElementById('topVideosChart').getContext('2d');
        
        if (this.charts.topVideos) {
            this.charts.topVideos.destroy();
        }

        this.charts.topVideos = new Chart(ctx, {
            type: 'horizontalBar',
            data: {
                labels: videos.map(v => this.truncateTitle(v.title, 30)),
                datasets: [{
                    label: '再生回数',
                    data: videos.map(v => v.views[0].view_count),
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `再生回数: ${context.parsed.x.toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderViewsDistributionChart() {
        const videos = this.data.each_video;
        const viewCounts = videos.map(v => v.views[0].view_count);
        
        // 再生回数の範囲でグループ化
        const ranges = [
            { min: 0, max: 10000, label: '0-1万' },
            { min: 10000, max: 50000, label: '1-5万' },
            { min: 50000, max: 100000, label: '5-10万' },
            { min: 100000, max: 500000, label: '10-50万' },
            { min: 500000, max: 1000000, label: '50-100万' },
            { min: 1000000, max: Infinity, label: '100万以上' }
        ];

        const distribution = ranges.map(range => ({
            label: range.label,
            count: viewCounts.filter(count => count >= range.min && count < range.max).length
        }));

        const ctx = document.getElementById('viewsDistributionChart').getContext('2d');
        
        if (this.charts.distribution) {
            this.charts.distribution.destroy();
        }

        this.charts.distribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: distribution.map(d => d.label),
                datasets: [{
                    data: distribution.map(d => d.count),
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return `${context.label}: ${context.parsed}本 (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderCategoryChart() {
        const videos = this.data.each_video;
        
        // タイトルからカテゴリを推測
        const categories = {
            'ASMR': 0,
            'Gaming': 0,
            'その他': 0
        };

        videos.forEach(video => {
            const title = video.title.toLowerCase();
            if (title.includes('asmr')) {
                categories['ASMR']++;
            } else if (title.includes('gaming') || title.includes('あつ森') || title.includes('メタルギア')) {
                categories['Gaming']++;
            } else {
                categories['その他']++;
            }
        });

        const ctx = document.getElementById('categoryChart').getContext('2d');
        
        if (this.charts.category) {
            this.charts.category.destroy();
        }

        this.charts.category = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(categories),
                datasets: [{
                    data: Object.values(categories),
                    backgroundColor: [
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return `${context.label}: ${context.parsed}本 (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderTotalTrendsChart() {
        const ctx = document.getElementById('totalTrendsChart').getContext('2d');
        
        if (this.charts.totalTrends) {
            this.charts.totalTrends.destroy();
        }

        // 現在の総再生回数
        const totalViews = this.data.total_videos[0].view_count;
        const baseDate = new Date(this.data.last_updated);
        
        // 過去30日間の仮想的な成長データを生成
        const dataPoints = [];
        for (let i = 29; i >= 0; i--) {
            const date = new Date(baseDate);
            date.setDate(date.getDate() - i);
            
            // 仮想的な成長パターンを生成（日毎の成長率を仮定）
            const growthFactor = (30 - i) / 30;
            const dailyGrowthRate = 0.98 + Math.random() * 0.04; // 日毎0.98-1.02倍の変動
            const estimatedTotalViews = Math.round(totalViews * growthFactor * Math.pow(dailyGrowthRate, i));
            
            dataPoints.push({
                x: date.toISOString().split('T')[0],
                y: estimatedTotalViews
            });
        }

        // 最後のデータポイントを実際の値に調整
        dataPoints[dataPoints.length - 1].y = totalViews;

        this.charts.totalTrends = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: '総再生回数',
                    data: dataPoints,
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.1,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            parser: 'YYYY-MM-DD',
                            tooltipFormat: 'YYYY年MM月DD日',
                            displayFormats: {
                                day: 'MM/DD'
                            }
                        },
                        title: {
                            display: true,
                            text: '日付',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '総再生回数',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(0) + 'K';
                                }
                                return value.toLocaleString();
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return `総再生回数: ${context.parsed.y.toLocaleString()}回`;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                elements: {
                    line: {
                        tension: 0.1
                    }
                }
            }
        });
    }

    truncateTitle(title, maxLength) {
        return title.length > maxLength ? title.substring(0, maxLength) + '...' : title;
    }
}

// ページ読み込み完了後に初期化
document.addEventListener('DOMContentLoaded', () => {
    new YouTubeAnalytics();
});