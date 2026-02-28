# 🦅 OpenClaw Demo Dashboard

> **一键启动 AI 演示看板** — 日报 · A股 · 加密货币 · 面经，永久后台运行，Windows 端直接访问。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)

---

## 📊 看板预览

四块面板，暗色极简 UI，每 5 分钟自动刷新：

| 面板 | 数据 | 来源 |
|------|------|------|
| 📰 **国智投洞见** | AI 产业周报 + 情绪柱状图 | 飞书文档直链 |
| 🌊 **加密货币** | BTC / ETH / SOL / BNB 实时价格 | CoinGecko 免费 API |
| 📈 **A股监控** | 8 只自选股行情 + 资金流向 | akshare |
| 🎓 **面经爪** | 已入库面经列表 + 一键跳转搜索 | offerclaw RAG |

---

## 🚀 快速安装（一条命令）

```bash
git clone https://github.com/InuyashaYang/openclaw-demo
cd openclaw-demo
bash scripts/install.sh sk-your-openrouter-key
```

安装完成后，**Windows 浏览器**直接访问：

```
http://localhost:6688   ← 统一看板（主入口）
http://localhost:5000   ← A股完整图表
http://localhost:3000   ← 面经搜索界面
http://localhost:8000/docs  ← API 文档
```

> **WSL2 用户**：脚本自动将 `openclaw-autostart.bat` 放入 Windows 启动文件夹，**开机自动拉起所有服务**。

---

## ⚡ 手动启停

```bash
bash scripts/demo_start.sh start    # 启动全部
bash scripts/demo_start.sh stop     # 停止全部
bash scripts/demo_start.sh status   # 查看状态
bash scripts/demo_start.sh restart  # 重启
```

---

## 🏗️ 文件结构

```
openclaw-demo/
├── scripts/
│   ├── install.sh              一键安装（systemd + Windows 自启）
│   ├── demo_start.sh           手动启停
│   ├── dashboard.py            看板服务（port 6688，纯标准库）
│   ├── openclaw-autostart.bat  Windows 开机自启
│   └── systemd/                systemd user service 配置
│       ├── astock.service
│       ├── offerclaw-api.service
│       ├── offerclaw-web.service
│       └── openclaw-dashboard.service
├── SKILL.md                    OpenClaw skill 描述
└── openclaw-demo.skill         打包好的 .skill 文件
```

---

## 🔒 永久保活

**双重机制**，崩了自动拉起：

1. **systemd user service** — 崩溃 5 秒内自动重启
2. **Windows 启动文件夹** — 开机 → WSL → 服务全自动上线

```bash
# 查看状态
systemctl --user status astock offerclaw-api offerclaw-web openclaw-dashboard

# 查看日志
tail -f /tmp/openclaw-demo/*.log
```

---

## 🤖 OpenClaw 一句话触发三件套

配合 [OpenClaw](https://github.com/openclaw/openclaw) 使用，发一条消息：

> 「跑今日三件套」

依次执行：📰 AI 产业日报 → 飞书 ｜ 🎓 爬取面经 → ChromaDB ｜ 📈 A股行情分析 → Telegram

---

## 关联项目

- [offerclaw](https://github.com/InuyashaYang/offerclaw) — 面经 RAG 系统
- [offerclaw-skill](https://github.com/InuyashaYang/offerclaw-skill) — 面经 OpenClaw skill 包
- [OpenClaw](https://github.com/openclaw/openclaw) — AI 个人助手平台

---

## ⚙️ 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `OPENROUTER_API_KEY` | 面经 RAG ✅ | Embedding + LLM |
| 其他 | ❌ | A股/看板/加密均免 key |

---

MIT License — Made with 🦅 OpenClaw
