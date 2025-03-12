from requests_html import AsyncHTMLSession
from pyppeteer import launch
import re, sys, os
import requests
import asyncio
import random

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
async def save_content_to_file(content, file_path):
    # 打开文件并写入内容
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"内容已保存到 {file_path}")
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

    while attempt < max_retries:
        browser = None
        try:
            is_windows = sys.platform.startswith('win')
            # 启动指定路径的 Chromium
            browser = await launch(
                executablePath=None if is_windows else '/usr/bin/chromium',
                args=browser_args,
                headless=True,
                timeout=60000  # 60秒超时
            )
            page = await browser.newPage()
            await page.setJavaScriptEnabled(True)
            # await page.setUserAgent(headers['User-Agent'])
            # 设置页面超时和重试策略
            page.setDefaultNavigationTimeout(60000)  # 60秒
            # 等待直到所有请求完成
            response = await page.goto(url, {'waitUntil': 'networkidle2'})
            # 等待页面完全加载，包括渲染的内容和异步请求
            await page.waitFor(5000 + (attempt * 1000))  # 延迟，确保所有脚本执行完毕
            await auto_scroll(page)  # 滚动页面，加载更多内容
            content = await page.content()
            # 保存内容到文件
            # await save_content_to_file(content, file_path=r'/app/111.html')
            if required_content in content:
                return content
            else:
                # print(f"未找到, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
                attempt += 1
        except Exception as e:
            # print(f"发生异常: {str(e)[:200]}, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
            attempt += 1
        finally:
            if browser:
                await browser.close()

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
            await response.html.arender(timeout=60, sleep=3+attempt, keep_page=True, scrolldown=3)
            # 检查页面内容是否包含指定的字符串
            if required_content in response.html.html:
                await session.close()
                return response.html.html
            else:
                # print(f"未找到, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
                attempt += 1
        except Exception as e:
            # print(f"发生异常: {e}, 重试... (Attempt {attempt + 1}/{max_retries})", flush=True)
            attempt += 1
    # print("未找到，已超出最多尝试次数。", flush=True)
    await session.close()
    return None
def extract_url(text):
    # 正则表达式提取src中完整的https://v3-web.douyinvod.com链接
    pattern = r'src="(https://v3-web\.douyinvod\.com[^\s"]+)"'
    match = re.search(pattern, text)
    if match:
        return match.group(1)  # 返回匹配到的第一个结果
    else:
        return None
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

if __name__ == '__main__':
    run_async()