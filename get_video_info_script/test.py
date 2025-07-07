import yt_dlp
import json

def json_serializable(obj):
    """
    JSONシリアライズ可能な形式に変換するヘルパー関数
    """
    if isinstance(obj, (set, frozenset)):
        return list(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# yt_dlp.YoutubeDL()._playlist_infodictの取得内容を確認
def get_playlist_infodict():
    ydl_opts = {
        'quiet': True,  # デバッグのため出力を表示
        'no_warnings': False,
        'extract_flat': True,  # 詳細情報も取得
        'getcomments': True,  # コメントを取得
        'max_videos': 3,  # 動画数の制限（デバッグ用）
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # YouTubeチャンネルのURLを指定
            channel_url = "https://www.youtube.com/@uise_iu_asmr"
            
            # チャンネルの動画情報を取得
            info = ydl.extract_info(channel_url, download=False)

            # 動画情報jsonで保存
            with open('youtube_playlist_info.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4, default=json_serializable)
            print("動画情報を 'youtube_playlist_info.json' に保存しました。")
        except Exception as e:
            print(f"動画情報の取得に失敗しました: {e}")

if __name__ == "__main__":
    # 動画情報を取得して保存
    get_playlist_infodict()
    