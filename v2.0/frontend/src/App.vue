<template>
  <div id="app-root" :class="currentTheme">
    <vue-particles
      id="tsparticles"
      :options="particlesOptions"
    />
    
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" @toggle-theme="toggleTheme" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const isPinkMode = ref(false);

const toggleTheme = () => {
  isPinkMode.value = !isPinkMode.value;
};

const currentTheme = computed(() => isPinkMode.value ? 'theme-cyberpunk' : 'theme-scifi');

// 粒子配置：神经网络风格
const particlesOptions = computed(() => ({
  background: { color: { value: "transparent" } },
  fpsLimit: 120,
  interactivity: {
    events: {
      onClick: { enable: true, mode: "push" },
      onHover: { enable: true, mode: "grab" },
    },
    modes: {
      grab: { distance: 140, links: { opacity: 1 } },
      push: { quantity: 4 }
    }
  },
  particles: {
    color: { value: isPinkMode.value ? "#ff00de" : "#00ff88" },
    links: {
      color: isPinkMode.value ? "#ff00de" : "#00ff88",
      distance: 150,
      enable: true,
      opacity: 0.3,
      width: 1
    },
    move: { enable: true, speed: 1.5 },
    number: { density: { enable: true, area: 800 }, value: 80 },
    opacity: { value: 0.5 },
    shape: { type: "circle" },
    size: { value: { min: 1, max: 3 } }
  },
  detectRetina: true
}));
</script>

<style>
/* CSS 变量定义：一键换肤的核心 */
:root {
  --bg-gradient: radial-gradient(circle at top right, #0f172a 0%, #020617 100%);
  --glass-bg: rgba(15, 23, 42, 0.9);
  --font-main: 'Orbitron', sans-serif;
}

.theme-scifi {
  --primary-color: #00ff88;
  --secondary-color: #00b862;
  --alert-color: #ff3333;
  --glow-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
}

.theme-cyberpunk {
  --primary-color: #ff00de; /* 赛博粉 */
  --secondary-color: #bc00a3;
  --alert-color: #00e5ff;   /* 赛博蓝警告 */
  --glow-shadow: 0 0 15px rgba(255, 0, 222, 0.5);
}

body {
  margin: 0;
  background: var(--bg-gradient);
  color: #e2e8f0;
  overflow-x: hidden;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* 页面切换动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 引入谷歌字体 */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap');

/* 全局滚动条美化 */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f172a; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; transition: background 0.3s; }
::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>
