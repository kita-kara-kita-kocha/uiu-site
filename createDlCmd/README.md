# createDlCmd

このフォルダには、動画配信サイトからのダウンロードコマンドを自動生成するPythonスクリプトが含まれています。

## 概要

配信情報JSONファイルから動画のダウンロードコマンド（PowerShellスクリプト）を生成するツールです。YouTubeのメンバーシップ限定動画とニコニコ生放送の両方に対応しています。

## ファイル構成

- `menbership.py` - YouTubeメンバーシップ限定動画のダウンロードコマンド生成
- `niconico.py` - ニコニコ生放送のダウンロードコマンド生成
- `README.md` - このファイル

## 機能

### menbership.py
- `docs/youtube.json`から購読者限定動画の情報を読み込み
- `yt-dlp`を使用したダウンロードコマンド（PowerShell）を生成
- 出力ファイル: `createDlCmd/menbership.ps1`

### niconico.py
- `docs/niconico_l.json`からニコニコ生放送の情報を読み込み
- `streamlink`と`ffmpeg`を使用したダウンロードコマンド（PowerShell）を生成
- 出力ファイル: `createDlCmd/niconico.ps1`

## 使用方法

### YouTubeメンバーシップ動画のコマンド生成
```bash
python3 createDlCmd/menbership.py
```

### ニコニコ生放送のコマンド生成
```bash
python3 createDlCmd/niconico.py
```

## 依存関係

### 必要なツール
- Python 3.x
- yt-dlp (YouTubeダウンロード用)
- streamlink (ニコニコ生放送用)
- ffmpeg (動画変換用)

### 必要なファイル
- `docs/youtube.json` - YouTube動画情報
- `docs/niconico_l.json` - ニコニコ生放送情報
- Cookieファイル（認証用）
  - YouTube: `tmp/www.youtube.com_cookies.txt`
  - ニコニコ: `*.nicovideo.jp_cookies.txt`

## 出力形式

生成されるPowerShellスクリプトには以下が含まれます：

### YouTube（menbership.ps1）
- 720p以下のMP4形式での動画ダウンロード
- HEVC NVENC エンコーダーの優先使用
- アーカイブファイルによる重複ダウンロード防止

### ニコニコ（niconico.ps1）
- streamlinkによる配信ダウンロード
- ffmpegによるMP4形式への変換
- 一時ファイルの自動削除

## 注意事項

- 実行前に適切なCookieファイルを配置してください
- ffmpegのパスは環境に応じて調整が必要な場合があります
- ダウンロードは配信者の利用規約に従って行ってください