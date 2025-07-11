#!/usr/bin/env python3
"""
YouTube動画情報取得スクリプト
yt-dlpを使用してuise_iu_asrのYouTubeチャンネルから動画情報を取得し、
docs/youtube.jsonファイルを更新します。
"""

import json
import sys
import time
from datetime import datetime
import yt_dlp
from pathlib import Path
import re

# 設定
CHANNEL_URL = "https://www.youtube.com/@uise_iu_asmr"
OUTPUT_FILE = "../docs/youtube.json"

class CustomLogger:
    """カスタムロガークラス"""
    def __init__(self, verbose=False):
        self.messages = []
        self.verbose = verbose
        
    def debug(self, message):
        self.messages.append({'logType': 'DEBUG', 'message': message})
        if self.verbose:
            print(f"[DEBUG] {message}")
        
    def warning(self, message):
        self.messages.append({'logType': 'WARNING', 'message': message})
        if self.verbose:
            print(f"[WARNING] {message}")
        
    def error(self, message):
        self.messages.append({'logType': 'ERROR', 'message': message})
        if self.verbose:
            print(f"[ERROR] {message}")
    
    def get_messages(self):
        return self.messages
    
    def get_latest_error(self):
        """
        最新のエラーメッセージを取得
        
        Returns:
            str: 最新のエラーメッセージ、存在しない場合はNone
        """
        for message in reversed(self.messages):
            if message['logType'] == 'ERROR':
                return message['message']
        return None
    
    def clear_messages(self):
        self.messages = []

def get_ydl_options():
    """
    yt-dlpの設定を取得
    
    Returns:
        dict: yt-dlpの設定辞書
    """
    # カスタムロガーのインスタンスを作成（CLI出力オフ）
    custom_logger = CustomLogger(verbose=False)
    return {
        'quiet': True,  # CLI出力を非表示
        'no_warnings': True, # 警告を非表示
        'extract_flat': True,  # 詳細情報も取得
        'ignoreerrors': True,  # エラーが発生しても続行
        'getcomments': True,  # コメントを取得
        # ロガーを使用する
        'logger': custom_logger,  # カスタムロガーを設定
        'sleep_interval': 5,  # リクエスト間隔を設定(秒)
        'max_sleep_interval': 15,  # 最大スリープ間隔
        'retries': 3,  # リトライ回数
        'fragment_retries': 3,  # フラグメントリトライ回数
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

def get_detailed_video_info(video_id, ydl_opts):
    """
    個別動画の詳細情報を取得（リトライ機能付き）
    
    Args:
        video_id (str): 動画ID
        ydl_opts (dict): yt-dlpの設定
    
    Returns:
        dict: 動画の詳細情報、失敗時はNone
    """
    # 個別動画用のyt-dlp設定
    video_ydl_opts = ydl_opts.copy()
    video_ydl_opts['extract_flat'] = False  # 詳細情報を取得
    
    video_info = None
    for attempt in range(3):  # 3回まで再試行
        try:
            if attempt > 0:
                print(f"    リトライ中... 試行 {attempt + 1}/3")

            with yt_dlp.YoutubeDL(video_ydl_opts) as video_ydl:
                video_info = video_ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}", 
                    download=False
                )
            break  # 成功したらループを抜ける
        except Exception as retry_error:
            print(f"    試行 {attempt + 1}/3 失敗: {str(retry_error)}")
            if attempt < 2:  # 最後の試行でなければ待機
                time.sleep(5)  # 5秒待機
            else:
                raise retry_error  # 最後の試行で失敗したら例外を上げる
    
    if video_info is None:
        # ロガーからの情報を取得
        logger = video_ydl_opts['logger']
        # 最新のエラーログメッセージを取得
        latest_error = logger.get_latest_error()
        if latest_error:
            logger.clear_messages()  # エラーメッセージをクリア
            raise Exception(latest_error)  # エラーメッセージを例外として上げる
    
    return video_info

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

def process_video_entry(entry, ydl_opts):
    """
    個別の動画エントリを処理
    
    Args:
        entry (dict): 動画エントリ情報
        ydl_opts (dict): yt-dlpの設定
    
    Returns:
        dict: 処理された動画データ
    """
    video_id = entry['id']
    
    try:
        # 個別の動画情報を取得（エラーハンドリング強化）
        print(f"動画ID {video_id} の詳細情報を取得中...")
        
        video_info = get_detailed_video_info(video_id, ydl_opts)

        # 動画情報を整形
        video_data = create_video_data_from_detailed_info(video_info, video_id)
        
        print(f"  → ✓ 取得完了: {video_data.get('title', 'タイトル不明')} (ID: {video_id})")
        return video_data
        
    except Exception as e: 
        # 個別動画の取得に失敗した場合は放送予定枠かメン限枠なので動画情報を整形する
        error_message = str(e)
        
        # エラーメッセージから特定の状況を判定
        if 'members-only' in error_message:
            print(f"  → ✓ メンバー限定動画: ID: {video_id} - 詳細情報の取得をスキップします")
        elif "This live event will" in error_message:
            print(f"  → ✓ 未放送枠: ID: {video_id} - 詳細情報の取得をスキップします")
        else:
            print(f"  → ✗ 詳細情報取得失敗: ID: {video_id} - {error_message}")
        print(f"    → 基本情報のみで処理を続行します")
        
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
            info = ydl.extract_info(channel_url, download=False)
            
            if 'entries' in info:
                print(f"発見された動画数: {len(info['entries'])}")
                
                for entry in info['entries']:
                    if entry and 'id' in entry:
                        video_data = process_video_entry(entry, ydl_opts)
                        videos.append(video_data)

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
    動画情報をJSONファイルに保存
    
    Args:
        videos (list): 動画情報のリスト
        output_file (str): 出力ファイルパス
    """
    
    # 出力ディレクトリを作成（存在しない場合）
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # JSON形式でデータを構築
    json_data = {
        "items": videos,
        "last_updated": datetime.now().isoformat(),
        "total_videos": len(videos)
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 動画情報を {output_file} に保存しました")
        print(f"📊 総動画数: {len(videos)}")
        
    except Exception as e:
        print(f"❌ ファイル保存エラー: {str(e)}")

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
