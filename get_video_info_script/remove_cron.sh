#!/bin/bash
# Cronジョブ削除用スクリプト
# run.shのスケジュール実行を停止

echo "🗑️  Cronジョブの削除を開始します..."

# 現在のディレクトリの絶対パスを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT_PATH="${SCRIPT_DIR}/run.sh"

# 削除対象のCronジョブパターン
CRON_PATTERN=".*${RUN_SCRIPT_PATH}.*"

echo "🔍 現在のCronジョブ一覧:"
crontab -l 2>/dev/null || echo "Cronジョブがありません"
echo ""

# 既存のcrontabをバックアップ
echo "💾 既存のcrontabをバックアップします..."
crontab -l > "${SCRIPT_DIR}/crontab_backup_before_remove_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || echo "既存のcrontabはありません"

# 対象のCronジョブを削除
echo "🗑️  対象のCronジョブを削除します..."
crontab -l 2>/dev/null | grep -v "${RUN_SCRIPT_PATH}" | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cronジョブの削除が完了しました！"
    echo ""
    echo "📋 削除後のCronジョブ一覧:"
    crontab -l 2>/dev/null || echo "Cronジョブがありません"
else
    echo "❌ Cronジョブの削除に失敗しました"
    exit 1
fi

echo ""
echo "🎉 スケジュール実行が停止されました"
