# YouTube動画情報取得スクリプト

このスクリプトは、yt-dlpを使用してYouTubeチャンネル「@uise_iu_asmr」から動画情報を取得し、`../design_layout_mock/youtube.json`ファイルを自動更新します。

## セットアップ

### 1. 必要なパッケージのインストール

```bash
cd get_video_info_script
pip install -r requirements.txt
```

または個別にインストール：

```bash
pip install yt-dlp requests
```

### 2. スクリプトの実行

```bash
python get_video_info_youtube.py
```

## 機能

- YouTubeチャンネル「@uise_iu_asmr」からすべての動画情報を取得
- 各動画の以下の情報を収集：
  - タイトル
  - サムネイル画像URL
  - 動画ID
  - 動画URL
  - 説明文（最初の100文字）
  - 再生時間
  - 視聴回数
  - 投稿日
- JSONファイル形式で保存

## 出力ファイル

- **場所**: `../design_layout_mock/youtube.json`
- **形式**: JSON
- **構造**:
```json
{
  "items": [
    {
      "title": "動画タイトル",
      "image": "サムネイルURL",
      "alt": "動画タイトル",
      "description": "動画説明...",
      "videoId": "動画ID",
      "video_url": "https://www.youtube.com/watch?v=動画ID",
      "metadata": [
        "再生時間: 3:45",
        "視聴回数: 1.2K回",
        "投稿日: 2024/01/15"
      ]
    }
  ],
  "last_updated": "2025-07-06T12:00:00",
  "total_videos": 50
}
```

## 設定

スクリプト内の以下の設定を変更できます：

- `CHANNEL_URL`: 対象のYouTubeチャンネルURL
- `OUTPUT_FILE`: 出力ファイルのパス
- `MAX_VIDEOS`: 取得する最大動画数（デフォルト: 50）

## トラブルシューティング

### yt-dlpがインストールされていない場合

```bash
pip install yt-dlp
```

### チャンネルが見つからない場合

- チャンネルURLが正しいか確認
- チャンネルが公開されているか確認
- インターネット接続を確認

### 動画の取得に失敗する場合

- 一部の動画が限定公開や削除されている可能性があります
- スクリプトはエラーをスキップして続行します

## 注意事項

- YouTube APIの利用規約に従って使用してください
- 大量のリクエストを避けるため、適切な間隔で実行してください
- 取得した情報は個人利用に留めてください
