// DOM元素
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const postureCanvas = document.getElementById('posture-canvas');
const ctx = canvas.getContext('2d');
const postureCtx = postureCanvas.getContext('2d');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const calibrateBtn = document.getElementById('calibrate-btn');
const cameraSelect = document.getElementById('camera-select');
const videoOverlay = document.getElementById('video-overlay');
const postureScore = document.getElementById('posture-score');
const focusScore = document.getElementById('focus-score');
const spineAngle = document.getElementById('spine-angle');
const headAngle = document.getElementById('head-angle');
const postureProgress = document.getElementById('posture-progress');
const focusProgress = document.getElementById('focus-progress');
const postureFeedback = document.getElementById('posture-feedback');
const logEntries = document.getElementById('log-entries');

// 状态变量
let isMonitoring = false;
let stream = null;
let animationId = null;
let calibrationDone = false;
let goodPostureTime = 0;
let monitoringStartTime = null;

// 模拟的姿势数据
let simulatedPosture = {
    spineAngle: 5,
    headAngle: 3,
    shoulderBalance: 2,
    postureScore: 85,
    focusScore: 78,
    isGoodPosture: true
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 设置姿势画布尺寸
    postureCanvas.width = 200;
    postureCanvas.height = 300;
    
    // 获取摄像头列表
    getCameraDevices();
    
    // 添加事件监听器
    startBtn.addEventListener('click', startMonitoring);
    stopBtn.addEventListener('click', stopMonitoring);
    calibrateBtn.addEventListener('click', calibratePosture);
    cameraSelect.addEventListener('change', changeCamera);
    
    // 添加日志
    addLogEntry("系统初始化完成，等待摄像头输入");
});

// 获取摄像头设备
async function getCameraDevices() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        cameraSelect.innerHTML = '<option value="">选择摄像头</option>';
        
        videoDevices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `摄像头 ${cameraSelect.options.length}`;
            cameraSelect.appendChild(option);
        });
        
        if (videoDevices.length > 0) {
            cameraSelect.value = videoDevices[0].deviceId;
        }
    } catch (error) {
        console.error('获取摄像头设备失败:', error);
        addLogEntry("获取摄像头设备失败: " + error.message);
    }
}

// 开始监测
async function startMonitoring() {
    try {
        addLogEntry("正在启动摄像头...");
        
        const deviceId = cameraSelect.value;
        const constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: "user"
            }
        };
        
        if (deviceId) {
            constraints.video.deviceId = { exact: deviceId };
        }
        
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        video.srcObject = stream;
        
        // 等待视频数据加载
        video.onloadedmetadata = () => {
            video.play();
            
            // 设置画布尺寸与视频一致
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // 开始绘制
            isMonitoring = true;
            monitoringStartTime = Date.now();
            videoOverlay.classList.add('hidden');
            startBtn.disabled = true;
            stopBtn.disabled = false;
            
            addLogEntry("摄像头启动成功，开始姿势监测");
            
            // 开始模拟姿势检测循环
            simulatePoseDetection();
            
            // 如果没有校准，提示用户进行校准
            if (!calibrationDone) {
                setTimeout(() => {
                    addLogEntry("建议：请点击'校准姿势'按钮进行初始姿势校准");
                }, 2000);
            }
        };
        
    } catch (error) {
        console.error('启动摄像头失败:', error);
        addLogEntry("摄像头启动失败: " + error.message);
        alert("无法访问摄像头。请确保已授予摄像头权限并尝试刷新页面。");
    }
}

// 停止监测
function stopMonitoring() {
    isMonitoring = false;
    
    if (animationId) {
        cancelAnimationFrame(animationId);
        animationId = null;
    }
    
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    video.srcObject = null;
    videoOverlay.classList.remove('hidden');
    startBtn.disabled = false;
    stopBtn.disabled = true;
    
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    postureCtx.clearRect(0, 0, postureCanvas.width, postureCanvas.height);
    
    addLogEntry("监测已停止");
}

// 校准姿势
function calibratePosture() {
    if (!isMonitoring) {
        alert("请先启动摄像头再进行校准");
        return;
    }
    
    addLogEntry("正在进行姿势校准...");
    
    // 模拟校准过程
    setTimeout(() => {
        calibrationDone = true;
        goodPostureTime = 0;
        
        // 设置理想姿势参数
        simulatedPosture = {
            spineAngle: 0,
            headAngle: 0,
            shoulderBalance: 0,
            postureScore: 95,
            focusScore: 85,
            isGoodPosture: true
        };
        
        updatePostureVisualization();
        updateStatusIndicators();
        
        addLogEntry("姿势校准完成！已记录您的理想坐姿");
        postureFeedback.textContent = "校准完成！请保持这个姿势";
        
        // 3秒后恢复普通反馈
        setTimeout(() => {
            postureFeedback.textContent = "姿势良好，请保持";
        }, 3000);
    }, 1500);
}

// 切换摄像头
async function changeCamera() {
    if (!isMonitoring) return;
    
    // 停止当前流
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
    
    // 重新启动监测
    await startMonitoring();
}

// 模拟姿势检测（在实际应用中，这里会调用TensorFlow.js PoseNet模型）
function simulatePoseDetection() {
    if (!isMonitoring) return;
    
    // 在画布上绘制视频帧（保持简单，只显示视频）
    ctx.save();
    ctx.scale(-1, 1); // 水平翻转以匹配视频镜像
    ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
    ctx.restore();
    
    // 不再绘制模拟的姿势关键点
    
    // 更新模拟的姿势数据（随机变化以模拟实时变化）
    updateSimulatedPostureData();
    
    // 更新状态显示
    updateStatusIndicators();
    updatePostureVisualization();
    
    // 检查姿势是否需要提醒
    checkPostureAlert();
    
    // 记录良好姿势时间
    if (simulatedPosture.isGoodPosture) {
        goodPostureTime += 100; // 模拟每100ms增加
    }
    
    // 继续循环
    animationId = requestAnimationFrame(simulatePoseDetection);
}

// 更新模拟的姿势数据
function updateSimulatedPostureData() {
    // 随机变化模拟实时数据
    const change = (Math.random() - 0.5) * 4;
    const focusChange = (Math.random() - 0.5) * 3;
    
    // 脊柱角度随机变化（但保持在合理范围内）
    simulatedPosture.spineAngle += change;
    simulatedPosture.spineAngle = Math.max(0, Math.min(25, simulatedPosture.spineAngle));
    
    // 头部角度随机变化
    simulatedPosture.headAngle += change * 0.8;
    simulatedPosture.headAngle = Math.max(-5, Math.min(20, simulatedPosture.headAngle));
    
    // 更新姿势评分
    simulatedPosture.postureScore = Math.max(30, Math.min(99, 
        100 - simulatedPosture.spineAngle * 2 - Math.abs(simulatedPosture.headAngle) * 1.5));
    
    // 更新专注度评分（随时间缓慢下降，良好姿势时回升）
    simulatedPosture.focusScore += focusChange;
    if (simulatedPosture.postureScore > 80) {
        simulatedPosture.focusScore += 0.5; // 良好姿势有助于专注
    }
    simulatedPosture.focusScore = Math.max(40, Math.min(95, simulatedPosture.focusScore));
    
    // 判断姿势是否良好
    simulatedPosture.isGoodPosture = 
        simulatedPosture.spineAngle < 15 && 
        simulatedPosture.headAngle < 15 && 
        simulatedPosture.postureScore > 70;
}

// 更新状态指示器
function updateStatusIndicators() {
    // 更新数值显示
    postureScore.textContent = Math.round(simulatedPosture.postureScore);
    focusScore.textContent = Math.round(simulatedPosture.focusScore);
    spineAngle.textContent = Math.round(simulatedPosture.spineAngle) + "°";
    headAngle.textContent = Math.round(simulatedPosture.headAngle) + "°";
    
    // 更新进度条
    postureProgress.style.width = simulatedPosture.postureScore + "%";
    focusProgress.style.width = simulatedPosture.focusScore + "%";
    
    // 根据评分设置颜色
    updateStatusColor(postureScore, simulatedPosture.postureScore, 80, 60);
    updateStatusColor(focusScore, simulatedPosture.focusScore, 75, 55);
    updateStatusColor(spineAngle, simulatedPosture.spineAngle, 10, 15, true);
    updateStatusColor(headAngle, simulatedPosture.headAngle, 10, 15, true);
    
    // 更新进度条颜色
    postureProgress.style.backgroundColor = getColorForScore(simulatedPosture.postureScore);
    focusProgress.style.backgroundColor = getColorForScore(simulatedPosture.focusScore);
}

// 更新状态颜色
function updateStatusColor(element, value, goodThreshold, warningThreshold, reverse = false) {
    element.classList.remove("status-good", "status-warning", "status-bad");
    
    if (reverse) {
        // 值越小越好（如角度）
        if (value <= goodThreshold) {
            element.classList.add("status-good");
        } else if (value <= warningThreshold) {
            element.classList.add("status-warning");
        } else {
            element.classList.add("status-bad");
        }
    } else {
        // 值越大越好（如评分）
        if (value >= goodThreshold) {
            element.classList.add("status-good");
        } else if (value >= warningThreshold) {
            element.classList.add("status-warning");
        } else {
            element.classList.add("status-bad");
        }
    }
}

// 根据评分获取颜色
function getColorForScore(score) {
    if (score >= 80) return "#10b981";
    if (score >= 60) return "#f59e0b";
    return "#ef4444";
}

// 更新姿势可视化
function updatePostureVisualization() {
    const width = postureCanvas.width;
    const height = postureCanvas.height;
    
    // 清空画布
    postureCtx.clearRect(0, 0, width, height);
    
    // 绘制背景
    postureCtx.fillStyle = '#0f172a';
    postureCtx.fillRect(0, 0, width, height);
    
    // 根据姿势数据绘制示意图
    const spineAngleRad = (simulatedPosture.spineAngle * Math.PI) / 180;
    const headAngleRad = (simulatedPosture.headAngle * Math.PI) / 180;
    
    // 绘制理想姿势参考线（灰色）
    postureCtx.strokeStyle = '#334155';
    postureCtx.lineWidth = 2;
    postureCtx.setLineDash([5, 5]);
    
    // 理想脊柱线
    postureCtx.beginPath();
    postureCtx.moveTo(width/2, 50);
    postureCtx.lineTo(width/2, height - 50);
    postureCtx.stroke();
    
    // 理想头部位置
    postureCtx.beginPath();
    postureCtx.arc(width/2, 30, 15, 0, Math.PI * 2);
    postureCtx.stroke();
    
    postureCtx.setLineDash([]);
    
    // 绘制实际姿势（彩色）
    // 脊柱
    postureCtx.strokeStyle = getColorForScore(simulatedPosture.postureScore);
    postureCtx.lineWidth = 4;
    postureCtx.beginPath();
    
    const spineTopX = width/2 + Math.sin(spineAngleRad) * 30;
    const spineBottomX = width/2 - Math.sin(spineAngleRad) * 30;
    
    postureCtx.moveTo(spineTopX, 80);
    postureCtx.lineTo(spineBottomX, height - 80);
    postureCtx.stroke();
    
    // 头部
    const headX = spineTopX + Math.sin(headAngleRad) * 20;
    postureCtx.beginPath();
    postureCtx.arc(headX, 50, 20, 0, Math.PI * 2);
    postureCtx.stroke();
    
    // 肩膀
    postureCtx.beginPath();
    postureCtx.moveTo(spineTopX - 40, 100);
    postureCtx.lineTo(spineTopX + 40, 100);
    postureCtx.stroke();
    
    // 显示角度
    postureCtx.fillStyle = '#e2e8f0';
    postureCtx.font = '12px Arial';
    postureCtx.fillText(`脊柱: ${Math.round(simulatedPosture.spineAngle)}°`, 10, 20);
    postureCtx.fillText(`头部: ${Math.round(simulatedPosture.headAngle)}°`, 10, 40);
}

// 检查姿势是否需要提醒
function checkPostureAlert() {
    // 如果姿势不良超过5秒，记录提醒
    if (!simulatedPosture.isGoodPosture) {
        // 在实际应用中，这里可以触发声音或视觉提醒
        postureFeedback.textContent = "检测到不良姿势，请调整坐姿！";
        postureFeedback.style.color = "#ef4444";
        
        // 每10秒记录一次提醒（避免重复记录）
        const now = Date.now();
        if (!simulatedPosture.lastAlertTime || now - simulatedPosture.lastAlertTime > 10000) {
            simulatedPosture.lastAlertTime = now;
            addLogEntry("检测到不良姿势，请挺直脊柱，收回头部");
        }
    } else {
        // 姿势良好时的反馈
        const minutes = Math.floor(goodPostureTime / 60000);
        const seconds = Math.floor((goodPostureTime % 60000) / 1000);
        
        if (goodPostureTime > 300000) { // 5分钟以上
            postureFeedback.textContent = `优秀！已保持良好姿势${minutes}分${seconds}秒`;
            postureFeedback.style.color = "#10b981";
        } else if (goodPostureTime > 60000) { // 1分钟以上
            postureFeedback.textContent = `良好！已保持良好姿势${minutes}分${seconds}秒`;
            postureFeedback.style.color = "#10b981";
        } else {
            postureFeedback.textContent = "姿势良好，请保持";
            postureFeedback.style.color = "#94a3b8";
        }
    }
    
    // 专注度提醒
    if (simulatedPosture.focusScore < 60) {
        // 每30秒记录一次专注度提醒
        const now = Date.now();
        if (!simulatedPosture.lastFocusAlertTime || now - simulatedPosture.lastFocusAlertTime > 30000) {
            simulatedPosture.lastFocusAlertTime = now;
            addLogEntry("专注度下降，建议短暂休息或调整姿势");
        }
    }
}

// 添加日志条目
function addLogEntry(message) {
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `
        <div class="log-time">${timeString}</div>
        <div>${message}</div>
    `;
    
    logEntries.prepend(logEntry);
    
    // 限制日志数量
    if (logEntries.children.length > 10) {
        logEntries.removeChild(logEntries.lastChild);
    }
}