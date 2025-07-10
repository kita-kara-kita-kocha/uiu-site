#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import sys

# 設定
CHANNEL_URL = "https://ch.nicovideo.jp/uise-iu/live"
OUTPUT_FILE = "../docs/niconico_l.json"

class NiconicoLiveVideoInfoExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_total_pages(self, base_url):
        """
        チャンネルページから総ページ数を取得
        """
        try:
            response = self.session.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # ページネーションから最終ページ番号を取得
            pagination = soup.find('ul', class_='pagination')
            if pagination:
                page_links = pagination.find_all('a')
                page_numbers = []
                for link in page_links:
                    href = link.get('href', '')
                    if 'page=' in href:
                        match = re.search(r'page=(\d+)', href)
                        if match:
                            page_numbers.append(int(match.group(1)))
                
                if page_numbers:
                    return max(page_numbers)
            
            # 代替方法: 最終ページのリンクを探す
            last_page_link = soup.find('a', string=re.compile(r'最後'))
            if last_page_link:
                href = last_page_link.get('href', '')
                match = re.search(r'page=(\d+)', href)
                if match:
                    return int(match.group(1))
                    
            return 1
            
        except Exception as e:
            print(f"総ページ数の取得に失敗: {e}")
            return 1

    def extract_video_info_from_page(self, url):
        """
        指定されたページから動画情報を抽出
        """
        video_list = []
        
        try:
            page = 0
            video_items = []
            while True:
                page += 1
                response = self.session.get(f'{url}?page={page}')
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 動画アイテムを探す（ニコニコ生放送のHTML構造に基づく）
                # sectionタグのclassがsubかつpastの両方を持つものを探す
                section_items = soup.find_all('section', class_=lambda x: x and 'sub' in x and 'past' in x)
                if not section_items:
                    print(f"ページ {page} で動画セクションが見つかりませんでした。終了します。")
                    break
                tmp_items = []
                for section in section_items:
                    tmp_items = section.find_all('div', class_='item')
                    print(f"ページ {page} から {len(tmp_items)} 個の動画アイテムを検出")
                    video_items.extend(tmp_items)
                if len(tmp_items) == 0:
                    print(f"ページ {page} で動画アイテムが見つかりませんでした。終了します。")
                    break
            for item in video_items:
                try:
                    video_info = self.extract_single_video_info(item)
                    print(f"動画情報を抽出: {video_info}")
                    if video_info:
                        video_list.append(video_info)
                except Exception as e:
                    print(f"動画情報の抽出でエラー: {e}")
                    continue
                        
        except Exception as e:
            print(f"ページの読み込みに失敗 ({url}): {e}")
            
        return video_list

    def extract_single_video_info(self, item):
        """
        単一の動画アイテムから情報を抽出
        """
        video_info = {}
        
        # タイトルの取得
        title_element = item.find('h3') or item.find('h2') or item.find('a', class_=re.compile(r'.*title.*'))
        if title_element:
            video_info['title'] = title_element.get_text(strip=True)
        
        # 動画リンクの取得
        link_element = item.find('a', href=re.compile(r'/watch/'))
        if link_element:
            href = link_element.get('href')
            if href.startswith('/'):
                video_info['video_url'] = f"https://live.nicovideo.jp{href}"
            else:
                video_info['video_url'] = href
        
        # サムネイルの取得
        img_element = item.find('img')
        if img_element:
            src = img_element.get('src') or img_element.get('data-src')
            if src:
                if src.startswith('/'):
                    video_info['image'] = f"https:{src}"
                elif src.startswith('//'):
                    video_info['image'] = f"https:{src}"
                else:
                    video_info['image'] = src

        # metadateの定義
        video_info['metadata'] = []
        
        # 放送開始日時の取得
        # pタグclass=dateの要素を探す
        date_element = item.find('p', class_='date')
        # ulタグからclass=itemsの要素を探す
        if date_element:
            # date_elementの空白を削除
            date_element = date_element.get_text(strip=True)
            # 放送開始：2025/07/03 (木) 00:00:00から2025/07/03 (木) 00:00:00の部分を抽出
            date_element = date_element.split('：')[-1]
            video_info['metadata'].append(f"放送開始: {date_element}")

        # タイムシフト視聴期限の取得
        # video_info['video_url']から動画IDの抽出
        # ~~/watch/lv348141543 の形式からlv348141543を抽出
        video_id = video_info['video_url'].split('/')[-1]
        # https://ch.nicovideo.jp/uise-iu/live/{video_id}?ref=WatchPage-ProgramPaymentInformation-PaymentActionMenu-NetTicketPurchaseOrChannelJoiningAnchor でタイムシフト視聴期限の情報を確認可能
        ts_check_url = f"https://ch.nicovideo.jp/uise-iu/live/{video_id}?ref=WatchPage-ProgramPaymentInformation-PaymentActionMenu-NetTicketPurchaseOrChannelJoiningAnchor"
        try:
            ts_response = self.session.get(ts_check_url)
            ts_response.raise_for_status()
            ts_soup = BeautifulSoup(ts_response.text, 'html.parser')
            
            # タイムシフト視聴期限の要素を探す
            timeshift_limit_element_ = ts_soup.find_all('dt', text=re.compile(r'タイムシフト視聴期限：'))
            # timeshift_limit_element_の親要素からdd要素を取得
            timeshift_limit_element = timeshift_limit_element_[0].find_next('dd')
            video_info['metadata'].append(f"タイムシフト視聴期限: {timeshift_limit_element.get_text(strip=True)}")
        except Exception as e:
            print(f"タイムシフト視聴期限の取得に失敗: {e}")
            video_info['metadata'].append('タイムシフト視聴期限: 不明')
        
        # 最低限必要な情報がある場合のみ返す
        if video_info.get('title') and video_info.get('video_url'):
            return video_info
        
        return None

    def get_all_video_info(self, base_url):
        """
        全ページから動画情報を取得
        """
        print(f"動画情報の取得を開始: {base_url}")
        
        all_videos = []
        total_pages = self.get_total_pages(base_url)
        
        print(f"総ページ数: {total_pages}")
        
        for page in range(1, total_pages + 1):
            if page == 1:
                url = base_url
            else:
                separator = '&' if '?' in base_url else '?'
                url = f"{base_url}{separator}page={page}"
            
            print(f"ページ {page}/{total_pages} を処理中: {url}")
            
            page_videos = self.extract_video_info_from_page(url)
            all_videos.extend(page_videos)
            
            print(f"ページ {page} から {len(page_videos)} 個の動画情報を取得")
            
            # レート制限対策
            time.sleep(1)
        
        return all_videos

    def save_to_json(self, video_list, filename=OUTPUT_FILE):
        """
        動画情報をJSONファイルに保存
        """
        try:
            # {"items": []} 形式で保存
            data = {"items": video_list}
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"動画情報を {filename} に保存しました")
        except Exception as e:
            print(f"ファイル保存に失敗: {e}")

def main():
    """
    メイン実行関数
    """
    # スクリプトの開始時間を記録
    start_time = datetime.now()

    print("🎬 ニコニコ動画ライブ情報取得スクリプト")
    
    extractor = NiconicoLiveVideoInfoExtractor()
    
    try:
        # 全動画情報を取得
        all_videos = extractor.get_all_video_info(CHANNEL_URL)
        
        print(f"\n合計 {len(all_videos)} 個の動画情報を取得しました")
        
        # 結果をJSONファイルに保存
        extractor.save_to_json(all_videos)
        
        # 取得した情報の一部を表示
        if all_videos:
            print("\n取得した動画情報のサンプル:")
            for i, video in enumerate(all_videos[:3]):  # 最初の3件を表示
                print(f"\n--- 動画 {i+1} ---")
                print(f"タイトル: {video.get('title', 'N/A')}")
                print(f"動画URL: {video.get('video_url', 'N/A')}")
                print(f"サムネイル: {video.get('image', 'N/A')}")
                print(f"放送開始: {video.get('broadcast_start', 'N/A')}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)

    finally:
        # スクリプトの終了時間を記録
        end_time = datetime.now()
        execution_time = end_time - start_time
        print(f"\n⏱ 実行時間: {execution_time}")
        print("🎉 処理が完了しました！")

if __name__ == "__main__":
    main()

