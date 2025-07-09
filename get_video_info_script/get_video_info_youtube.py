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

def get_video_info(channel_url):
    """
    YouTubeチャンネルから動画情報を取得
    
    Args:
        channel_url (str): YouTubeチャンネルのURL
    
    Returns:
        list: 動画情報のリスト
    """
    
    # yt-dlpの設定（GitHub Actions対応）
    ydl_opts = {
        'quiet': False,  # Falseでエラー以外の出力を表示
        'no_warnings': True, # 警告を非表示
        'extract_flat': True,  # 詳細情報も取得
        'ignoreerrors': True,  # エラーが発生しても続行
        'getcomments': True,  # コメントを取得
        # GitHub Actions環境での対策
        'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sleep_interval': 2,  # リクエスト間隔を2秒に設定
        'max_sleep_interval': 5,  # 最大スリープ間隔
        'retries': 3,  # リトライ回数
        'fragment_retries': 3,  # フラグメントリトライ回数
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    }
    
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
                        try:
                            # 個別の動画情報を取得（エラーハンドリング強化）
                            print(f"  → 動画ID {entry['id']} の詳細情報を取得中...")
                            
                            # 個別動画用のyt-dlp設定
                            video_ydl_opts = ydl_opts.copy()
                            video_ydl_opts['extract_flat'] = False  # 詳細情報を取得
                            
                            video_info = None
                            for attempt in range(3):  # 3回まで再試行
                                try:
                                    with yt_dlp.YoutubeDL(video_ydl_opts) as video_ydl:
                                        video_info = video_ydl.extract_info(
                                            f"https://www.youtube.com/watch?v={entry['id']}", 
                                            download=False
                                        )
                                    break  # 成功したらループを抜ける
                                except Exception as retry_error:
                                    print(f"    試行 {attempt + 1}/3 失敗: {str(retry_error)}")
                                    if attempt < 2:  # 最後の試行でなければ待機
                                        import time
                                        time.sleep(5)  # 5秒待機
                                    else:
                                        raise retry_error  # 最後の試行で失敗したら例外を上げる

                            if not video_info:
                                raise Exception("動画情報の取得に失敗しました")

                            # コメント情報からTimeStamp情報を取得
                            # コメント情報から"author": "@shokoaz"の"text"を取得
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

                            # 動画情報を整形
                            video_data = {
                                "title": video_info.get('title', 'タイトル不明'),
                                "image": f"https://i.ytimg.com/vi/{entry['id']}/maxresdefault.jpg",
                                "alt": video_info.get('title', 'タイトル不明'),
                                "description": video_info.get('description', '')[:100] + "..." if video_info.get('description') else "説明なし",
                                "videoId": entry['id'],
                                "video_url": f"https://www.youtube.com/watch?v={entry['id']}",
                                "tags": video_info.get('tags', []),
                                "timestamps": timestamps,
                                "metadata": [
                                    f"再生時間: {format_duration(video_info.get('duration', 0))}",
                                    f"視聴回数: {format_view_count(video_info.get('view_count', 0))}",
                                    f"投稿日: {format_upload_date(video_info.get('upload_date', ''))}"
                                ],
                                "addAdditionalClass": [video_info.get('availability', '')],  # "availability": "subscriber_only"なら"subscriber_only", それ以外は"-"
                            }
                            
                            videos.append(video_data)
                            print(f"✓ 取得完了: {video_data.get('title', 'タイトル不明')} (ID: {entry['id']})")
                            
                        except Exception as e:
                            # 個別動画の取得に失敗した場合は放送予定枠かメン限枠なので動画情報を整形する
                            print(f"✗ 詳細取得失敗: {entry.get('title', 'タイトル不明')} (ID: {entry['id']}) - {str(e)}")
                            print(f"  → 基本情報のみで処理を続行します")
                            
                            # availability情報の取得を試行
                            availability = entry.get('availability', 'unknown')
                            add_class = []
                            
                            if availability == 'subscriber_only':
                                add_class = ['subscriber_only']
                            elif entry.get('live_status') == 'is_upcoming':
                                add_class = ['schedule']
                            else:
                                add_class = ['unavailable']
                            
                            video_data = {
                                "title": entry.get('title', 'タイトル不明'),
                                "image": f"https://i.ytimg.com/vi/{entry['id']}/maxresdefault.jpg",
                                "alt": entry.get('title', 'タイトル不明'),
                                "description": entry.get('description')[:100] + "..." if entry.get('description') else "説明なし",
                                "videoId": entry['id'],
                                "video_url": entry.get('url', f"https://www.youtube.com/watch?v={entry['id']}"),
                                "addAdditionalClass": add_class,
                            }
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

def main():
    """
    メイン実行関数
    """
    print("🎬 YouTube動画情報取得スクリプト")
    
    # 実行環境の情報を表示
    import os
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("🤖 GitHub Actions環境で実行中")
        print(f"📁 キャッシュディレクトリ: {os.getenv('YT_DLP_CACHE_DIR', 'デフォルト')}")
    
    # yt-dlpがインストールされているかチェック
    try:
        import yt_dlp
        print(f"✅ yt-dlp バージョン: {yt_dlp.version.__version__}")
    except ImportError:
        print("❌ yt-dlpがインストールされていません。")
        print("以下のコマンドでインストールしてください:")
        print("pip install yt-dlp")
        sys.exit(1)
    
    # 動画情報を取得
    print(f"🔍 チャンネル '{CHANNEL_URL}' から動画情報を取得します...")
    videos = get_video_info(CHANNEL_URL)
    
    if videos:
        # JSONファイルに保存
        save_to_json(videos, OUTPUT_FILE)
        
        # 取得した動画の最初の3つを表示
        print("\n📝 取得した動画の例:")
        for i, video in enumerate(videos[:3]):
            print(f"\n{i+1}. {video['title']}")
            print(f"   ID: {video['videoId']}")
            print(f"   説明: {video['description']}")
            if 'metadata' in video:
                print(f"   メタデータ: {', '.join(video['metadata'])}")
            print(f"   クラス: {video.get('addAdditionalClass', [])}")
        
        if len(videos) > 3:
            print(f"\n... 他 {len(videos) - 3} 個の動画")
            
    else:
        print("❌ 動画情報の取得に失敗しました。")
        sys.exit(1)
    
    print("\n🎉 処理が完了しました！")

if __name__ == "__main__":
    main()
