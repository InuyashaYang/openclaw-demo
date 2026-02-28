# 🦅 OpenClaw Demo Dashboard

> 四合一 AI 演示看板 — 一键拉起「AI日报 + A股监控 + 加密货币 + 面经搜索」

![暗色主题](https://img.shields.io/badge/UI-暗色极简-0a0e1a?style=flat)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat)
![Port](https://img.shields.io/badge/端口-6688-6366f1?style=flat)

## 🚀 一键启动

```bash
bash scripts/demo_start.sh start
```

打开浏览器访问：**http://localhost:6688**

## 📊 看板内容

| 面板 | 数据来源 | 说明 |
|------|---------|------|
| 📰 国智投洞见 | 飞书文档 | AI产业周报直链 + 情绪柱状图 |
| 🌊 加密货币 | CoinGecko 实时 | BTC/ETH/SOL/BNB 价格、涨跌幅、市值 |
| 📈 A股监控 | a-stock-monitor | 8只自选股，资金流向标注 |
| 🎓 面经爬取 | offerclaw | 已收录帖子 + 跳转完整搜索界面 |

## 📂 文件结构

```
scripts/
  demo_start.sh    一键启动脚本（start/stop/status/restart）
  dashboard.py     看板服务（port 6688，纯标准库，无需额外依赖）
SKILL.md           OpenClaw skill 描述
openclaw-demo.skill  打包好的 .skill 文件
```

## 🔧 依赖服务

| 服务 | 端口 | GitHub |
|------|------|--------|
| A股监控 | 5000 | [a-stock-monitor](https://clawhub.com/skills/a-stock-monitor) |
| 面经API | 8000 | [offerclaw](https://github.com/InuyashaYang/offerclaw) |
| 面经前端 | 3000 | [offerclaw](https://github.com/InuyashaYang/offerclaw) |

## ⚙️ 环境变量

```bash
OPENROUTER_API_KEY=sk-xxx   # 面经 RAG 必填，A股/看板不需要
```

## 📦 作为 OpenClaw Skill 安装

将 `openclaw-demo.skill` 文件拖入 OpenClaw skills 目录，或：

```bash
# 等待 clawhub 发布后
clawhub install openclaw-demo
```

---
Made with 🦅 OpenClaw
