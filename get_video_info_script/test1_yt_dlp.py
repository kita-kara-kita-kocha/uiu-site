# https://www.youtube.com/watch?v=BNYl51enrcsの動画情報を取得するためのスクリプト

import yt_dlp

def get_video_info(youtube_video_url):
    ydl_opts = {
        'force_generic_extractor': True,
        'quiet': True,  # CLI出力を非表示
        'no_warnings': True, # 警告を非表示
        'extract_flat': True,  # 詳細情報も取得
        'ignoreerrors': True,  # エラーが発生しても続行
        'sleep_interval': 5,  # リクエスト間隔を設定(秒)
        'max_sleep_interval': 15,  # 最大スリープ間隔
        'retries': 3,  # リトライ回数
        'fragment_retries': 3,  # フラグメントリトライ回数
        'ignore_no_formats_error': True, # フォーマットが見つからないエラーを無視
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_video_url, download=False)
            if 'entries' in result:
                return result['entries']
            else:
                return [result]
        except Exception as e:
            print(f"Error extracting video info: {e}")
            return []

def get_video_info(video_url):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(video_url, download=False)
            return result
        except Exception as e:
            print(f"Error extracting video info: {e}")
            return None

# json形式で動画情報を保存する関数
def save_videos_info(videos_info, filename='videos_info.json'):
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(videos_info, f, ensure_ascii=False, indent=4)

def main():
    
    youtube_video_url = "https://www.youtube.com/watch?v=2TmxvltEB1g"
    video_info = get_video_info(youtube_video_url)
    if video_info:
        save_videos_info([video_info], 'single_video_info.json')
        # print(f"動画情報: {video_info}")
    else:
        print("動画情報の取得に失敗しました。")


if __name__ == "__main__":
    main()