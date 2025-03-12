from wordcloud import WordCloud
async def createWordCloud(text, width, height, background_color, max_words):
    # 配置词云参数
    wc_config = {
        'width': width,
        'height': height,
        'background_color': background_color,
        'max_words': max_words,
        'scale': 3,  # 提升渲染清晰度
        'min_font_size': 10  # 最新字体大小
        # 'collocations': False  # 禁用词组组合
    }

    # 生成词云（优化字体渲染）
    try:
        wordcloud = WordCloud(**wc_config).generate(text)
        return wordcloud
    except ValueError as e:
        return None