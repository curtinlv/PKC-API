# PKC-API 
### v1.1.0
### API接口名称
***    
- *1.词云分析*
- *2.抖音视频解析*
- *3. ...*
***
## Ⅰ.搭建PKC-API
环境要求：   
CPU: 2核心或以上    
内存: 4GB或更高  
其他：国内IP
### 方式一：Docker一键部署
```bash
docker run -d --name pkc-api -p 80:80 curtinlv/pkc-api:latest
```

### 方式二：Docker-compose部署    
建立文件`docker-compose.yaml`，文件内容以下：
```yaml
version: '3'
services:
  pkc-api:
    image: curtinlv/pkc-api:latest
    container_name: pkc-api
    ports:
      - "80:80"  # 可改端口，如 8888:80
#    volumes:
#      - ./static/pkc.ttf:/app/static/pkc.ttf #词云字体
    restart: unless-stopped
```
启动
```bash
docker-compose up -d
```
### 方式三：Python启动
版本要求：`python3.9 +` 
```bash
# 拉取本项目
git clone https://github.com/curtinlv/PKC-API.git
# 切换项目目录
cd PKC-API
# 安装依赖包
pip install -r requirements.txt 
# 词云字体（可自定义）
export FONT_PATH=./static/pkc.ttf 
# 启动
python main.py  
# 或
nohup python main.py >./log.log 2>&1 & #后台启动
````
## Ⅱ.Swagger API调试页面
```html
http://ip/swagger
```
![swagger.png](swagger.png)