# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :tools.py
# @Time      :2025/3/6 11:28
# @Author    :Curtin


import random
import string

def generate_random_name(length=8):
    # 随机生成一个包含字母和数字的名称
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return name