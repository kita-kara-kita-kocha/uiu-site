# 実行コマンド
# source get_video_info_script/venv/bin/activate
# python createDlCmd/menbership.py


import json
import os
from datetime import datetime

def load_json_file():
    """
    docs/youtube.jsonを読み込んで必要情報を取得する関数

    :return: [{title, video_url, date}]
    """
    result = []
    if not os.path.exists('docs/youtube.json'):
        raise FileNotFoundError("docs/youtube.jsonが存在しません。")
    with open('docs/youtube.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data['items']:
            if "subscriber_only" in item.get('addAdditionalClass', ''):
                # items[].video_urlを取得
                video_url = item.get('video_url', '')

                result.append({
                    'video_url': video_url
                })
    return result

def save_json_file(data):
    """
    データをdocs/youtube.jsonに保存する関数

    :param data: list of string, ['command1', 'command2', ...]
    """
    with open('createDlCmd/menbership.ps1', 'w', encoding='utf-8') as file:
        for item in data:
            file.write(item + '\n')

def create_download_command(stream_info):
    """
    stream_infoからダウンロードコマンドを生成する関数
    :param stream_info: dict, {'title': str, 'video_url': str}
    :return: str, ダウンロードコマンド(ps1)
    """
    video_url = stream_info['video_url']

    command_lines = []
    command_lines.append(f"# command to download youtube menbership video")
    command_lines.append(f"$video_url=\"{video_url}\"")
    command_lines.append(f"yt-dlp -o \"【メン限】[%(upload_date)s]%(title)s.%(ext)s\" $video_url -f bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a] -S vcodec:hevc_nvenc --cookies .\\tmp\\www.youtube.com_cookies.txt --download-archive acv")

    command = '\n'.join(command_lines)
    return command + '\n'

def main():
    """
    メイン関数
    1. docs/youtube.jsonを読み込み、必要情報を取得
    2. 各動画のダウンロードコマンドを生成し、表示
    """
    try:
        data = []
        stream_info_list = load_json_file()
        for stream_info in stream_info_list:
            command = create_download_command(stream_info)
            data.append(command)
            # print(command)
        save_json_file(data)
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()