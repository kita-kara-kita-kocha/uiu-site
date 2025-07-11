# Cron実行でのプッシュ失敗 - 解決方法

## 問題の概要
cronジョブで実行される `get_video_info_script/run.sh` スクリプトにおいて、Gitプッシュが失敗する問題が発生していました。

## 原因
- cron環境では対話式認証（ユーザー名・パスワード入力）ができない
- HTTPSリモートURLでの認証に失敗

## 解決策

### 1. SSH鍵の設定
SSH鍵が既に生成されています:
```bash
# 公開鍵を確認
cat ~/.ssh/id_ed25519.pub
```

出力:
```
ssh-ed25519 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx kttpc@github-automation
```

### 2. GitHubでの設定
**重要**: 上記のSSH公開鍵をGitHubのSSH鍵に登録してください：

1. GitHub > Settings > SSH and GPG keys
2. "New SSH key" をクリック
3. Title: "Server Automation Key"
4. Key: 上記の公開鍵を貼り付け
5. "Add SSH key" をクリック

### 3. 実装された修正内容

#### スクリプト修正 (`run.sh`)
- **Cron環境の検出**: `CRON_RUNNING`環境変数で自動判定
- **SSH認証テスト**: プッシュ前にSSH接続をテスト
- **詳細エラーログ**: 失敗時に詳細な診断情報を出力
- **自動URL変更**: HTTPSからSSHへの自動変更
- **環境変数設定**: cron環境での適切なPATH設定

#### Cron設定修正
```bash
# 修正前
0 */3 * * * cd "/home/kttpc/uiu-site/get_video_info_script" && bash "/home/kttpc/uiu-site/get_video_info_script/run.sh" > "/home/kttpc/uiu-site/get_video_info_script/logs/cron_execution.log" 2>&1

# 修正後
0 */3 * * * SSH_AUTH_SOCK="" SSH_AGENT_PID="" cd "/home/kttpc/uiu-site/get_video_info_script" && bash "/home/kttpc/uiu-site/get_video_info_script/run.sh" > "/home/kttpc/uiu-site/get_video_info_script/logs/cron_execution.log" 2>&1
```

#### Git設定修正
```bash
# リモートURLをSSHに変更
git remote set-url origin git@github.com:kita-kara-kita-kocha/uiu-site.git
```

### 4. 動作確認
SSH鍵をGitHubに登録後、以下のコマンドで接続テストを実行:
```bash
ssh -T git@github.com
```

成功した場合の出力例:
```
Hi kita-kara-kita-kocha! You've successfully authenticated, but GitHub does not provide shell access.
```

### 5. トラブルシューティング

#### SSH接続が失敗する場合
```bash
# SSH設定の確認
cat ~/.ssh/config

# SSH接続デバッグ
ssh -vT git@github.com

# SSH鍵権限の確認
ls -la ~/.ssh/
```

#### 手動でのプッシュテスト
```bash
cd /home/kttpc/uiu-site
git status
git add docs/
git commit -m "Test commit"
git push
```

## 次回のcron実行
SSH鍵をGitHubに登録後、次回のcron実行（3時間ごと）でプッシュが自動的に成功するはずです。

ログで確認できる成功メッセージ:
```
✅ SSH認証が有効です
✅ プッシュが完了しました！
🌐 変更がリモートリポジトリに反映されました
```
