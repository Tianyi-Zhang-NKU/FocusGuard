<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-overlay" @click.self="handleClose">
      
      <div class="modal-card">
        <div class="deco-bar"></div>

        <div class="modal-header">
          <h2 class="title">FocusGuard</h2>
          <p class="subtitle">AI 智能专注监测系统</p>
        </div>

        <div class="auth-tabs">
          <div class="tab-item" :class="{ active: isLogin }" @click="isLogin = true">登 录</div>
          <div class="tab-item" :class="{ active: !isLogin }" @click="isLogin = false">注 册</div>
        </div>

        <el-form :model="form" class="auth-form" size="large" @submit.prevent @keyup.enter="handleSubmit">
          
          <el-form-item>
            <el-input 
              v-model="form.username" 
              placeholder="请输入用户名或邮箱"
              class="custom-input"
            />
          </el-form-item>

          <el-input-item style="display:none"></el-input-item> <!-- Hack for some browser issues -->

          <el-form-item>
            <el-input 
              v-model="form.password" 
              type="password" 
              placeholder="请输入密码"
              show-password 
              class="custom-input"
            />
          </el-form-item>

          <el-form-item v-if="!isLogin">
            <el-input 
              v-model="form.confirmPass" 
              type="password" 
              placeholder="请再次确认密码"
              show-password 
              class="custom-input"
            />
          </el-form-item>

          <button class="submit-btn" @click.prevent="handleSubmit" :disabled="loading">
            <span v-if="loading">加载中...</span>
            <span v-else>{{ isLogin ? '进入系统' : '立即注册' }}</span>
          </button>
          
          <div class="form-footer" v-if="isLogin">
            <span class="forgot-pwd">忘记密码?</span>
          </div>
        </el-form>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { ElNotification } from 'element-plus';
import axios from 'axios';

// Props & Emits
const props = defineProps(['modelValue']);
const emit = defineEmits(['update:modelValue', 'login-success']);

const isLogin = ref(true);
const loading = ref(false);

const API_BASE = 'http://localhost:5000/api';

// 控制显示隐藏
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const form = reactive({ username: '', password: '', confirmPass: '' });

const handleClose = () => {
  // Allow closing: close the modal when clicking the mask
  visible.value = false;
};

const handleSubmit = async () => {
  if (!form.username || !form.password) {
    ElNotification.warning('请输入用户名和密码');
    return;
  }

  if (!isLogin.value && form.password !== form.confirmPass) {
    ElNotification.error('两次输入的密码不一致');
    return;
  }
  
  loading.value = true;
  
  try {
    const endpoint = isLogin.value ? '/login' : '/register';
    const res = await axios.post(`${API_BASE}${endpoint}`, {
      username: form.username,
      password: form.password
    });

    if (res.data.code === 200) {
      if (isLogin.value) {
        ElNotification.success(`欢迎回来，${res.data.user}`);
        localStorage.setItem('user', res.data.user);
        emit('login-success', res.data.user);
        visible.value = false;
      } else {
        ElNotification.success('注册成功，请登录');
        isLogin.value = true;
      }
    }
  } catch (err) {
    ElNotification.error(err.response?.data?.msg || '操作失败');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* --- 🔴 关键修复：强制设置输入框样式，确保可见 --- */
:deep(.el-input__wrapper) {
  background-color: #f5f7fa !important; /* 浅灰色背景，不再是白色 */
  box-shadow: 0 0 0 1px #dcdfe6 inset !important; /* 灰色边框 */
  color: #333 !important;
  border-radius: 4px !important;
  padding: 0 15px !important;
  height: 40px !important;
}

:deep(.el-input__inner) {
  color: #333 !important; /* 深黑色文字，确保可见 */
  height: 100% !important;
  background: transparent !important;
}

/* 聚焦时的样式 */
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #42d392 inset !important; /* 聚焦变成青色 */
  background-color: #ffffff !important;
}

/* --- 核心布局：Fixed 强制悬浮 --- */
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.6); /* 深色背景遮罩 */
  backdrop-filter: blur(5px);
  z-index: 20000; /* 极高层级，确保在最上层 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-card {
  width: 400px;
  background: #ffffff; /* 纯白背景 */
  border-radius: 12px;
  padding: 40px 35px;
  text-align: center;
  position: relative;
  box-shadow: 0 25px 50px rgba(0,0,0,0.25);
}

.deco-bar {
  position: absolute; top: 0; left: 0; width: 100%; height: 5px;
  background: linear-gradient(90deg, #42d392 0%, #3bb2b8 100%);
}

.title { font-family: sans-serif; color: #2c3e50; margin: 0; font-size: 1.8rem; font-weight: bold; }
.subtitle { color: #95a5a6; font-size: 0.9rem; margin-top: 5px; margin-bottom: 20px; }

.auth-tabs { display: flex; justify-content: center; gap: 40px; margin: 20px 0; border-bottom: 1px solid #eee; }
.tab-item { padding-bottom: 10px; cursor: pointer; font-weight: 600; color: #909399; border-bottom: 2px solid transparent; transition: all 0.3s; }
.tab-item.active { color: #42d392; border-bottom-color: #42d392; }

.submit-btn {
  width: 100%; padding: 12px; margin-top: 20px;
  border: none; border-radius: 4px;
  background: linear-gradient(90deg, #42d392 0%, #3bb2b8 100%);
  color: white; font-size: 1rem; font-weight: bold;
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(66, 211, 146, 0.25);
  transition: opacity 0.3s;
}
.submit-btn:hover { opacity: 0.9; transform: translateY(-1px); }

.form-footer { margin-top: 15px; font-size: 0.85rem; color: #42d392; cursor: pointer; }

/* 动画 */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
</style>
