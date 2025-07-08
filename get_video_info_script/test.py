import yt_dlp
import json
import re

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
        'max_videos': 50,  # 動画数の制限（デバッグ用）
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # YouTubeチャンネルのURLを指定
            channel_url = "https://www.youtube.com/@uise_iu_asmr"
            
            # チャンネルの動画情報を取得
            info = ydl.extract_info(channel_url, download=False)

            with open('video_info.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2, default=json_serializable)

            for entry in info.get('entries', []):
                if entry and 'id' in entry:
                    try:
                        # 個別の動画情報を取得
                        video_info = ydl.extract_info(
                            f"https://www.youtube.com/watch?v={entry['id']}", 
                            download=False
                        )

                        # print(json.dumps(video_info, ensure_ascii=False, indent=2))

                        # コメント情報からTimeStamp情報を取得
                        raw_az_texts = [
                            comment['text'] for comment in video_info.get('comments', [])
                            if 'author' in comment and comment['author'].startswith('@あずにゃんch')
                        ]
                        print(f"取得したazコメント数: {len(raw_az_texts)}")
                        timestamps = []
                        # "text"を改行\n\rで配列化し、[0-9]{1,2}:[0-9]{2}.*と一致するものを抽出
                        for raw_az_text in raw_az_texts:
                            rn_az_texts = raw_az_text.splitlines()
                            for rn_az_text in rn_az_texts:
                                # rn_az_textが正規表現で"[0-9]{1,2}:[0-9]{2}.*"と一致するか確認
                                if re.match(r'[0-9]{1,2}:[0-9]{2}.*', rn_az_text):
                                    # 一致した場合は、timestampsリストに追加
                                    timestamps.append(rn_az_text.strip())
                        
                        # 動画情報を整形
                        video_data = {
                            "title": video_info.get('title', 'タイトル不明'),
                            "videoId": entry['id'],
                            "video_url": f"https://www.youtube.com/watch?v={entry['id']}",
                            "tags": video_info.get('tags', []),
                            "timestamps": timestamps,
                            "metadata": [
                                f"再生時間: {video_info.get('duration', 0)}秒",
                                f"視聴回数: {video_info.get('view_count', 0)}回"
                            ]
                        }
                        
                        print(json.dumps(video_data, ensure_ascii=False, indent=2))

                    except Exception as e:
                        print(f"動画情報の取得に失敗しましたB: {e}")
            print("動画情報の取得と保存が完了しました。")

        except Exception as e:
            print(f"動画情報の取得に失敗しましたA: {e}")

if __name__ == "__main__":
    # 動画情報を取得して保存
    get_playlist_infodict()
    