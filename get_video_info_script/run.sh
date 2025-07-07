#!/bin/bash
# YouTube動画情報取得スクリプト実行用

echo "🎬 YouTube動画情報取得スクリプトを開始します..."

# 現在のディレクトリをget_video_info_scriptに変更
cd "$(dirname "$0")"

# Python仮想環境の確認（オプション）
if [ -d "venv" ]; then
    echo "📦 仮想環境をアクティベートします..."
    source venv/bin/activate
fi

# 必要なパッケージがインストールされているかチェック
echo "🔍 依存関係をチェックしています..."
python -c "import yt_dlp; print('✅ yt-dlp インストール済み')" 2>/dev/null || {
    echo "❌ yt-dlpがインストールされていません。インストールしています..."
    pip install yt-dlp
}

# メインスクリプトを実行
echo "🚀 スクリプトを実行します..."
python get_video_info_youtube.py

echo "✨ 完了しました！"
