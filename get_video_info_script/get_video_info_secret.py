#!/usr/bin/env python3
"""
ファンサイト動画情報取得スクリプト
Webページ「https://candfans.jp/iu_nyaa」を開き、一番下までスクロールした状態で
すべてのdivタグ・class="grid grid-cols-2 gap-x-1 gap-y-3 pt-2 items-end"
の子要素(サムネイル)から投稿情報
    動画なら
    ・記事タイトル
    ・記事URL
    ・サムネイルURL
    ・meta情報(閲覧回数、投稿時期、動画時間)
    画像なら
    ・記事タイトル
    ・記事URL
    ・サムネイルURL
    ・meta情報(閲覧回数、投稿時期)
を取得し、
docs/secret_ac.jsonファイルを更新します。
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# 設定
SECRET_PAGE_URL = "https://candfans.jp/api/contents/get-timeline?user_id=1189871&sort_order=new&post_type[]=1&record=50&page="
OUTPUT_FILE = "../docs/secret_ac.json"

class SecretVideoInfoExtractor:
    def __init__(self):
        """
        コンストラクタ
        """
        self.post_list = []
        self.current_page = 1

    def get_video_info(self):
        """
        動画情報を取得するメソッド
        {SECRET_PAGE_URL}{ページ数}でリクエストして情報を取得

        args:
            なし
        returns:
            なし
        """
        try:
            # ページを取得
            while True:
                url = f"{SECRET_PAGE_URL}{self.current_page}"
                res = self.fetch_data(url)
                data = res.get("data", [])
                if len(data) == 0:
                    break
                for item in data:
                    post_id = item.get("post_id")
                    contents_type = item.get("contents_type")
                    image = ""
                    if contents_type == 1:  # 画像
                        image = f'https://image.candfans.jp{item.get("secret_file", "")}'
                    elif contents_type == 2:  # 動画
                        image = f'https://video.candfans.jp{item.get("secret_file", "")}'
                    self.post_list.append({
                        "title": item.get("title", "タイトル情報なし"),
                        "video_url": f'https://candfans.jp/posts/comment/show/{post_id}',
                        "image": image,
                        "alt": item.get("title", "タイトル情報なし"),
                        "metadata": [
                            f'投稿日時: {item.get("post_date", "不明")}',
                            f'内容: {item.get("contents_text", "内容情報なし")}',
                            f'閲覧回数: {item.get("attachment_play_count", 0)}',
                            f'❤x{item.get("like_cnt", 0)}',
                        ]
                    })
                self.current_page += 1
        except Exception as e:
            print(f"動画情報の取得に失敗: {e}")
            raise e
        finally:
            self.save_to_json(self.post_list, OUTPUT_FILE)

    def fetch_data(self, url):
        """
        指定されたURLからデータを取得するメソッド

        args:
            url (str): データを取得するURL
        returns:
            dict: 取得したデータ
        """
        import requests
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTPエラーが発生した場合は例外を投げる
            return response.json()
        except requests.RequestException as e:
            print(f"データの取得に失敗: {e}")
            sys.exit(1)

    def save_to_json(self, post_list, filename=OUTPUT_FILE):
        """
        投稿情報をJSONファイルに保存（{"items": []} 形式）
        """
        try:
            # ディレクトリが存在しない場合は作成
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # {"items": []} 形式で保存
            data = {"items": post_list}
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"投稿情報を {filename} に保存しました")
            
        except Exception as e:
            print(f"ファイル保存に失敗: {e}")


def main():
    """
    メイン実行関数
    """
    # スクリプトの開始時間を記録
    start_time = datetime.now()

    print("🎬 ファンサイト動画情報取得スクリプト")

    extractor = SecretVideoInfoExtractor()
    
    try:
        extractor.get_video_info()
        print("✅ 動画情報の取得が完了しました！")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        raise e

    finally:
        # 実行時間を表示
        end_time = datetime.now()
        execution_time = end_time - start_time
        print(f"\n⏱ 実行時間: {execution_time}")
        print("🎉 処理が完了しました！")

if __name__ == "__main__":
    main()
