import yt_dlp

# 视频下载链接，需要替换为实际的视频链接
urls = ['https://www.bilibili.com/video/BV15b4y117RJ/?vd_source=7746d38fd4e722f93f1458816516c553',
        'https://www.bilibili.com/video/BV15b4y117RJ?vd_source=7746d38fd4e722f93f1458816516c553&p=2&spm_id_from=333.788.videopod.episodes']
for url in urls:
    # yt-dlp配置选项
    ydl_opts = {
        # cookies文件路径，用于加载登录cookies
        'cookies': r'E:\py\yt-dlp\cookies.txt',
        # 输出文件模板，定义了视频文件的保存路径和文件名格式
        'outtmpl': r'D:\Users\ZhangYao\Videos\download\%(title)s.%(ext)s',
        # 视频格式选择，这里选择最好的视频和音频质量，然后合并成一个mp4文件
        'format': 'bestvideo+bestaudio/best',
        # 合并输出文件格式，这里选择mp4
        'merge_output_format': 'mp4',
        # 片段重试次数，增加重试次数可以提高下载成功率
        'fragment_retries': 20,  # 默认是10，设大一点
        # 整体重试次数，增加重试次数可以提高下载成功率
        'retries': 10,  # 整体重试次数
        # 断点续传，开启后可以在下载中断后继续下载
        'continuedl': True,  # 断点续传
        # 如需限制清晰度可加，例如只下载720p及以下清晰度的视频
        # 'format': 'best[height<=720]',
        # 如需代理可加，定义HTTP代理服务器地址
        # 'proxy': 'http://127.0.0.1:7890',
        # HTTP头部信息，可以添加用户代理和Referer等信息
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Referer': url,
        },
    }
    # 使用yt-dlp下载视频
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # 开始下载视频
        ydl.download([url])
