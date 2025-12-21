# FocusGuard-backend

## 目录结构

```css
FocusGuard/
├─ backend/
│  ├─ app.py
│  ├─ camera.py
│  ├─ utils.py
│  └─ core/
│     ├─ detector.py
│     ├─ geometry.py
│     └─ rules.py
├─ main.py
└─ start.html
```

------

## 快速运行

1.**安装依赖**

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt`，可直接：

```bash
pip install flask flask-cors opencv-python mediapipe numpy
```

2.**启动后端**

```bash
python main.py
```

3.**打开网页测试**

在浏览器访问：

```cpp
http://127.0.0.1:5000/
```

- 点击 **START** 开始摄像头采集和算法处理
- 点击 **STOP** 停止
- 可查看实时画面和检测状态