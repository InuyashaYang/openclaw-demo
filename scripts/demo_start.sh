#!/bin/bash
# ╔══════════════════════════════════════════════╗
# ║   OpenClaw Demo · 一键启动                   ║
# ║   ./demo_start.sh [start|stop|status]        ║
# ╚══════════════════════════════════════════════╝

set -e
WORKSPACE="$HOME/.openclaw/workspace"
OFFERCLAW="$WORKSPACE/offerclaw/backend"
FRONTEND="$WORKSPACE/offerclaw/frontend"
ASTOCK="$WORKSPACE/skills/a-stock-monitor/scripts"
DEMO="$WORKSPACE/demo"
LOG_DIR="/tmp/openclaw-demo"
OR_KEY=$(python3 -c "import json; d=json.load(open('$HOME/.openclaw/openclaw.json')); print(d.get('env',{}).get('OPENROUTER_API_KEY',''))" 2>/dev/null)

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ACTION="${1:-start}"

banner() {
  echo -e "${CYAN}"
  echo "  ╔═══════════════════════════════════════╗"
  echo "  ║  🦅  OpenClaw Demo Dashboard          ║"
  echo "  ║      日报 · A股 · 加密 · 面经         ║"
  echo "  ╚═══════════════════════════════════════╝"
  echo -e "${NC}"
}

wait_port() {
  local port=$1 name=$2 retries=20
  echo -ne "   ⏳ 等待 $name (port $port)"
  for i in $(seq 1 $retries); do
    if curl -sf "http://localhost:$port" -o /dev/null 2>/dev/null || \
       curl -sf "http://localhost:$port/health" -o /dev/null 2>/dev/null; then
      echo -e " ${GREEN}✓${NC}"
      return 0
    fi
    echo -ne "."
    sleep 1
  done
  echo -e " ${YELLOW}⚠ timeout (继续)${NC}"
}

start_services() {
  mkdir -p "$LOG_DIR"
  banner
  echo -e "${BOLD}启动所有服务...${NC}\n"

  # 1. A股后端
  echo -e "${BLUE}[1/4]${NC} A股监控 (port 5000)"
  pkill -f "web_app.py" 2>/dev/null || true; sleep 0.5
  screen -dmS astock bash -c "cd $ASTOCK && python3 web_app.py > $LOG_DIR/astock.log 2>&1"
  wait_port 5000 "A股"

  # 2. 面经后端
  echo -e "${BLUE}[2/4]${NC} 面经API (port 8000)"
  pkill -f "offerclaw.*uvicorn\|uvicorn.*main:app" 2>/dev/null || true; sleep 0.5
  screen -dmS offerclaw-api bash -c "cd $OFFERCLAW && OPENROUTER_API_KEY=$OR_KEY uvicorn main:app --host 0.0.0.0 --port 8000 > $LOG_DIR/api.log 2>&1"
  wait_port 8000 "面经API"

  # 3. 面经前端
  echo -e "${BLUE}[3/4]${NC} 面经前端 (port 3000)"
  pkill -f "next-server\|next dev" 2>/dev/null || true; sleep 0.5
  screen -dmS offerclaw-web bash -c "cd $FRONTEND && npm run dev > $LOG_DIR/web.log 2>&1"
  wait_port 3000 "面经前端"

  # 4. 统一看板
  echo -e "${BLUE}[4/4]${NC} Demo看板 (port 6688)"
  pkill -f "dashboard.py" 2>/dev/null || true; sleep 0.5
  screen -dmS demo-dashboard bash -c "python3 $DEMO/dashboard.py > $LOG_DIR/dashboard.log 2>&1"
  wait_port 6688 "看板"

  echo ""
  echo -e "${GREEN}${BOLD}✅ 全部启动完成！${NC}\n"
  echo -e "  ${CYAN}🌐 统一看板${NC}   http://localhost:6688"
  echo -e "  ${CYAN}📈 A股图表${NC}   http://localhost:5000"
  echo -e "  ${CYAN}🎓 面经搜索${NC}  http://localhost:3000"
  echo -e "  ${CYAN}📡 API文档${NC}   http://localhost:8000/docs"
  echo ""
  echo -e "  ${YELLOW}停止：${NC} ./demo_start.sh stop"
  echo -e "  ${YELLOW}日志：${NC} tail -f $LOG_DIR/*.log"
}

stop_services() {
  banner
  echo -e "${BOLD}停止所有服务...${NC}"
  pkill -f "web_app.py" 2>/dev/null && echo -e "  ${GREEN}✓${NC} A股" || echo -e "  - A股未运行"
  pkill -f "uvicorn main:app" 2>/dev/null && echo -e "  ${GREEN}✓${NC} 面经API" || echo -e "  - 面经API未运行"
  pkill -f "next-server\|next dev" 2>/dev/null && echo -e "  ${GREEN}✓${NC} 面经前端" || echo -e "  - 面经前端未运行"
  pkill -f "dashboard.py" 2>/dev/null && echo -e "  ${GREEN}✓${NC} 看板" || echo -e "  - 看板未运行"
  screen -wipe 2>/dev/null || true
  echo -e "\n${GREEN}全部停止。${NC}"
}

status_services() {
  banner
  check() {
    local name=$1 port=$2
    if curl -sf "http://localhost:$port" -o /dev/null 2>/dev/null || \
       curl -sf "http://localhost:$port/health" -o /dev/null 2>/dev/null; then
      echo -e "  ${GREEN}●${NC} $name (port $port)"
    else
      echo -e "  ${RED}○${NC} $name (port $port) — 未运行"
    fi
  }
  echo -e "${BOLD}服务状态：${NC}"
  check "统一看板" 6688
  check "A股监控" 5000
  check "面经前端" 3000
  check "面经API" 8000
  echo ""
}

case "$ACTION" in
  start)   start_services ;;
  stop)    stop_services ;;
  status)  status_services ;;
  restart) stop_services; sleep 2; start_services ;;
  *) echo "用法: $0 [start|stop|status|restart]"; exit 1 ;;
esac
