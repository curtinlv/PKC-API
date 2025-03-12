from dataclasses import dataclass, field

@dataclass
class wordcloudTodo:
    text: str = field(default='PKC很棒，也很简单')
    width: int = field(default=600)  # 默认宽度
    height: int = field(default=600)  # 默认高度
    dpi: int = field(default=400)   # 默认DPI,值越大越清晰
    max_words: int = field(default=100)  # 最大词数
    background_color: str = field(default='white')   # 背景色,默认白色

@dataclass
class dyQuery:
    url: str
    # ua: str = field(default=None)

@dataclass
class dyResp:
    video_url: str = '视频原始链接'

@dataclass
class ApiErrorResponse:
    code: int = 500
    error: str = '错误信息'

@dataclass
class ApiSuccessResponse:
    """
    Default success response
    """
