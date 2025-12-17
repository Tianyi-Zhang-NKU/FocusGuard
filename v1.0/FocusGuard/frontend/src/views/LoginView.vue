<template>
  <div class="login-container">
    <div class="login-card" v-tilt>
      <div class="logo-area">
        <i class="fas fa-shield-alt logo-icon"></i>
      </div>
      <h1 class="title">FocusGuard <span class="version">OS v2.0</span></h1>
      
      <div class="system-check">
        <div v-for="(item, index) in checkItems" :key="index" class="check-item" :class="{ done: item.done }">
          <span class="status-icon">[{{ item.done ? 'OK' : '..' }}]</span> {{ item.text }}
        </div>
      </div>

      <button class="access-btn" @click="handleLogin" :disabled="!allReady">
        <span v-if="!loading">INITIALIZE SYSTEM (接入系统)</span>
        <span v-else>ACCESSING...</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import gsap from 'gsap';

const router = useRouter();
const loading = ref(false);
const checkItems = ref([
  { text: 'Loading Neural Network...', done: false },
  { text: 'Connecting to Vision Sensors...', done: false },
  { text: 'Calibrating Biometric Engine...', done: false },
]);

const allReady = computed(() => checkItems.value.every(i => i.done));

onMounted(() => {
  // GSAP 进场动画
  gsap.from(".login-card", { y: 50, opacity: 0, duration: 1.2, ease: "power3.out" });
  
  // 模拟自检过程
  checkItems.value.forEach((item, index) => {
    setTimeout(() => {
      item.done = true;
    }, 800 * (index + 1));
  });
});

const handleLogin = () => {
  loading.value = true;
  // 模拟登录延迟
  setTimeout(() => {
    // 路由跳转到主控台
    router.push('/dashboard');
  }, 1000);
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 10;
}

.login-card {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(20px);
  padding: 40px 60px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  text-align: center;
  width: 450px;
  transform-style: preserve-3d; /* 3D 效果关键 */
}

.logo-icon {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: 20px;
  filter: drop-shadow(0 0 10px var(--primary-color));
  animation: float 3s ease-in-out infinite;
}

.title {
  font-family: 'Orbitron', sans-serif;
  color: #fff;
  margin-bottom: 30px;
}
.version { font-size: 0.8rem; color: var(--primary-color); border: 1px solid var(--primary-color); padding: 2px 6px; border-radius: 4px; }

.system-check {
  text-align: left;
  margin-bottom: 30px;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.9rem;
  color: #64748b;
  background: rgba(0,0,0,0.3);
  padding: 15px;
  border-radius: 8px;
}

.check-item { margin-bottom: 5px; opacity: 0.5; transition: all 0.3s; }
.check-item.done { opacity: 1; color: var(--primary-color); text-shadow: 0 0 5px var(--primary-color); }

.access-btn {
  width: 100%;
  padding: 15px;
  background: transparent;
  color: var(--primary-color);
  border: 2px solid var(--primary-color);
  font-family: 'Orbitron', sans-serif;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.access-btn::before {
  content: '';
  position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: var(--primary-color);
  transition: left 0.3s;
  z-index: -1;
}

.access-btn:hover:not(:disabled) {
  color: #000;
}
.access-btn:hover:not(:disabled)::before {
  left: 0;
}

.access-btn:disabled { opacity: 0.5; cursor: not-allowed; border-color: #64748b; color: #64748b; }

@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
</style>
