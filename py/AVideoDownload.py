import yt_dlp
import sys

# 进度钩子函数
def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes:
            percent = downloaded_bytes / total_bytes * 100
            bar_len = 40
            filled_len = int(round(bar_len * percent / 100))
            bar = '=' * filled_len + '-' * (bar_len - filled_len)
            sys.stdout.write(f'\r[{bar}] {percent:.2f}%')
            sys.stdout.flush()
        else:
            sys.stdout.write(f"\r已下载 {downloaded_bytes / 1024 / 1024:.2f} MB")
            sys.stdout.flush()
    elif d['status'] == 'finished':
        print("\n下载完成，正在合并或处理文件...")

# 视频下载链接列表
urls = [
    'https://cn.pornhub.com/view_video.php?viewkey=ph5ec7ffaac3fea&pkey=182354621' # 替换为实际链接
    ,'https://cn.pornhub.com/view_video.php?viewkey=ph57ff6d73ac5b6&pkey=182354621'
]

# 下载配置
ydl_opts = {
    'extractor_args': {'generic': ['impersonate']},
    'cookies': r'E:\py\yt-dlp\cookies.txt',
    'outtmpl': r'D:\Users\ZhangYao\Videos\download\%(title)s.%(ext)s',
    'format': 'bestvideo+bestaudio/best',
    'merge_output_format': 'mp4',
    'fragment_retries': 20,
    'retries': 10,
    'continuedl': True,
    'progress_hooks': [progress_hook],
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'Referer': '',  # 下面会动态赋值
    },
    'quiet': True,  # 关闭默认输出，只保留进度条
}

# 执行下载
for url in urls:
    print(f"\n开始下载: {url}")
    ydl_opts['http_headers']['Referer'] = url
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"\n下载失败: {url}\n错误信息: {e}")
