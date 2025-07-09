# GitHub Actions ワークフロー設定

このディレクトリには、動画情報サイトの自動更新とデプロイのためのGitHub Actionsワークフローが含まれています。

## ワークフロー一覧

### 1. 動画情報自動更新 (`update-video-info.yml`)

**目的**: 6時間ごとに動画情報を自動取得し、更新があった場合に直接mainブランチにコミットする

**実行スケジュール**:
- 毎日 0時、6時、12時、18時（日本時間）
- 手動実行も可能（Actions タブから）

**処理フロー**:
1. Ubuntu環境でPythonとChromiumをセットアップ
2. `get_video_info_script/run.sh` を実行して動画情報を取得
3. `docs/` フォルダ内のJSONファイルに変更があるかチェック
4. 変更がある場合：
   - 変更をコミット
   - 直接mainブランチにプッシュ

**必要な権限**: 
- `contents: write`

### 2. GitHub Pages デプロイ (`deploy-pages.yml`)

**目的**: `docs/` フォルダの変更時にGitHub Pagesサイトを自動更新

**実行トリガー**:
- `main` ブランチの `docs/` フォルダに変更がプッシュされた時
- 手動実行も可能

**処理フロー**:
1. `docs/` フォルダの内容をGitHub Pagesにデプロイ
2. サイトのURLを出力

**必要な権限**:
- `contents: read`
- `pages: write`
- `id-token: write`

## 変更点（エラー修正）

### 元の問題
GitHub Actionsの標準トークン（`GITHUB_TOKEN`）では、プルリクエストの作成ができない制限がありました。

### 解決方法
プルリクエストを使わず、直接mainブランチにコミットする方式に変更しました。これにより：
- ✅ 標準のGitHub Actionsトークンで動作
- ✅ 設定が簡単
- ✅ 即座に変更が反映される

### プルリクエストを使いたい場合
もしプルリクエストベースのワークフローが必要な場合は、以下の手順で設定できます：

1. **Personal Access Token (PAT) の作成**:
   - GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - `Contents` と `Pull requests` の権限を付与

2. **リポジトリシークレットに追加**:
   - リポジトリ → Settings → Secrets and variables → Actions
   - `PAT_TOKEN` という名前でPATを追加

3. **ワークフローの修正**:
   - `token: ${{ secrets.GITHUB_TOKEN }}` を `token: ${{ secrets.PAT_TOKEN }}` に変更

## セットアップ手順

### 1. GitHub Pagesの有効化

1. リポジトリの Settings → Pages に移動
2. Source を "GitHub Actions" に設定

### 2. ワークフローの有効化

1. Actions タブに移動
2. ワークフローを有効化

## 注意事項

- **スケジュール実行時間**: UTC時間で設定されているため、日本時間との時差（9時間）に注意
- **実行時間**: 動画情報取得には20-45分程度かかる場合があります
- **エラー処理**: スクリプトが失敗した場合、ワークフローは継続し、取得できた情報のみで更新されます
- **ブランチ保護**: mainブランチに直接コミットするため、ブランチ保護ルールが厳しい場合は調整が必要

## トラブルシューティング

### ワークフローが実行されない場合

1. Actions タブでワークフローが有効化されているか確認
2. リポジトリの権限設定を確認
3. `get_video_info_script/run.sh` に実行権限があるか確認

### デプロイが失敗する場合

1. GitHub Pages の設定を確認
2. `docs/` フォルダに必要なファイル（`index.html` など）があるか確認
3. ファイルサイズがGitHubの制限内（100MB未満）であるか確認

### 動画情報取得が失敗する場合

1. 各PythonスクリプトのAPI設定を確認
2. 依存関係（`requirements.txt`）が最新であるか確認
3. 手動でスクリプトを実行してエラーの詳細を確認

## ファイル構成

```
.github/workflows/
├── update-video-info.yml  # 動画情報自動更新（直接コミット版）
├── deploy-pages.yml       # GitHub Pages デプロイ
└── README.md             # このファイル
```
