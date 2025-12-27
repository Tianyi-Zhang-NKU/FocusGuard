<div align="center">
  <img src="https://img.shields.io/badge/Focus-Guard-00ff88?style=for-the-badge&logo=shield&logoColor=black&labelColor=black" alt="FocusGuard Logo" />
  
  <h1 style="font-family: 'Orbitron', sans-serif;">🛡️ FocusGuard 专注守卫</h1>
  
  <p>
    <strong>AI 驱动的智能坐姿矫正与专注力监测系统 (v2.0)</strong>
  </p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Flask-2.0+-000000?style=flat-square&logo=flask&logoColor=white" />
    <img src="https://img.shields.io/badge/Vue.js-3.0+-4FC08D?style=flat-square&logo=vue.js&logoColor=white" />
    <img src="https://img.shields.io/badge/MediaPipe-Vision-0055FF?style=flat-square&logo=google&logoColor=white" />
    <img src="https://img.shields.io/badge/Style-Cyberpunk-ff00de?style=flat-square" />
  </p>

  <p>
    <em>2025 Python 语言程序设计课程大作业 | 组名：关键问题是问题的关键</em>
  </p>
</div>

---

## 📖 1. 项目简介 (Introduction)

**FocusGuard** 是一款融合了**计算机视觉 (CV)** 与 **游戏化 (Gamification)** 理念的桌面端健康辅助系统。

针对现代学生和办公人群长期面对屏幕导致的体态问题与视疲劳，本项目采用前后端分离架构。后端利用 **MediaPipe** 实时分析面部网格与身体骨骼；前端通过 **RPG 升级机制**，将枯燥的“保持专注”转化为有趣的“打怪升级”体验，帮助用户在沉浸式体验中养成健康的办公习惯。

> **🎨 设计理念**：采用 **赛博朋克 (Cyberpunk)** 视觉风格，结合 CSS3 毛玻璃特效、流光动画与 HUD 界面，打造未来科技感的交互体验。

---

## ✨ 2. 核心功能 (Key Features)

### 👁️ A. 智能视觉监测 (AI-Powered Monitoring)
基于 **OpenCV** 与 **MediaPipe** 的多维度实时分析算法：
* **📐 坐姿评估**：计算脊柱角度与头部前倾距离，实时判定“驼背”、“侧倾”等不良体态。
* **😴 疲劳检测**：
    * **EAR (Eye Aspect Ratio)**：监测闭眼时长，识别困倦/睡眠。
    * **MAR (Mouth Aspect Ratio)**：识别打哈欠频率。
* **📏 距离监测**：估算人脸与屏幕的距离，防止贴屏过近造成视力损伤。
* **☀ 环境光线分析**：利用 HSV 颜色空间计算环境亮度，当光线过暗 (<60) 时发出护眼提醒。

### 🎮 B. 沉浸式游戏化系统 (RPG System)
将专注过程转化为角色成长，提升用户粘性：
* **经验值 (XP)**：每保持专注 1 秒获得 1 XP，经验条满额自动升级。
* **军衔体系**：
    * `LV 1-5`: 🛡️ **见习守卫**
    * `LV 6-10`: 🕵️ **资深特工**
    * `LV 11-20`: ⚡ **赛博大师**
    * `LV 20+`: 👑 **传奇领主**
* **多用户存档**：不同账号（登录/注册）拥有独立的等级与经验记录。
* **HUD 状态栏**：顶部导航栏实时展示等级徽章与 XP 流光进度条。

### ⚡ C. 交互与反馈 (Interaction)
* **⏱️ 自定义番茄钟**：支持用户自由设定 **1 - 180 分钟** 的专注倒计时。
* **🚨 多重报警机制**：
    * **视觉**：全屏红色闪烁警告 + 视频画面 HUD 文字覆盖。
    * **听觉**：内置 Web Audio API 蜂鸣报警音（无延迟，无需外部文件）。
* **📈 数据可视化**：基于 **ECharts** 的实时折线图，展示最近 60 秒的“姿态完整度”趋势。

### 👤 D. 用户系统 (User System)
* **账号管理**：基于 SQLite 本地数据库，支持注册与登录。
* **游客模式**：未登录即可使用基础监测功能（不记录 RPG 存档）。
* **历史回溯**：记录每次专注过程中的异常状态统计。

---

## 🛠️ 3. 技术栈 (Tech Stack)

| 模块 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **Frontend** | **Vue 3** | 核心框架 (Composition API + Vite) |
| UI Library | **Element Plus** | 深度定制的深色主题组件库 |
| Visualization | **ECharts 5** | 实时数据大屏可视化 |
| Animation | **GSAP / Vanilla-Tilt** | 平滑过渡与 3D 悬停视差特效 |
| Styling | **CSS3 Variables** | 霓虹配色系统 (#ff00de / #00ff88) |
| **Backend** | **Flask** | Python 微型 Web 框架，处理 API 与视频流 |
| CV Engine | **MediaPipe** | 高精度 BlazePose 与 Face Mesh 模型 |
| Image Process | **OpenCV (cv2)** | 图像流处理、色彩空间转换、绘图 |
| Database | **SQLite** | 轻量级本地存储，零配置 |

---

## 📂 4. 项目结构 (Project Structure)

```text
FocusGuard/
├── backend/                  # Python 后端核心
│   ├── core/
│   │   └── processor.py      # [核心算法] 姿态/人脸/光线分析实现
│   ├── app.py                # Flask 入口：API 路由与视频流推送
│   ├── database.py           # SQLite 数据库模型与操作
│   ├── config.py             # 全局配置 (阈值/常量)
│   └── requirements.txt      # Python 依赖清单
│
└── frontend/                 # Vue 前端应用
    ├── src/
    │   ├── components/       # 公共组件 (LoginModal, etc.)
    │   ├── views/
    │   │   └── DashboardView.vue # [核心视图] 仪表盘：整合视频、图表与 RPG 逻辑
    │   ├── App.vue           # 根组件 (含全局粒子背景)
    │   └── main.js           # Vue 入口配置
    ├── index.html            # HTML 模板
    └── vite.config.js        # Vite 构建配置

```

---

## 🚀 5. 安装与运行 (Setup Guide)

请确保本地环境已安装 **Python 3.8+** 和 **Node.js 16+**。

### 🟢 后端启动 (Backend)

1. 进入后端目录：
```bash
cd backend

```


2. 创建并激活虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

```


3. 安装依赖：
```bash
pip install -r requirements.txt

```


4. 启动服务：
```bash
python app.py

```


> 后端服务默认运行在: `http://localhost:5000`



### 🔵 前端启动 (Frontend)

1. 进入前端目录（打开新终端）：
```bash
cd frontend

```


2. 安装依赖：
```bash
npm install

```


3. 启动开发服务器：
```bash
npm run dev

```


> 前端页面默认运行在: `http://localhost:5173`



---

## 👥 6. 团队分工 (Team)

| 成员 | 角色 | 主要职责 |
| --- | --- | --- |
| **龙辅仁** | 全栈开发 / 组长 | 系统架构设计 (Flask+Vue)，前后端视频流整合，可视化报表开发 |
| **赵迎迎** | 核心算法 | Python CV 核心实现 (MediaPipe Pose/Face)，坐姿判定与疲劳算法设计 |
| **李紫嫣** | 后端逻辑 | RESTful API 设计，数据库结构设计，多用户系统逻辑实现 |
| **张天译** | 文档与测试 | 需求分析，多场景系统测试 (光线/姿态)，撰写实验报告与用户手册 |

---

## 📜 版权说明 (License)

本项目仅供 **南开大学 2025 Python 语言程序设计** 课程作业展示使用。

**隐私声明 (Privacy Policy)**:
所有摄像头图像数据仅在用户本地设备的内存中进行实时分析处理，**绝不上传至任何云端服务器**，充分保障用户隐私安全。

---

<div align="center">
<sub>Created with ❤️ by FocusGuard Team</sub>
</div>

```

```
