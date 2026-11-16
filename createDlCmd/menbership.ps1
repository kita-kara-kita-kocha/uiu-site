# command to download youtube menbership video
$video_url="https://www.youtube.com/watch?v=Js0wWjlCbTk"
yt-dlp -o "【メン限】[%(upload_date)s]%(title)s.%(ext)s" $video_url -f bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a] -S vcodec:hevc_nvenc --cookies .\tmp\www.youtube.com_cookies.txt --download-archive acv

# command to download youtube menbership video
$video_url="https://www.youtube.com/watch?v=XcQeQ4Lja2I"
yt-dlp -o "【メン限】[%(upload_date)s]%(title)s.%(ext)s" $video_url -f bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a] -S vcodec:hevc_nvenc --cookies .\tmp\www.youtube.com_cookies.txt --download-archive acv

# command to download youtube menbership video
$video_url="https://www.youtube.com/watch?v=IDOi3e25pBc"
yt-dlp -o "【メン限】[%(upload_date)s]%(title)s.%(ext)s" $video_url -f bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a] -S vcodec:hevc_nvenc --cookies .\tmp\www.youtube.com_cookies.txt --download-archive acv

