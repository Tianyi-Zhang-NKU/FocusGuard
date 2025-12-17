# FocusGuard 运行说明

本项目包含独立的前端和后端，您需要分别在各自的目录中安装依赖并启动它们。

## 环境准备

请确保您的电脑上已经安装了以下软件：
- Python (3.8 或更高版本)
- Node.js (16.x 或更高版本)
- pip (通常随 Python 一起安装)
- npm (通常随 Node.js 一起安装)

## 后端启动步骤 (Backend)

1. **进入后端目录**
   ```bash
   cd FocusGuard/backend
   ```

2. **创建并激活虚拟环境**
   - **Windows:**
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动后端服务**
   ```bash
   python app.py
   ```
   当您看到服务成功运行的提示时，请不要关闭此终端窗口。

## 前端启动步骤 (Frontend)

1. **打开一个新的终端窗口**。

2. **进入前端目录**
   ```bash
   cd FocusGuard/frontend
   ```

3. **安装依赖**
   ```bash
   npm install
   ```

4. **启动前端开发服务器**
   ```bash
   npm run dev
   ```

## 访问应用

当后端和前端服务都成功运行后，您可以在浏览器中打开前端服务启动时提示的地址（通常是 `http://localhost:5173` 或类似地址）来访问和使用本应用。
