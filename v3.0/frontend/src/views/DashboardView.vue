<template>
  <div class="dashboard-container">
    <header class="app-header">
      <div class="header-left">
        <h1 style="cursor: pointer">FocusGuard-专注守卫 <span class="subtitle">仪表盘</span></h1>
      </div>

      <div class="header-center" v-if="isLoggedIn">
        <div class="mini-rpg-stat" v-tilt>
          <div class="mini-badge">LV.{{ userLevel }}</div>
          <div class="mini-xp-container">
            <div class="mini-rank">{{ rankTitle }}</div>
            <div class="mini-xp-track">
              <div class="mini-xp-fill" :style="{ width: (currentXP / maxXP * 100) + '%' }"></div>
            </div>
          </div>
          <div class="mini-xp-text">{{ currentXP.toFixed(0) }}/{{ maxXP }}</div>
        </div>
      </div>
      <div class="header-center guest-mode" v-else>
        <span><i class="fas fa-user-secret"></i> 游客模式 (登录以记录等级)</span>
      </div>

      <div class="header-right">
        <div v-if="isLoggedIn" class="user-info">
          <span class="username"><i class="fas fa-user-astronaut"></i> {{ currentUser }}</span>
          <button class="nav-btn logout" @click="handleLogout">退出</button>
        </div>
        <button v-else class="nav-btn" @click="showLoginModal = true">
          <i class="fas fa-sign-in-alt"></i> 登录 / 注册
        </button>

        <button class="nav-btn" @click="showHelpModal = true">
          <i class="fas fa-book-medical"></i> 使用说明
        </button>

        <button class="nav-btn" @click="$emit('toggle-theme')">
          <i class="fas fa-palette"></i> 切换主题
        </button>
      </div>
    </header>

    <div class="main-content">
      <div class="panels-wrapper">
        
        <!-- 左侧面板：移除统一背景，改为透明容器 -->
        <div class="left-panel" v-tilt>
          
          <!-- 模块 1: 视频监控区 (独立封装) -->
          <div class="video-wrapper glass-panel">
            <div class="panel-header"><h2><i class="fas fa-video"></i> 传感器画面</h2></div>
            <div class="video-container">
              <div class="hud-corner top-left"></div>
              <div class="hud-corner top-right"></div>
              <div class="hud-corner bottom-left"></div>
              <div class="hud-corner bottom-right"></div>
              
              <img id="video" :src="videoStreamUrl" alt="视频流" />
              
              <div v-if="!isMonitoring" class="video-overlay-standby">
                <div class="icon-pulse"><i class="fas fa-power-off"></i></div>
                <h3>{{ backendStatus }}</h3>
              </div>
              
              <div class="light-indicator" :class="{ 'warning': lightingWarning }" v-if="isMonitoring">
                <i class="fas" :class="lightingWarning ? 'fa-moon' : 'fa-sun'"></i>
                <span>{{ lightingValue }}</span>
              </div>

              <div class="low-light-overlay" v-if="lightingWarning && isMonitoring">
                <div class="low-light-text">⚠ LOW LIGHT DETECTED</div>
              </div>

              <div class="proximity-ruler" :class="{ 'danger': distanceWarning }" v-if="isMonitoring">
                <div v-for="i in 10" :key="i" class="ruler-tick"></div>
                <div class="proximity-alert-text" v-if="distanceWarning">PROXIMITY ALERT</div>
              </div>
              
              <div class="tech-scan-grid" v-if="isMonitoring"></div>
            </div>
          </div>

          <!-- 模块 2: 控制栏 (独立封装) -->
          <div class="controls glass-panel controls-panel">
            <button class="btn btn-primary" @click="startMonitoring" :disabled="isMonitoring">
              <i class="fas fa-stopwatch"></i> {{ isMonitoring ? formatTime(pomodoroTime) : '开启专注' }}
            </button>
            
            <button class="btn btn-danger" @click="stopMonitoring" :disabled="!isMonitoring">
              <i class="fas fa-stop"></i> 停止监测
            </button>
            
            <button class="btn btn-secondary" @click="isMuted = !isMuted">
              <i :class="isMuted ? 'fas fa-volume-xmark' : 'fas fa-volume-high'"></i> {{ isMuted ? '已静音' : '声音开' }}
            </button>
            
            <button class="btn btn-secondary" @click="showHistory">
              <i class="fas fa-history"></i> 历史记录
            </button>
          </div>
        </div>

        <!-- 右侧面板：移除统一背景 -->
        <div class="right-panel" v-tilt>
          
          <!-- 模块 3: 生物特征 (独立封装) -->
          <div class="glass-panel">
            <div class="panel-header"><h2><i class="fas fa-chart-network"></i> 生物特征</h2></div>
            <div class="status-indicators">
              <div class="metrics-grid">
                <div class="status-item">
                  <div class="status-label">姿态完整度</div>
                  <div class="status-row">
                    <div class="status-value tech-font" :style="{ color: 'var(--primary-color)' }">
                      {{ tweenedPosture.toFixed(0) }}<span class="unit">%</span>
                    </div>
                  </div>
                  <div class="progress-bg">
                    <div class="progress-bar" 
                         :style="{ width: tweenedPosture + '%', backgroundColor: 'var(--primary-color)' }">
                      <div class="progress-glare"></div>
                    </div>
                  </div>
                </div>

                <div class="status-item">
                  <div class="status-label">专注指数</div>
                  <div class="status-row">
                    <div class="status-value tech-font" :style="{ color: 'var(--primary-color)' }">
                      {{ tweenedFocus.toFixed(0) }}<span class="unit">%</span>
                    </div>
                  </div>
                  <div class="progress-bg">
                    <div class="progress-bar" 
                         :style="{ width: tweenedFocus + '%', backgroundColor: 'var(--primary-color)' }">
                      <div class="progress-glare"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 模块 4: 环境感知 (独立封装) -->
          <div class="glass-panel">
            <div class="panel-header"><h2><i class="fas fa-globe"></i> 环境感知</h2></div>
            <div class="env-grid">
              <div class="env-card" :class="{ 'alert': lightingWarning }">
                <div class="env-icon"><i class="fas" :class="lightingWarning ? 'fa-lightbulb-slash' : 'fa-lightbulb'"></i></div>
                <div class="env-data">
                  <div class="env-label">光照强度</div>
                  <div class="env-value">{{ lightingValue }} <span class="unit">Lux</span></div>
                </div>
              </div>
              <div class="env-card" :class="{ 'alert': distanceWarning }">
                <div class="env-icon"><i class="fas fa-ruler-combined"></i></div>
                <div class="env-data">
                  <div class="env-label">面部距离</div>
                  <div class="env-value">{{ distanceWarning ? '过近 (TOO CLOSE)' : '正常 (OPTIMAL)' }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 模块 5: 趋势图 (独立封装) -->
          <div class="chart-wrapper glass-panel">
            <div class="chart-header">姿态完整度趋势 (60s)</div>
            <div ref="chartRef" class="focus-chart"></div>
          </div>

          <!-- 模块 6: 终端日志 (独立封装) -->
          <div class="log-container glass-panel">
             <div v-for="(log, i) in logs" :key="i" class="log-entry">
               <span class="log-time">></span> {{ log.message }}
             </div>
          </div>
          
          <div class="posture-visualization">
            <div class="feedback-box" :class="{'active': isMonitoring}">
              <i class="fas fa-terminal"></i> {{ feedbackText }}
            </div>
          </div>

        </div>
      </div>
    </div>
    
    <footer class="app-footer">
      <div class="footer-links">
        <span><i class="fas fa-shield-alt"></i> 隐私安全</span>
        <span><i class="fas fa-code"></i> 开源协议</span>
        <span><i class="fas fa-bug"></i> 问题反馈</span>
      </div>
      <p class="copyright">© 2025 FocusGuard AI Lab. All rights reserved.</p>
    </footer>

    <el-dialog v-model="historyVisible" title="历史监测记录" width="50%">
      <el-table :data="historyData" style="width: 100%" height="400">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="posture" label="坐姿状态" width="180" />
        <el-table-column prop="fatigue" label="疲劳状态" />
      </el-table>
    </el-dialog>

    <div v-if="showWarning" class="warning-overlay">
      <div class="warning-box">
        <div class="warning-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h2>⚠ 警告：状态异常 ⚠</h2>
        <p>{{ warningMessage }}</p>
        <p class="sub-warning">请立即调整坐姿或休息！</p>
      </div>
    </div>

    <LoginModal v-model="showLoginModal" @login-success="onLoginSuccess" />

    <el-dialog v-model="showHelpModal" :show-close="false" width="700px" align-center class="help-dialog" :append-to-body="true">
      <template #header>
        <div class="terminal-header">
          <div class="header-deco"></div>
          <span class="terminal-title">>> SYSTEM_MANUAL_V2.0 // 操作简报</span>
          <button class="close-icon" @click="showHelpModal = false"><i class="fas fa-times"></i></button>
        </div>
      </template>

      <div class="manual-container">
        <div class="scan-overlay"></div>

        <div class="tactical-grid">
          
          <div class="tactical-card visual-module">
            <div class="card-label">MODULE_01: VISUAL_CORE</div>
            <div class="card-content row">
              <div class="feature-box">
                <i class="fas fa-user-check"></i>
                <div>
                  <div class="f-title">坐姿判定</div>
                  <div class="f-desc">实时计算脊柱/肩部角度</div>
                </div>
              </div>
              <div class="feature-divider"></div>
              <div class="feature-box">
                <i class="fas fa-bed"></i>
                <div>
                  <div class="f-title">疲劳检测</div>
                  <div class="f-desc">监测闭眼时长 (EAR)</div>
                </div>
              </div>
            </div>
          </div>

          <div class="tactical-card env-light warning-bg">
            <div class="card-label">ENV_SENSOR_A</div>
            <div class="card-icon"><i class="fas fa-lightbulb"></i></div>
            <div class="card-main">
              <div class="stat-value text-yellow">LIGHT &lt; 60</div>
              <div class="stat-desc">光线过暗触发红屏</div>
            </div>
          </div>

          <div class="tactical-card env-dist danger-bg">
            <div class="card-label">ENV_SENSOR_B</div>
            <div class="card-icon"><i class="fas fa-ruler-combined"></i></div>
            <div class="card-main">
              <div class="stat-value text-red">TOO CLOSE</div>
              <div class="stat-desc">面部贴屏触发警报</div>
            </div>
          </div>

          <div class="tactical-card rpg-module">
            <div class="card-label">MODULE_02: GAMIFICATION</div>
            <div class="rpg-header">
              <i class="fas fa-gamepad"></i> 专注 RPG
            </div>
            <div class="xp-rules-list">
              <div class="xp-row gain">
                <span class="xp-badge">+1 XP/s</span>
                <span class="xp-cond">状态良好</span>
              </div>
              <div class="xp-row loss">
                <span class="xp-badge">-1 XP/s</span>
                <span class="xp-cond">状态异常</span>
              </div>
            </div>
            <div class="rpg-footer">
              *登录后可启用云存档
            </div>
          </div>

        </div>

        <div class="privacy-terminal">
          <span class="blink">_</span> PRIVACY_PROTOCOL: LOCAL_PROCESSING_ONLY. NO_CLOUD_UPLOAD.
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer-custom">
          <button class="glitch-btn" @click="showHelpModal = false">
            <span class="btn-text">INITIALIZE SYSTEM</span>
            <span class="btn-deco"></span>
          </button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="timerDialogVisible" title="⏱ 设定专注目标" width="400px" align-center custom-class="glass-dialog">
      <div class="timer-setup" style="text-align: center; padding: 20px 0;">
        <p style="color: #ccc; margin-bottom: 15px;">请输入您想专注的时长 (1 - 180 分钟)</p>
        <el-input-number v-model="customDuration" :min="1" :max="180" size="large" />
      </div>
      <template #footer>
        <div class="dialog-footer" style="text-align: center; padding-bottom: 10px;">
          <el-button @click="timerDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmStartFocus" style="background: var(--primary-color); border:none; color:#000; font-weight:bold;">
            🚀 启动引擎
          </el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount, shallowRef, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import gsap from 'gsap'; 
import * as echarts from 'echarts'; 
import LoginModal from '../components/LoginModal.vue';
import { ElNotification } from 'element-plus'; 

const router = useRouter();
const isMonitoring = ref(false);
const backendStatus = ref('待机');
const videoStreamUrl = ref('');
const logs = ref([{message: '系统已初始化。'}]);
const feedbackText = ref('等待信号...');
const lightingValue = ref(0);
const lightingWarning = ref(false);
const distanceWarning = ref(false);
const isBadState = ref(false); 
const showHelpModal = ref(false);
const timerDialogVisible = ref(false);
const customDuration = ref(25);
const userLevel = ref(1);
const currentXP = ref(0);
const maxXP = ref(100);
const rankTitle = ref('见习守卫');
const chartRef = ref(null);
const chartInstance = shallowRef(null);
const focusHistory = ref([]);
const showWarning = ref(false);
const warningMessage = ref('');
const isMuted = ref(false);
const badPostureStreak = ref(0);
const pomodoroTime = ref(25 * 60);
let timerInterval = null;

const playAlert = () => {
  if (isMuted.value) return;
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(880, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.3);
  } catch (err) { console.error(err); }
};

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const showLoginModal = ref(false);
const isLoggedIn = ref(false);
const currentUser = ref('');
const historyVisible = ref(false);
const historyData = ref([]);
const scores = reactive({ posture: 0, focus: 0 });
const tweenedPosture = ref(0);
const tweenedFocus = ref(0);

watch(() => scores.posture, (newVal) => { gsap.to(tweenedPosture, { duration: 0.8, value: newVal, ease: "power2.out" }); });
watch(() => scores.focus, (newVal) => { gsap.to(tweenedFocus, { duration: 0.8, value: newVal, ease: "power2.out" }); });

const updateRank = () => {
  if (userLevel.value <= 5) rankTitle.value = '见习守卫';
  else if (userLevel.value <= 10) rankTitle.value = '资深特工';
  else if (userLevel.value <= 20) rankTitle.value = '赛博大师';
  else rankTitle.value = '传奇领主';
};

const loadUserStats = (username) => {
  if (!username) { userLevel.value = 1; currentXP.value = 0; maxXP.value = 100; updateRank(); return; }
  const key = `focus_rpg_stats_${username}`;
  const savedRPG = localStorage.getItem(key);
  if (savedRPG) {
    const parsed = JSON.parse(savedRPG);
    userLevel.value = parsed.level || 1; currentXP.value = parsed.xp || 0; maxXP.value = parsed.max_xp || 100;
  }
  updateRank();
};

const saveRPGStats = () => {
  if (!isLoggedIn.value || !currentUser.value) return;
  localStorage.setItem(`focus_rpg_stats_${currentUser.value}`, JSON.stringify({ level: userLevel.value, xp: currentXP.value, max_xp: maxXP.value }));
};

const gainXP = (amount) => {
  if (!isLoggedIn.value) return;
  if (amount < 0) {
    if (currentXP.value > 0) { currentXP.value += amount; if (currentXP.value < 0) currentXP.value = 0; }
    saveRPGStats(); return;
  }
  currentXP.value += amount;
  if (currentXP.value >= maxXP.value) {
    userLevel.value++; currentXP.value -= maxXP.value; maxXP.value = userLevel.value * 100;
    updateRank(); ElNotification({ title: '🎉 升级达成！', message: `晋升为 LV.${userLevel.value} ${rankTitle.value}`, type: 'success' });
  }
  saveRPGStats();
};

let dataFetcher = null;

const startMonitoring = () => { timerDialogVisible.value = true; };

const confirmStartFocus = () => {
  timerDialogVisible.value = false; isMonitoring.value = true; videoStreamUrl.value = 'http://localhost:5000/video_feed';
  pomodoroTime.value = customDuration.value * 60;
  if(timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    pomodoroTime.value--;
    if (isBadState.value) gainXP(-1); else gainXP(1);
    if (pomodoroTime.value <= 0) stopMonitoring();
  }, 1000);
  dataFetcher = setInterval(fetchStatus, 1500);
};

const stopMonitoring = () => {
  isMonitoring.value = false; videoStreamUrl.value = '';
  if(dataFetcher) clearInterval(dataFetcher); if(timerInterval) clearInterval(timerInterval); saveRPGStats();
};

const fetchStatus = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/status');
    const data = res.data;
    let warning = false; let hasIssue = false;
    if (data.posture_score !== undefined) scores.posture = data.posture_score;
    if (data.focus_score !== undefined) scores.focus = data.focus_score;
    if (data.brightness_value !== undefined) {
      lightingValue.value = data.brightness_value; lightingWarning.value = data.lighting_warning;
      if (data.lighting_warning) { warning = true; hasIssue = true; }
    }
    if (data.posture_status === '姿态不佳' || data.fatigue_status === '疲劳/困倦') { warning = true; hasIssue = true; }
    distanceWarning.value = !!data.distance_warning;
    if (distanceWarning.value) { warning = true; hasIssue = true; }
    isBadState.value = hasIssue;
    if (hasIssue) {
        badPostureStreak.value++;
        if (badPostureStreak.value >= 2) { playAlert(); badPostureStreak.value = 0; }
        feedbackText.value = `检测到异常: ${data.posture_status || '环境异常'}`;
        logs.value.unshift({ message: `异常: ${data.posture_status} | 光照:${lightingValue.value}` });
    } else { 
        badPostureStreak.value = 0; feedbackText.value = "状态良好，系统运行中..."; 
        logs.value.unshift({ message: "监测正常..." });
    }
    if(logs.value.length > 20) logs.value.pop();
    updateChart(scores.posture);
    showWarning.value = warning; warningMessage.value = warning ? "状态异常，请调整！" : "";
  } catch (e) { stopMonitoring(); }
};

const showHistory = async () => {
  if(!isLoggedIn.value) { showLoginModal.value = true; return; }
  const res = await axios.get(`http://localhost:5000/api/history?username=${currentUser.value}`);
  historyData.value = res.data; historyVisible.value = true;
};

const onLoginSuccess = (user) => { isLoggedIn.value = true; currentUser.value = user; loadUserStats(user); };
const handleLogout = () => { localStorage.removeItem('user'); isLoggedIn.value = false; loadUserStats(null); };

const initChart = () => {
  if (!chartRef.value) return;
  chartInstance.value = echarts.init(chartRef.value);
  chartInstance.value.setOption({
    grid: { top: '10%', bottom: '5%', left: '0%', right: '0%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, axisLabel: { color: '#64748b' }, axisLine: {show: false}, axisTick: {show: false} },
    yAxis: { type: 'value', max: 100, min: 0, splitLine: { show: false }, axisLabel: {show: false} },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.8)', textStyle: {color: '#fff'} },
    series: [{ data: [], type: 'line', smooth: true, showSymbol: false, lineStyle: { color: '#00ff88', width: 2 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(0, 255, 136, 0.3)'}, {offset: 1, color: 'rgba(0, 255, 136, 0.01)'}]) } }]
  });
};

const updateChart = (score) => {
  if (!chartInstance.value) return;
  const now = new Date().toLocaleTimeString('en-US', {hour12: false});
  focusHistory.value.push({ time: now, value: score });
  if (focusHistory.value.length > 60) focusHistory.value.shift();
  chartInstance.value.setOption({
    xAxis: { data: focusHistory.value.map(item => item.time) },
    series: [{ data: focusHistory.value.map(item => item.value) }]
  });
};

onMounted(() => {
  const user = localStorage.getItem('user');
  if(user) { isLoggedIn.value = true; currentUser.value = user; loadUserStats(user); }
  nextTick(() => { initChart(); window.addEventListener('resize', () => chartInstance.value?.resize()); });
});
onBeforeUnmount(() => { stopMonitoring(); chartInstance.value?.dispose(); });
</script>

<style scoped>
.dashboard-container { padding: 20px 100px !important; height: 100dvh; display: flex; flex-direction: column; background: #0b0f19; color: #fff; overflow: hidden; box-sizing: border-box; }
.app-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--primary-color); padding-bottom: 15px; margin-bottom: 20px; flex-shrink: 0; }
.app-header h1 {
  color: var(--title-accent);
  text-shadow: 0 0 10px var(--title-accent); /* 增加同色辉光 */
  font-family: 'Orbitron', sans-serif;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.header-center { flex: 1; display: flex; justify-content: center; }
.mini-rpg-stat { background: rgba(0,0,0,0.5); padding: 5px 20px; border-radius: 20px; display: flex; align-items: center; gap: 15px; border: 1px solid #333; height: 40px; }
.mini-badge { color: var(--primary-color); font-family: 'Orbitron'; font-weight: bold; font-size: 1.1rem; }
.mini-xp-track { width: 150px; height: 6px; background: #222; border-radius: 3px; overflow: hidden; }
.mini-xp-fill { 
  height: 100%; 
  /* 赛博朋克全息渐变：青 -> 粉 -> 紫 -> 青 */
  background: linear-gradient(90deg, 
    #00ff88 0%, 
    #00e5ff 25%, 
    #ff00de 50%, 
    #bc00a3 75%, 
    #00ff88 100%
  );
  background-size: 200% 100%; /* 拉长背景以支持流动 */
  animation: neon-flow 3s linear infinite; /* 流动动画 */
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.6); /* 基础辉光 */
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}

/* 增加一道扫光特效 */
.mini-xp-fill::after {
  content: '';
  position: absolute;
  top: 0; left: 0; bottom: 0; width: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  transform: skewX(-20deg) translateX(-150%);
  animation: shine-scan 2s infinite;
}
.mini-rank { font-size: 0.9rem; color: #ccc; }
.mini-xp-text { font-family: 'Roboto Mono'; font-size: 0.8rem; color: #888; }
.header-right { display: flex; gap: 12px; align-items: center; }

/* 🔹 战术切角导航按钮 */
.nav-btn {
  position: relative;
  background: rgba(0, 0, 0, 0.5); /* 半透明黑底 */
  border: 1px solid var(--primary-color); /* 跟随主题色 */
  color: #fff;
  padding: 6px 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.85rem;
  letter-spacing: 1px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  /* 复杂的战术切角 */
  clip-path: polygon(
    10px 0, 100% 0, 
    100% calc(100% - 10px), calc(100% - 10px) 100%, 
    0 100%, 0 10px
  );
  box-shadow: inset 0 0 10px rgba(0,0,0,0.8); /* 内阴影增加厚度感 */
}

/* 按钮内部的装饰线条 */
.nav-btn::before {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: 0.5s;
  transform: skewX(-20deg);
}

/* 悬停态：高亮 + 辉光 */
.nav-btn:hover {
  background: #000;
  box-shadow: 0 0 15px var(--primary-color), inset 0 0 10px var(--primary-color);
  text-shadow: 0 0 5px #fff;
  border-color: #fff;
  transform: translateY(-2px);
}

.nav-btn:hover::before {
  left: 100%; /* 划过一道光 */
}

/* 点击态 */
.nav-btn:active {
  transform: translateY(1px);
  box-shadow: 0 0 5px var(--primary-color);
}

/* 🔴 “退出”按钮特殊样式 (警示红) */
.nav-btn.logout {
  border-color: #ff3333;
  color: #ffaaaa;
}
.nav-btn.logout:hover {
  background: rgba(255, 51, 51, 0.2);
  box-shadow: 0 0 20px #ff3333;
  color: #fff;
  border-color: #ff3333;
}

/* --- 1. 主内容区：禁止外层滚动 --- */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 🔴 关键：禁止整个页面滚动，强制在内部布局 */
  padding-bottom: 10px;
  min-height: 0;
}

.panels-wrapper {
  display: flex;
  gap: 20px;
  width: 100%;
  height: 100%; /* 🔴 关键：占满剩余高度 */
  min-height: 0;
}

.glass-panel { background: rgba(255,255,255,0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }

/* --- 2. 左侧面板：垂直弹性布局 --- */
.left-panel {
  flex: 1.1 !important; /* 调整比例 */
  display: flex;
  flex-direction: column;
  gap: 15px; /* 视频和按钮之间的间距 */
  height: 100%; /* 强制占满父容器高度 */
  min-height: 0; /* 允许压缩 */
  overflow: hidden; /* 防止内部元素撑破 */
}

/* --- 6. 右侧面板：保持独立滚动 --- */
.right-panel {
  flex: 1 !important; /* 增加相对权重 */
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* 右侧内容多，允许它自己滚动 */
  padding-right: 5px;
  background: rgba(13, 20, 35, 0.9) !important;
}

.panel-header { display: flex; align-items: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; }
.panel-header h2 { 
  margin: 0; 
  font-family: 'Orbitron'; 
  font-size: 1.1rem; 
  color: var(--title-accent) !important; /* 强制互补撞色 */
  text-shadow: 0 0 8px var(--title-accent);
  display: flex; align-items: center; gap: 10px;
}
.panel-header h2 i { color: var(--title-accent); margin-right: 5px; }

/* --- 3. 视频包裹层：占据剩余所有空间 --- */
.video-wrapper {
  flex: 1; /* 🔴 关键：自动填充剩余高度 */
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
  min-height: 0; /* 🔴 关键：允许 flex 子项缩小到内容以下 */
  padding: 8px 12px 12px 12px !important; /* 顶部保持紧凑 */
}

.video-wrapper .panel-header {
  flex: 0 0 auto; /* 标题高度固定 */
  margin-bottom: 5px !important;
  padding-left: 0;
  display: flex;
  align-items: center;
  height: 32px; /* 恢复并微调高度 */
}

.video-wrapper .panel-header h2 {
  font-size: 1.1rem !important; /* 恢复到标准大小 */
  line-height: 1;
  margin: 0;
  opacity: 1 !important; /* 恢复不透明度 */
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 1px;
}

/* --- 4. 视频容器：完全跟随父级大小 --- */
.video-container {
  width: 100%;
  height: 100%; /* 填满 video-wrapper 的剩余部分 */
  background: #000;
  position: relative;
  border: 2px solid var(--primary-color);
  border-radius: 4px;
  overflow: hidden;
  display: flex;          /* 用于居中视频 */
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
}

#video {
  width: 100%;
  height: 100%;
  object-fit: contain; /* 🔴 关键：保持比例缩放，不裁切，不撑开容器 */
}
.video-overlay-standby { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; background: rgba(0,0,0,0.7); z-index: 5; }
.icon-pulse { font-size: 4rem; color: var(--primary-color); margin-bottom: 10px; opacity: 0.5; animation: pulse 2s infinite; }
.video-overlay-standby h3 { font-family: 'Orbitron'; letter-spacing: 2px; color: var(--primary-color); }

.hud-corner { position: absolute; width: 25px; height: 25px; border-color: var(--primary-color); border-style: solid; z-index: 6; pointer-events: none; opacity: 0.8; box-shadow: 0 0 10px rgba(0,255,136,0.2); }
.top-left { top: 10px; left: 10px; border-width: 2px 0 0 2px; }
.top-right { top: 10px; right: 10px; border-width: 2px 2px 0 0; }
.bottom-left { bottom: 10px; left: 10px; border-width: 0 0 2px 2px; }
.bottom-right { bottom: 10px; right: 10px; border-width: 0 2px 2px 0; }

.tech-scan-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px); background-size: 40px 40px; z-index: 2; pointer-events: none; opacity: 0.3; }

.low-light-overlay { position: absolute; inset: 0; box-shadow: inset 0 0 80px rgba(255,51,51,0.6); border: 4px solid #ff3333; display: flex; justify-content: center; align-items: center; animation: pulse 1s infinite alternate; z-index: 8; pointer-events: none; }
.low-light-text { color: #ff3333; font-family: 'Orbitron'; font-size: 1.5rem; font-weight: bold; background: rgba(0,0,0,0.9); padding: 10px 20px; border: 1px solid #ff3333; }

.proximity-ruler { position: absolute; left: 10px; top: 10%; height: 80%; width: 10px; border-right: 2px solid var(--primary-color); display: flex; flex-direction: column; justify-content: space-between; z-index: 8; }
.proximity-ruler.danger { border-color: #ff3333; filter: drop-shadow(0 0 5px #ff3333); }
.proximity-ruler.danger .ruler-tick { background: #ff3333; }
.ruler-tick { width: 100%; height: 2px; background: var(--primary-color); opacity: 0.5; }
.proximity-alert-text { position: absolute; left: 20px; top: 50%; transform: translateY(-50%); color: #ff3333; font-family: 'Orbitron'; font-weight: bold; background: rgba(0,0,0,0.9); padding: 5px; white-space: nowrap; animation: flash 0.2s infinite; }

.light-indicator { position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.6); padding: 5px 12px; border-radius: 15px; border: 1px solid var(--primary-color); color: var(--primary-color); font-family: 'Orbitron'; z-index: 10; display: flex; align-items: center; gap: 8px; }
.light-indicator.warning { border-color: #ff3333; color: #ff3333; animation: shake 0.5s infinite; }

/* --- 5. 底部按钮：固定高度 --- */
.controls.controls-panel {
  display: flex;
  gap: 15px;
  flex: 0 0 auto; /* 🔴 关键：不缩放，高度由内容决定 */
  margin-top: 0;
  padding: 12px; /* 稍微紧凑一点 */
}
.btn { flex: 1; padding: 15px; border-radius: 8px; font-family: 'Orbitron'; font-weight: bold; cursor: pointer; border: none; transition: all 0.3s; display: flex; align-items: center; justify-content: center; gap: 8px; text-transform: uppercase; }
.btn-primary { background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)); color: #000; box-shadow: 0 0 15px rgba(0,255,136,0.3); }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 0 25px rgba(0,255,136,0.6); }
.btn-danger { background: rgba(255, 51, 51, 0.2); border: 1px solid #ff3333; color: #ff3333; }
.btn-secondary { background: rgba(255,255,255,0.1); color: #fff; border: 1px solid rgba(255,255,255,0.2); }
.help-btn { background: none; border: 1px solid rgba(255,255,255,0.3); color: #fff; padding: 6px 15px; border-radius: 20px; cursor: pointer; transition: 0.3s; margin-right: 15px; font-family: 'Orbitron'; font-size: 0.9rem; }
.help-btn:hover { background: var(--primary-color); color: #000; border-color: var(--primary-color); }
.theme-toggle, .logout-btn, .login-btn-header { background: none; border: 1px solid rgba(255,255,255,0.2); color: #aaa; padding: 6px 12px; border-radius: 4px; cursor: pointer; transition: 0.3s; }
.theme-toggle:hover { color: #fff; border-color: #fff; }

.status-group-header { font-family: 'Orbitron'; color: #64748b; font-size: 0.9rem; margin: 25px 0 10px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }

/* 📊 数据网格布局 */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

.status-item { margin-bottom: 0; /* Grid 处理了间距 */ }
.status-label { color: #a0aec0; font-size: 0.85rem; margin-bottom: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.status-row { display: flex; align-items: baseline; gap: 5px; margin-bottom: 5px; }
.status-value { font-size: 2.2rem; font-weight: bold; font-family: 'Roboto Mono'; color: #fff; text-shadow: 0 0 15px var(--primary-color); }
.unit { font-size: 0.9rem; color: rgba(255,255,255,0.5); }

/* 🔋 能量槽进度条 */
.progress-bg { 
  flex: none; width: 100%; height: 12px; 
  background: rgba(0, 0, 0, 0.4); 
  border-radius: 6px; 
  border: 1px solid rgba(255, 255, 255, 0.1); 
  padding: 2px;
}
.progress-bar { 
  height: 100%; 
  border-radius: 4px; 
  position: relative; 
  /* 条纹纹理 */
  background-image: linear-gradient(45deg, 
    rgba(0,0,0,0.2) 25%, transparent 25%, 
    transparent 50%, rgba(0,0,0,0.2) 50%, 
    rgba(0,0,0,0.2) 75%, transparent 75%, transparent);
  background-size: 8px 8px;
  background-color: var(--primary-color);
  box-shadow: 0 0 15px var(--primary-color);
  transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.progress-glare { display: none; } /* 移除旧光效 */

.env-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }

/* 🧊 数据晶片卡片 */
.env-card { 
  background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
  padding: 15px; 
  border-radius: 12px; 
  border: 1px solid rgba(255,255,255,0.08); 
  display: flex; align-items: center; gap: 15px; 
  transition: all 0.3s; 
  position: relative;
  overflow: hidden;
}
.env-card::after {
  content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}
.env-card:hover { 
  background: rgba(255,255,255,0.06); 
  border-color: var(--primary-color); 
  transform: translateY(-2px); 
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}
.env-card.alert { 
  border-color: #ff3333; 
  background: linear-gradient(180deg, rgba(255,51,51,0.15) 0%, rgba(255,51,51,0.05) 100%);
  box-shadow: 0 0 20px rgba(255,0,0,0.2); 
  animation: shake 0.5s infinite; 
}

/* --- 🧊 传感器图标：全息晶体风格 --- */
.env-icon {
  width: 48px; height: 48px; /* 稍微加大一点 */
  /* 玻璃渐变背景 */
  background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
  border-radius: 12px;
  display: flex; justify-content: center; align-items: center;
  
  /* 边框高光 */
  border: 1px solid rgba(255,255,255,0.15);
  border-top: 1px solid rgba(255,255,255,0.3); /* 顶部更亮，模拟光源 */
  border-bottom: 1px solid rgba(0,0,0,0.2);
  
  /* 图标颜色与光晕 */
  color: var(--primary-color); 
  font-size: 1.5rem;
  
  /* 增加内发光和投影 */
  box-shadow: 
    0 4px 10px rgba(0,0,0,0.3),
    inset 0 0 15px rgba(255,255,255,0.02);
    
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* 装饰：微弱的扫描光效 */
.env-icon::after {
  content: '';
  position: absolute;
  top: -50%; left: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
  opacity: 0;
  transform: scale(0.5);
  transition: 0.5s;
}

/* 悬停效果：点亮晶体 */
.env-card:hover .env-icon {
  background: rgba(255,255,255,0.1);
  border-color: var(--primary-color);
  color: #fff; /* 悬停时图标变白 */
  box-shadow: 
    0 0 15px var(--glow-shadow), /* 使用定义好的主题光晕变量 */
    inset 0 0 10px rgba(255,255,255,0.1);
  transform: scale(1.05);
}

.env-card:hover .env-icon::after {
  opacity: 1;
  transform: scale(1);
}

/* 🚨 报警状态下的图标 (保持红色闪烁) */
.env-card.alert .env-icon {
  background: rgba(255, 51, 51, 0.2);
  border-color: #ff3333;
  color: #ff3333;
  box-shadow: 0 0 15px rgba(255, 51, 51, 0.4);
  animation: pulse-red 1s infinite;
}

.env-data { display: flex; flex-direction: column; }
.env-label { font-size: 0.75rem; color: #888; margin-bottom: 2px; text-transform: uppercase; }
.env-value { font-family: 'Orbitron'; font-size: 1.1rem; color: #fff; letter-spacing: 1px; }
.env-card.alert .env-value { color: #ff3333; }

.chart-wrapper { background: rgba(0,0,0,0.2); border-radius: 8px; padding: 15px; border: 1px solid rgba(255,255,255,0.05); margin-top: 10px; }
.chart-header { font-size: 0.85rem; color: var(--primary-color); margin-bottom: 10px; font-family: 'Orbitron'; }
.focus-chart { width: 100%; height: 180px; }

.feedback-box { margin-top: 20px; background: rgba(0,0,0,0.4); border: 1px dashed #444; color: #888; padding: 12px; text-align: center; border-radius: 6px; font-family: 'Orbitron'; font-size: 0.9rem; transition: 0.3s; }
.feedback-box.active { border: 1px solid var(--primary-color); color: var(--primary-color); box-shadow: inset 0 0 20px rgba(0,255,136,0.1); }

/* 🖥️ 终端风格日志区 */
.log-container { 
  flex: 1; 
  margin-top: 20px; 
  overflow-y: auto; 
  background: #050505 !important; /* 纯黑底 */
  border-radius: 8px; 
  padding: 12px; 
  border: 1px solid #333; 
  font-family: 'JetBrains Mono', 'Roboto Mono', monospace; 
  font-size: 0.8rem; 
  min-height: 100px; 
  position: relative;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}
/* 扫描线装饰 */
.log-container::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
              linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
  background-size: 100% 2px, 3px 100%;
  pointer-events: none;
  z-index: 1;
}

.log-entry { 
  position: relative; z-index: 2;
  margin-bottom: 2px; 
  padding-left: 0; 
  border-left: none; 
  animation: slideIn 0.3s ease; 
  border-bottom: 1px solid rgba(255,255,255,0.03);
  padding: 4px 0;
  display: flex;
}
.log-entry:first-child { 
  border-left: none; 
  background: none; 
  color: #fff; 
  font-weight: bold;
}
.log-time { color: var(--primary-color); margin-right: 10px; opacity: 0.8; font-weight: bold; min-width: 60px; }

.app-footer { padding: 5px 0 !important; border-top: 1px solid rgba(255, 255, 255, 0.05); text-align: center; font-family: 'Roboto Mono', sans-serif; font-size: 0.75rem !important; color: #64748b; flex-shrink: 0; }
.footer-links { display: flex; justify-content: center; gap: 20px !important; margin-bottom: 2px !important; }
.footer-links span { cursor: pointer; transition: color 0.3s; display: flex; align-items: center; gap: 5px; }
.footer-links span:hover { color: var(--primary-color); }

.warning-overlay { position: fixed; inset: 0; background: rgba(255,0,0,0.2); z-index: 9999; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(5px); }
.warning-box { background: rgba(10,10,10,0.95); border: 3px solid #ff3333; padding: 40px; border-radius: 16px; text-align: center; box-shadow: 0 0 50px rgba(255,0,0,0.5); width: 400px; }
.warning-icon { font-size: 4rem; color: #ff3333; margin-bottom: 20px; animation: pulse 0.5s infinite alternate; }
.warning-box h2 { font-family: 'Orbitron'; color: #ff3333; margin: 0 0 15px; }
.warning-box p { font-size: 1.2rem; color: #fff; }

 @keyframes pulse { from { opacity: 0.6; } to { opacity: 1; } }
 @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-3px); } 75% { transform: translateX(3px); } }
 @keyframes flash { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
 @keyframes glare { 0% { left: -100%; } 100% { left: 200%; } }
 @keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }

 @keyframes neon-flow {
  0% { background-position: 100% 0; }
  100% { background-position: 0 0; }
}

 @keyframes shine-scan {
  0% { transform: skewX(-20deg) translateX(-150%); }
  20% { transform: skewX(-20deg) translateX(150%); } /* 快速划过 */
  100% { transform: skewX(-20deg) translateX(150%); } /* 这里的停顿是为了让扫光有间隔 */
}

 @keyframes pulse-red {
  0% { box-shadow: 0 0 0 rgba(255, 51, 51, 0.4); }
  70% { box-shadow: 0 0 20px rgba(255, 51, 51, 0); }
  100% { box-shadow: 0 0 0 rgba(255, 51, 51, 0); }
}
</style>

<style>
/* 🔴 全局覆盖 Element Plus 弹窗样式 */
/* --- 📘 战术简报弹窗样式 (Tactical Manual) --- */

/* 1. 弹窗容器重置 */
.help-dialog.el-dialog {
  background: rgba(10, 15, 25, 0.98) !important;
  border: 1px solid rgba(0, 255, 136, 0.3) !important;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.8) !important;
  overflow: hidden;
  border-radius: 6px !important; /* 更硬朗的圆角 */
}
.help-dialog .el-dialog__header { display: none; /* 隐藏默认头部 */ }
.help-dialog .el-dialog__body { padding: 0 !important; }
.help-dialog .el-dialog__footer { 
  background: rgba(0,0,0,0.3); 
  border-top: 1px solid rgba(255,255,255,0.05); 
  padding: 20px !important;
}

/* 2. 自定义头部 */
.terminal-header {
  background: linear-gradient(90deg, rgba(0,255,136,0.1), transparent);
  padding: 15px 20px;
  border-bottom: 1px solid rgba(0,255,136,0.2);
  display: flex; justify-content: space-between; align-items: center;
}
.header-deco { width: 4px; height: 16px; background: var(--primary-color); margin-right: 10px; display: inline-block; }
.terminal-title { font-family: 'Orbitron'; color: var(--primary-color); letter-spacing: 1px; font-size: 1rem; }
.close-icon { background: none; border: none; color: #666; cursor: pointer; font-size: 1.2rem; transition: 0.3s; }
.close-icon:hover { color: #fff; transform: rotate(90deg); }

/* 3. 内容区与网格 */
.manual-container { padding: 25px; position: relative; }

/* 动态扫描线背景 */
.scan-overlay {
  position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 255, 136, 0.02) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
  background-size: 100% 3px, 3px 100%;
  z-index: 0;
}

.tactical-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr; /* 左宽右窄 */
  grid-template-rows: auto auto;
  gap: 15px;
  position: relative; z-index: 1;
}

/* 通用卡片样式 */
.tactical-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 15px;
  position: relative;
}
.card-label {
  position: absolute; top: 0; left: 0;
  background: rgba(255,255,255,0.1);
  color: #aaa; font-size: 0.6rem;
  padding: 2px 6px;
  font-family: 'Roboto Mono';
  border-bottom-right-radius: 6px;
}

/* 模块 1: 视觉监测 */
.visual-module { grid-column: 1 / 2; }
.card-content.row { display: flex; align-items: center; justify-content: space-around; margin-top: 10px; }
.feature-box { display: flex; gap: 12px; align-items: center; }
.feature-box i { font-size: 1.5rem; color: #00ff88; }
.f-title { font-family: 'Orbitron'; color: #fff; font-size: 0.9rem; }
.f-desc { font-size: 0.75rem; color: #888; }
.feature-divider { width: 1px; height: 30px; background: rgba(255,255,255,0.1); }

/* 模块 2 & 3: 环境感知 */
.env-light { grid-column: 1 / 2; grid-row: 2 / 3; display: flex; align-items: center; gap: 15px; }
.env-dist { grid-column: 2 / 3; grid-row: 2 / 3; display: flex; align-items: center; gap: 15px; } /* 修正位置 */

.warning-bg { border-color: rgba(245, 158, 11, 0.3); background: radial-gradient(circle at center, rgba(245, 158, 11, 0.1), transparent); }
.danger-bg { border-color: rgba(239, 68, 68, 0.3); background: radial-gradient(circle at center, rgba(239, 68, 68, 0.1), transparent); }

.card-icon { font-size: 1.8rem; color: #fff; opacity: 0.8; }
.stat-value { font-family: 'Orbitron'; font-weight: bold; font-size: 1.1rem; }
.stat-desc { font-size: 0.75rem; color: #aaa; }
.text-yellow { color: #f59e0b; }
.text-red { color: #ef4444; }

/* 模块 4: RPG (右侧纵向) */
.rpg-module { grid-column: 2 / 3; grid-row: 1 / 2; display: flex; flex-direction: column; justify-content: center; }
.rpg-header { font-family: 'Orbitron'; color: #ff00de; margin-bottom: 15px; font-size: 1.1rem; text-align: center; }
.xp-rules-list { display: flex; flex-direction: column; gap: 8px; }
.xp-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
.xp-badge { padding: 4px 8px; border-radius: 4px; font-family: 'Roboto Mono'; font-weight: bold; font-size: 0.8rem; }
.xp-cond { color: #bbb; }

.xp-row.gain .xp-badge { background: rgba(0,255,136,0.2); color: #00ff88; border: 1px solid #00ff88; }
.xp-row.loss .xp-badge { background: rgba(255,51,51,0.2); color: #ff3333; border: 1px solid #ff3333; }
.rpg-footer { margin-top: 10px; font-size: 0.7rem; color: #666; text-align: center; }

/* 隐私声明 */
.privacy-terminal {
  margin-top: 20px; 
  font-family: 'Roboto Mono'; font-size: 0.75rem; color: #444; 
  text-align: center; border-top: 1px dashed #333; padding-top: 10px;
}
.blink { animation: blink 1s infinite; }
 @keyframes blink { 50% { opacity: 0; } }

/* 🔴 故障风按钮 (Glitch Button) */
.dialog-footer-custom { display: flex; justify-content: center; width: 100%; }
.glitch-btn {
  /* 🔴 修改点 1：背景改为强制高亮荧光青 */
  background: #00e5ff !important;
  /* 🔴 修改点 2：文字维持黑色以确保最高对比度 */
  color: #000 !important;
  /* 🔴 修改点 3：增加常驻的基础辉光，使其看起来在发光 */
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.5) !important;
  
  border: none;
  padding: 12px 40px;
  font-family: 'Orbitron'; font-weight: bold; font-size: 1rem;
  cursor: pointer;
  position: relative;
  clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
  transition: 0.2s;
}
.glitch-btn:hover {
  /* 🔴 修改点 4：悬停时变为纯白超高亮 */
  background: #ffffff !important;
  /* 🔴 修改点 5：增强悬停时的光晕范围和亮度 */
  box-shadow: 0 0 40px #00e5ff, 0 0 10px #ffffff !important;
  transform: scale(1.05);
}
.glitch-btn:active { transform: scale(0.98); }
</style>