import requests
import json

# URL
# url = "https://api.uise-official.com/fc/fanclub_sites/434/live_pages?page=1&live_type=1&per_page=10" # 配信中 or 配信予定
# url = "https://api.uise-official.com/fc/fanclub_sites/434/live_pages?page=1&live_type=2&per_page=10" # 配信中 or 配信予定
url = "https://api.uise-official.com/fc/fanclub_sites/434/live_pages?page=1&live_type=3&per_page=10" # 過去の配信
# url = "https://api.uise-official.com/fc/fanclub_sites/434/live_pages?page=1&live_type=4&per_page=10" # 過去の配信 古い順
# url = "https://api.uise-official.com/fc/video_pages/smjsfppgLfY293jfTVFBfNso"

# ヘッダー情報
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    # "accept-language": "ja",
    # "cookie": "_ga=GA1.1.1077262162.1754839672; _ga_Q1PGB3XV3B=GS2.1.s1754839671$o1$g1$t1754839744$j48$l0$h0",
    "fc_site_id": "434", # add video single 
    "fc_use_device": "null",
    # "origin": "https://uise-official.com",
    # "referer": "https://uise-official.com/",
    # "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
    # "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
    # "sec-fetch-dest": "empty",
    # "sec-fetch-mode": "cors",
    # "sec-fetch-site": "same-site",
    # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"
}

# GETリクエストを送信
response = requests.get(url, headers=headers)

# レスポンスの確認
if response.status_code == 200:
    print("リクエスト成功!")
    # 保存
    with open('live_pages.json', 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)
    print("データをlive_pages.jsonに保存しました。")
else:
    print(f"リクエスト失敗: ステータスコード {response.status_code}")