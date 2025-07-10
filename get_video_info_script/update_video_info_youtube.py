#!/usr/bin/env python3
"""
YouTube動画情報取得スクリプト
yt-dlpを使用してuise_iu_asrのYouTubeチャンネルから動画情報を取得し、
docs/youtube.jsonファイルを更新します。
"""

import json
import sys
from datetime import datetime
import yt_dlp
from pathlib import Path
import re

# 設定
CHANNEL_URL = "https://www.youtube.com/@uise_iu_asmr"
OUTPUT_FILE = "../docs/youtube.json"

def get_ydl_options():
    """
    yt-dlpの設定を取得
    
    Returns:
        dict: yt-dlpの設定辞書
    """
    return {
        'quiet': True,  # CLI出力を非表示
        'no_warnings': True, # 警告を非表示
        'extract_flat': False,  # 詳細情報も取得
        'ignoreerrors': True,  # エラーが発生しても続行
        'getcomments': True,  # コメントを取得
    }

def extract_timestamps_from_comments(video_info):
    """
    動画のコメントからタイムスタンプ情報を抽出
    
    Args:
        video_info (dict): 動画情報
    
    Returns:
        list: タイムスタンプのリスト
    """
    # コメント情報から"author": "@あずにゃんch"の"text"を取得
    raw_az_texts = [
        comment['text'] for comment in video_info.get('comments', [])
        if 'author' in comment and comment['author'].startswith('@あずにゃんch')
    ]
    
    timestamps = []
    # "text"を改行\n\rで配列化し、[0-9]{1,2}:[0-9]{2}.*と一致するものを抽出
    for raw_az_text in raw_az_texts:
        # 改行で分割
        rn_az_texts = raw_az_text.splitlines()
        # ".*[0-9]{1,2}:[0-9]{2}.*"と一致する行を抽出
        rn_az_texts = [text for text in rn_az_texts if re.match(r'.*[0-9]{1,2}:[0-9]{2}.*', text)]
        # 最初の行が"[0-9]{1,2}:[0-9]{2}.*START.*"と一致していなかったらスキップ
        if not rn_az_texts or not re.match(r'.*[0-9]{1,2}:[0-9]{2}.*START.*', rn_az_texts[0]):
            continue
        timestamps.extend(rn_az_texts)
    
    return timestamps

def create_video_data_from_detailed_info(video_info, video_id):
    """
    詳細な動画情報から動画データを作成
    
    Args:
        video_info (dict): 詳細な動画情報
        video_id (str): 動画ID
    
    Returns:
        dict: 整形された動画データ
    """
    timestamps = extract_timestamps_from_comments(video_info)
    
    return {
        "title": video_info.get('title', 'タイトル不明'),
        "image": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        "alt": video_info.get('title', 'タイトル不明'),
        "description": video_info.get('description', '')[:100] + "..." if video_info.get('description') else "説明なし",
        "videoId": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "tags": video_info.get('tags', []),
        "timestamps": timestamps,
        "metadata": [
            f"再生時間: {format_duration(video_info.get('duration', 0))}",
            f"視聴回数: {format_view_count(video_info.get('view_count', 0))}",
            f"投稿日: {format_upload_date(video_info.get('upload_date', ''))}"
        ],
        "addAdditionalClass": [video_info.get('availability', '')],  # "availability": "subscriber_only"なら"subscriber_only", それ以外は"-"
    }

def create_video_data_from_basic_info(entry):
    """
    基本的な動画情報から動画データを作成（詳細取得失敗時用）
    
    Args:
        entry (dict): 基本的な動画情報
    
    Returns:
        dict: 整形された動画データ
    """
    video_id = entry['id']
    
    # availability情報の取得を試行
    availability = entry.get('availability', 'unknown')
    add_class = []
    
    if availability == 'subscriber_only':
        add_class = ['subscriber_only']
    elif entry.get('live_status') == 'is_upcoming':
        add_class = ['schedule']
    else:
        add_class = ['unavailable']
    
    return {
        "title": entry.get('title', 'タイトル不明'),
        "image": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
        "alt": entry.get('title', 'タイトル不明'),
        "description": entry.get('description')[:100] + "..." if entry.get('description') else "説明なし",
        "videoId": video_id,
        "video_url": entry.get('url', f"https://www.youtube.com/watch?v={video_id}"),
        "addAdditionalClass": add_class,
    }

def process_video_entry(entry):
    """
    個別の動画エントリを処理
    
    Args:
        entry (dict): 動画エントリ情報
    
    Returns:
        dict: 処理された動画データ
    """
    video_id = entry['id']
    
    try:
        print(f"動画ID: {video_id} の詳細情報を取得")
        # 動画情報を整形
        video_data = create_video_data_from_detailed_info(entry, video_id)
        
        print(f"  → ✓ 取得完了: {video_data.get('title', 'タイトル不明')} (ID: {video_id})")
        return video_data
        
    except Exception as e:
        # 個別動画の取得に失敗した場合は...
        print(f"  → ✗ 詳細取得失敗: {entry.get('title', 'タイトル不明')} (ID: {video_id}) - {str(e)}")
        print(f"    → 基本情報のみで処理を続行")
        
        return create_video_data_from_basic_info(entry)

def get_video_info(channel_url):
    """
    YouTubeチャンネルから動画情報を取得
    
    Args:
        channel_url (str): YouTubeチャンネルのURL
    
    Returns:
        list: 動画情報のリスト
    """
    
    ydl_opts = get_ydl_options()
    
    videos = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"'{channel_url}/stream' から動画情報を取得中...")
            
            # チャンネルの動画一覧を取得
            # 動画ごとの詳細情報、コメントも取得
            info = ydl.extract_info(channel_url, download=False)
            print(f"チャンネル '{channel_url}' の動画情報を取得しました")
            
            if 'entries' in info:
                print(f"発見された動画数: {len(info['entries'])}")
                
                for entry in info['entries']:
                    if entry and 'id' in entry:
                        video_data = process_video_entry(entry)
                        videos.append(video_data)
                    elif entry:
                        print(f"  → ✗ 無効な動画エントリ: {entry.get('title', '不明')}")
                    else:
                        print("  → ✗ エントリが空です(updateスクリプトではメン限は取得できないため)")

            else:
                print("チャンネルに動画が見つかりませんでした。")
                
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return []
    
    return videos

def format_duration(seconds):
    """
    秒数を時:分:秒形式に変換
    
    Args:
        seconds (int): 秒数
    
    Returns:
        str: フォーマットされた時間文字列
    """
    if not seconds:
        return "0:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def format_view_count(count):
    """
    視聴回数をフォーマット
    
    Args:
        count (int): 視聴回数
    
    Returns:
        str: フォーマットされた視聴回数
    """
    if not count:
        return "0回"
    
    if count >= 1000000:
        return f"{count / 1000000:.1f}M回"
    elif count >= 1000:
        return f"{count / 1000:.1f}K回"
    else:
        return f"{count:,}回"

def format_upload_date(date_str):
    """
    アップロード日をフォーマット
    
    Args:
        date_str (str): YYYYMMDD形式の日付文字列
    
    Returns:
        str: フォーマットされた日付
    """
    if not date_str or len(date_str) != 8:
        return "日付不明"
    
    try:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}/{month}/{day}"
    except:
        return "日付不明"

def save_to_json(videos, output_file):
    """
    動画情報をJSONファイルに統合
    
    Args:
        videos (list): 動画情報のリスト
        output_file (str): 出力ファイルパス
    """
    
    # 出力ディレクトリを作成（存在しない場合）
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            # 既存のデータとマージ

            for raw_item in existing_data['items']:
                # 既存の動画IDをキーにして、動画情報を更新
                existing_video_id = raw_item['videoId']
                for video in videos:
                    if video and video['videoId'] == existing_video_id:
                        raw_item.update(video)
                        break

            # `json_data`を適切に初期化
            json_data = {
                'items': existing_data['items'],
                'last_updated': datetime.now().isoformat(),
                'total_videos': len(existing_data['items']),
            }
    except FileNotFoundError:
        # ファイルが存在しない場合はget_video_info_youtube.pyを実行するように指示
        print("先にget_video_info_youtube.pyを実行して、正確な動画情報を取得してください。")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"動画情報を {output_file} に保存しました")


def check_dependencies():
    """
    必要な依存関係をチェック
    
    Returns:
        bool: 依存関係が満たされている場合True
    """
    try:
        import yt_dlp
        print(f"✅ yt-dlp バージョン: {yt_dlp.version.__version__}")
        return True
    except ImportError:
        print("❌ yt-dlpがインストールされていません。")
        print("以下のコマンドでインストールしてください:")
        print("pip install yt-dlp")
        return False

def display_execution_environment():
    """
    実行環境の情報を表示
    """
    import os
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("🤖 GitHub Actions環境で実行中")
        print(f"📁 キャッシュディレクトリ: {os.getenv('YT_DLP_CACHE_DIR', 'デフォルト')}")

def display_video_samples(videos, sample_count=3):
    """
    取得した動画のサンプルを表示
    
    Args:
        videos (list): 動画情報のリスト
        sample_count (int): 表示するサンプル数
    """
    print("\n📝 取得した動画の例:")
    for i, video in enumerate(videos[:sample_count]):
        print(f"\n{i+1}. {video['title']}")
        print(f"   ID: {video['videoId']}")
        print(f"   説明: {video['description']}")
        if 'metadata' in video:
            print(f"   メタデータ: {', '.join(video['metadata'])}")
        print(f"   クラス: {video.get('addAdditionalClass', [])}")
    
    if len(videos) > sample_count:
        print(f"\n... 他 {len(videos) - sample_count} 個の動画")

def main():
    """
    メイン実行関数
    """
    # スクリプトの開始時間を記録
    start_time = datetime.now()

    print("🎬 YouTube動画情報取得スクリプト")
    
    # 実行環境の情報を表示
    display_execution_environment()
    
    # yt-dlpがインストールされているかチェック
    if not check_dependencies():
        print("❌ 必要な依存関係が満たされていません。スクリプトを終了します。")
        sys.exit(1)
    
    # 動画情報を取得
    print(f"🔍 チャンネル '{CHANNEL_URL}' から動画情報を取得します...")
    videos = get_video_info(CHANNEL_URL)
    
    if videos:
        # JSONファイルに保存
        save_to_json(videos, OUTPUT_FILE)
        
        # 取得した動画の最初の3つを表示
        display_video_samples(videos)
            
    else:
        print("❌ 動画情報の取得に失敗しました。")
        sys.exit(1)
    
    # 実行時間を表示
    end_time = datetime.now()
    execution_time = end_time - start_time
    print(f"\n⏱ 実行時間: {execution_time}")
    print("\n🎉 処理が完了しました！")

if __name__ == "__main__":
    main()
