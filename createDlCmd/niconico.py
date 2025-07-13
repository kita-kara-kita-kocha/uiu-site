import json
import os
from datetime import datetime



def load_json_file():
    """
    docs/niconico_l.jsonを読み込んで必要情報を取得する関数
    
    :return: [{title, video_url, date}]
    """
    result = []
    if not os.path.exists('docs/niconico_l.json'):
        raise FileNotFoundError("docs/niconico_l.jsonが存在しません。")
    with open('docs/niconico_l.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data['items']:
            # items[].titleを取得
            title = item.get('title', '')
            
            # items[].video_urlを取得
            video_url = item.get('video_url', '')

            # video_urlの形式はhttps://live.nicovideo.jp/watch/{video_id}なので、video_idを抽出
            video_id = video_url.split('/')[-1]
            
            # items[].metadataの配列から"放送開始: YYYY/MM/DD (?) HH:mm:SS"の文字列を取得し、"YYYYMMDD"に整形して取得
            metadata = item.get('metadata', [])
            date_str = ''
            for meta in metadata:
                if '放送開始' in meta:
                    date_str = meta.split(': ')[1].split(' ')[0].replace('/', '')
                    break
            result.append({
                'title': title,
                'video_id': video_id,
                'video_url': video_url,
                'date': date_str
            })
    return result

def save_json_file(data):
    """
    データをcreateDlCmd/niconico.ps1に保存する関数
    
    :param data: list of string, ['command1', 'command2', ...]
    """
    with open('createDlCmd/niconico.ps1', 'w', encoding='utf-8') as file:
        for item in data:
            file.write(item + '\n')

def create_download_command(stream_info):
    """
    stream_infoからダウンロードコマンドを生成する関数
    :param stream_info: dict, {'title': str, 'video_url': str, 'date': str}
    :return: str, ダウンロードコマンド(ps1)
    """
    title = stream_info['title']
    tmp_video = f"{stream_info['video_id']}_tmp.ts"
    video_url = stream_info['video_url']
    date = stream_info['date']
    output_mp4 = f"【ういせとおやすみ】{date}_{title}.mp4"
    
    command_lines = []
    command_lines.append(f"# command to download niconico video")
    command_lines.append(f"$video_url=\"{video_url}\"")
    command_lines.append("# cookieファイル「*.nicovideo.jp_cookies.txt」から、Tab区切りで5つめの要素がuser_sessionの行から6つ目の値を取得し、$user_sessionに格納")
    command_lines.append("$user_session = (Get-Content .\\*.nicovideo.jp_cookies.txt | Where-Object {$_ -match \"user_session\"}) -split \"`t\" | Select-Object -Index 6")
    command_lines.append(f"streamlink $video_url --niconico-user-session $user_session --default-stream best -o \"{tmp_video}\" --ffmpeg-ffmpeg \"D:\\Youtube-DL\\ffmpeg.exe\"")
    command_lines.append(f"ffmpeg -i \"{tmp_video}\" -c:v copy -c:a copy \"{output_mp4}\"")
    command_lines.append(f"Remove-Item \"{tmp_video}\"")
    command = '\n'.join(command_lines)

    return command + '\n'

def main():
    """
    メイン関数
    1. docs/niconico_l.jsonを読み込み、必要情報を取得
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