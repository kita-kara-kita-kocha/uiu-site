#!/bin/bash
# Cron設定用スクリプト
# run.shを6時間ごとに実行するようにスケジュール設定

echo "⏰ Cronジョブの設定を開始します..."

# 現在のディレクトリの絶対パスを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_SCRIPT_PATH="${SCRIPT_DIR}/run.sh"

# ログファイルのパス
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/cron_execution.log"

# ログディレクトリの作成
mkdir -p "${LOG_DIR}"

# Cronジョブの設定（6時間ごと: 0時、6時、12時、18時）
CRON_JOB="0 */6 * * * cd \"${SCRIPT_DIR}\" && bash \"${RUN_SCRIPT_PATH}\" >> \"${LOG_FILE}\" 2>&1"

echo "📝 設定するCronジョブ:"
echo "${CRON_JOB}"
echo ""

# 既存のcrontabをバックアップ
echo "💾 既存のcrontabをバックアップします..."
crontab -l > "${SCRIPT_DIR}/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || echo "既存のcrontabはありません"

# 新しいcronジョブを追加
echo "➕ 新しいCronジョブを追加します..."
(crontab -l 2>/dev/null || echo ""; echo "${CRON_JOB}") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cronジョブの設定が完了しました！"
    echo ""
    echo "📋 現在のCronジョブ一覧:"
    crontab -l
    echo ""
    echo "📁 ログファイル: ${LOG_FILE}"
    echo "📂 ログディレクトリ: ${LOG_DIR}"
    echo ""
    echo "🕐 実行スケジュール:"
    echo "   - 毎日 00:00 (午前0時)"
    echo "   - 毎日 06:00 (午前6時)"
    echo "   - 毎日 12:00 (午後12時)"
    echo "   - 毎日 18:00 (午後6時)"
else
    echo "❌ Cronジョブの設定に失敗しました"
    exit 1
fi

echo ""
echo "🔍 Cronジョブの状態確認方法:"
echo "   crontab -l                    # 設定されたジョブを表示"
echo "   tail -f ${LOG_FILE}          # ログをリアルタイム表示"
echo "   systemctl status cron         # Cronサービスの状態確認"
echo ""
echo "🗑️  Cronジョブを削除する場合:"
echo "   crontab -e                    # エディタでcrontabを編集"
echo "   または"
echo "   bash remove_cron.sh           # 削除用スクリプトを実行"
