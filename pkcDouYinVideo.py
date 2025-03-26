from requests_html import AsyncHTMLSession
from pyppeteer import launch
import re, sys, os
import requests
import asyncio
import random
from utils import kill_chromium_if_long_running, config, log

# 动态生成一个版本号
def generate_version():
    major_version = random.randint(10, 20)  # 随机生成主版本号
    minor_version = random.randint(0, 10)   # 随机生成次版本号
    return f"{major_version}.{minor_version}"
# 创建动态的 User-Agent
def generate_user_agent():
    version = generate_version()
    user_agent = f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
    return user_agent
headers = {
    "Accept": "application/json, text/javascript",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": generate_user_agent()
}
def getExtract_lonGurl(dyLink):
    # 正则表达式来提取 URL
    url_pattern = r'https?://[^\s/$.?#].[^\s]*'
    # 使用 re.search 查找匹配的部分
    urls = re.findall(url_pattern, dyLink)
    if urls:
        # 如果找到了匹配的 URL，返回 URL
        return urls[0]
    else:
        # 如果没有找到匹配的 URL，返回 None
        return None
async def downloadViden(url, hd=None):
    h = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "range": "bytes=0-",
        "Referer": url,
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    if hd:
        h['User-Agent'] = hd['User-Agent']
    return requests.get(url, headers=h, stream=True)
async def getDyHtml(url):
    # 跨平台配置
    is_windows = sys.platform.startswith('win')
    if is_windows:
        html_content = await get_rendered_html_win(url)
    else:
        html_content = await get_rendered_html(url)
    return html_content
def getLongURL(url, hd=None):
    if 'https://www.douyin.com/video/' in url:
        return url
    else:
        if not url.startswith('https'):
            url = getExtract_lonGurl(url)
        header = headers.copy()
        if hd:
            header['User-Agent'] = hd['User-Agent']
        response = requests.get(url, headers=header, allow_redirects=False)
        new_url = response.headers['Location']
        video_id = re.findall(r'video/(.*?)/\?', new_url)[0]
        new_url = "https://www.douyin.com/video/"+video_id
        # print(f"抖音动态原始链接：{new_url}", flush=True)
        return new_url

async def get_rendered_html(url, max_retries=3, required_content="https://v3-web.douyinvod.com"):
    attempt = 0
    # 配置浏览器参数
    browser_args = [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--window-size=1920x1080'
    ]
    # 启动指定路径的 Chromium
    # browser = None
    browser = await launch(
        executablePath='/usr/bin/chromium' if os.path.exists('/usr/bin/chromium') else None,
        args=browser_args,
        headless=True,
        timeout=60000  # 60秒超时
    )
    page = await browser.newPage()
    await page.setJavaScriptEnabled(True)
    # await page.setUserAgent(headers['User-Agent'])
    # 设置页面超时和重试策略
    page.setDefaultNavigationTimeout(60000)  # 60秒
    while attempt < max_retries:
        try:
            # 等待直到所有请求完成
            response = await page.goto(url, {'waitUntil': 'networkidle2'})
            # 等待页面完全加载，包括渲染的内容和异步请求
            await page.waitFor((config.sleepNum * 1000) + (attempt * 1000))  # 延迟，确保所有脚本执行完毕
            await auto_scroll(page)  # 滚动页面，加载更多内容
            content = await page.content()
            if required_content in content:
                if page:
                    await page.close()
                if browser:
                    await browser.close()
                kill_chromium_if_long_running()
                return content
            else:
                # print(f"未找到, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
                attempt += 1
        except Exception as e:
            # print(f"发生异常: {str(e)[:200]}, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
            attempt += 1
        # finally:
        #     if browser:
        #         await browser.close()
    if page:
        await page.close()
    if browser:
        await browser.close()
    kill_chromium_if_long_running()
    return None
async def auto_scroll(page):
    # 执行页面滚动，直到底部
    last_height = await page.evaluate('document.body.scrollHeight')
    while True:
        # 滚动到底部
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
        # 等待新的内容加载
        await page.waitFor(1000)
        new_height = await page.evaluate('document.body.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
async def get_rendered_html_win(url, max_retries=3, required_content="https://v3-web.douyinvod.com"):
    session = AsyncHTMLSession()
    attempt = 0
    while attempt < max_retries:
        try:
            # 发起请求并获取响应
            response = await session.get(url, headers=headers)
            # 执行JavaScript并等待页面加载完成
            await response.html.arender(timeout=60, sleep=config.sleepNum+attempt, keep_page=True, scrolldown=3)
            # 检查页面内容是否包含指定的字符串
            if required_content in response.html.html:
                html_text = response.html.html
                if session:
                    await session.close()
                kill_chromium_if_long_running()
                return html_text
            else:
                # print(f"未找到, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
                attempt += 1
        except Exception as e:
            # print(f"发生异常: {e}, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
            attempt += 1
    # print("未找到，已超出最多尝试次数。", flush=True)
    if session:
        await session.close()
    kill_chromium_if_long_running()
    return None
def extract_url(text):
    # 正则表达式提取src中完整的https://v3-web.douyinvod.com链接
    pattern = r'src="(https://v3-web\.douyinvod\.com[^\s"]+)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)  # 返回匹配到的第一个结果
    else:
        return None


def get_seconds_from_html(html_str):
    # 使用正则表达式提取时间字符串，允许跨行匹配
    match = re.search(r'<span class="time-duration">([\d:]+)</span>', html_str, re.DOTALL)
    if match:
        time_str = match.group(1)  # 获取时间字符串
        # 分割时间字符串
        time_parts = time_str.split(':')

        # 根据时间字符串长度处理不同格式
        if len(time_parts) == 3:  # "HH:MM:SS"
            hours = int(time_parts[0])
            minutes = int(time_parts[1])
            seconds = int(time_parts[2])
        elif len(time_parts) == 2:  # "MM:SS"
            hours = 0
            minutes = int(time_parts[0])
            seconds = int(time_parts[1])
        else:
            return 0
        # 计算总秒数
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        return 0


async def main():
    # 使用示例
    url = 'https://www.douyin.com/video/1'
    newUrl = getExtract_lonGurl(url)
    html_content = await get_rendered_html_win(newUrl)
    # print(html_content)

    videoUrl = extract_url(html_content)
    print(f"视频链接为：{videoUrl}")
def run_async():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if loop.is_running():
            loop.close()  # 确保事件循环关闭
def read_file(file_path):
    try:
        # 打开文件并读取内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()  # 读取文件的所有内容
        return content
    except FileNotFoundError:
        return f"Error: The file at {file_path} was not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    # run_async()
    pass
