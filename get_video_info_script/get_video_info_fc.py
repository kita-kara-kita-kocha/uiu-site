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
from datetime import datetime, timedelta
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
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            
        Returns:
            dict: 動画情報辞書（title, video_url, image, alt, metadata）
                  情報が取得できない場合はNone
        """
        video_info = {}
        
        try:
            # 各種情報を順次取得
            video_info.update(self._extract_title(element))
            video_info.update(self._extract_video_link(element))
            video_info.update(self._extract_thumbnail(element))
            video_info.update(self._extract_date_info(element))

            
            # メタデータを取得
            metadata = []
            metadata.append(self._extract_date_time_info(element))
            metadata.append(self._extract_duration_info(element))
            metadata.append(self._extract_pricing_info(element, video_info))

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
        
        Returns:
            list: 取得した全動画情報のリスト
        """
        print(f"ページを読み込み中: {FC_PAGE_URL}")
        
        try:
            # ページの初期化と読み込み
            self._load_page()
            
            # 対象コンテナの検出
            container = self._find_video_container()
            if container is None:
                return []
            
            # 動画要素の取得と情報抽出
            return self._extract_videos_from_container(container)
            
        except Exception as e:
            print(f"動画情報の抽出でエラーが発生: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _load_page(self):
        """
        ページを読み込み、必要な初期化処理を実行
        """
        # ページを開く
        self.driver.get(FC_PAGE_URL)
        
        # ページが読み込まれるまで待機
        time.sleep(5)
        
        # 年齢認証ダイアログの処理
        self._handle_age_confirmation()
        
        # コンテンツローダーの完了待機
        self._wait_for_content_loading()
        
        # 一番下までスクロール
        self.scroll_to_bottom()

    def _handle_age_confirmation(self):
        """
        年齢認証ダイアログの処理
        """
        try:
            print("年齢認証ダイアログを確認中...")
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
                            return
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"年齢認証処理でエラー: {e}")

    def _wait_for_content_loading(self):
        """
        コンテンツローダーの完了を待機
        """
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

    def _find_video_container(self):
        """
        動画コンテナ要素を検出
        
        Returns:
            WebElement: 動画コンテナ要素、見つからない場合はNone
        """
        print("動画コンテナを検索中...")
        
        # ページの構造をデバッグ
        self._debug_page_structure()
        
        # 潜在的なセレクタのリスト
        potential_selectors = [
            # "div.find_elements.LivestreamListScreen-row2.CustomInfiniteScroll-inner",
            "div.infinite-scroll-component",
            "dev.MuiPaper-root"
            # "div[class*='LivestreamListScreen']",
            # "div[class*='infinite-scroll']",
            # "div[class*='CustomInfiniteScroll']",
            # ".LivestreamListScreen-row2",
            # ".CustomInfiniteScroll-inner",
            # "[class*='video']",
            # "[class*='stream']",
            # "[class*='live']",
            # "[class*='card']",
            # "[class*='item']"
        ]
        
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
                            return element
            except Exception as e:
                print(f"セレクタ '{selector}' でエラー: {e}")
        
        print("対象コンテナが見つかりません")
        return None

    def _debug_page_structure(self):
        """
        ページ構造のデバッグ情報を出力
        """
        print("ページタイトル:", self.driver.title)
        print("ページURL:", self.driver.current_url)
        
        # すべてのdiv要素のクラス名を確認
        all_divs = self.driver.find_elements(By.TAG_NAME, "div")
        print(f"ページ内のdiv要素数: {len(all_divs)}")
        
        # ページの現在のHTML構造を一部保存（デバッグ用）
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

    def _extract_videos_from_container(self, container):
        """
        コンテナから動画情報を抽出
        
        Args:
            container: WebElement - 動画コンテナ要素
            
        Returns:
            list: 取得した動画情報のリスト
        """
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

    def save_to_json(self, video_list, filename=OUTPUT_FILE):
        """
        動画情報をJSONファイルに保存（{"items": []} 形式）
        
        Args:
            video_list: list - 保存する動画情報のリスト
            filename: str - 保存先ファイルパス
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
        動画ページにアクセスして料金タイプを確認
        
        Args:
            video_url: str - 確認する動画のURL
            
        Returns:
            str: 料金タイプ（"全編無料"、"一部無料"、"会員のみ"）
        """
        if not video_url:
            return "会員のみ"
        
        try:
            print(f"料金確認のため動画ページにアクセス中: {video_url}")
            
            # 新しいタブを開いて動画ページを確認
            return self._check_pricing_in_new_tab(video_url)
                
        except Exception as e:
            print(f"動画ページの料金確認でエラー: {e}")
            return "会員のみ"  # エラー時はデフォルト

    def _check_pricing_in_new_tab(self, video_url):
        """
        新しいタブで動画ページの料金情報を確認
        
        Args:
            video_url: str - 確認する動画のURL
            
        Returns:
            str: 料金タイプ
        """
        # 新しいタブで動画ページを開く
        original_window = self.driver.current_window_handle
        self.driver.execute_script("window.open('');")
        new_window = [window for window in self.driver.window_handles if window != original_window][0]
        self.driver.switch_to.window(new_window)
        
        try:
            # 動画ページにアクセス
            self.driver.get(video_url)
            time.sleep(5)  # ページ読み込み待機
            
            # 動画ページでも年齢認証ダイアログを処理
            self._handle_video_page_age_confirmation()
            
            # 追加の待機時間
            time.sleep(3)
            
            # 料金タイプを判定
            return self._determine_pricing_type()
            
        finally:
            # タブを閉じて元のウィンドウに戻る
            self.driver.close()
            self.driver.switch_to.window(original_window)

    def _handle_video_page_age_confirmation(self):
        """
        動画ページでの年齢認証ダイアログ処理
        """
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
                            return
                except Exception:
                    continue
        except Exception as e:
            print(f"動画ページの年齢認証処理でエラー: {e}")

    def _determine_pricing_type(self):
        """
        動画ページから料金タイプを判定
        
        Returns:
            str: 料金タイプ
        """
        print(f"動画ページURL: {self.driver.current_url}")
        
        try:
            # 全編無料のタグを探す
            wrapper = self.driver.find_element(By.ID, "video-page-wrapper")
            all_links = wrapper.find_elements(By.TAG_NAME, "a")
            
            # #全編無料♡が含まれるリンクがあれば全編無料
            for link in all_links:
                if '#全編無料♡' in link.text:
                    print("全編無料のタグリンクを発見")
                    return "全編無料"
            
            return "会員のみ"
            
        except Exception as e:
            print(f"料金タイプ判定でエラー: {e}")
            return "会員のみ"

    def _extract_title(self, element):
        """
        動画要素からタイトル情報を抽出
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            
        Returns:
            dict: タイトル情報を含む辞書
        """
        title_info = {}
        title_selectors = [
            "h3", "h1", "h2", "h4", "h5", "h6",
            "[class*='title']", "[class*='Title']", 
            "p", "span", "div"
        ]
        
        for selector in title_selectors:
            try:
                title_elements = element.find_elements(By.CSS_SELECTOR, selector)
                for title_elem in title_elements:
                    title_text = title_elem.text.strip()
                    if title_text and len(title_text) > 3:  # 3文字以上のテキスト
                        title_info['title'] = title_text
                        return title_info
            except Exception:
                continue
        
        return title_info

    def _extract_video_link(self, element):
        """
        動画要素から動画リンクを抽出
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            
        Returns:
            dict: 動画URL情報を含む辞書
        """
        link_info = {}
        try:
            link_element = element.find_element(By.TAG_NAME, "a")
            if link_element:
                href = link_element.get_attribute('href')
                if href:
                    link_info['video_url'] = href
        except Exception:
            pass
        
        return link_info

    def _extract_thumbnail(self, element):
        """
        動画要素からサムネイル画像情報を抽出
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            
        Returns:
            dict: サムネイル情報を含む辞書（image, alt）
        """
        thumbnail_info = {}
        try:
            img_element = element.find_element(By.TAG_NAME, "img")
            if img_element:
                src = img_element.get_attribute('src') or img_element.get_attribute('data-src')
                if src:
                    thumbnail_info['image'] = src
                    
                # alt属性も取得
                alt = img_element.get_attribute('alt')
                if alt:
                    thumbnail_info['alt'] = alt
        except Exception:
            pass
        
        return thumbnail_info
    
    def _adjust_date(self, date_str, days=0):
        """
        日付文字列を調整（1日前にするなど）
        
        Args:
            date_str: str - 日付文字列
            days: int - 調整する日数（デフォルトは0）
            
        Returns:
            str: 調整後の日付文字列
        """
        
        try:
            # 日付のパース
            date_obj = datetime.strptime(date_str, "%Y/%m/%d")
            adjusted_date = date_obj + timedelta(days=days)
            return adjusted_date.strftime("%Y/%m/%d")
        except ValueError:
            print(f"日付のパースに失敗: {date_str}")
            return date_str
    
    def _extract_date_info(self, element, title=None):
        """
        動画要素から配信日時情報を抽出
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            title: str - 動画タイトル（オプション）

        Returns:
            dict: 配信日時情報 yyyy/mm/dd を含む辞書
        """
        date_info = {}
        date_selectors = [
            "time", "[datetime]", ".date", ".time", ".datetime",
            "[class*='date']", "[class*='time']", "[class*='Date']", "[class*='Time']",
            "span", "div", "p"
        ]
        for selector in date_selectors:
            try:
                date_elements = element.find_elements(By.CSS_SELECTOR, selector)
                for date_elem in date_elements:
                    # テキストから日時らしきものを抽出
                    date_info['upload_date'] = date_elem.text.strip()
                    if date_info['upload_date'] and any(pattern in date_info['upload_date'] for pattern in 
                                       ['年', '月', '日', '時', '分', '/', '-', ':']):
                        if len(date_info['upload_date']) < 50:  # 長すぎるテキストは除外
                            # タイトルに「~スマホ~お風呂~」,「False」が含まれる場合はそのままreturn
                            if title and (('スマホ' in title and 'お風呂' in title) or False):
                                return date_info
                            # date_info['upload_date']を1日前にする
                            date_info['upload_date'] = self._adjust_date(date_info['upload_date'], days=-1)
                            return date_info
            except Exception:
                continue
        # 日時情報が見つからない場合は空の辞書を返す
        return date_info


    def _extract_date_time_info(self, element, title=None):
        """
        動画要素から配信日時情報を抽出
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            title: str - 動画タイトル（オプション）

        Returns:
            str: 配信日時情報
        """
        try:
            date = self._extract_date_info(element, title).get("upload_date", None)
            return f"配信日時: {date}" if date else ""
        except Exception as e:
            print(f"配信日時情報の抽出でエラー: {e}")
            return ""

    def _extract_duration_info(self, element):
        """
        動画要素から再生時間情報を抽出
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            
        Returns:
            str: 再生時間情報
        """
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
                            return f"再生時間: {duration_text}"

            except Exception:
                continue
        
        return ""

    def _extract_pricing_info(self, element, video_info):
        """
        動画要素から視聴条件（料金タイプ）情報を抽出
        
        Args:
            element: Selenium WebElement - 動画要素のDOM要素
            video_info: dict - 既に取得済みの動画情報
            
        Returns:
            list: 視聴条件情報のリスト
        """
        pricing_type = "-"  # デフォルト
        
        try:
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

            return f"視聴条件: {pricing_type}"

        except Exception:
            return f"視聴条件: {pricing_type}"

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
        all_videos = _extract_and_display_progress(extractor)
        
        # 結果をJSONファイルに保存
        extractor.save_to_json(all_videos)
        
        # 取得した情報の一部を表示
        _display_sample_results(all_videos)
                    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)
        
    finally:
        # WebDriverを閉じる
        extractor.close()
        # 実行時間の表示
        _display_execution_summary(start_time)

def _extract_and_display_progress(extractor):
    """
    動画情報を取得し、進捗を表示
    
    Args:
        extractor: FCVideoInfoExtractor - 動画情報抽出器
        
    Returns:
        list: 取得した動画情報のリスト
    """
    all_videos = extractor.extract_all_video_info()
    print(f"\n合計 {len(all_videos)} 個の動画情報を取得しました")
    return all_videos

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
            print(f"alt: {video.get('upload_date', 'N/A')}")
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

