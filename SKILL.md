---
name: openclaw-demo
description: "OpenClaw 综合演示看板 — 一键拉起「AI日报 + A股监控 + 加密货币 + 面经搜索」四合一仪表盘。触发词：演示、demo、看板、一键启动、dashboard。包含 demo_start.sh（start/stop/status/restart）和 dashboard.py（port 6688 炫酷暗色 UI）。"
---

# OpenClaw Demo Dashboard

四合一演示看板，暗色极简 UI，自动聚合实时数据。

## 一键启动

```bash
bash scripts/demo_start.sh start    # 启动全部（约30秒）
bash scripts/demo_start.sh stop     # 停止全部
bash scripts/demo_start.sh status   # 查看状态
bash scripts/demo_start.sh restart  # 重启
```

启动后访问：**http://localhost:6688**

## 服务一览

| 服务 | 端口 | 说明 |
|------|------|------|
| 统一看板 | 6688 | dashboard.py，聚合所有数据 |
| A股监控 | 5000 | a-stock-monitor，8只自选股 |
| 面经前端 | 3000 | offerclaw Next.js |
| 面经API | 8000 | offerclaw FastAPI + RAG |

## 看板功能

- **📰 国智投洞见**：飞书日报直链 + AI产业情绪柱状图
- **🌊 加密货币**：CoinGecko 实时价格（BTC/ETH/SOL/BNB），含涨跌幅和市值
- **📈 A股监控**：8只自选股卡片，含资金流向标注
- **🎓 面经爪**：已收录帖子列表 + 快速跳转搜索

## 依赖

```bash
# Python（看板 + A股）
pip install flask flask-login flask-sqlalchemy akshare

# Node.js（面经前端）
cd offerclaw/frontend && npm install

# Python（面经后端）
pip install fastapi uvicorn chromadb aiosqlite httpx beautifulsoup4
```

## 环境变量

```bash
OPENROUTER_API_KEY=sk-xxx   # 面经RAG + Embedding 必填
# A股和看板无需额外 key
```

## 自定义看板

编辑 `scripts/dashboard.py`：
- `FEISHU_DOC`：替换飞书日报链接
- `ASTOCK_URL` / `OFFERCLAW_URL`：修改后端地址
- `CRYPTO_IDS`：修改监控的加密货币（CoinGecko ID）
- `PORT`：默认 6688，可改

看板每 5 分钟自动刷新。
