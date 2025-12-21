<template>
  <div class="dashboard-container">
    <header class="app-header">
      <div class="header-left">
        <h1 style="cursor: pointer">FocusGuard-专注守卫 <span class="subtitle">仪表盘</span></h1>
      </div>
      <div class="header-right">
        <!-- Auth Controls -->
        <div v-if="isLoggedIn" class="user-info">
          <span class="username"><i class="fas fa-user-astronaut"></i> {{ currentUser }}</span>
          <button class="logout-btn" @click="handleLogout">退出</button>
        </div>
        <button v-else class="login-btn-header" @click="showLoginModal = true">
          <i class="fas fa-sign-in-alt"></i> 登录 / 注册
        </button>

        <button class="theme-toggle" @click="$emit('toggle-theme')">
          <i class="fas fa-palette"></i> 切换主题
        </button>
      </div>
    </header>

    <div class="main-content">
      <div class="left-panel glass-panel" v-tilt>
        <div class="panel-header"><h2><i class="fas fa-video"></i> 传感器画面</h2></div>
        
        <div class="video-wrapper">
          <div class="video-container">
            <!-- HUD Corners -->
            <div class="hud-corner top-left"></div>
            <div class="hud-corner top-right"></div>
            <div class="hud-corner bottom-left"></div>
            <div class="hud-corner bottom-right"></div>
            
            <img id="video" :src="videoStreamUrl" alt="视频流" />
            <div v-if="!isMonitoring" class="video-overlay-standby">
              <div class="icon-pulse"><i class="fas fa-power-off"></i></div>
              <h3>{{ backendStatus }}</h3>
            </div>
            <div class="tech-scan-grid" v-if="isMonitoring"></div>
          </div>
        </div>

        <div class="controls">
          <button class="btn btn-primary" @click="startMonitoring" :disabled="isMonitoring">
            <i class="fas fa-stopwatch"></i> {{ isMonitoring ? formatTime(pomodoroTime) : '开启专注 (25min)' }}
          </button>
          <button class="btn btn-danger" @click="stopMonitoring" :disabled="!isMonitoring">
            <i class="fas fa-stop"></i> 停止
          </button>
          <button class="btn btn-secondary" @click="isMuted = !isMuted">
            <i :class="isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up'"></i>
          </button>
          <button class="btn btn-secondary" @click="showHistory">
            <i class="fas fa-history"></i> 历史
          </button>
        </div>
      </div>

      <div class="right-panel glass-panel" v-tilt>
        <div class="panel-header"><h2><i class="fas fa-chart-network"></i> 生物特征</h2></div>

        <div class="status-indicators">
          <div class="status-item">
            <div class="status-label">姿态完整度</div>
            <div class="status-row">
              <div class="status-value tech-font" :style="{ color: 'var(--primary-color)' }">
                {{ tweenedPosture.toFixed(0) }}<span class="unit">%</span>
              </div>
              <div class="progress-bg">
                <div class="progress-bar" 
                     :style="{ width: tweenedPosture + '%', backgroundColor: 'var(--primary-color)' }">
                  <div class="progress-glare"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="status-item">
            <div class="status-label">专注指数</div>
            <div class="status-row">
              <div class="status-value tech-font" :style="{ color: 'var(--primary-color)' }">
                {{ tweenedFocus.toFixed(0) }}<span class="unit">%</span>
              </div>
              <div class="progress-bg">
                <div class="progress-bar" 
                     :style="{ width: tweenedFocus + '%', backgroundColor: 'var(--primary-color)' }">
                  <div class="progress-glare"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 📈 实时姿态完整度折线图 -->
          <div class="chart-wrapper">
            <div class="chart-header">姿态完整度趋势 (60s)</div>
            <div ref="chartRef" class="focus-chart"></div>
          </div>

           <div class="posture-visualization">
            <div class="feedback-box" :class="{'active': isMonitoring}">
              {{ feedbackText }}
            </div>
          </div>
          
           <div class="log-container glass-inset">
             <div v-for="(log, i) in logs" :key="i" class="log-entry">
               <span class="log-time">></span> {{ log.message }}
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- History Dialog -->
    <el-dialog v-model="historyVisible" title="历史监测记录" width="50%">
      <el-table :data="historyData" style="width: 100%" height="400">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="posture" label="坐姿状态" width="180" />
        <el-table-column prop="fatigue" label="疲劳状态" />
      </el-table>
    </el-dialog>

    <!-- 🔴 全屏警告弹窗 -->
    <div v-if="showWarning" class="warning-overlay">
      <div class="warning-box">
        <div class="warning-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h2>⚠ 警告：状态异常 ⚠</h2>
        <p>{{ warningMessage }}</p>
        <p class="sub-warning">请立即调整坐姿或休息！</p>
      </div>
    </div>

    <!-- Login Modal Component -->
    <LoginModal v-model="showLoginModal" @login-success="onLoginSuccess" />

  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount, shallowRef, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import gsap from 'gsap'; // 引入动画库
import * as echarts from 'echarts'; // 引入 ECharts
import LoginModal from '../components/LoginModal.vue';
import { ElNotification } from 'element-plus'; // 引入通知

const router = useRouter();
const isMonitoring = ref(false);
const backendStatus = ref('待机');
const videoStreamUrl = ref('');
const logs = ref([{message: '系统已初始化。'}]);
const feedbackText = ref('等待信号...');

// Chart State
const chartRef = ref(null);
const chartInstance = shallowRef(null);
const focusHistory = ref([]);

// Warning State
const showWarning = ref(false);
const warningMessage = ref('');

// Sound & Interaction State
const ALERT_SOUND = "data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU"; // Short beep placeholder
const isMuted = ref(false);
const badPostureStreak = ref(0);
const pomodoroTime = ref(25 * 60);
let timerInterval = null;

const playAlert = () => {
  if (!isMuted.value) {
    new Audio(ALERT_SOUND).play().catch(() => {}); // Catch error if user hasn't interacted
  }
};

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

// Auth State
const showLoginModal = ref(false);
const isLoggedIn = ref(false);
const currentUser = ref('');

// History Data
const historyVisible = ref(false);
const historyData = ref([]);

// 真实数据
const scores = reactive({ posture: 0, focus: 0 });
// 用于显示的动画数据
const tweenedPosture = ref(0);
const tweenedFocus = ref(0);

// 监听真实数据变化，驱动 GSAP 动画
watch(() => scores.posture, (newVal) => {
  gsap.to(tweenedPosture, { duration: 0.8, value: newVal, ease: "power2.out" });
});
watch(() => scores.focus, (newVal) => {
  gsap.to(tweenedFocus, { duration: 0.8, value: newVal, ease: "power2.out" });
});

let dataFetcher = null;

const startMonitoring = () => {
  isMonitoring.value = true;
  videoStreamUrl.value = 'http://localhost:5000/video_feed';
  logs.value.unshift({message: '流连接已建立。'});
  
  // Pomodoro Timer Logic
  pomodoroTime.value = 25 * 60;
  if(timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    pomodoroTime.value--;
    if (pomodoroTime.value <= 0) {
      stopMonitoring();
      ElNotification.success({
        title: '专注完成',
        message: '您已完成一个番茄钟，请休息5分钟！',
        duration: 0
      });
    }
  }, 1000);

  dataFetcher = setInterval(fetchStatus, 1500);
};

const stopMonitoring = () => {
  isMonitoring.value = false;
  videoStreamUrl.value = '';
  scores.posture = 0;
  scores.focus = 0;
  if(dataFetcher) clearInterval(dataFetcher);
  if(timerInterval) clearInterval(timerInterval);
};

const showHistory = async () => {
  if(!isLoggedIn.value) {
    showLoginModal.value = true; // Not logged in? Show modal instead
    return;
  }
  try {
    const res = await axios.get(`http://localhost:5000/api/history?username=${currentUser.value}`);
    historyData.value = res.data;
    historyVisible.value = true;
  } catch (e) {
    console.error("Failed to fetch history", e);
    alert("获取历史数据失败");
  }
};

const onLoginSuccess = (user) => {
  isLoggedIn.value = true;
  currentUser.value = user;
};

const handleLogout = () => {
  localStorage.removeItem('user');
  isLoggedIn.value = false;
  currentUser.value = '';
};

const initChart = () => {
  if (!chartRef.value) return;
  
  chartInstance.value = echarts.init(chartRef.value);
  
  const option = {
    grid: { top: '10%', bottom: '15%', left: '5%', right: '5%', containLabel: true },
    xAxis: { 
      type: 'category', 
      boundaryGap: false, 
      show: true,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#64748b', fontSize: 10, margin: 10 },
      axisTick: { show: false }
    },
    yAxis: { 
      type: 'value', 
      max: 100, 
      min: 0, 
      splitLine: { 
        show: true, 
        lineStyle: { color: 'rgba(255,255,255,0.05)', type: 'dashed' } 
      },
      axisLine: { show: true, lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#64748b', fontSize: 10 }
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0,0,0,0.7)',
      textStyle: { color: '#fff' },
      borderWidth: 0,
      formatter: '{c}%'
    },
    series: [{
      data: [],
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: {
        color: '#00ff88',
        width: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 255, 136, 0.3)' },
          { offset: 1, color: 'rgba(0, 255, 136, 0.01)' }
        ])
      }
    }]
  };
  
  chartInstance.value.setOption(option);
};

const updateChart = (score) => {
  if (!chartInstance.value) return;

  const now = new Date().toLocaleTimeString();
  focusHistory.value.push({ time: now, value: score });

  // Keep last 60 points
  if (focusHistory.value.length > 60) {
    focusHistory.value.shift();
  }

  chartInstance.value.setOption({
    xAxis: {
      data: focusHistory.value.map(item => item.time)
    },
    series: [{
      data: focusHistory.value.map(item => item.value)
    }]
  });
};

const fetchStatus = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/status');
    const data = res.data;
    
    // 更新数据，GSAP 会自动处理过渡动画
    let warning = false;
    let msg = "";

    // 🟢 直接使用后端计算的平滑分数
    if (data.posture_score !== undefined) {
      scores.posture = data.posture_score;
    }
    if (data.focus_score !== undefined) {
      scores.focus = data.focus_score;
    }

    // 状态文字反馈
    if (data.posture_status === '姿态良好') {
      feedbackText.value = '姿态良好';
      badPostureStreak.value = 0; // Reset streak
    } else if (data.posture_status === '姿态不佳') {
      feedbackText.value = '⚠ 姿态危险';
      warning = true;
      msg = "检测到不良坐姿！";
      badPostureStreak.value++;
    }

    if (data.fatigue_status === '疲劳/困倦' || data.fatigue_status === '打哈欠(疲劳)') {
      warning = true;
      msg = msg ? msg + " & 疲劳预警！" : "检测到疲劳/困倦！";
      badPostureStreak.value++; // Fatigue also counts towards alert
    }

    if (data.distance_warning) {
      warning = true;
      msg = msg ? msg + " & 距离过近！" : "距离屏幕太近！";
      badPostureStreak.value++;
    }

    // Sound Alert Logic: Trigger if streak >= 3
    if (badPostureStreak.value >= 3) {
      playAlert();
      badPostureStreak.value = 0; // Reset after playing to avoid constant noise
    }

    // Update Chart with real posture score
    updateChart(scores.posture);

    showWarning.value = warning;
    warningMessage.value = msg;

  } catch (e) {
    stopMonitoring();
  }
};

onMounted(() => {
  // Check auth
  const user = localStorage.getItem('user');
  if(user) {
    isLoggedIn.value = true;
    currentUser.value = user;
  }
  
  // Init Chart
  nextTick(() => {
    initChart();
    window.addEventListener('resize', () => chartInstance.value && chartInstance.value.resize());
  });

  // 面板进场动画
  gsap.from(".left-panel", { x: -50, opacity: 0, duration: 1, ease: "back.out(1.7)" });
  
  // 修改这里：确保右侧面板完全显示
  gsap.fromTo(".right-panel", 
    { x: 50, opacity: 0 }, 
    { x: 0, opacity: 1, duration: 1, delay: 0.2, ease: "back.out(1.7)" }
  );
});

onBeforeUnmount(() => {
  stopMonitoring();
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
});
</script>

<style scoped>
/* 使用 CSS 变量来控制颜色，跟随主题切换 */
.dashboard-container { padding: 20px 40px; position: relative; z-index: 10; height: 100vh; display: flex; flex-direction: column; }
.app-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid var(--primary-color); padding-bottom: 15px; }
.app-header h1 { color: #fff; font-family: 'Orbitron'; margin: 0; }
.subtitle { color: var(--primary-color); font-size: 0.8rem; margin-left: 10px; }

/* Header Right Buttons */
.header-right { display: flex; align-items: center; gap: 15px; }

.login-btn-header {
  background: transparent;
  border: 1px solid #fff;
  color: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-family: 'Orbitron';
  transition: 0.3s;
}
.login-btn-header:hover {
  background: var(--primary-color);
  color: #000;
  border-color: var(--primary-color);
  box-shadow: 0 0 10px var(--primary-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  color: #fff;
  font-family: 'Orbitron';
}
.username {
  color: var(--primary-color);
  font-weight: bold;
}
.logout-btn {
  background: rgba(255, 0, 0, 0.2);
  border: 1px solid rgba(255, 0, 0, 0.5);
  color: #ff6b6b;
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: 0.3s;
}
.logout-btn:hover {
  background: rgba(255, 0, 0, 0.4);
}

/* 主题切换按钮 */
.theme-toggle {
  background: rgba(255,255,255,0.1); border: 1px solid var(--primary-color); color: var(--primary-color);
  padding: 8px 15px; cursor: pointer; font-family: 'Orbitron'; transition: all 0.3s;
}
.theme-toggle:hover { background: var(--primary-color); color: #000; box-shadow: var(--glow-shadow); }

.main-content { display: flex; gap: 30px; flex: 1; }

.glass-panel {
  background: var(--glass-bg);
  backdrop-filter: blur(16px); /* 保持毛玻璃 */
  -webkit-backdrop-filter: blur(16px); /* 兼容 Safari */
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 25px;
  display: flex; 
  flex-direction: column;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  /* 添加这行优化渲染性能 */
  will-change: transform; 
}
.left-panel { flex: 3; }
.right-panel { 
  flex: 2; 
  background: rgba(13, 20, 35, 0.85) !important; /* 加深背景颜色，减少透明度 */
}

.panel-header h2 { color: var(--primary-color); font-family: 'Orbitron'; margin-top: 0; font-size: 1.2rem; }

/* 视频区域复用之前的 CSS，但颜色使用变量 */
.video-wrapper {
  flex: 1;
  display: flex;
}
.video-container { 
  width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 8px; overflow: hidden; position: relative; 
  border: 2px solid var(--primary-color); box-shadow: var(--glow-shadow);
}
#video { width: 100%; height: 100%; object-fit: cover; }
.video-overlay-standby { position: absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.8); display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--primary-color); }
.tech-scan-grid {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;
  background-image: linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
}
.tech-scan-grid::after {
  content: ''; position: absolute; top: -50%; left: 0; width: 100%; height: 50%;
  background: linear-gradient(to bottom, transparent, var(--primary-color));
  opacity: 0.2; animation: scan 3s linear infinite;
}
@keyframes scan { 0% {top: -50%} 100% {top: 100%} }

.controls { margin-top: 20px; display: flex; gap: 15px; }
.btn { flex: 1; padding: 15px; font-family: 'Orbitron'; font-weight: bold; border: none; cursor: pointer; transition: 0.3s; }
.btn-primary { 
  background: var(--primary-color); 
  color: #000; 
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.3); 
  position: relative;
  overflow: hidden;
}
.btn-primary:hover:not(:disabled) { 
  transform: translateY(-2px); 
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.6);
  letter-spacing: 1px;
}
.btn-primary:disabled { background: #333; color: #666; box-shadow: none; transform: none; cursor: not-allowed; }
.btn-danger { background: transparent; border: 1px solid var(--alert-color); color: var(--alert-color); }
.btn-secondary { background: rgba(255,255,255,0.1); border: 1px solid #fff; color: #fff; }
.btn-secondary:hover { background: rgba(255,255,255,0.2); }

/* HUD Corner Markers */
.hud-corner {
  position: absolute;
  width: 25px; height: 25px;
  border-color: var(--primary-color);
  border-style: solid;
  z-index: 5;
  pointer-events: none;
  transition: all 0.5s ease;
  opacity: 0.8;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
}
.top-left { top: 10px; left: 10px; border-width: 2px 0 0 2px; border-top-left-radius: 4px; }
.top-right { top: 10px; right: 10px; border-width: 2px 2px 0 0; border-top-right-radius: 4px; }
.bottom-left { bottom: 10px; left: 10px; border-width: 0 0 2px 2px; border-bottom-left-radius: 4px; }
.bottom-right { bottom: 10px; right: 10px; border-width: 0 2px 2px 0; border-bottom-right-radius: 4px; }

.video-container:hover .top-left { top: 5px; left: 5px; box-shadow: -2px -2px 15px var(--primary-color); }
.video-container:hover .top-right { top: 5px; right: 5px; box-shadow: 2px -2px 15px var(--primary-color); }
.video-container:hover .bottom-left { bottom: 5px; left: 5px; box-shadow: -2px 2px 15px var(--primary-color); }
.video-container:hover .bottom-right { bottom: 5px; right: 5px; box-shadow: 2px 2px 15px var(--primary-color); }

/* 图表容器样式 */
.chart-wrapper {
  margin-top: 20px;
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid rgba(0, 255, 136, 0.2);
  box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
}
.chart-header {
  font-size: 0.9rem;
  color: var(--primary-color);
  margin-bottom: 10px;
  font-family: 'Orbitron';
  letter-spacing: 1px;
}
.focus-chart { width: 100%; height: 180px; }

/* 右侧数据 */
.status-indicators { flex: 1; }
.status-item { margin-bottom: 25px; }
/* 强制让所有标签文字变亮 */
.status-label, .metric-label {
  color: #a0aec0 !important; /* 浅灰色，比原来的深灰更亮 */
  font-weight: 600; /* 加粗字体，抗模糊效果更好 */
  text-shadow: 0 1px 2px rgba(0,0,0,0.8); /* 加一点文字阴影，让字浮现出来 */
}
.status-row { display: flex; align-items: center; gap: 15px; }
/* 强制让数值变得极亮 */
.status-value {
  font-size: 2rem; 
  font-weight: bold; 
  font-family: 'Roboto Mono'; 
  min-width: 80px;
  color: #ffffff !important; /* 纯白 */
  text-shadow: 0 0 10px var(--primary-color); /* 保留发光效果 */
}

/* 让单位文字也清晰 */
.unit {
  color: rgba(255,255,255,0.6) !important;
}
.progress-bg { flex: 1; height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden; }
.progress-bar { height: 100%; position: relative; }
.progress-glare { position: absolute; top:0; left:0; width:100%; height:100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent); animation: glare 2s infinite; }
@keyframes glare { 0% {transform: translateX(-100%)} 100% {transform: translateX(100%)} }

.feedback-box { background: rgba(0,0,0,0.3); padding: 15px; text-align: center; color: #888; border: 1px dashed #444; margin-top: auto; font-family: 'Orbitron'; }
.feedback-box.active { border: 1px solid var(--primary-color); color: var(--primary-color); box-shadow: var(--glow-shadow); }

.log-container { 
  height: 150px; 
  overflow-y: auto; 
  background: rgba(0, 0, 0, 0.6) !important;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-top: 20px; 
  padding: 10px; 
  font-family: 'Roboto Mono'; 
  font-size: 0.8rem; 
  color: #888; 
}
.log-entry {
  animation: fadeInLog 0.3s ease-out forwards;
  border-left: 2px solid transparent;
  padding-left: 8px;
  margin-bottom: 4px;
}
.log-entry:first-child {
  border-left-color: var(--primary-color);
  background: linear-gradient(90deg, rgba(0,255,136,0.1), transparent);
  color: #fff;
}
@keyframes fadeInLog {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}
.log-time { color: var(--primary-color); margin-right: 5px; }

/* 🔴 警告弹窗样式 */
.warning-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(255, 0, 0, 0.3); /* 红色半透明背景 */
  backdrop-filter: blur(5px);
  z-index: 9999;
  display: flex; justify-content: center; align-items: center;
  animation: flash 1s infinite alternate;
}
@keyframes flash { from { background: rgba(255,0,0,0.2); } to { background: rgba(255,0,0,0.4); } }

.warning-box {
  background: rgba(0, 0, 0, 0.85);
  border: 3px solid #ff3333;
  padding: 40px 60px;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 0 50px rgba(255, 0, 0, 0.6);
  color: #ff3333;
  font-family: 'Orbitron';
}
.warning-icon { font-size: 80px; margin-bottom: 20px; }
.warning-box h2 { font-size: 2rem; margin: 0; text-transform: uppercase; letter-spacing: 2px; }
.warning-box p { font-size: 1.5rem; color: #fff; margin: 15px 0; font-weight: bold; }
.sub-warning { font-size: 1rem !important; color: #aaa !important; font-weight: normal !important; }
</style>