@echo off
:: OpenClaw Demo — WSL 自动启动脚本
:: 放入 Windows 启动文件夹: Win+R → shell:startup → 粘贴此文件
:: 或用任务计划程序设置"登录时运行"

echo [OpenClaw] 正在启动 WSL 演示服务...

:: 启动 WSL 并确保 systemd user 服务运行
wsl -e bash -c "mkdir -p /tmp/openclaw-demo && systemctl --user start astock offerclaw-api offerclaw-web openclaw-dashboard 2>/dev/null; echo 'Services started'" > nul 2>&1

:: 等待服务就绪（约10秒）
timeout /t 10 /nobreak > nul

:: 可选：自动打开看板（取消注释下行启用）
:: start http://localhost:6688

echo [OpenClaw] 演示服务已就绪 → http://localhost:6688
