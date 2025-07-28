import json
import matplotlib.pyplot as plt
from datetime import datetime

# JSONファイルを読み込む
with open('docs/youtube_analyzed.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 総再生回数のグラフを作成・保存
total_videos = data['total_videos']
dates = [datetime.fromisoformat(item['v_datetime']) for item in total_videos]
view_counts = [item['view_count'] for item in total_videos]

plt.figure(figsize=(12, 8))
plt.plot(dates, view_counts, marker='o', linestyle='-', color='b', label='Total Views')
plt.title('Total Video Views Over Time', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('View Count', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('output_total_views.png')  # 総再生回数グラフを保存
print("総再生回数グラフを 'output_total_views.png' に保存しました。")

# 動画ごとの再生回数をまとめたグラフを作成
fig, ax = plt.subplots(figsize=(12, 8))
for video in data['each_video']:
    if 'id' in video and 'views' in video and video['views']:
        video_title = video['title']
        video_views = [view['view_count'] for view in video['views']]
        video_dates = [datetime.fromisoformat(view['v_datetime']) for view in video['views']]
        ax.plot(video_dates, video_views, marker='o', linestyle='-', label=video_title[:30])  # タイトルを短縮

ax.set_title('Individual Video Views Over Time', fontsize=16)
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('View Count', fontsize=12)
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_xticks(ax.get_xticks())
plt.xticks(rotation=45)
plt.tight_layout()

# グラフ本体を保存
fig.savefig('output_combined_views.png')
print("全動画の再生回数をまとめたグラフを 'output_combined_views.png' に保存しました。")

# 凡例を別ファイルに保存
fig_legend = plt.figure(figsize=(8, 12))  # 縦長の画像サイズに調整
handles, labels = ax.get_legend_handles_labels()  # 凡例情報を取得
fig_legend.legend(handles, labels, loc='center', fontsize=8, ncol=1)  # 1列で縦方向に配置
fig_legend.tight_layout()
fig_legend.savefig('output_combined_views_legend.png')
print("凡例を 'output_combined_views_legend.png' に保存しました。")