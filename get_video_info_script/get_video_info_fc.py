#!/usr/bin/env python3
"""
ファンサイト動画情報取得スクリプト
Webページ「https://uise-official.com/lives」を開き、一番下までスクロールした状態で
divタグ・class="infinite-scroll-component LivestreamListScreen-row2 CustomInfiniteScroll-inner"
の子要素(サムネイル)から動画情報を取得し、
docs/fciu.jsonファイルを更新します。
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
FC_PAGE_URL = "https://uise-official.com/lives"
OUTPUT_FILE = "../docs/fciu.json"

class FCVideoInfoExtractor:
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
            
            # 新しいコンテンツが読み込まれるまで待機
            time.sleep(2)
            
            # 新しいスクロール高さを取得
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # スクロール高さが変わらなければ終了
            if new_height == last_height:
                print("スクロール完了")
                break
                
            last_height = new_height

    def extract_video_info_from_element(self, element):
        """
        単一の動画要素から情報を抽出
        """
        video_info = {}
        
        try:
            # タイトルを取得（複数のセレクタを試行）
            title_selectors = [
                "h3", "h1", "h2", "h4", "h5", "h6",
                "[class*='title']", "[class*='Title']", 
                "p", "span", "div"
            ]
            
            title_found = False
            for selector in title_selectors:
                try:
                    title_elements = element.find_elements(By.CSS_SELECTOR, selector)
                    for title_elem in title_elements:
                        title_text = title_elem.text.strip()
                        if title_text and len(title_text) > 3:  # 3文字以上のテキスト
                            video_info['title'] = title_text
                            title_found = True
                            break
                    if title_found:
                        break
                except Exception:
                    continue
            
            # 動画リンクを取得
            try:
                link_element = element.find_element(By.TAG_NAME, "a")
                if link_element:
                    href = link_element.get_attribute('href')
                    if href:
                        video_info['video_url'] = href
            except Exception:
                pass
            
            # サムネイル画像を取得
            try:
                img_element = element.find_element(By.TAG_NAME, "img")
                if img_element:
                    src = img_element.get_attribute('src') or img_element.get_attribute('data-src')
                    if src:
                        video_info['image'] = src
                        
                    # alt属性も取得
                    alt = img_element.get_attribute('alt')
                    if alt:
                        video_info['alt'] = alt
            except Exception:
                pass

            # メタデータを取得（日時情報など）
            metadata = []
            
            # 日時情報を探す
            try:
                # 様々な日時表示パターンを探す
                date_selectors = [
                    "time", "[datetime]", ".date", ".time", ".datetime",
                    "[class*='date']", "[class*='time']", "[class*='Date']", "[class*='Time']",
                    "span", "div", "p"
                ]
                
                for selector in date_selectors:
                    try:
                        date_elements = element.find_elements(By.CSS_SELECTOR, selector)
                        for date_elem in date_elements:
                            # datetime属性をチェック
                            datetime_attr = date_elem.get_attribute('datetime')
                            if datetime_attr:
                                metadata.append(f"配信日時: {datetime_attr}")
                                break
                            
                            # テキストから日時らしきものを抽出
                            date_text = date_elem.text.strip()
                            if date_text and any(pattern in date_text for pattern in 
                                               ['年', '月', '日', '時', '分', '/', '-', ':', '202', '2025']):
                                if len(date_text) < 50:  # 長すぎるテキストは除外
                                    metadata.append(f"配信日時: {date_text}")
                                    break
                        if metadata:  # 日時が見つかったら終了
                            break
                    except Exception:
                        continue
            except Exception:
                pass
            
            # 再生時間を探す
            try:
                # 再生時間表示パターンを探す
                duration_selectors = [
                    "[class*='duration']", "[class*='Duration']", "[class*='time']",
                    ".length", ".runtime", "span", "div"
                ]
                
                for selector in duration_selectors:
                    try:
                        duration_elements = element.find_elements(By.CSS_SELECTOR, selector)
                        for duration_elem in duration_elements:
                            duration_text = duration_elem.text.strip()
                            # 時間らしいパターン（例: "12:34", "1:23:45", "34分"）
                            if duration_text and any(pattern in duration_text for pattern in 
                                                   [':', '分', '秒', '時間']):
                                # 短時間フォーマットかチェック
                                if len(duration_text) < 20 and any(char.isdigit() for char in duration_text):
                                    metadata.append(f"再生時間: {duration_text}")
                                    break
                        if any("再生時間" in m for m in metadata):  # 再生時間が見つかったら終了
                            break
                    except Exception:
                        continue
            except Exception:
                pass

            # 全編無料か一部無料か会員のみかを探す
            try:
                pricing_type = "-"  # デフォルト
                
                # タイトルに全編無料が含まれる場合→全編無料
                title_text = video_info.get('title', '')
                if '全編無料' in title_text:
                    pricing_type = "全編無料"
                else:
                    # 一部無料のチップを探す
                    chip_selectors = [
                        "span.MuiChip-label.MuiChip-labelMedium",
                        ".MuiChip-label", "[class*='Chip']", "[class*='chip']",
                        "span", "div", ".badge", ".tag"
                    ]
                    
                    for selector in chip_selectors:
                        try:
                            chip_elements = element.find_elements(By.CSS_SELECTOR, selector)
                            for chip_elem in chip_elements:
                                chip_text = chip_elem.text.strip()
                                if '一部無料' in chip_text:
                                    pricing_type = "一部無料"
                                    break
                            if pricing_type != "-":
                                break

                        except Exception:
                            continue
                    if pricing_type == "-":
                        # リンク先にアクセスして、全編無料のタグがあるか確認
                        pricing_type = self.check_pricing_from_video_page(video_info.get('video_url'))

                metadata.append(f"視聴条件: {pricing_type}")
                
            except Exception:
                metadata.append(f"視聴条件: {pricing_type}")

            
            if metadata:
                video_info['metadata'] = metadata
            
            # タイトルまたは動画URLがある場合のみ返す
            if video_info.get('title') or video_info.get('video_url'):
                return video_info
                
        except Exception as e:
            print(f"動画情報の抽出でエラー: {e}")
            
        return None

    def extract_all_video_info(self):
        """
        ページからすべての動画情報を抽出
        """
        print(f"ページを読み込み中: {FC_PAGE_URL}")
        
        try:
            # ページを開く
            self.driver.get(FC_PAGE_URL)
            
            # ページが読み込まれるまで待機
            time.sleep(5)
            
            # 年齢認証ダイアログの処理
            try:
                print("年齢認証ダイアログを確認中...")
                # 年齢認証のボタンを探して押す
                age_confirm_selectors = [
                    "button[aria-label*='確認']",
                    "button[aria-label*='同意']", 
                    "button[data-testid*='confirm']",
                    "button:contains('はい')",
                    "button:contains('同意')",
                    ".MuiButton-root",
                    "button[type='button']"
                ]
                
                for selector in age_confirm_selectors:
                    try:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for button in buttons:
                            button_text = button.text.strip().lower()
                            if any(keyword in button_text for keyword in ['はい', '同意', '確認', 'yes', 'confirm', 'agree']):
                                print(f"年齢認証ボタンをクリック: {button_text}")
                                button.click()
                                time.sleep(2)
                                break
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"年齢認証処理でエラー: {e}")
            
            # ローダーが消えるまで待機
            print("コンテンツの読み込み完了を待機中...")
            try:
                # ローダーが消えるまで最大30秒待機
                WebDriverWait(self.driver, 30).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='loader']"))
                )
                print("ローダーが消えました")
            except TimeoutException:
                print("ローダーの待機がタイムアウトしました。続行します。")
            
            # さらに追加の待機時間
            time.sleep(10)
            
            # 一番下までスクロール
            self.scroll_to_bottom()
            
            # ページの構造をデバッグ
            print("ページタイトル:", self.driver.title)
            print("ページURL:", self.driver.current_url)
            
            # すべてのdiv要素のクラス名を確認
            all_divs = self.driver.find_elements(By.TAG_NAME, "div")
            print(f"ページ内のdiv要素数: {len(all_divs)}")
            
            # よく使われるコンテナクラス名を探す
            potential_selectors = [
                "div.infinite-scroll-component.LivestreamListScreen-row2.CustomInfiniteScroll-inner",
                "div.infinite-scroll-component",
                "div[class*='LivestreamListScreen']",
                "div[class*='infinite-scroll']",
                "div[class*='CustomInfiniteScroll']",
                ".LivestreamListScreen-row2",
                ".CustomInfiniteScroll-inner",
                "[class*='video']",
                "[class*='stream']",
                "[class*='live']",
                "[class*='card']",
                "[class*='item']"
            ]
            
            container = None
            working_selector = None
            
            for selector in potential_selectors:
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
                print("対象コンテナが見つかりません。ページの構造をさらに詳しく調べます。")
                
                # ページの現在のHTML構造を一部表示
                try:
                    body_html = self.driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
                    # HTML構造をファイルに保存してデバッグ
                    with open("/tmp/debug_page.html", "w", encoding="utf-8") as f:
                        f.write(body_html)
                    print("ページのHTMLを /tmp/debug_page.html に保存しました")
                    
                    # HTML内で動画やライブ配信っぽいキーワードを探す
                    video_keywords = ['video', 'live', 'stream', 'thumbnail', 'title', 'card', 'item']
                    for keyword in video_keywords:
                        if keyword in body_html.lower():
                            print(f"キーワード '{keyword}' がHTML内に存在")
                except Exception as e:
                    print(f"HTMLダンプでエラー: {e}")
                
                return []
            
            print(f"対象コンテナを発見: {working_selector}")
            
            # 子要素（サムネイル）を取得
            video_elements = container.find_elements(By.XPATH, "./*")
            print(f"{len(video_elements)} 個の動画要素を発見")
            
            video_list = []
            for i, element in enumerate(video_elements):
                # 10個ごとに進捗を報告
                if i % 10 == 0:
                    print(f"\n=== 進捗: {i+1}/{len(video_elements)} 処理中 ===")
                
                video_info = self.extract_video_info_from_element(element)
                if video_info:
                    video_list.append(video_info)
                    print(f"✓ {i+1}: {video_info.get('title', 'タイトル不明')[:50]}...")
                else:
                    print(f"✗ {i+1}: 動画情報を取得できませんでした")
                
                # レート制限対策
                time.sleep(0.1)
            
            return video_list
            
        except Exception as e:
            print(f"動画情報の抽出でエラーが発生: {e}")
            import traceback
            traceback.print_exc()
            return []

    def save_to_json(self, video_list, filename=OUTPUT_FILE):
        """
        動画情報をJSONファイルに保存（{"items": []} 形式）
        """
        try:
            # ディレクトリが存在しない場合は作成
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # {"items": []} 形式で保存
            data = {"items": video_list}
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print(f"動画情報を {filename} に保存しました")
            
        except Exception as e:
            print(f"ファイル保存に失敗: {e}")

    def close(self):
        """
        WebDriverを閉じる
        """
        if hasattr(self, 'driver'):
            self.driver.quit()

    def check_pricing_from_video_page(self, video_url):
        """
        動画ページにアクセスして料金タイプを確認する
        """
        if not video_url:
            return "会員のみ"
        
        try:
            print(f"料金確認のため動画ページにアクセス中: {video_url}")
            
            # 新しいタブで動画ページを開く
            original_window = self.driver.current_window_handle
            self.driver.execute_script("window.open('');")
            new_window = [window for window in self.driver.window_handles if window != original_window][0]
            self.driver.switch_to.window(new_window)
            
            try:
                # 動画ページにアクセス
                self.driver.get(video_url)
                time.sleep(5)  # ページ読み込み待機を延長
                
                # 動画ページでも年齢認証ダイアログを処理
                try:
                    print("動画ページで年齢認証ダイアログを確認中...")
                    age_confirm_selectors = [
                        "button[aria-label*='確認']",
                        "button[aria-label*='同意']", 
                        ".MuiButton-root",
                        "button[type='button']"
                    ]
                    
                    for selector in age_confirm_selectors:
                        try:
                            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for button in buttons:
                                button_text = button.text.strip().lower()
                                if any(keyword in button_text for keyword in ['はい', '同意', '確認']):
                                    print(f"動画ページで年齢認証ボタンをクリック: {button_text}")
                                    button.click()
                                    time.sleep(3)
                                    break
                        except Exception:
                            continue
                except Exception as e:
                    print(f"動画ページの年齢認証処理でエラー: {e}")
                
                # 追加の待機時間
                time.sleep(3)
                
                # ページの構造をデバッグ出力
                print(f"動画ページURL: {self.driver.current_url}")
                
                # 全編無料のタグを探す
                wrapper = self.driver.find_element(By.ID, "video-page-wrapper")
                all_links = wrapper.find_elements(By.TAG_NAME, "a")
                # #全編無料♡が含まれるリンクがあれば全編無料
                for link in all_links:
                    if '#全編無料♡' in link.text:
                        print("全編無料のタグリンクを発見")
                        return "全編無料"

                return "会員のみ"
                # video-page-wrapper内の全aタグとspanタグを出力
                try:
                    wrapper = self.driver.find_element(By.ID, "video-page-wrapper")
                    all_links = wrapper.find_elements(By.TAG_NAME, "a")
                    all_spans = wrapper.find_elements(By.TAG_NAME, "span")
                    
                    print(f"video-page-wrapper内のaタグ数: {len(all_links)}")
                    for i, link in enumerate(all_links[:10]):  # 最初の10個のみ表示
                        print(f"  a[{i}]: '{link.text.strip()}'")
                    
                    print(f"video-page-wrapper内のspanタグ数: {len(all_spans)}")
                    for i, span in enumerate(all_spans[:20]):  # 最初の20個のみ表示
                        span_text = span.text.strip()
                        if span_text:
                            print(f"  span[{i}]: '{span_text}'")
                            
                except Exception as e:
                    print(f"要素詳細確認でエラー: {e}")
                
                # HTMLをファイルに保存
                body_html = self.driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
                timestamp = int(time.time())
                with open(f"/tmp/debug_video_page_{timestamp}.html", "w", encoding="utf-8") as f:
                    f.write(body_html)
                print(f"デバッグ用HTMLを /tmp/debug_video_page_{timestamp}.html に保存")
                
                return "会員のみ"

            finally:
                # タブを閉じて元のウィンドウに戻る
                self.driver.close()
                self.driver.switch_to.window(original_window)
                
        except Exception as e:
            print(f"動画ページの料金確認でエラー: {e}")
            return "会員のみ"  # エラー時はデフォルト

def main():
    extractor = FCVideoInfoExtractor()
    
    try:
        # 全動画情報を取得
        all_videos = extractor.extract_all_video_info()
        
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
                if video.get('metadata'):
                    print(f"メタデータ: {video['metadata']}")
                    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
        
    finally:
        extractor.close()

if __name__ == "__main__":
    main()

