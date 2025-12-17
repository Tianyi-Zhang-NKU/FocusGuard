<template>
  <div class="dashboard-container">
    <header class="app-header">
      <div class="header-left">
        <h1 @click="router.push('/')" style="cursor: pointer">专注守卫 <span class="subtitle">仪表盘</span></h1>
      </div>
      <div class="header-right">
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
            <i class="fas fa-play"></i> 启动引擎
          </button>
          <button class="btn btn-danger" @click="stopMonitoring" :disabled="!isMonitoring">
            <i class="fas fa-stop"></i> 停止
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
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import gsap from 'gsap'; // 引入动画库

const router = useRouter();
const isMonitoring = ref(false);
const backendStatus = ref('待机');
const videoStreamUrl = ref('');
const logs = ref([{message: '系统已初始化。'}]);
const feedbackText = ref('等待信号...');

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
  dataFetcher = setInterval(fetchStatus, 1500);
};

const stopMonitoring = () => {
  isMonitoring.value = false;
  videoStreamUrl.value = '';
  scores.posture = 0;
  scores.focus = 0;
  if(dataFetcher) clearInterval(dataFetcher);
};

const fetchStatus = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/status');
    const data = res.data;
    
    // 更新数据，GSAP 会自动处理过渡动画
    if (data.posture_status === '姿态良好') {
      scores.posture = 98;
      feedbackText.value = '姿态良好';
    } else if (data.posture_status === '姿态不佳') {
      scores.posture = 45;
      feedbackText.value = '⚠ 姿态危险';
    } else {
      scores.posture = 0;
    }

    if (data.fatigue_status === '清醒') scores.focus = 92;
    else if (data.fatigue_status === '疲劳/困倦') scores.focus = 30;
    else scores.focus = 0;

  } catch (e) {
    stopMonitoring();
  }
};

onMounted(() => {
  // 面板进场动画
  gsap.from(".left-panel", { x: -50, opacity: 0, duration: 1, ease: "back.out(1.7)" });
  
  // 修改这里：确保右侧面板完全显示
  gsap.fromTo(".right-panel", 
    { x: 50, opacity: 0 }, 
    { x: 0, opacity: 1, duration: 1, delay: 0.2, ease: "back.out(1.7)" }
  );
});
onBeforeUnmount(() => stopMonitoring());
</script>

<style scoped>
/* 使用 CSS 变量来控制颜色，跟随主题切换 */
.dashboard-container { padding: 20px 40px; position: relative; z-index: 10; height: 100vh; display: flex; flex-direction: column; }
.app-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid var(--primary-color); padding-bottom: 15px; }
.app-header h1 { color: #fff; font-family: 'Orbitron'; margin: 0; }
.subtitle { color: var(--primary-color); font-size: 0.8rem; margin-left: 10px; }

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
.btn-primary { background: var(--primary-color); color: #000; box-shadow: var(--glow-shadow); }
.btn-primary:hover { transform: translateY(-3px); }
.btn-primary:disabled { background: #333; color: #666; box-shadow: none; transform: none; cursor: not-allowed; }
.btn-danger { background: transparent; border: 1px solid var(--alert-color); color: var(--alert-color); }

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

.log-container { height: 150px; overflow-y: auto; background: rgba(0,0,0,0.2); margin-top: 20px; padding: 10px; font-family: 'Roboto Mono'; font-size: 0.8rem; color: #888; }
.log-time { color: var(--primary-color); margin-right: 5px; }
</style>
