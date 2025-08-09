# https://www.youtube.com/@koyuchan_/streamsから最新5件を取得するためのスクリプト

import yt_dlp

def get_videos_info(youtube_channel_url):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_channel_url, download=False)
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
    youtube_channel_url = "https://www.youtube.com/@koyuchan_/streams"
    videos_info = get_videos_info(youtube_channel_url)
    if videos_info:
        save_videos_info(videos_info)
        print(f"動画情報を{len(videos_info)}件保存しました。")
    else:
        print("動画情報の取得に失敗しました。")
    
    youtube_video_url = "https://www.youtube.com/watch?v=mEl2zwQFTB4"
    video_info = get_video_info(youtube_video_url)
    if video_info:
        save_videos_info([video_info], 'single_video_info.json')
        print(f"動画情報: {video_info}")
    else:
        print("動画情報の取得に失敗しました。")


if __name__ == "__main__":
    main()