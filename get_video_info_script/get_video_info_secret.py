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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys

# 設定
SECRET_PAGE_URL = "https://candfans.jp/iu_nyaa"
OUTPUT_FILE = "../docs/secret_ac.json"

class SecretVideoInfoExtractor:
    def __init__(self):
        self.setup_driver()

    def setup_driver(self):
        """
        Selenium WebDriverのセットアップ
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # ヘッドレスモード
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            # WebDriverManagerを使用してChromeDriverを自動管理
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            print(f"WebDriverの初期化に失敗: {e}")
            print("ChromeDriverManagerが使用できない場合は、手動でChromeDriverをインストールしてください")
            try:
                # フォールバック: 直接Chromeを使用
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 10)
            except Exception as e2:
                print(f"フォールバックでのWebDriver初期化も失敗: {e2}")
                sys.exit(1)

    def scroll_to_bottom(self):
        """
        ページの一番下までスクロールして、すべてのコンテンツを読み込む
        """
        print("ページの一番下までスクロール中...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # 一番下までスクロール
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 新しいコンテンツが読み込まれるまで待機（遅延読み込み対応）
            time.sleep(5)
            
            # 新しいスクロール高さを取得
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # スクロール高さが変わらなければ終了
            if new_height == last_height:
                print("スクロール完了")
                break
                
            last_height = new_height
        
        # 最後にもう一度待機して、すべての画像が読み込まれるのを待つ
        print("画像の遅延読み込み完了を待機中...")
        
        # 遅延読み込み画像を強制的にトリガー
        try:
            self.driver.execute_script("""
                // すべてのimg要素に対してスクロールイベントをトリガー
                const images = document.querySelectorAll('img');
                images.forEach(img => {
                    if (img.dataset.src || img.dataset.lazySrc || img.dataset.original) {
                        img.scrollIntoView();
                    }
                });
                
                // Intersection Observer APIが使われている場合の対応
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('resize'));
            """)
        except Exception as e:
            print(f"画像読み込みトリガーでエラー: {e}")
        
        time.sleep(10)

    def extract_post_info_from_element(self, element):
        """
        単一の投稿要素から情報を抽出
        """
        post_info = {}
        
        try:
            # 投稿のタイプを判定（動画か画像か）
            post_type = "image"  # デフォルトは画像
            
            # 動画時間があるかチェック
            duration_selectors = [
                "[class*='duration']", ".duration", "[data-duration]",
                ".time", "[class*='time']", ".video-time"
            ]
            
            for selector in duration_selectors:
                try:
                    duration_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for duration_elem in duration_elements:
                        duration_text = duration_elem.text.strip()
                        # 時間形式 (mm:ss または hh:mm:ss) をチェック
                        if duration_text and ":" in duration_text and len(duration_text) >= 4:
                            # 数字と:のみで構成されているかチェック
                            import re
                            if re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', duration_text):
                                post_type = "video"
                                post_info['duration'] = duration_text
                                break
                    if post_type == "video":
                        break
                except Exception:
                    continue
            
            # ビデオタグがあるかチェック
            try:
                video_elements = element.find_elements(By.TAG_NAME, "video")
                if video_elements:
                    post_type = "video"
            except Exception:
                pass
            
            # タイトルを取得（複数のセレクタを試行）
            title_selectors = [
                "h1", "h2", "h3", "h4", "h5", "h6",
                "[class*='title']", "[class*='Title']",
                "p", "span", "div", "a"
            ]
            
            title_found = False
            for selector in title_selectors:
                try:
                    title_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for title_elem in title_elements:
                        title_text = title_elem.text.strip()
                        if title_text and len(title_text) > 3 and len(title_text) < 200:
                            post_info['title'] = title_text
                            title_found = True
                            break
                    if title_found:
                        break
                except Exception:
                    continue
            
            # 投稿リンクを取得
            try:
                link_element = element.find_element(By.TAG_NAME, "a")
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        post_info['video_url'] = href
            except Exception:
                pass
            
            # サムネイル画像を取得
            try:
                img_elements = element.find_elements(By.TAG_NAME, "img")
                for img_element in img_elements:
                    # 複数の属性から画像URLを取得
                    src_candidates = [
                        img_element.get_attribute('src'),
                        img_element.get_attribute('data-src'),
                        img_element.get_attribute('data-lazy-src'),
                        img_element.get_attribute('data-original'),
                        img_element.get_attribute('data-url'),
                        img_element.get_attribute('srcset')  # srcsetから最初のURLを抽出
                    ]
                    
                    valid_src = None
                    for src in src_candidates:
                        if (src and 
                            'progress-circle' not in src and 
                            'loading' not in src.lower() and
                            'placeholder' not in src.lower() and
                            src.startswith(('http', '//'))):
                            # srcsetの場合は最初のURLを取得
                            if 'srcset' in str(src):
                                src = src.split(',')[0].split(' ')[0]
                            valid_src = src
                            break
                    
                    if valid_src:
                        post_info['image'] = valid_src
                        break
                        
                # alt属性も取得
                if img_elements:
                    alt = img_elements[0].get_attribute('alt')
                    if alt:
                        post_info['alt'] = alt
            except Exception:
                pass

            # メタデータを取得（閲覧回数、投稿時期など）
            metadata = []
            
            # 日時情報を探す
            date_selectors = [
                "time", ".date", ".datetime", "[datetime]",
                "[class*='date']", "[class*='time']", "[class*='publish']"
            ]
            
            # for selector in date_selectors:
            #     try:
            #         date_elements = element.find_elements(By.CSS_SELECTOR, selector)
            #         for date_elem in date_elements:
            #             date_text = date_elem.text.strip()
            #             if date_text and len(date_text) > 0:
            #                 metadata.append(f"投稿日時: {date_text}")
            #                 break
            #     except Exception:
            #         continue
            
            # 閲覧回数を探す
            view_selectors = [
                "[class*='view']", "[class*='count']", "[class*='number']"
            ]
            
            for selector in view_selectors:
                try:
                    view_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for view_elem in view_elements:
                        view_text = view_elem.text.strip()
                        if view_text and any(keyword in view_text.lower() for keyword in ['回', 'view', 'count', '万', '千']):
                            metadata.append(f"閲覧回数: {view_text}")
                            break
                except Exception:
                    continue
            
            # その他のメタデータを探す
            meta_elements = element.find_elements(By.CSS_SELECTOR, "span, div, p")
            for meta_elem in meta_elements[:5]:
                meta_text = meta_elem.text.strip()
                if (meta_text and 
                    len(meta_text) < 100 and 
                    meta_text not in [post_info.get('title', '')] and
                    meta_text not in metadata):
                    metadata.append(meta_text)
                if len(metadata) >= 5:
                    break
            
            if metadata:
                post_info['metadata'] = metadata
            
            # 投稿タイプを設定
            post_info['type'] = post_type
            
            # タイトルまたは投稿URLがある場合のみ返す
            if post_info.get('title') or post_info.get('video_url'):
                return post_info
                
        except Exception as e:
            print(f"投稿情報の抽出でエラー: {e}")
            
        return None

    def extract_all_post_info(self):
        """
        ページからすべての投稿情報を抽出
        """
        print(f"ページを読み込み中: {SECRET_PAGE_URL}")
        
        try:
            # ページを開く
            self.driver.get(SECRET_PAGE_URL)
            
            # ページが読み込まれるまで待機
            time.sleep(5)
            
            # 年齢認証やログインが必要な場合の処理
            try:
                print("ページの初期処理を確認中...")
                
                # 年齢認証、同意ボタンなどを探して押す
                consent_selectors = [
                    "button[aria-label*='確認']",
                    "button[aria-label*='同意']", 
                    "button[data-testid*='confirm']",
                    "button:contains('はい')",
                    "button:contains('同意')",
                    "button:contains('確認')",
                    "button:contains('OK')",
                    ".btn", ".button",
                    "input[type='submit']"
                ]
                
                for selector in consent_selectors:
                    try:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in buttons:
                            button_text = button.text.strip().lower()
                            if any(keyword in button_text for keyword in ['はい', '同意', '確認', 'yes', 'confirm', 'agree', 'ok']):
                                print(f"同意ボタンをクリック: {button_text}")
                                button.click()
                                time.sleep(2)
                                break
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"初期処理でエラー: {e}")
            
            # コンテンツの読み込み完了を待機
            time.sleep(10)
            
            # 一番下までスクロール
            self.scroll_to_bottom()
            
            # ページの構造をデバッグ
            print("ページタイトル:", self.driver.title)
            print("ページURL:", self.driver.current_url)
            
            # 対象のコンテナを探す
            container_selectors = [
                "div.grid.grid-cols-2.gap-x-1.gap-y-3.pt-2.items-end",
                ".grid.grid-cols-2",
                ".grid-cols-2",
                "[class*='grid']",
                "[class*='cols-2']"
            ]
            
            container = None
            working_selector = None
            
            for selector in container_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"セレクタ '{selector}' で {len(elements)} 個の要素を発見")
                        # 子要素があるかチェック
                        for element in elements:
                            children = element.find_elements(By.XPATH, "./*")
                            if len(children) > 0:
                                print(f"子要素 {len(children)} 個を持つコンテナを発見")
                                container = element
                                working_selector = selector
                                break
                        if container:
                            break
                except Exception as e:
                    print(f"セレクタ '{selector}' でエラー: {e}")
            
            if container is None:
                print("対象コンテナが見つかりません。ページの構造を確認します。")
                
                # すべてのdiv要素を確認
                all_divs = self.driver.find_elements(By.TAG_NAME, "div")
                print(f"ページ内のdiv要素数: {len(all_divs)}")
                
                # grid関連のクラスを持つ要素を探す
                grid_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='grid']")
                print(f"grid関連の要素数: {len(grid_elements)}")
                
                if grid_elements:
                    print("grid要素のクラス名をチェック中...")
                    for i, grid_elem in enumerate(grid_elements[:5]):
                        class_name = grid_elem.get_attribute('class')
                        children_count = len(grid_elem.find_elements(By.XPATH, "./*"))
                        print(f"Grid要素 {i+1}: class='{class_name}', 子要素={children_count}個")
                        
                        if children_count > 0:
                            container = grid_elem
                            working_selector = f"grid要素{i+1}"
                            break
                
                if container is None:
                    return []
            
            print(f"対象コンテナを発見: {working_selector}")
            
            # 子要素（投稿）を取得
            post_elements = container.find_elements(By.XPATH, "./*")
            print(f"{len(post_elements)} 個の投稿要素を発見")
            
            post_list = []
            for i, element in enumerate(post_elements):
                # 10個ごとに進捗を報告
                if i % 10 == 0:
                    print(f"\n=== 進捗: {i+1}/{len(post_elements)} 処理中 ===")
                
                post_info = self.extract_post_info_from_element(element)
                if post_info:
                    post_list.append(post_info)
                    post_type = post_info.get('type', 'unknown')
                    title = post_info.get('title', 'タイトル不明')[:50]
                    print(f"✓ {i+1}: [{post_type}] {title}...")
                else:
                    print(f"✗ {i+1}: 投稿情報を取得できませんでした")
                
                # レート制限対策
                time.sleep(0.1)
            
            return post_list
            
        except Exception as e:
            print(f"投稿情報の抽出でエラーが発生: {e}")
            import traceback
            traceback.print_exc()
            return []

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

    def close(self):
        """
        WebDriverを閉じる
        """
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    extractor = SecretVideoInfoExtractor()
    
    try:
        # 全投稿情報を取得
        all_posts = extractor.extract_all_post_info()
        
        print(f"\n合計 {len(all_posts)} 個の投稿情報を取得しました")
        
        # 結果をJSONファイルに保存
        extractor.save_to_json(all_posts)
        
        # 取得した情報の一部を表示
        if all_posts:
            print("\n取得した投稿情報のサンプル:")
            
            # 動画と画像の数をカウント
            video_count = len([p for p in all_posts if p.get('type') == 'video'])
            image_count = len([p for p in all_posts if p.get('type') == 'image'])
            print(f"動画: {video_count}個, 画像: {image_count}個")
            
            # ローディングSVG問題のチェック
            loading_count = len([p for p in all_posts if p.get('image', '').find('progress-circle') != -1])
            if loading_count > 0:
                print(f"⚠️ 警告: {loading_count}個の投稿でローディングSVGが検出されました")
            
            for i, post in enumerate(all_posts[:3]):  # 最初の3件を表示
                print(f"\n--- 投稿 {i+1} [{post.get('type', 'unknown')}] ---")
                print(f"タイトル: {post.get('title', 'N/A')}")
                print(f"投稿URL: {post.get('post_url', 'N/A')}")
                print(f"サムネイル: {post.get('image', 'N/A')}")
                if post.get('duration'):
                    print(f"動画時間: {post['duration']}")
                if post.get('metadata'):
                    print(f"メタデータ: {post['metadata'][:2]}")  # 最初の2つのみ表示
                    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
        
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
