#使用基础镜像
FROM python:3.6.8 As builder

#指定工作工作目录
WORKDIR /xiaolige/app/op-python-real-ip

#拷贝pip依赖包文件并进行安装
COPY requirements.txt .
RUN  pip install --upgrade pip  &&  pip install  flask  json-logging==1.3.0

#引入python:3.6.8-alpine3.8 精简版
FROM python:3.6.8-alpine3.8

#Dockerfile多阶段构建从Docker 17.05版本以后，新增了Dockerfile多阶段构建.
COPY --from=builder /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

# Set 阿里云软件更新源,安装时间和curl命令和目录调整
RUN   sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
apk add --no-cache tzdata &&  apk add curl && \
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
echo $TZ > /etc/timezone && mkdir -p /xiaolige/app/op-python-real-ip/ && mkdir /data/log/service -p  && chmod 775 -R /xiaolige
#设置环境变量
ENV TZ=Asia/Shanghai LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

#开放应用端口
EXPOSE 8080

#工作路径
WORKDIR /xiaolige/app/op-python-real-ip/

#复制本地ops-py-flask-api 目录到容器工作目录
COPY boot.py .

#执行容器启动运行flask应用命令
CMD ["python","boot.py"]
