# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :tools.py
# @Time      :2025/3/6 11:28
# @Author    :Curtin


import random
import string
import psutil
import time
import sys
from .log import log

def generate_random_name(length=8):
    # 随机生成一个包含字母和数字的名称
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return name

async def save_content_to_file(content, file_path):
    # 打开文件并写入内容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    # print(f"内容已保存到 {file_path}")

def kill_chromium_if_long_running():
    # 遍历系统中的所有进程
    if not sys.platform.startswith('win'):
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                if 'chrom' in proc.info['name'].lower():
                    # 计算进程的运行时间
                    create_time = proc.info['create_time']
                    current_time = time.time()  # 当前时间
                    run_time = current_time - create_time  # 进程运行时间（秒）
                    # 如果运行时间超过30秒，则杀掉进程
                    if run_time > 60:
                        # log.info(f"Process {proc.info['name']} (PID: {proc.info['pid']}) running for {run_time:.2f} seconds. Killing process.")
                        proc.terminate()  # 终止进程
                        # proc.wait()  # 等待进程终止
                        # log.info(f"Process {proc.info['pid']} has been terminated.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 捕获异常，避免权限问题或进程已结束
                pass



