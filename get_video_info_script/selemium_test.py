
from datetime import datetime
from datetime import timedelta
from pathlib import Path
import time
import os
import json
import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

def get_login_cookies(email: str, password: str) -> dict:
    """
    ログインクッキーを取得する関数
    
    Args:
        email (str): ログイン用メールアドレス
        password (str): ログイン用パスワード
    
    Returns:
        dict: クッキーの辞書
    """
    options = Options()
    # ヘッドレスモードを無効化（ログインには視覚的な確認が必要な場合がある）
    # options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    wait = WebDriverWait(driver, 20)
    
    try:
        print("YouTubeにアクセス中...")
        driver.get("https://www.youtube.com/")
        time.sleep(3)
        
        # ログインボタンを見つける（複数のパターンを試す）
        login_selector = "//a[contains(@href, 'accounts.google.com')]"
        
        login_button = None
        try:
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_selector)))
            # ログインボタンをクリック
            driver.execute_script("arguments[0].click();", login_button)
            print("ログインボタンをクリックしました")
        except TimeoutException:
            print(f"ログインボタンが見つかりませんでした。セレクター: {login_selector}")
            print(f"現在のURL: {driver.current_url}")
            page_source = driver.page_source[:1000]
            print(f"ページソース（最初の1000文字）:\n{page_source}")
            raise Exception("ログインボタンが見つかりませんでした")
        
        # Googleのログインページに移動するまで待機
        wait.until(lambda driver: "accounts.google.com" in driver.current_url)
        print("Googleログインページに移動しました")
        
        # メールアドレスを入力して次へをクリック
        try:
            email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
            email_input.clear()
            email_input.send_keys(email)
            print("メールアドレスを入力しました")
            
            # 次へボタンをクリック
            next_button = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
            next_button.click()
            print("次へボタンをクリックしました")
        except TimeoutException as e:
            print(f"メールアドレス入力でタイムアウト: {e}")
            print(f"現在のURL: {driver.current_url}")
            page_source = driver.page_source[:1000]
            print(f"ページソース（最初の1000文字）:\n{page_source}")
            raise Exception("メールアドレスの入力に失敗しました")
        
        # パスワード入力ページ移動するまで待機
        time.sleep(5)  # ページ読み込み待機
        wait.until(lambda driver: "accounts.google.com" in driver.current_url and "pwd" in driver.current_url)
        print("パスワード入力ページに移動しました")
        
        try:
            # パスワードフィールドを検索
            password_input = None
            password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
            print("パスワード入力フィールドを見つけました")

            # ActionChainsでパスワードを入力
            actions = ActionChains(driver)
            actions.click(password_input).pause(0.5).send_keys(password).perform()
            print("パスワードを入力しました")
            time.sleep(2)
            
            # 次へボタンをクリック
            next_button_selectors = [
                (By.ID, "passwordNext"),
                (By.CSS_SELECTOR, "#passwordNext"),
                (By.XPATH, "//button[@id='passwordNext']"),
                (By.XPATH, "//button[contains(text(), '次へ')]"),
                (By.XPATH, "//div[@role='button' and contains(@jsname, 'passwordNext')]"),
                (By.XPATH, "//span[contains(text(), 'Next')]/parent::button"),
                (By.XPATH, "//button[@type='button']"),
            ]
            
            password_next = None
            for selector_type, selector_value in next_button_selectors:
                try:
                    password_next = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                    print(f"次へボタンを見つけました: {selector_type} = {selector_value}")
                    break
                except TimeoutException:
                    continue
            
            if password_next is None:
                raise Exception("次へボタンが見つかりません")
            
            driver.execute_script("arguments[0].click();", password_next)
            print("次へボタンをクリックしました")

        except TimeoutException as e:
            print(f"パスワード入力でタイムアウト: {e}")
            print(f"現在のURL: {driver.current_url}")
            page_source = driver.page_source[:1000]
            print(f"ページソース（最初の1000文字）:\n{page_source}")
            raise Exception("パスワードの入力に失敗しました")
            
        # YouTubeに戻るまで待機
        wait.until(lambda driver: "youtube.com" in driver.current_url)
        print("YouTubeに戻りました")
        time.sleep(3)
                    
        # クッキーを取得
        cookies = driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        print(f"クッキーを取得しました: {len(cookie_dict)}個")
        return cookie_dict
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print(f"現在のURL: {driver.current_url}")
        # デバッグ用にページのソースを部分的に表示
        try:
            page_source = driver.page_source[:1000]
            print(f"ページソース（最初の1000文字）:\n{page_source}")
        except:
            pass
        return {}
    finally:
        driver.quit()

def main():
    """
    メイン関数：環境変数または入力からクレデンシャルを取得してログインクッキーを取得
    """
    print("YouTube ログインクッキー取得ツール")
    print("=" * 40)
    
    # 環境変数からクレデンシャルを取得を試す
    email = os.getenv('YOUTUBE_EMAIL')
    password = os.getenv('YOUTUBE_PASSWORD')
    
    # 環境変数が設定されていない場合は入力を求める
    if not email:
        email = input("YouTubeログイン用メールアドレスを入力してください: ").strip()
    if not password:
        password = getpass.getpass("パスワードを入力してください: ")
    
    if not email or not password:
        print("メールアドレスとパスワードが必要です。")
        return
    
    print(f"\nメールアドレス: {email}")
    print("ログイン処理を開始します...\n")
    
    try:
        cookies = get_login_cookies(email, password)
        if cookies:
            print(f"\n✅ 成功! {len(cookies)}個のクッキーを取得しました")
            
            # クッキーをファイルに保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cookies_file = f"youtube_cookies_{timestamp}.json"
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"クッキーを保存しました: {cookies_file}")
            
            # 主要なクッキーを表示
            important_cookies = ['SAPISID', 'SSID', 'HSID', 'SID', 'APISID']
            print("\n📋 主要なクッキー:")
            for cookie_name in important_cookies:
                if cookie_name in cookies:
                    value = cookies[cookie_name]
                    display_value = value[:20] + "..." if len(value) > 20 else value
                    print(f"  {cookie_name}: {display_value}")
        else:
            print("\n❌ クッキーの取得に失敗しました")
    except KeyboardInterrupt:
        print("\n\n⚠️  処理が中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()