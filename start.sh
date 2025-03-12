#!/bin/sh
# 设置 Chromium 参数并启动 Xvfb
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
# 解决 /dev/shm 太小的问题
export DISPLAY=:99
exec python main.py
