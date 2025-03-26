import logging
import colorlog
import time
import sys

def print_header():
    print("\n" + "="*50, flush=True)
    print("        ____    __  __     ____  ", flush=True)
    print("       |  _ \   | |/ /    / ___| ", flush=True)
    print("       | |_) |  | ' /    | |     ", flush=True)
    print("       |  __/   | . \    | |____  ", flush=True)
    print("       |_|      |_|\_\\   |______\ ", flush=True)
    print("\n" + "=" * 50, flush=True)
    print("Initializing PKC-API...\n", flush=True)
print_header()
def typing_effect(text, delay=0.1):
    """模拟打字效果"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()  # 打印新的一行

class Logger:
    def __init__(self, log_level=logging.DEBUG):
        # 创建一个日志器
        self.logger = logging.getLogger()

        # 设置日志级别
        self.logger.setLevel(log_level)

        # 创建带颜色的流处理器
        log_handler = colorlog.StreamHandler()

        # 创建带颜色的日志格式
        formatter = colorlog.ColoredFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        # 设置日志格式
        log_handler.setFormatter(formatter)

        # 将处理器添加到日志器
        self.logger.addHandler(log_handler)

    def get_logger(self):
        """返回日志器对象"""
        return self.logger

# 示例：如何在其他模块中使用这个带颜色的 Logger 类
# 创建日志实例
log = Logger(log_level=logging.INFO).get_logger()

# 在需要使用日志的模块中调用 Logger
if __name__ == '__main__':
    # 创建日志实例
    logger = Logger().get_logger()
    # 使用 logger 打印日志
    logger.debug("这是一个调试信息")  # 蓝色
    logger.info("这是一个普通信息")  # 绿色
    logger.warning("这是一个警告信息")  # 黄色
    logger.error("这是一个错误信息")  # 红色
    logger.critical("这是一个严重错误信息")  # 粗体红色
