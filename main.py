# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :main.py
# @Time      :2025/3/1 09:02
# @Author    :Curtin

from quart import Quart, Blueprint, jsonify, send_file, redirect, request, abort
from pkcWordcloud import createWordCloud
from pkcDouYinVideo import getDyHtml, extract_url, downloadViden, getExtract_lonGurl, get_seconds_from_html
from io import BytesIO
from quart_schema import QuartSchema, tag, validate_request, validate_response, hide, validate_querystring
from utils import config, log, ApiTags, wordcloudTodo, dyQuery, dyResp, ApiErrorResponse, generate_random_name

#
version = "v1.2.0"
app = Quart(__name__)
QuartSchema(
    app,
    security=[{"apiKey": []}],
    security_schemes={
        "apiKey": {"type": "apiKey", "name": "apiKey", "in": "query"}
    },
    info={
        "title": "PKC-API",
        "version": version,
        "description": '<a href="https://github.com/curtinlv/PKC-API.git" target="_blank">开发者：Curtinlv<a>'
    },
    convert_casing=True,
    swagger_ui_path='/swagger'
)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁止缓存
app.config['TIMEOUT'] = 180  # 请求超时设置为3分钟
# 创建一个蓝图
pkcTools = Blueprint('PKC工具', __name__)

@app.errorhandler(401)
async def handle_401_error(error):
    return jsonify(ApiErrorResponse(code=401, msg="请带上 API Key 验证")), 401
@app.errorhandler(403)
async def handle_403_error(error):
    return jsonify(ApiErrorResponse(code=403, msg="无效的 API Key")), 403
@app.errorhandler(405)
async def handle_405_error(error):
    return jsonify(ApiErrorResponse(405, msg="接口已被禁用")), 405
async def verify_api_key():
    api_key = request.args.get('apiKey')
    if not api_key:
        abort(401)
    if api_key != config.apiKey:
        abort(403)

@app.before_request
async def before_request():
    # 获取当前路由的路径
    current_route = request.url_rule.rule
    # 如果当前路由不在 NO_API_KEY_REQUIRED_ROUTES 列表中，则验证 API Key
    if current_route not in config.NO_API_KEY_REQUIRED_ROUTES:
        await verify_api_key()
    if current_route in config.disableInterfaces:
        abort(405)
@pkcTools.route('/')
@hide
async def pkcApiIndex():
    return redirect('/swagger', code=301)

@pkcTools.route('/favicon.ico')
@hide
async def pkcIndexIcon():
    result = await send_file('./static/favicon.ico')
    return result

###########################【Route】###########################
########## 词云分析
@pkcTools.route('/generate_wordcloud', methods=['POST'])
@tag([ApiTags.PKC])
@validate_request(wordcloudTodo)
async def generate_wordcloud(data: wordcloudTodo):
    """
    词云生成
    <br>
    Request：
    <br>
    `text`：分析的字符串，必要
     <br>
    `width`：默认宽度，非必要
    <br>
    `height`：默认高度，非必要
    <br>
    `dpi`：默认DPI,值越大越清晰，非必要
    <br>
    `max_words`：最大词数，非必要
    <br>
    `background_color`：背景色,默认白色，非必要
    <br>
    ------
    <br>
    Response：image/png
    """
    # 解析请求参数
    text = data.text.encode('utf-8').decode('utf-8')  # 确保是UTF-8编码
    if not text:
        return jsonify({"code": 400, "msg": "请提供要分析的文本内容。"}), 400

    # 生成词云（优化字体渲染）
    try:
        wordcloud = await createWordCloud(text, data.width, data.height, data.background_color, data.max_words)
    except ValueError as e:
        return jsonify({"code": 400, "msg": f"文本分析失败: {str(e)}"}), 400
    # 生成高清图像
    img = BytesIO()
    image = wordcloud.to_image()
    # 保存为高清PNG
    image.save(img, format='PNG', dpi=(data.dpi, data.dpi), optimize=True, quality=95)
    img.seek(0)
    result = await send_file(img, mimetype='image/png')
    return result
########## 抖音视频解析
@pkcTools.route('/getDouyinVideoUrl', methods=['GET'])
@tag([ApiTags.PKC])
@validate_querystring(dyQuery)
@validate_response(dyResp, 200)
@validate_response(ApiErrorResponse, 500)
async def getDouyinVideoUrl(query_args: dyQuery):
    """
    抖音视频链接提取

    <br><br>
    `url`：抖音分享的链接<br>
    Response：<br>
    {<br>
        "videoUrl": "视频原始链接"<br>
   }   <br>
    """
    # 获取入参URL
    url = query_args.url
    # log.info(f'url={url}')
    if not url or 'douyin.com' not in url:
        return ApiErrorResponse(code=400, msg="请带上正确的参数：url"), 400
    try:
        # 获取视频链接
        newUrl = getExtract_lonGurl(url)
        html_content = await getDyHtml(newUrl)
        if not html_content:
            return ApiErrorResponse(code=500, msg="失败"), 500
        # time = get_seconds_from_html(html_content)
        # log.info(f"时长为{time}")
        video_url = extract_url(html_content)
        if video_url:
            return dyResp(video_url=video_url)
        else:
            return ApiErrorResponse(code=404, msg="视频链接提取失败！"), 404
    except Exception as e:
        return ApiErrorResponse(code=500, msg=str(e)), 500
########## 抖音视频解析响应视频
@pkcTools.route('/getDouyinVideo', methods=['GET'])
@tag([ApiTags.PKC])
@validate_querystring(dyQuery)
async def getDouyinVideo(query_args: dyQuery):
    """
    抖音视频提取
    <br><br>
    `url`：抖音分享的链接
    <br>
    Response：video/mp4
    """
    # 获取入参URL
    url = query_args.url
    if not url or 'douyin.com' not in url:
        return ApiErrorResponse(code=400, msg="请带上正确的参数：url"), 400
    try:
        # 获取视频链接
        newUrl = getExtract_lonGurl(url)
        html_content = await getDyHtml(newUrl)
        if not html_content:
            return ApiErrorResponse(code=500, msg="失败"), 500
        video_url = extract_url(html_content)
        if video_url:
            # 下载远程视频
            response = await downloadViden(video_url)
            # log.info(f'resp: {response.status_code}, {video_url}')
            if response.status_code > 206:
                return ApiErrorResponse(code=500, msg="视频下载失败！"), 500
            # 将下载的视频存储到内存中
            video_data = BytesIO(response.content)
            # # 返回视频文件，客户端会自动下载
            return await send_file(video_data, as_attachment=True, attachment_filename=f"{generate_random_name()}.mp4",
                                   mimetype='video/mp4')
        else:
            return ApiErrorResponse(code=404, msg="视频链接提取失败！"), 404
    except Exception as e:
        return ApiErrorResponse(code=500, msg=str(e)), 500
# 注册蓝图
app.register_blueprint(pkcTools, url_prefix='')

if __name__ == '__main__':
    print(f"版本：{version}")
    app.run(host='0.0.0.0', port=config.port)
