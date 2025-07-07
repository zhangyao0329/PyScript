@echo off
ffmpeg -i 1.mp4 -i 2.m4a  -vcodec copy -acodec copy output.mp4
pause & exit