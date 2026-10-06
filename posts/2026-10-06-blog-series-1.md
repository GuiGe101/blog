---
title: 博客搭建日志（上）：从零到能打开
date: 2026-10-06
summary: 用免费方案把个人站跑起来：静态生成、GitHub Pages、自定义域名。
tags: 技术, 博客
category: 技术
series: 博客搭建日志
series_order: 1
cover: assets/valorant/hero-jett16.jpg
---

本篇讲 **怎么把一个博客从零弄到能打开**。下一篇讲评论、样式和细节能打的部分。

## 目标

- 不花钱（或极少钱）
- 自己能发文章
- 别人能看、能留言、点赞

## 方案

1. 本地 Markdown 写文章
2. 一个小构建脚本生成静态 HTML
3. 推到 GitHub，用 Pages 发布
4. 域名解析到 `zixuann.top`

```text
posts/*.md  ->  build.py  ->  dist/  ->  GitHub Pages
```

## 关键点

- **静态站**很稳，没有服务器也行
- **Actions** 可以自动构建，推一下就更新
- **域名**用 A 记录指向 GitHub Pages 的 IP

## 踩坑

- 家宽没有公网 IP，别指望拿自己电脑当服务器
- 中文 GitHub 界面翻译可能把 `main` 译成「主要角色」，别慌

下一篇：评论、点赞和阅读体验。
