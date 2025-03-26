# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :config.py
# @Time      :2025/3/14 11:47
# @Author    :Curtin
import os
from configparser import RawConfigParser
from .tools import generate_random_name
from .log import log
class Config:
    def __init__(self):
        # 获取当前工作目录
        pwd = os.path.dirname(os.path.abspath(__file__))
        pwd = pwd.replace('utils', '')
        # 路由标记是否需要 API Key 验证
        self.NO_API_KEY_REQUIRED_ROUTES = ['/', '/favicon.ico', '/swagger', '/openapi.json']
        # 路由标记是否需要 API Key 验证
        self.disableInterfaces = []
        self.port = 80
        self.apiKey = ''
        ##### 抖音配置
        self.sleepNum = 10.0
        # 获取账号参数
        try:
            configinfo = RawConfigParser()
            try:
                configinfo.read(pwd + "config.ini", encoding="UTF-8")
            except Exception as e:
                with open(pwd + "config.ini", "r", encoding="UTF-8") as config:
                    getConfig = config.read().encode('utf-8').decode('utf-8-sig')
                with open(pwd + "config.ini", "w", encoding="UTF-8") as config:
                    config.write(getConfig)
                try:
                    configinfo.read(pwd + "config.ini", encoding="UTF-8")
                except:
                    configinfo.read(pwd + "config.ini", encoding="gbk")
            self.disableInterfaces = strToList(configinfo.get('main', 'disableInterfaces'))
            self.port = configinfo.getint('main', 'port')
            self.apiKey = configinfo.get('main', 'apiKey')
            self.sleepNum = configinfo.getfloat('DouYin', 'sleepNum')
        except Exception as e:
            print("参数配置有误，config.ini\nError:", e, flush=True)
        # 判断系统环境变量(优先使用)
        if "disableInterfaces" in os.environ:
            self.disableInterfaces = strToList(os.environ["disableInterfaces"])
        if "port" in os.environ:
            if len(os.environ["port"]) > 1:
                self.port = int(os.environ["port"])
        if "apiKey" in os.environ:
            self.apiKey = os.environ["apiKey"]
        if "sleepNum" in os.environ:
            if len(os.environ["sleepNum"]) > 0:
                self.sleepNum = int(os.environ["sleepNum"])
        if len(self.apiKey) == 0:
            tmpApiKey = generate_random_name(length=32)
            log.info(f"你的接口密钥(temp apiKey)：{tmpApiKey}      ！！！这是临时接口密钥，如需修改请到config.ini文件配置apiKey")
            self.apiKey = tmpApiKey

    def getConfig(self):
        """返回日志器对象"""
        return self

def strToList(text: str, s = ','):
    list = []
    try:
        list = text.split(s)
    except:
        pass
    return list
config = Config().getConfig()

if __name__ == "__main__":
    print("Curtin")
