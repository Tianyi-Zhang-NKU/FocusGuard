import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Particles from "@tsparticles/vue3";
import { loadSlim } from "tsparticles-slim";

const app = createApp(App)

// 注册粒子引擎
app.use(Particles, {
  init: async engine => {
    await loadSlim(engine);
  }
});

// 注册自定义指令 v-tilt (用于 3D 倾斜)
import VanillaTilt from 'vanilla-tilt';
app.directive('tilt', {
  mounted(el, binding) {
    VanillaTilt.init(el, {
      max: 10,           // 最大倾斜度
      speed: 400,        // 响应速度
      glare: true,       // 开启反光
      "max-glare": 0.4,  // 反光强度
      scale: 1.02,       // 悬停放大
      ...binding.value   // 允许传入自定义参数
    });
  },
  unmounted(el) {
    if (el.vanillaTilt) el.vanillaTilt.destroy();
  }
});

app.use(router)
app.mount('#app')