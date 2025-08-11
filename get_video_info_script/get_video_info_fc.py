#!/usr/bin/env python3
"""
python get_video_info_fc.py
ファンサイト動画情報取得スクリプト
01. 動画情報をAPIから取得
02. 取得した動画情報をJSONファイルに保存
03. 動画情報のサンプルを表示
"""

import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
import time

# 設定
# 動画ページのURLテンプレート($1は動画ID)
FC_VIDEO_PAGE_URL: str = "https://uise-official.com/live/$1"
# 動画情報APIのURLテンプレート($1はlive_type, $2はページ番号)
FC_API_BASE_URL: str = "https://api.uise-official.com/fc/fanclub_sites/434/live_pages?page=$2&live_type=$1&per_page=10"
OUTPUT_FILE: str = "../docs/fciu.json"

class FCVideoInfoExtractor:
    def __init__(self):
        # headersの設定
        self.headers: dict = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "fc_site_id": "434",
            "fc_use_device": "null",
        }


    def _date_str_fmt(self, date_str: str) -> tuple:
        """
        日付文字列を日本時間に直し、以下のフォーマットして日付と時間を返す
            - 日付: YYYY-MM-DD
            - 時間: HH:MM:SS
            - 00:00:00~03:59:59は前日扱いで、24:00:00~27:59:59の形式で返す

        Args:
            date_str: str - 日付文字列
        Returns:
            tuple: (日付:YYYY/MM/DD, 時間:HH:MM:SS)
        """
        if not date_str:
            print("日付文字列が空です。空の値を返します。")
            return "", ""
        try:
            # 日付文字列をdatetimeオブジェクトに変換
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            # 日本時間に変換
            dt_japan = dt + timedelta(hours=9)  # UTC+9時間
            # 日付と時間をフォーマット
            upload_date = dt_japan.strftime("%Y/%m/%d")
            upload_time = dt_japan.strftime("%H:%M:%S")
            # 00:00:00~03:59:59は前日扱いで、24:00:00~27:59:59の形式で返す
            if dt_japan.hour < 4:
                upload_date = (dt_japan - timedelta(days=1)).strftime("%Y/%m/%d")
                hour = "{:02}".format(dt_japan.hour + 24)
                upload_time = f"{hour}:{dt_japan.minute:02}:{dt_japan.second:02}"
            return upload_date, upload_time
        except ValueError as e:
            print(f"日付のフォーマットエラー: {e}")
            raise e

    def get_api_all_video_info(self):
        """
        APIからすべての動画情報を取得
        """
        # 放送予定のlive_typeは1 (↓と逆かも)
        # 配信中のlive_typeは2 (↑と逆かも)
        # 過去の配信のlive_typeは3
        # 1から3までのlive_typeを順に取得
        video_info_list: list = []
        for live_type in range(1, 4):
            page = 1
            while True:
                url = FC_API_BASE_URL.replace("$1", str(live_type)).replace("$2", str(page))
                print(f"取得中: {url}")
                try:
                    response = requests.get(url, headers=self.headers)
                    if response.status_code == 200:
                        res = response.json()
                        data = res.get('data', {})
                        video_pages = data.get('video_pages', {})
                        items = video_pages.get('list', [])
                        if len(items) == 0:
                            print(f"live_type {live_type} はページ {page-1} で終了") 
                            break
                        print(f"live_type {live_type} のページ {page} を取得")
                        for item in items:
                            # 動画情報を抽出
                            upload_date: str = ""
                            upload_time: str = ""
                            # 配信日時情報取得
                            if live_type == 1:
                                upload_date, upload_time = self._date_str_fmt(item.get('live_scheduled_start_at', ''))
                            elif live_type == 2:
                                upload_date, upload_time = self._date_str_fmt(item.get('live_started_at', ''))
                            else:
                                upload_date, upload_time = self._date_str_fmt(item.get('live_started_at', ''))
                            metadata:list = []
                            metadata.append("配信日時: " + upload_date + " " + upload_time)
                            # 配信状態のメタデータを追加
                            if live_type == 1:
                                metadata.append("配信予定")
                            elif live_type == 2:
                                metadata.append("配信中")
                            else:
                                # 過去の配信の場合
                                # 再生時間を計算し、メタデータに追加
                                live_started_time_str:str = item.get('live_started_at')
                                live_started_time:datetime = datetime.strptime(live_started_time_str, "%Y-%m-%d %H:%M:%S")
                                live_finished_time_str:str = item.get('live_finished_at')
                                # 2025-08-10 16:00:00
                                live_finished_time:datetime = datetime.strptime(live_finished_time_str, "%Y-%m-%d %H:%M:%S")
                                duration:timedelta = live_finished_time - live_started_time
                                metadata.append(f"再生時間: {duration}")
                                # 再生回数をメタデータに追加
                                view_count = item.get('video_aggregate_info', {"total_views": 0}).get('total_views', 0)
                                metadata.append(f"再生回数: {view_count}回")
                            # 視聴条件をメタデータに追加
                            pricing_info: int = item.get('video_delivery_target', {"id": 0}).get('id', 0)
                            if pricing_info == 1:
                                video_free_periods = item.get('video_free_periods', [])
                                if video_free_periods:
                                    metadata.append("視聴条件: 一部無料")
                                    free_periods = []
                                    for period in video_free_periods:
                                        free_start:int = period.get('elapsed_started_time', 0)
                                        free_end:int = period.get('elapsed_ended_time', 0)
                                        # free_start, free_end が秒数なので、hh:mm:ss形式に変換(hhが0の場合はmm:ss形式)
                                        if free_start // 3600 == 0:
                                            free_start = f"{((free_start % 3600) // 60):02}:{free_start % 60:02}"
                                            free_end = f"{((free_end % 3600) // 60):02}:{free_end % 60:02}"
                                        else:
                                            free_start = f"{free_start // 3600}:{((free_start % 3600) // 60):02}:{free_start % 60:02}"
                                            free_end = f"{free_end // 3600}:{((free_end % 3600) // 60):02}:{free_end % 60:02}"
                                        free_periods.append(f"{free_start}~{free_end}")
                                    metadata.append("無料部分 " + ", ".join(free_periods))
                                else:
                                    metadata.append("視聴条件: 会員のみ")
                            elif pricing_info == 2:
                                metadata.append("視聴条件: 全編無料")
                            else:
                                metadata.append("視聴条件: 不明")

                            # 動画情報を辞書にまとめる
                            video_info = {
                                'title': item.get('title', ''),
                                'video_url': f"https://uise-official.com/live/{item.get('content_code', '')}",
                                'image': item.get('thumbnail_url', ''),
                                'upload_date': upload_date,
                                'metadata': metadata,
                            }
                            # 動画情報をリストに追加
                            video_info_list.append(video_info)
                    page += 1
                except Exception as e:
                    raise e
        # 取得した動画情報をクラス変数に保存
        self.all_videos = video_info_list

    def save_to_json(self, filename=OUTPUT_FILE):
        """
        動画情報をJSONファイルに保存（{"items": []} 形式）
        
        Args:
            filename: str - 保存先ファイルパス
        """
        try:
            # ディレクトリが存在しない場合は作成
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # {"items": []} 形式で保存
            data = {"items": self.all_videos}
            # JSONファイルに書き込み
            if not data['items']:
                raise Exception("動画情報が空です。保存をスキップします。")  # 空のデータは保存しない
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"動画情報を {filename} に保存しました")
            
        except Exception as e:
            print(f"ファイル保存に失敗: {e}")

def main():
    """
    メイン実行関数 - スクリプトのエントリーポイント
    
    処理の流れ：
    1. FCVideoInfoExtractorインスタンスの作成
    2. 全動画情報の取得
    3. 結果のJSONファイル保存
    4. 取得結果のサマリー表示
    """
    # スクリプトの開始時間を記録
    start_time = time.time()

    print("🎬 ファンクラブ動画情報取得スクリプト")

    extractor = FCVideoInfoExtractor()
    
    try:
        # 全動画情報を取得
        extractor.get_api_all_video_info()
        
        # 結果をJSONファイルに保存
        extractor.save_to_json()
        
        # 取得した情報の一部を表示
        _display_sample_results(extractor.all_videos)

    except Exception as e:
        raise e
        
    finally:
        # 実行時間の表示
        _display_execution_summary(start_time)

def _display_sample_results(all_videos):
    """
    取得した動画情報のサンプルを表示
    
    Args:
        all_videos: list - 取得した動画情報のリスト
    """
    if all_videos:
        print("\n取得した動画情報のサンプル:")
        for i, video in enumerate(all_videos[:3]):  # 最初の3件を表示
            print(f"\n--- 動画 {i+1} ---")
            print(f"タイトル: {video.get('title', 'N/A')}")
            print(f"動画URL: {video.get('video_url', 'N/A')}")
            print(f"サムネイル: {video.get('image', 'N/A')}")
            print(f"配信日: {video.get('upload_date', 'N/A')}")
            if video.get('metadata'):
                print(f"メタデータ: {video['metadata']}")

def _display_execution_summary(start_time):
    """
    実行時間とスクリプト完了メッセージを表示
    
    Args:
        start_time: float - スクリプト開始時間
    """
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n⏱ 実行時間: {execution_time:.2f}秒")
    print("🎉 処理が完了しました！")

if __name__ == "__main__":
    main()

