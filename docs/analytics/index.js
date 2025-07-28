document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch('../youtube_analyzed.json');
    const data = await response.json();

    // 各動画のデータを取得
    const datasets = data.each_video.map(video => {
        // 1時間ごとの視聴回数増加分の平均を計算
        const hourlyAverages = calculateHourlyAverages(video.views).slice(1); // 最初のデータポイントを除外

        return {
            label: video.title,
            data: hourlyAverages.map(item => item.average),
            borderColor: getRandomColor(),
            backgroundColor: 'rgba(0, 0, 0, 0)', // 背景色を透明に
            borderWidth: 1,
            tension: 0.1
        };
    });

    // ラベルを統一（最初のデータポイントを除外）
    const labels = calculateHourlyAverages(data.each_video[0].views).slice(1).map(item => item.hour);

    // Chart.js を使用してグラフを描画
    const ctx = document.getElementById('viewChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false // 凡例を非表示
                },
                tooltip: {
                    enabled: true, // ツールチップを有効化
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '日時 (3時間ごと)'
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
        }
    });
});

// 1時間ごとの平均視聴回数増加分を計算する関数
function calculateHourlyAverages(views) {
    const hourlyData = {};

    views.forEach((view, index) => {
        const hour = new Date(new Date(view.v_datetime).getTime() + 9 * 60 * 60 * 1000).toISOString().slice(0, 13); // 日本時間 (UTC+9) に変換
        let increment = 0;

        if (index > 0) {
            const currentTime = new Date(view.v_datetime).getTime();
            const previousTime = new Date(views[index - 1].v_datetime).getTime();
            const timeDifferenceInHours = (currentTime - previousTime) / (1000 * 60 * 60); // 時間差を計算
            increment = (view.view_count - views[index - 1].view_count) / timeDifferenceInHours; // 1時間あたりの増加分
        }

        if (!hourlyData[hour]) {
            hourlyData[hour] = { sum: 0, count: 0 };
        }
        hourlyData[hour].sum += increment;
        hourlyData[hour].count += 1;
    });

    return Object.keys(hourlyData).map(hour => ({
        hour: hour.replace('T', ' '), // 表示用にフォーマット変更
        average: Math.floor(hourlyData[hour].sum / hourlyData[hour].count) // 1時間単位の平均値を計算
    }));
}

// ランダムな色を生成する関数
function getRandomColor() {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, 1)`;
}