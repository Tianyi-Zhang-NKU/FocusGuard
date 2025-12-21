import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 引入 Element Plus 及其样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 粒子特效
import Particles from "@tsparticles/vue3";
import { loadSlim } from "tsparticles-slim";

// 3D 倾斜库
import VanillaTilt from 'vanilla-tilt';

const app = createApp(App)

// 注册 Element Plus
app.use(ElementPlus)

// 注册粒子引擎
app.use(Particles, {
  init: async engine => {
    await loadSlim(engine);
  }
});

// 注册自定义指令 v-tilt
app.directive('tilt', {
  mounted(el, binding) {
    VanillaTilt.init(el, {
      max: 2,            // 🔴 从 10 改为 2 (最大倾斜角度变小)
      speed: 1000,       // 🔴 从 400 改为 1000 (回弹变慢，更优雅)
      glare: true,       // 保持反光
      "max-glare": 0.1,  // 🔴 从 0.4 改为 0.1 (反光不要太刺眼)
      scale: 1.005,      // 🔴 从 1.02 改为 1.005 (几乎不放大，防止糊字)
      gyroscope: false,  // 禁用手机陀螺仪，防止误触
      ...binding.value
    });
  },
  unmounted(el) {
    if (el.vanillaTilt) el.vanillaTilt.destroy();
  }
});

app.use(router)
app.mount('#app')
