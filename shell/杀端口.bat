@echo off
chcp 65001
set /p port=请输入端口号:
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "%port%"') do (
    taskkill /PID %%a /F
)
