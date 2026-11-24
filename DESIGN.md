# 归舸的大窝 · 设计与结构 v4

## 视觉方向
“个人田野笔记”而不是游戏壁纸站：暖纸色底、朱砂色单一强调、宋/楷体展示标题、系统无衬线正文。图片只承担叙事，不再用整屏背景压住内容。

## 色板
| 用途 | Light | Dark |
|------|-------|------|
| 背景 | `#F1EDE4` | `#0D1115` |
| 面层 | `#FBF8F2` | `#14191E` |
| 正文 | `#1D1C19` | `#ECE7DC` |
| 次要 | `#6B6458` | `#938D82` |
| 强调 | `#B73E2C` | `#EF6B54` |

只保留一个强调色。浅色和深色都属于同一套暖中性色，不混用冷暖灰。

## 字体
- 展示/标题：`LXGW WenKai` 自托管子集
- 正文阅读：`LXGW WenKai`
- 界面/表格：系统无衬线
- 数据/标签：系统等宽

## 页面骨架
- 首页：大标题 + 人物肖像 + 最新一篇特稿 + 最近三篇 + 日志流 + 站点侧栏
- 文章：780px 正文 + 236px 可滚动目录，移动端目录折叠
- 归档：年份时间线
- 分类/标签：锚点索引 + 条目列表
- 关于/项目：760px 文档式排版
- 搜索：命令面板式全站检索

## 动效层
- 首屏桌面端钉住滚动，标题下移淡出、肖像反向漂移、装饰环旋转
- 标题按字/单词分组入场，滚动顺序揭示正文模块
- 顶部信息条持续横向流动，导航随滚动收窄
- 图片使用滚动驱动缩放与亮度收敛（`animation-timeline: view()`）
- 光标在首屏产生柔和径向光
- 同源页面使用跨文档 View Transition + Speculation Rules 预渲染
- `prefers-reduced-motion: reduce` 下关闭全部位移、拆分和钉住效果

## 构建结构
```
build.py                 # 唯一入口
blogkit/config.py        # 路径、站点信息、导航、第三方服务
blogkit/markdown.py      # front matter、Markdown、目录锚点
blogkit/content.py       # Post 模型、排序、统计、分类/标签/相关文章
blogkit/templates.py     # 页面、组件、SEO、评论
blogkit/build.py         # 写出 dist/docs/preview、RSS、sitemap、搜索索引
```

## 发布约定
- 运行 `python build.py`
- 构建输出 `dist/`，同时镜像到 `docs/` 与 `../preview/`
- 构建后运行 `python tools/check_site.py` 检查链接、元信息、RSS、sitemap 和镜像一致性
- `docs/` 兼容旧版 Pages 发布源；`dist/` 供 GitHub Actions 发布
- 内容仍是 `posts/*.md`，无需改动写作流程