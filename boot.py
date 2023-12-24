from datetime import datetime
import json
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

import flask
import json_logging
from flask import request, Response

app = flask.Flask(__name__)

json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

# 日志存放目录
log_dir = "/data/log/service/"

# init the logger as usual
logger = logging.getLogger("Flask-App-logger")
logger.setLevel(logging.DEBUG)


# 创建FileHandler，实现每小时切割一次访问日志文件
def access_log_filename():
    formatted_time = (datetime.now().strftime("%Y%m%d%H")) # cst 时间
    return os.path.join(log_dir, f"op-python-real-ip-access-{formatted_time}00.log")


# 创建 RotatingFileHandler，并设置日志格式
log_handler = TimedRotatingFileHandler(access_log_filename(), when="H", interval=1, backupCount=5, utc=True)
# log_handler = RotatingFileHandler(access_log_filename(), maxBytes=1000000, backupCount=5)

# logger.addHandler(logging.StreamHandler(sys.stdout)) # 标准输出
# 文件输出
logger.addHandler(log_handler)


def checkLogPath():
    """
     1.确保日志目录存在，如果不存在则创建
     2.创建错误给出提示
    :return:
    """
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError:
            print(f"创建日志目录失败: {log_dir}")
            exit(1)


@app.route('/')
def home():
    return "Hello world  Flask App: " + str(datetime.datetime.now())


@app.route('/get_client_ip', methods=['GET'])
def healthy_run():
    parameter_info = "healthy success"
    client = request.headers.get("x-forwarded-for", request.remote_addr)
    logger.info("Flask App Get_client_ip Info 200 request",
                extra={'props': {"server_name": 'op-python-real-ip',
                                 "remote_host": client,
                                 "request_method": request.method,
                                 "request_path": request.path,
                                 "request_size": request.content_length}}
                )
    return Response(json.dumps({"code": 200, "data": parameter_info, "clientIp": client}), mimetype='application/json')


@app.route('/get_client_ip', methods=['POST'])
def handle_post_request():
    parameter_info = "POST 请求不支持, 只支持GET"
    client = request.headers.get("x-forwarded-for", request.remote_addr)
    logger.info("Flask App Get_client_ip 400 ", extra={'props':
        {
            "server_name": 'op-python-real-ip',
            "remote_host": client,
            "request_method": request.method,
            "request_path": request.path,
            "request_size": request.content_length
        }})

    return Response(json.dumps({"code": 400, "data": parameter_info}), mimetype='application/json')

if __name__ == "__main__":
    checkLogPath()
    app.run(
    host='0.0.0.0',
    debug=False,
    port=int(8080),
    use_reloader=False)
