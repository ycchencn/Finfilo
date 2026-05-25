import {fileURLToPath, URL} from 'node:url';

import {PrimeVueResolver} from '@primevue/auto-import-resolver';
import vue from '@vitejs/plugin-vue';
import Components from 'unplugin-vue-components/vite';
import {defineConfig} from 'vite';
import {viteStaticCopy} from 'vite-plugin-static-copy';
import viteCompression from 'vite-plugin-compression'

// https://vitejs.dev/config/
export default defineConfig({
    server: {
        port: 3000,
        host: '0.0.0.0',
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8080', // 后端服务器地址
                changeOrigin: true // 是否改变请求的源头
            }
        }
    },
    optimizeDeps: {
        noDiscovery: true
    },
    plugins: [
        vue(),
        Components({
            resolvers: [PrimeVueResolver()]
        }),
        viteStaticCopy({
            targets: [
                {
                    src: 'node_modules/monaco-editor/min/vs/**/*',
                    dest: 'vs'
                }
            ]
        }),
        // ✅ gzip 压缩
        viteCompression({
            verbose: true,          // 显示压缩日志
            disable: false,         // 是否禁用
            threshold: 614400,       // 只压缩大于 600KB 的文件
            algorithm: 'gzip',      // gzip | brotliCompress | deflate | deflateRaw
            ext: '.gz',             // 生成的文件后缀
            deleteOriginFile: false // 是否删除源文件
        })
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    }
});
