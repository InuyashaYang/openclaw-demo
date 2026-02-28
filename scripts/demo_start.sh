#!/bin/bash
# 🦅 OpenClaw Demo — 一键跑起来
# 用法: bash demo_start.sh

PORT=6688
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

echo ""
echo "  🦅 OpenClaw Demo"
echo "  ─────────────────────────────────"

# 检查并启动 A股
if ! curl -sf http://localhost:5000 >/dev/null 2>&1; then
  python3 "$WORKSPACE/skills/a-stock-monitor/scripts/web_app.py" \
    > /tmp/demo-astock.log 2>&1 &
  echo "  📈 A股监控      启动中..."
else
  echo "  📈 A股监控      已就绪"
fi

# 检查并启动面经 API
if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
  OR_KEY=$(python3 -c "import json; d=json.load(open('$HOME/.openclaw/openclaw.json')); print(d['env']['OPENROUTER_API_KEY'])" 2>/dev/null)
  OPENROUTER_API_KEY="$OR_KEY" python3 -m uvicorn main:app \
    --app-dir "$WORKSPACE/offerclaw/backend" \
    --host 0.0.0.0 --port 8000 \
    > /tmp/demo-api.log 2>&1 &
  echo "  🎓 面经 API     启动中..."
else
  echo "  🎓 面经 API     已就绪"
fi

# 检查并启动面经前端
if ! curl -sf http://localhost:3000 >/dev/null 2>&1; then
  (cd "$WORKSPACE/offerclaw/frontend" && npm run dev > /tmp/demo-web.log 2>&1) &
  echo "  🎓 面经前端     启动中..."
else
  echo "  🎓 面经前端     已就绪"
fi

# 启动看板（前台运行）
pkill -f "dashboard.py" 2>/dev/null; sleep 0.5
echo "  🌐 看板         http://localhost:$PORT"
echo "  ─────────────────────────────────"
echo ""
python3 "$(dirname "$0")/dashboard.py"
