from fastapi import FastAPI, Query, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse, JSONResponse
import yt_dlp
import tempfile
import os
import threading
import uuid

# 启动命令：  uvicorn main:app --host 0.0.0.0 --port 8000

app = FastAPI()

download_tasks = {}  # task_id: {status, progress, filename, error}

def download_worker(url, task_id):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, '%(title)s.%(ext)s')
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'progress_hooks': [lambda d: ydl_progress_hook(d, task_id)],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp4')
            download_tasks[task_id]['status'] = 'finished'
            download_tasks[task_id]['filename'] = filename
    except Exception as e:
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['error'] = str(e)

def ydl_progress_hook(d, task_id):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
        downloaded = d.get('downloaded_bytes', 0)
        percent = int(downloaded / total * 100)
        download_tasks[task_id]['progress'] = percent
    elif d['status'] == 'finished':
        download_tasks[task_id]['progress'] = 100

@app.get("/", response_class=HTMLResponse)
def index():
    return """
  <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>视频下载器</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 40px;
            width: 500px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            text-align: center;
            color: #333;
            animation: fadeIn 1s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        h2 {
            margin-bottom: 20px;
            font-size: 26px;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px 15px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
            margin-bottom: 20px;
            outline: none;
            background: rgba(255, 255, 255, 0.6);
        }

        button {
            background: linear-gradient(45deg, #4facfe, #00f2fe);
            border: none;
            padding: 12px 25px;
            border-radius: 30px;
            font-size: 16px;
            color: white;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }

        #progress {
            margin-top: 30px;
            width: 100%;
            height: 30px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }

        #bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #43e97b, #38f9d7);
            color: #fff;
            line-height: 30px;
            text-align: center;
            transition: width 0.3s ease;
        }

        #download-link {
            margin-top: 20px;
        }

        #download-link a {
            color: #007aff;
            text-decoration: none;
            font-weight: bold;
        }

        #download-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>在线视频下载器</h2>
        <input type="text" id="url" placeholder="粘贴视频链接，例如：https://www.bilibili.com/..." required />
        <button onclick="startDownload()">开始下载</button>

        <div id="progress">
            <div id="bar">0%</div>
        </div>

        <div id="download-link"></div>
    </div>

    <script>
        function startDownload() {
            var url = document.getElementById('url').value;
            document.getElementById('bar').style.width = '0%';
            document.getElementById('bar').innerText = '0%';
            document.getElementById('download-link').innerHTML = '';
            fetch('/start_download?url=' + encodeURIComponent(url))
              .then(resp => resp.json())
              .then(data => {
                if (data.task_id) {
                    pollProgress(data.task_id);
                } else {
                    alert('任务创建失败');
                }
              });
        }

        function pollProgress(task_id) {
            fetch('/progress?task_id=' + task_id)
              .then(resp => resp.json())
              .then(data => {
                var percent = data.progress || 0;
                document.getElementById('bar').style.width = percent + '%';
                document.getElementById('bar').innerText = percent + '%';
                if (data.status === 'finished') {
                    document.getElementById('download-link').innerHTML = `<a href="/download_file?task_id=${task_id}">点击下载视频</a>`;
                } else if (data.status === 'error') {
                    document.getElementById('download-link').innerText = '下载出错: ' + data.error;
                } else {
                    setTimeout(() => pollProgress(task_id), 1000);
                }
              });
        }
    </script>
</body>
</html>

    """


@app.get("/start_download")
def start_download(url: str):
    task_id = str(uuid.uuid4())
    download_tasks[task_id] = {'status': 'downloading', 'progress': 0, 'filename': None, 'error': None}
    threading.Thread(target=download_worker, args=(url, task_id), daemon=True).start()
    return {"task_id": task_id}

@app.get("/progress")
def get_progress(task_id: str):
    task = download_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"status": task['status'], "progress": task['progress'], "error": task['error']}

@app.get("/download_file")
def download_file(task_id: str):
    task = download_tasks.get(task_id)
    if not task or task['status'] != 'finished' or not task['filename']:
        raise HTTPException(status_code=404, detail="文件未就绪")
    filename = os.path.basename(task['filename'])
    return FileResponse(task['filename'], media_type="video/mp4", filename=filename)
