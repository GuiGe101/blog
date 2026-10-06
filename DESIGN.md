# 个人博客 · 设计说明

## 风格锚点
少数字派 / Medium 阅读体验：干净、安静、以文字为主。像一本轻量的个人小刊，而不是炫技作品集。

## 调色板
| 用途 | 色值 | 说明 |
|------|------|------|
| 背景 | `#FAFAF8` | 暖纸白，阅读不刺眼 |
| 正文墨色 | `#1A1A1A` | 近黑，对比舒适 |
| 次要文字 | `#6B6B66` | 日期、标签、注释 |
| 强调色 | `#2F6F6F` | 深青，链接/点赞/选中 |
| 分割线 | `#E8E6E1` | 极浅暖灰 |

## 字体
- 标题：`Georgia, "Noto Serif SC", "Songti SC", serif`
- 正文：`-apple-system, "PingFang SC", "Microsoft YaHei", sans-serif`
- 正文 16–17px，行高 1.8；标题 28–32px，字重 600

## 版式
- 单栏阅读，内容最大宽度 680px
- 页边距宽松，段间距明显
- 移动端同样单栏，字号略缩

## 页面清单
| 页面 | 类型 | 要点 |
|------|------|------|
| 首页 | 文章列表 | 标题 + 日期 + 摘要，点进正文 |
| 文章页 | 图文 | 正文 + 点赞 + 评论（giscus） |
| 关于 | 文字页 | 一句话自我介绍 |

## 签名细节
1. 文章头：日期 + 细分割线，像翻开一页纸
2. 文末「回声区」：点赞反应 + 评论，用强调色轻轻托住

## 技术
- 纯静态：`posts/*.md` → 构建脚本 → `dist/*.html`
- 评论点赞：giscus（GitHub Discussions，免费）
- 托管：Cloudflare Pages / GitHub Pages（免费）
- 不依赖付费服务，不占用你电脑

## 发布流程（小白友好）
1. 你把想发的内容告诉我（或放进 `posts/` 里的 `.md` 文件）
2. 运行构建：`python build.py`
3. 上传/推送后自动出现在网站上

## 免费上线步骤（后面做）
1. 注册/登录 GitHub，建一个公开仓库（比如 `blog`）
2. 仓库 Settings → Features → 打开 **Discussions**
3. 打开 https://giscus.app/zh-CN ，填你的仓库，复制 `repo-id` / `category-id`
4. 把值填进 `build.py` 顶部的 `GISCUS`，重新 `python build.py`
5. 部署二选一（都免费）：
   - **GitHub Pages**：仓库 Settings → Pages → 选 `main` 分支，把 `dist/` 内容推上去（或推源码用 Actions 构建）
   - **Cloudflare Pages**：连接 GitHub 仓库，构建命令 `python build.py`，输出目录 `dist`
6. 域名：在域名解析里加 CNAME 指到 Pages 给的地址，再到 Pages 后台填自定义域名

## 你本地怎么发文章
- 告诉我内容，我帮你写进 `posts/` 并构建
- 或自己新建 `posts/2026-10-07-xxx.md`，然后在 `E:\AI\MIMO\Blog` 跑 `python build.py`
