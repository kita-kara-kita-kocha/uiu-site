# 動画情報取得スクリプト集

このディレクトリには、複数のプラットフォームから動画情報を取得するスクリプトが含まれています。以下の4つのスクリプトが利用可能です：

1. **get_video_info_youtube.py** - YouTubeチャンネル「@uise_iu_asmr」から動画情報を取得
2. **get_video_info_niconico_live.py** - ニコニコ動画チャンネルのライブ動画情報を取得  
3. **get_video_info_secret.py** - [ファンサイト（candfans.jp）](https://candfans.jp/iu_nyaa)から投稿情報を取得
4. **get_video_info_fc.py** - [ファンクラブサイト（uise-official.com）](https://uise-official.com/lives)から動画情報を取得

## セットアップ

### 1. 必要なパッケージのインストール

```bash
cd get_video_info_script
pip install -r requirements.txt
```

または個別にインストール：

```bash
pip install yt-dlp requests beautifulsoup4 lxml selenium webdriver-manager
```

### 2. スクリプトの実行

#### 一括実行（推奨）
すべてのスクリプトを順次実行し、実行後に自動的にGitコミット&プッシュを実行：
```bash
bash run.sh
```

この一括実行スクリプトでは、以下の処理を順次実行します：
1. すべての動画情報取得スクリプトを実行
2. 更新されたJSONファイルをGitにコミット
3. リモートリポジトリにプッシュ

**注意**: Gitリポジトリ内で実行する必要があります。リポジトリ外で実行した場合は、コミット&プッシュ処理はスキップされます。

#### 個別実行
特定のスクリプトのみ実行：
```bash
# YouTube動画情報取得
python get_video_info_youtube.py

# ニコニコ動画ライブ情報取得
python get_video_info_niconico_live.py

# ファンサイト投稿情報取得
python get_video_info_secret.py

# ファンクラブ動画情報取得
python get_video_info_fc.py
```

#### スケジュール実行（6時間ごと）
自動的に6時間ごとにスクリプトを実行するよう設定：
```bash
# Cronジョブの設定
bash setup_cron.sh

# Cronジョブの削除（停止）
bash remove_cron.sh
```

**実行タイミング**: 毎日 00:00、06:00、12:00、18:00 に自動実行
**ログファイル**: `logs/cron_execution.log` に実行ログが記録されます

## 機能

### 1. YouTube動画情報取得 (get_video_info_youtube.py)
- YouTubeチャンネル「@uise_iu_asmr」からすべての動画情報を取得
- 出力ファイル: `../docs/youtube.json`
- 取得情報: タイトル、サムネイル、動画ID、URL、説明文、再生時間、視聴回数、投稿日

### 2. ニコニコ動画ライブ情報取得 (get_video_info_niconico_live.py)
- ニコニコ動画チャンネルのライブ動画情報を取得
- 出力ファイル: `../docs/niconico_l.json`
- 取得情報: タイトル、サムネイル、動画URL、投稿日時、視聴回数

### 3. ファンサイト投稿情報取得 (get_video_info_secret.py)
- candfans.jpサイトから投稿情報を取得
- 出力ファイル: `../docs/secret_ac.json`
- 取得情報: 記事タイトル、記事URL、サムネイル、メタ情報（閲覧回数、投稿時期、動画時間）

### 4. ファンクラブ動画情報取得 (get_video_info_fc.py)
- uise-official.comサイトから動画情報を取得
- 出力ファイル: `../docs/fciu.json`
- 取得情報: タイトル、動画URL、サムネイル、配信日時、視聴条件

## 出力ファイル

すべてのスクリプトは `../docs/` ディレクトリにJSONファイルを生成します：

- **../docs/youtube.json** - YouTube動画情報
- **../docs/niconico_l.json** - ニコニコ動画ライブ情報  
- **../docs/secret_ac.json** - ファンサイト投稿情報
- **../docs/fciu.json** - ファンクラブ動画情報

### JSONファイル構造
すべてのファイルは以下の基本構造を持ちます：
```json
{
  "items": [
    {
      "title": "動画/投稿タイトル",
      "image": "サムネイルURL",
      "alt": "動画タイトル",
      "description": "動画説明...",
      "video_url": "動画URL",
      "metadata": [
        "再生時間: 3:45",
        "視聴回数: 1.2K回",
        "投稿日: 2024/01/15"
      ]
    }
  ],
  "last_updated": "2025-07-09T12:00:00",
  "total_items": 50
}
```

## 設定

各スクリプトの設定は以下の通りです：

### YouTube (get_video_info_youtube.py)
- `CHANNEL_URL`: 対象のYouTubeチャンネルURL
- `OUTPUT_FILE`: 出力ファイルのパス

### ニコニコ動画 (get_video_info_niconico_live.py)
- `CHANNEL_URL`: 対象のニコニコ動画チャンネルURL
- `OUTPUT_FILE`: 出力ファイルのパス

### ファンサイト (get_video_info_secret.py)
- `SECRET_PAGE_URL`: 対象のファンサイトURL
- `OUTPUT_FILE`: 出力ファイルのパス

### ファンクラブ (get_video_info_fc.py)
- `FC_PAGE_URL`: 対象のファンクラブサイトURL
- `OUTPUT_FILE`: 出力ファイルのパス

## トラブルシューティング

### 依存関係のインストールに関する問題

#### ChromeDriverに関する問題
- ChromeDriverはwebdriver-managerにより自動的にダウンロードされます
- 手動でChromeDriverをインストールする必要はありません

### ネットワーク関連の問題

#### チャンネルが見つからない場合
- チャンネルURLが正しいか確認
- チャンネルが公開されているか確認
- インターネット接続を確認

#### 動画の取得に失敗する場合
- 一部の動画が限定公開や削除されている可能性があります
- スクリプトはエラーをスキップして続行します

### Selenium関連の問題

#### ヘッドレスモードで実行されない場合
- 年齢認証ダイアログが表示される場合があります
- スクリプトは自動的に認証を試行します

#### ページの読み込みが遅い場合
- 待機時間を調整してください
- ネットワーク環境によって実行時間が異なります

## 注意事項

- 各プラットフォームの利用規約に従って使用してください
- 大量のリクエストを避けるため、適切な間隔で実行してください
- 取得した情報は個人利用に留めてください
- 一部のサイトでは年齢認証が必要な場合があります
- ヘッドレスモードで実行されるため、ブラウザウィンドウは表示されません

## 実行時間の目安

- YouTube: 3分程度
- ニコニコ動画ライブ: 1分程度  
- 裏垢サイト: 1分程度
- ファンクラブ: 2分程度
- Gitコミット&プッシュ: 30秒程度

合計実行時間: 約8分程度

## スケジュール実行設定

### Cronジョブの設定
6時間ごと（00:00、06:00、12:00、18:00）に自動実行するよう設定できます：

#### 設定手順
1. **Cronジョブの設定**
   ```bash
   bash setup_cron.sh
   ```

2. **設定の確認**
   ```bash
   crontab -l
   ```

3. **ログの確認**
   ```bash
   tail -f logs/cron_execution.log
   ```

#### 停止手順
```bash
bash remove_cron.sh
```

### 実行スケジュール
- **毎日 00:00** (午前0時) - 深夜実行
- **毎日 06:00** (午前6時) - 朝実行
- **毎日 12:00** (午後12時) - 昼実行
- **毎日 18:00** (午後6時) - 夕方実行

### ログファイル
- **場所**: `logs/cron_execution.log`
- **内容**: 実行ログ、エラーログ、完了通知
- **ローテーション**: 手動でログファイルを管理してください

### 注意点
- Cronサービスが動作している必要があります
- 実行時間が長い場合、次の実行時間と重複する可能性があります
- ログファイルは定期的に確認・管理してください

## Git 自動コミット&プッシュ機能

`bash run.sh` で一括実行する場合、スクリプト実行後に以下の処理が自動的に実行されます：

1. **変更の確認**: 動画情報JSONファイルに変更があるかチェック
2. **ステージング**: 更新されたJSONファイルをステージングに追加
3. **コミット**: 現在日時付きのコミットメッセージで自動コミット
4. **プッシュ**: リモートリポジトリに変更を反映

### コミットメッセージ例
```
Update video info data - 2025-07-10 15:30:25
```

### 対象ファイル
- `docs/youtube.json`
- `docs/niconico_l.json`
- `docs/secret_ac.json`
- `docs/fciu.json`

### 自動コミット&プッシュをスキップする場合
変更がない場合や、Gitリポジトリ外で実行した場合は自動的にスキップされます。手動でコミット&プッシュを実行したい場合は、個別スクリプトを実行してください。

## トラブルシューティング（スケジュール実行）

### Cronジョブが実行されない場合
```bash
# Cronサービスの状態確認
systemctl status cron

# Cronサービスの起動
sudo systemctl start cron

# Cronサービスの自動起動設定
sudo systemctl enable cron
```

### ログが記録されない場合
```bash
# ログディレクトリの確認
ls -la logs/

# ログファイルの権限確認
ls -la logs/cron_execution.log

# 手動でログファイルを作成
touch logs/cron_execution.log
```

### 実行権限の問題
```bash
# スクリプトの実行権限を確認
ls -la *.sh

# 実行権限を付与
chmod +x setup_cron.sh remove_cron.sh run.sh
```
