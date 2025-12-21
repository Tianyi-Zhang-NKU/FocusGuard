from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import threading
import time
import datetime
import cv2

import config
import database

# 导入假数据模块
# 注释：因为队友B还没写好算法，我先用这个假的测试一下接口通不通
from placeholders import MockCamera, MockAlgorithm

app = Flask(__name__)
CORS(app)  # 解决跨域问题，不然Vue前端访问会报错

# 全局变量：用来在不同线程之间共享数据
# 比如后台线程算出来“累了”，API线程得能读取到
global_state = {
    "posture": "初始化...",
    "fatigue": 0.0,
    "is_alert": False,
    "timestamp": ""
}

# 线程锁：防止读写冲突
state_lock = threading.Lock()

# 启动时初始化
database.init_db()
camera = MockCamera()
algorithm = MockAlgorithm()


def background_task():
    """
    后台任务：不停地读取摄像头和跑算法
    这个函数会一直死循环运行，不能卡住主程序
    """
    print("后台线程开始运行...")
    last_save_time = time.time()

    while True:
        # 1. 获取画面
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue

        # 2. 调用算法分析
        result = algorithm.analyze(frame)
        show_frame = result['frame']
        data = result['data']  # 这是具体的数值

        # 3. 更新全局变量（加锁是为了安全）
        with state_lock:
            global_state['posture'] = data['posture']
            global_state['fatigue'] = data['fatigue']
            global_state['is_alert'] = data['is_alert']
            global_state['timestamp'] = datetime.datetime.now().strftime("%H:%M:%S")

        # 4. 定时保存到数据库 (每隔几秒存一次，不用太频繁)
        now = time.time()
        if now - last_save_time > config.SAVE_INTERVAL:
            database.add_log(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data['posture'],
                data['fatigue'],
                data['is_alert']
            )
            last_save_time = now

        # 5. 把图片转成视频流格式发给前端
        ret, buffer = cv2.imencode('.jpg', show_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# === 下面是给前端调用的接口 ===

@app.route('/')
def index():
    return "后端运行正常"


# 视频流地址：<img src="/video_feed">
@app.route('/video_feed')
def video_feed():
    return Response(background_task(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 获取实时状态
@app.route('/api/status', methods=['GET'])
def get_status():
    with state_lock:
        return jsonify(global_state)


# 获取历史数据（画图表用）
@app.route('/api/history', methods=['GET'])
def get_history():
    data = database.get_logs()
    return jsonify(data)


# 注册功能
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    # 简单的非空判断
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "账号密码不能为空"}), 400

    # 调用数据库模块去注册
    success, msg = database.add_user(data['username'], data['password'])
    if success:
        return jsonify({"code": 200, "msg": msg})
    else:
        return jsonify({"code": 409, "msg": msg}), 409


# 登录功能
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"msg": "请输入账号密码"}), 400

    success, msg = database.check_login(data['username'], data['password'])
    if success:
        return jsonify({"code": 200, "msg": msg, "user": data['username']})
    else:
        return jsonify({"code": 401, "msg": msg}), 401


if __name__ == '__main__':
    # threaded=True 必须开，不然视频流会卡死
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)