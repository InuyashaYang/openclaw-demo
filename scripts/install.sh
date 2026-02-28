#!/bin/bash
# OpenClaw Demo 一键安装脚本
# 用法: bash install.sh [YOUR_OPENROUTER_KEY]

set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
OR_KEY="${1:-}"

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║  🦅 OpenClaw Demo · 安装向导             ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$HOME/.openclaw/workspace"

# 1. 检查依赖
echo -e "${YELLOW}[1/5]${NC} 检查依赖..."
command -v python3 >/dev/null || { echo "❌ 需要 python3"; exit 1; }
command -v npm    >/dev/null || { echo "❌ 需要 Node.js 18+"; exit 1; }
command -v git    >/dev/null || { echo "❌ 需要 git"; exit 1; }
echo -e "  ${GREEN}✓${NC} 依赖检查通过"

# 2. 克隆子项目
echo -e "${YELLOW}[2/5]${NC} 拉取子项目..."
mkdir -p "$WORKSPACE"

if [ ! -d "$WORKSPACE/offerclaw" ]; then
  git clone https://github.com/InuyashaYang/offerclaw "$WORKSPACE/offerclaw"
  echo -e "  ${GREEN}✓${NC} offerclaw 克隆完成"
else
  echo -e "  - offerclaw 已存在，跳过"
fi

if [ ! -d "$WORKSPACE/skills/a-stock-monitor" ]; then
  pip3 install clawhub -q 2>/dev/null || npm install -g clawhub -q 2>/dev/null || true
  clawhub install a-stock-monitor --workdir "$WORKSPACE" 2>/dev/null || \
    echo -e "  ${YELLOW}⚠${NC} 请手动安装 a-stock-monitor skill"
fi

# 3. 安装 Python 依赖
echo -e "${YELLOW}[3/5]${NC} 安装 Python 依赖..."
pip3 install -q fastapi uvicorn chromadb aiosqlite httpx pydantic beautifulsoup4 \
  flask flask-login flask-sqlalchemy akshare pandas numpy 2>&1 | tail -1
echo -e "  ${GREEN}✓${NC} Python 依赖安装完成"

# 4. 配置 systemd
echo -e "${YELLOW}[4/5]${NC} 配置 systemd 服务..."
mkdir -p ~/.config/systemd/user
SDIR="$SCRIPT_DIR/systemd"

for svc in astock offerclaw-api offerclaw-web openclaw-dashboard; do
  if [ -f "$SDIR/${svc}.service" ]; then
    # 替换路径占位符
    sed "s|/home/inuyasha|$HOME|g" "$SDIR/${svc}.service" > ~/.config/systemd/user/${svc}.service
  fi
done

# 注入 OR_KEY
if [ -n "$OR_KEY" ]; then
  sed -i "s|OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=$OR_KEY|g" \
    ~/.config/systemd/user/offerclaw-api.service
fi

mkdir -p /tmp/openclaw-demo
systemctl --user daemon-reload
systemctl --user enable astock offerclaw-api offerclaw-web openclaw-dashboard
systemctl --user start  astock offerclaw-api offerclaw-web openclaw-dashboard
echo -e "  ${GREEN}✓${NC} systemd 服务已启用（开机自启）"

# 5. Windows 自启（WSL 环境下）
echo -e "${YELLOW}[5/5]${NC} Windows 开机自启..."
WINUSER=$(ls /mnt/c/Users/ 2>/dev/null | grep -v "All Users\|Default\|Public\|desktop" | head -1)
if [ -n "$WINUSER" ]; then
  STARTUP="/mnt/c/Users/$WINUSER/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
  [ -d "$STARTUP" ] && cp "$SCRIPT_DIR/openclaw-autostart.bat" "$STARTUP/" && \
    echo -e "  ${GREEN}✓${NC} 已放入 Windows 启动文件夹" || true
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ 安装完成！                               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  🌐 统一看板  ${CYAN}http://localhost:6688${NC}"
echo -e "  📈 A股监控   ${CYAN}http://localhost:5000${NC}"
echo -e "  🎓 面经搜索  ${CYAN}http://localhost:3000${NC}"
echo -e "  📡 API 文档  ${CYAN}http://localhost:8000/docs${NC}"
echo ""
echo -e "  ${YELLOW}手动启停：${NC} bash demo_start.sh [start|stop|status]"
