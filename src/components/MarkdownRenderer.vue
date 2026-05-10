<template>
    <article :class="$style.markdownWrapper">
        <!-- 警告：如果公式渲染失败，可能会显示原始 LaTeX 代码 -->
        <div :class="$style.markdownContent" v-html="compiledMarkdown"></div>
    </article>
</template>

<script>
import { ref, watch } from 'vue';
import { marked } from 'marked';
import markedKatex from 'marked-katex-extension';
// 确保已在 main.js 或此处引入了 katex 的 CSS: import 'katex/dist/katex.min.css';

// 配置 marked
marked.use(markedKatex({
    throwOnError: false, // 公式错误时不抛出异常，而是显示原始文本
    inlineDelimiters: [['$', '$'], ['\\(', '\\)']], // 行内公式分隔符
    blockDelimiters: [['$$', '$$'], ['\\[', '\\]']]  // 块级公式分隔符
}));

export default {
    name: 'MarkdownRenderer',
    props: {
        markdown: {
            type: String,
            required: true
        }
    },
    setup(props) {
        const compiledMarkdown = ref('');

        const renderMarkdown = (text) => {
            if (!text) {
                compiledMarkdown.value = '';
                return;
            }
            try {
                // marked.parse 会自动处理 LaTeX 并生成 HTML
                compiledMarkdown.value = marked.parse(text);
            } catch (e) {
                console.error('Markdown/KaTeX parsing error:', e);
                compiledMarkdown.value = `<p style="color:red">解析失败: ${e.message}</p>`;
            }
        };

        watch(() => props.markdown, (newVal) => {
            renderMarkdown(newVal);
        }, { immediate: true });

        return {
            compiledMarkdown
        };
    }
};
</script>

<style module>
.markdownContent {
    //font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-size: 12px; /* 主字体缩小 */
    line-height: 1.5;
    color: #333;
    max-width: none; /* 取消居中限制 */
    margin: 0; /* 确保不居中 */
    padding: 0;
    text-align: left; /* 明确左对齐 */
}

/* 标题：进一步缩小并弱化层级差异（适合数据展示） */
.markdownContent h1,
.markdownContent h2,
.markdownContent h3,
.markdownContent h4,
.markdownContent h5,
.markdownContent h6 {
    font-weight: 600;
    margin-top: 1em;
    margin-bottom: 0.5em;
    color: #2c3e50;
    line-height: 1.3;
    border-bottom: none; /* 移除下划线 */
    padding: 0;
}

/* 段落 */
.markdownContent p {
    margin: 0 0 0.8em 0;
}

/* 链接 */
.markdownContent a {
    color: #007bff;
    text-decoration: none;
}

.markdownContent a:hover {
    text-decoration: underline;
}

/* 行内代码 */
.markdownContent code {
    background-color: #f6f8fa;
    padding: 0.15em 0.3em;
    border-radius: 3px;
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: 12px;
    color: #d73a49;
}

/* 代码块 */
.markdownContent pre {
    background-color: #f6f8fa;
    border: 1px solid #eaecef;
    border-radius: 4px;
    padding: 10px;
    overflow-x: auto;
    margin: 0.8em 0;
    font-size: 12px;
    line-height: 1.4;
}

.markdownContent pre code {
    background: none;
    padding: 0;
    color: #24292e;
    font-size: inherit;
}

/* 引用 */
.markdownContent blockquote {
    margin: 0.8em 0;
    padding-left: 12px;
    border-left: 3px solid #007bff;
    background-color: #fafafa;
    color: #555;
    font-style: normal; /* 不用斜体，更清晰 */
    font-size: 12px;
}

.markdownContent blockquote p {
    margin: 0;
}

/* 列表：紧凑布局 */
.markdownContent ul,
.markdownContent ol {
    padding-left: 1.5em; /* 适当缩进 */
    margin: 0 0 0.8em 0;
    font-size: 12px;
}

.markdownContent li {
    margin-bottom: 0.3em;
    list-style: circle;
}

.markdownContent li strong {
    //display: block;
    //padding-bottom: 5px;
}

/* 表格：紧凑型 */
.markdownContent table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.8em 0;
    font-size: 12px;
}

.markdownContent th,
.markdownContent td {
    padding: 6px 8px;
    text-align: left;
    border: 1px solid #eaecef;
}

.markdownContent th {
    background-color: #f8f9fa;
    font-weight: 600;
}

.markdownContent tr:nth-child(even) {
    background-color: #fcfcfc;
}

/* === 关键：KaTeX 公式样式修正 === */
/* 确保公式在行内垂直对齐 */
.markdownContent .katex {
    font-size: 1.1em; /* 稍微放大公式以匹配正文 */
    vertical-align: middle;
}

/* 块级公式居中且增加间距 */
.markdownContent .katex-display {
    margin: 1.2em 0;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0.5em 0;
}

/* 防止公式在小屏幕上溢出 */
.markdownContent .katex-display > .katex {
    max-width: 100%;
    overflow-x: auto;
    display: block;
}

</style>
