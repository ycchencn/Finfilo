// 导入必要的库
import { createStore } from 'vuex';

// 创建一个新的Vuex store
export const store = createStore({
    state: {
        token: localStorage.getItem('token') || null
    },
    mutations: {
        setToken(state, token) {
            state.token = token;
            localStorage.setItem('token', token);
        },
        removeToken(state) {
            state.token = null;
            localStorage.removeItem('token');
        }
    },
    getters: {
        isAuthenticated: state => !!state.token
    },
    actions: {
        // 可以在这里定义一些异步操作
    }
});
