#!/bin/bash
# 動画情報取得スクリプト一括実行用

echo "🎬 動画情報取得スクリプトを開始します..."
echo "📅 実行開始時刻: $(date)"

# 現在のディレクトリをget_video_info_scriptに変更
cd "$(dirname "$0")"

# Python仮想環境の確認（オプション）
if [ -d "venv" ]; then
    echo "📦 仮想環境をアクティベートします..."
    source venv/bin/activate
fi

# 必要なパッケージがインストールされているかチェック
echo "🔍 依存関係をチェックしています..."

# GitHub Actions環境の検出
if [ "$GITHUB_ACTIONS" = "true" ]; then
    echo "🤖 GitHub Actions環境を検出しました"
    # yt-dlpキャッシュディレクトリの作成
    mkdir -p /tmp/yt-dlp-cache
    export YT_DLP_CACHE_DIR=/tmp/yt-dlp-cache
fi

check_package() {
    python -c "import $1; print('✅ $1 インストール済み')" 2>/dev/null || {
        echo "❌ $1がインストールされていません。インストールしています..."
        pip install $2
    }
}

check_package "yt_dlp" "yt-dlp"
check_package "requests" "requests"
check_package "bs4" "beautifulsoup4"
check_package "lxml" "lxml"
check_package "selenium" "selenium"
check_package "webdriver_manager" "webdriver-manager"

echo ""
echo "🚀 すべてのスクリプトを順次実行します..."
echo "⏱️  予想実行時間: 約20-45分"
echo ""

# カウンター
script_count=0
success_count=0
failed_scripts=()

# スクリプト実行関数
run_script() {
    local script_name=$1
    local description=$2
    script_count=$((script_count + 1))
    
    echo "=================================================================================="
    echo "📺 [$script_count/4] $description"
    echo "🎯 実行スクリプト: $script_name"
    echo "⏰ 開始時刻: $(date)"
    echo "=================================================================================="
    
    # GitHub Actions環境では追加の待機時間を設ける
    if [ "$GITHUB_ACTIONS" = "true" ]; then
        echo "🤖 CI環境での実行 - レート制限回避のため少し待機します..."
        sleep 3
    fi
    
    if python "$script_name"; then
        echo "✅ $description - 完了"
        success_count=$((success_count + 1))
    else
        echo "❌ $description - 失敗"
        failed_scripts+=("$script_name")
    fi
    
    echo "📊 完了時刻: $(date)"
    echo ""
    
    # GitHub Actions環境では次のスクリプト実行前に少し待機
    if [ "$GITHUB_ACTIONS" = "true" ] && [ $script_count -lt 4 ]; then
        echo "⏳ 次のスクリプト実行まで少し待機します..."
        sleep 5
    fi
}

# 各スクリプトを順次実行
run_script "get_video_info_youtube.py" "YouTube動画情報取得"
run_script "get_video_info_niconico_live.py" "ニコニコ動画ライブ情報取得"
run_script "get_video_info_secret.py" "ファンサイト投稿情報取得"
run_script "get_video_info_fc.py" "ファンクラブ動画情報取得"

# 実行結果サマリー
echo "=================================================================================="
echo "🎉 すべてのスクリプトの実行が完了しました！"
echo "📅 実行完了時刻: $(date)"
echo "📊 実行結果: $success_count/4 スクリプトが成功"

if [ ${#failed_scripts[@]} -eq 0 ]; then
    echo "✨ すべてのスクリプトが正常に完了しました！"
    echo ""
    echo "📁 出力ファイル:"
    echo "   - ../docs/youtube.json"
    echo "   - ../docs/niconico_l.json" 
    echo "   - ../docs/secret_ac.json"
    echo "   - ../docs/fciu.json"
else
    echo "⚠️  以下のスクリプトが失敗しました:"
    for script in "${failed_scripts[@]}"; do
        echo "   - $script"
    done
    echo ""
    echo "💡 失敗したスクリプトは個別に実行して詳細を確認してください。"
fi

echo "=================================================================================="
