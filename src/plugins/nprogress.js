// src/plugins/nprogress.js
import NProgress from 'nprogress';

export default {
  install(Vue) {
    Vue.prototype.$nprogress = NProgress;

    // 在每次请求开始时显示进度条
    Vue.prototype.$http.interceptors.request.use(config => {
      NProgress.start();
      return config;
    }, error => {
      NProgress.done();
      return Promise.reject(error);
    });

    // 在每次请求结束时隐藏进度条
    Vue.prototype.$http.interceptors.response.use(response => {
      NProgress.done();
      return response;
    }, error => {
      NProgress.done();
      return Promise.reject(error);
    });
  }
};
