# 使用多架构兼容的 Python 基础镜像
FROM python:3.9-slim
# 设置工作目录
WORKDIR /app
COPY PKC-API/ .
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    build-essential \
    python3-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    libpng-dev \
    && apt-get install -y --no-install-recommends \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxtst6 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libxcb1 \
    libxss1 \
    libxkbcommon0 \
    xvfb \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# 设置 Chromium 环境变量
ENV FONT_PATH=/app/static/pkc.ttf
ENV DISPLAY=:99
ENV CHROMIUM_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 80

# 启动脚本
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]

# buildx build --platform linux/amd64,linux/arm64 -t curtinlv/pkc-api:latest --push .
