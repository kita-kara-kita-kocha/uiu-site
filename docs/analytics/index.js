let globalData = null;
let chart = null;

document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch('../youtube_analyzed.json');
    globalData = await response.json();

    // 初期表示
    renderChart();

    // イベントリスナーを設定
    document.getElementById('applyFilter').addEventListener('click', applyDateFilter);
    document.getElementById('resetFilter').addEventListener('click', resetFilter);
    
    // 初期日付範囲を設定
    setInitialDateRange();
});

function setInitialDateRange() {
    // 全データから最小・最大日時を取得
    let minDate = null;
    let maxDate = null;
    
    globalData.each_video.forEach(video => {
        video.views.forEach(view => {
            const date = new Date(view.v_datetime);
            if (!minDate || date < minDate) minDate = date;
            if (!maxDate || date > maxDate) maxDate = date;
        });
    });
    
    if (minDate && maxDate) {
        // 日本時間に変換してinput要素に設定
        const jstMinDate = new Date(minDate.getTime() + 9 * 60 * 60 * 1000);
        const jstMaxDate = new Date(maxDate.getTime() + 9 * 60 * 60 * 1000);
        
        document.getElementById('startDate').value = jstMinDate.toISOString().slice(0, 16);
        document.getElementById('endDate').value = jstMaxDate.toISOString().slice(0, 16);
    }
}

function applyDateFilter() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!startDate || !endDate) {
        alert('開始日と終了日を両方指定してください。');
        return;
    }
    
    // 日本時間をUTCに変換
    const startDateUTC = new Date(startDate).getTime() - 9 * 60 * 60 * 1000;
    const endDateUTC = new Date(endDate).getTime() - 9 * 60 * 60 * 1000;
    
    renderChart(new Date(startDateUTC), new Date(endDateUTC));
}

function resetFilter() {
    setInitialDateRange();
    renderChart();
}

function renderChart(startDate = null, endDate = null) {
    // 期間でフィルタリング
    const filteredData = {
        each_video: globalData.each_video.map(video => ({
            ...video,
            views: video.views.filter(view => {
                const viewDate = new Date(view.v_datetime);
                if (startDate && viewDate < startDate) return false;
                if (endDate && viewDate > endDate) return false;
                return true;
            })
        })).filter(video => video.views.length > 0) // データがある動画のみ
    };

    // 全動画から全ての時間ポイントを収集して統一された時間軸を作成
    const allTimePoints = new Set();
    filteredData.each_video.forEach(video => {
        video.views.forEach(view => {
            const jstDate = new Date(new Date(view.v_datetime).getTime() + 9 * 60 * 60 * 1000);
            const hour = jstDate.toISOString().slice(0, 13);
            allTimePoints.add(hour);
        });
    });

    // 時間順にソートされた統一時間軸を作成
    const sortedTimePoints = Array.from(allTimePoints).sort();
    const labels = sortedTimePoints.map(hour => formatHourDisplay(hour));

    // 各動画のデータを取得
    const datasets = filteredData.each_video.map(video => {
        // 1時間ごとの視聴回数増加分の平均を計算
        const hourlyAverages = calculateHourlyAverages(video.views);
        
        // 統一された時間軸に合わせてデータを配置
        const alignedData = sortedTimePoints.map(timePoint => {
            const found = hourlyAverages.find(item => item.hourKey === timePoint);
            return found ? found.average : null; // データがない場合はnull
        });

        return {
            label: video.title,
            data: alignedData,
            borderColor: getRandomColor(),
            backgroundColor: 'rgba(0, 0, 0, 0)', // 背景色を透明に
            borderWidth: 1,
            tension: 0.1,
            spanGaps: true // データの抜けを線で繋ぐ
        };
    });

    // 既存のチャートを破棄
    if (chart) {
        chart.destroy();
    }

    // Chart.js を使用してグラフを描画
    const ctx = document.getElementById('viewChart').getContext('2d');
    chart = new Chart(ctx, {
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
        }
    });
}

// 1時間ごとの平均視聴回数増加分を計算する関数
function calculateHourlyAverages(views) {
    const hourlyData = {};

    views.forEach((view, index) => {
        const jstDate = new Date(new Date(view.v_datetime).getTime() + 9 * 60 * 60 * 1000);
        const hour = jstDate.toISOString().slice(0, 13); // 日本時間 (UTC+9) に変換
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

    // 時間順にソートして返す（hourKeyも含める）
    return Object.keys(hourlyData)
        .sort()
        .filter((_, index) => index > 0) // 最初のデータポイントを除外（増加分が0のため）
        .map(hour => ({
            hourKey: hour, // 時間軸合わせ用のキー
            hour: formatHourDisplay(hour), // 表示用にフォーマット変更
            average: Math.floor(hourlyData[hour].sum / hourlyData[hour].count) // 1時間単位の平均値を計算
        }));
}

// 表示用の時間フォーマット関数
function formatHourDisplay(hour) {
    // hour は "2025-07-25T23" のような形式
    const date = new Date(hour + ':00:00.000Z');
    const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
    const day = date.getUTCDate().toString().padStart(2, '0');
    const hourStr = date.getUTCHours().toString().padStart(2, '0');
    return `${month}/${day} ${hourStr}:00`;
}

// ランダムな色を生成する関数
function getRandomColor() {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, 1)`;
}