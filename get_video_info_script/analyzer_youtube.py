# docs/youtube.jsonを読み込み、再生回数などの推移を分析する


import os
import json
import datetime

src_json_file_path = '../docs/youtube.json'
put_json_file_path = '../docs/youtube_analyzed.json'

class YouTubeAnalyzer:
    def __init__(self):
        """
        初期化メソッド
        param:
            json_file: str, 読み込むJSONファイルのパス
        """
        self.src_data = self.load_json_file(src_json_file_path)
        # {
        #     "items": [
        #         {
        #             "id": str,
        #             "title": str,
        #             "views": int,
        #         },...
        #     ],
        #     "tags": [],
        #     "last_updated": str,
        #     "total_videos": int,
        # }
        self.analyzed_data = self.load_json_file(put_json_file_path)
        # {
        #     "each_video": [
        #         {
        #             "id": str,
        #             "title": str,
        #             "views": [
        #                 {
        #                     "v_datetime": datetime,
        #                     "view_count": int
        #                 },...
        #             ]
        #         },...
        #     ],
        #     "total_videos": [
        #         {
        #             "v_datetime": datetime,
        #             "view_count": int
        #         },...
        #     ]
        # }

    def load_json_file(self, json_file_path):
        """
        JSONファイルを読み込むメソッド
        return:
            dict, 読み込んだデータ
        raises:
            FileNotFoundError: 指定されたファイルが存在しない場合
        """
        if not os.path.exists(json_file_path):
            # ファイルが存在しない場合は、ファイルを作成して空のデータを返す
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=4)
            return {}
        with open(json_file_path, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                # JSONファイルが空の場合は空の辞書を返す
                if os.path.getsize(json_file_path) == 0:
                    return {}
                # JSONファイルが空でない場合はエラーを投げる
                raise ValueError(f"JSONファイルの読み込みに失敗しました: {json_file_path}")

    def analyze_views(self):
        """
        再生回数の推移を分析するメソッド
        return:
            dict: {'scan_datetime': datetime, [{'id': str, 'views': int}]}
        """
        scan_datetime = self.src_data.get('last_updated', '')
        scan_datetime = datetime.datetime.strptime(scan_datetime, '%Y-%m-%dT%H:%M:%S.%f') if scan_datetime else None
        views_data = []
        for item in self.src_data.get('items', []):
            video_id = item.get('videoId', '')  # 'id' を 'videoId' に変更
            views = item.get('view_count', 0)  # view_countフィールドがない場合は0
            title = item.get('title', '')
            views_data.append({'id': video_id, 'views': views, 'title': title})
        return {'scan_datetime': scan_datetime, 'views_data': views_data}
    
    def put_analyzed_data(self):
        """
        分析結果を整形してanalyzed_data[each_video]とanalyzed_data[total_videos]にアペンドするメソッド
        """
        analysis_result = self.analyze_views()

        if 'each_video' not in self.analyzed_data:
            self.analyzed_data['each_video'] = []                                                                    
        # 各動画の情報取得日と再生回数を追加
        if analysis_result and analysis_result['scan_datetime']:
            scan_datetime_str = analysis_result['scan_datetime'].isoformat()
            
            # 各動画の処理
            for view_data in analysis_result['views_data']:
                video_id = view_data['id']
                views = view_data.get('views', 0)  # viewsフィールドがない場合は0
                # viewsが0の場合はスキップ
                if views == 0:
                    continue
                title = view_data['title']
                
                # 既存の動画データを検索
                existing_video = None
                for video in self.analyzed_data['each_video']:
                    if video.get('id') == video_id:
                        existing_video = video
                        break
                
                if existing_video:
                    # 既存の動画の場合、同じ時間のv_datetimeが存在しない場合のみ追加
                    if not any(v['v_datetime'] == scan_datetime_str for v in existing_video['views']):
                        existing_video['views'].append({
                            'v_datetime': scan_datetime_str,
                            'view_count': views
                        })
                else:
                    # 新しい動画の場合は追加
                    self.analyzed_data['each_video'].append({
                        'id': video_id,
                        'title': title,
                        'views': [{
                            'v_datetime': scan_datetime_str,
                            'view_count': views
                        }]
                    })
            
            # 総再生回数の情報を追加
            # total_videosが存在しない場合は初期化
            if 'total_videos' not in self.analyzed_data:
                self.analyzed_data['total_videos'] = []
            # 同じ時間のv_datetimeが存在する場合は追加しない
            if not any(v['v_datetime'] == scan_datetime_str for v in self.analyzed_data['total_videos']):
                # view_countが0より大きい動画のみを対象にして総再生回数を計算
                total_view_count = sum(view['views'] for view in analysis_result['views_data'] if view['views'] > 0)
                self.analyzed_data['total_videos'].append({
                    'v_datetime': scan_datetime_str,
                    'view_count': total_view_count
                })
            self.analyzed_data['last_updated'] = scan_datetime_str

    def save_video_info(self):
        def convert_datetime(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()  # datetime を ISO 8601 形式の文字列に変換
            raise TypeError(f"Type {type(obj)} not serializable")
        with open(put_json_file_path, 'w', encoding='utf-8') as file:
            json.dump(self.analyzed_data, file, ensure_ascii=False, indent=4, default=convert_datetime)

    def main(self):
        """
        メインメソッド
        1. 再生回数の推移を分析
        2. 分析結果を保存
        """
        self.put_analyzed_data()
        self.save_video_info()

if __name__ == "__main__":
    analyzer = YouTubeAnalyzer()
    analyzer.main()