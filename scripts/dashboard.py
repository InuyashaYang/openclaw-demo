#!/usr/bin/env python3
"""
OpenClaw Demo Dashboard — 统一演示入口
端口 6688，聚合：日报 / A股 / 加密货币 / 面经
"""
import json, urllib.request, urllib.error, threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 6688
ASTOCK_URL  = "http://localhost:5000"
OFFERCLAW_URL = "http://localhost:8000"

CRYPTO_IDS = "bitcoin,ethereum,solana,binancecoin"
FEISHU_DOC = "https://frz7vmtv3a.feishu.cn/docx/XmI2dxCp2oLfmXxXJRfcnP3Lnkg"

def fetch_json(url, timeout=5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def fetch_crypto():
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={CRYPTO_IDS}&order=market_cap_desc&sparkline=false"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception as e:
        # fallback demo data
        return [
            {"id":"bitcoin","name":"Bitcoin","symbol":"BTC","current_price":63561,"price_change_percentage_24h":-6.53,"market_cap":1270739863854},
            {"id":"ethereum","name":"Ethereum","symbol":"ETH","current_price":1852.68,"price_change_percentage_24h":-8.96,"market_cap":223645623316},
            {"id":"solana","name":"Solana","symbol":"SOL","current_price":143.22,"price_change_percentage_24h":-7.81,"market_cap":73400000000},
            {"id":"binancecoin","name":"BNB","symbol":"BNB","current_price":591.38,"price_change_percentage_24h":-5.22,"market_cap":80650854149},
        ]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenClaw · 演示看板</title>
<style>
  :root {{
    --bg: #0a0e1a;
    --card: #111827;
    --border: #1f2937;
    --accent: #6366f1;
    --green: #10b981;
    --red: #ef4444;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --gold: #f59e0b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'SF Pro Display', -apple-system, 'PingFang SC', sans-serif;
    min-height: 100vh;
    padding: 24px;
    background-image: radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.08) 0%, transparent 50%),
                      radial-gradient(ellipse at 80% 80%, rgba(16,185,129,0.05) 0%, transparent 50%);
  }}
  header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 4px 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
  }}
  .logo {{ display: flex; align-items: center; gap: 12px; }}
  .logo-icon {{ font-size: 28px; }}
  .logo h1 {{ font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }}
  .logo span {{ color: var(--muted); font-size: 13px; margin-top: 2px; display: block; }}
  .live-badge {{
    background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3);
    color: var(--green); font-size: 12px; padding: 4px 10px; border-radius: 20px;
    display: flex; align-items: center; gap: 6px;
  }}
  .pulse {{ width: 7px; height: 7px; background: var(--green); border-radius: 50%;
    animation: pulse 1.5s infinite; }}
  @keyframes pulse {{ 0%,100%{{ opacity:1; transform:scale(1); }}
    50%{{ opacity:0.5; transform:scale(1.4); }} }}

  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .full {{ grid-column: 1 / -1; }}

  .card {{
    background: var(--card); border: 1px solid var(--border);
    border-radius: 16px; padding: 20px;
    transition: border-color 0.2s;
  }}
  .card:hover {{ border-color: #374151; }}
  .card-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px;
  }}
  .card-title {{ font-size: 14px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.8px; display: flex; align-items: center; gap: 8px; }}
  .card-badge {{
    font-size: 11px; padding: 2px 8px; border-radius: 10px;
    background: rgba(99,102,241,0.15); color: var(--accent); border: 1px solid rgba(99,102,241,0.3);
  }}

  /* A股 */
  .stock-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .stock-item {{
    background: rgba(255,255,255,0.03); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px; text-align: center;
  }}
  .stock-name {{ font-size: 12px; color: var(--muted); margin-bottom: 4px; }}
  .stock-code {{ font-size: 10px; color: #475569; margin-bottom: 8px; }}
  .stock-price {{ font-size: 18px; font-weight: 700; margin-bottom: 4px; }}
  .stock-chg {{ font-size: 12px; font-weight: 600; padding: 2px 6px; border-radius: 4px; }}
  .up {{ color: var(--red); }}
  .down {{ color: var(--green); }}
  .up-bg {{ background: rgba(239,68,68,0.1); color: var(--red); }}
  .down-bg {{ background: rgba(16,185,129,0.1); color: var(--green); }}

  /* 加密货币 */
  .crypto-list {{ display: flex; flex-direction: column; gap: 12px; }}
  .crypto-item {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 14px; background: rgba(255,255,255,0.03);
    border: 1px solid var(--border); border-radius: 10px;
  }}
  .crypto-left {{ display: flex; align-items: center; gap: 10px; }}
  .crypto-icon {{ width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700; }}
  .crypto-name {{ font-size: 14px; font-weight: 600; }}
  .crypto-sym {{ font-size: 11px; color: var(--muted); }}
  .crypto-right {{ text-align: right; }}
  .crypto-price {{ font-size: 15px; font-weight: 700; }}
  .crypto-pct {{ font-size: 12px; font-weight: 600; }}
  .crypto-mcap {{ font-size: 11px; color: var(--muted); }}

  /* 面经 */
  .offer-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }}
  .stat-box {{
    text-align: center; padding: 14px;
    background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 10px;
  }}
  .stat-num {{ font-size: 28px; font-weight: 800; color: var(--accent); }}
  .stat-label {{ font-size: 11px; color: var(--muted); margin-top: 4px; }}
  .post-list {{ display: flex; flex-direction: column; gap: 8px; }}
  .post-item {{
    display: flex; align-items: center; gap: 10px; padding: 10px 12px;
    background: rgba(255,255,255,0.03); border: 1px solid var(--border); border-radius: 8px;
  }}
  .post-company {{
    font-size: 11px; padding: 2px 7px; border-radius: 6px; white-space: nowrap;
    font-weight: 600;
  }}
  .bytedance {{ background: rgba(239,68,68,0.15); color: #fb7185; }}
  .tencent {{ background: rgba(16,185,129,0.15); color: #34d399; }}
  .goldman {{ background: rgba(245,158,11,0.15); color: var(--gold); }}
  .post-title {{ font-size: 13px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .post-date {{ font-size: 11px; color: var(--muted); white-space: nowrap; }}

  /* 日报 */
  .report-link {{
    display: block; padding: 16px 20px;
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(16,185,129,0.08));
    border: 1px solid rgba(99,102,241,0.3); border-radius: 12px;
    text-decoration: none; color: var(--text); transition: all 0.2s;
    margin-bottom: 14px;
  }}
  .report-link:hover {{ border-color: var(--accent); transform: translateY(-1px); }}
  .report-title {{ font-size: 16px; font-weight: 700; margin-bottom: 6px; }}
  .report-meta {{ font-size: 12px; color: var(--muted); }}
  .report-tags {{ display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }}
  .tag {{
    font-size: 11px; padding: 3px 9px; border-radius: 6px;
    background: rgba(99,102,241,0.15); color: var(--accent); border: 1px solid rgba(99,102,241,0.2);
  }}

  /* 市场情绪 */
  .sentiment-bar {{
    display: flex; align-items: center; gap: 10px; margin: 8px 0;
  }}
  .sentiment-label {{ font-size: 12px; color: var(--muted); width: 60px; }}
  .bar-track {{ flex: 1; height: 8px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 4px; transition: width 1s ease; }}
  .bar-val {{ font-size: 12px; font-weight: 600; width: 40px; text-align: right; }}

  .footer {{
    text-align: center; margin-top: 28px; padding-top: 20px;
    border-top: 1px solid var(--border); color: #475569; font-size: 12px;
  }}
  .quick-links {{ display: flex; justify-content: center; gap: 20px; margin-top: 10px; }}
  .quick-links a {{
    color: var(--muted); text-decoration: none; font-size: 12px;
    transition: color 0.2s;
  }}
  .quick-links a:hover {{ color: var(--accent); }}
</style>
</head>
<body>
<header>
  <div class="logo">
    <span class="logo-icon">🦅</span>
    <div>
      <h1>OpenClaw Demo</h1>
      <span>AI 投研 · 面经 · 市场监控</span>
    </div>
  </div>
  <div style="text-align:right">
    <div class="live-badge"><span class="pulse"></span> LIVE {updated}</div>
    <div style="font-size:11px;color:#475569;margin-top:6px">周六 · A股休市</div>
  </div>
</header>

<div class="grid">
  <!-- 日报 -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">📰 国智投洞见</div>
      <span class="card-badge">第4期</span>
    </div>
    <a class="report-link" href="{feishu_url}" target="_blank">
      <div class="report-title">国智投洞见 · 第4期</div>
      <div class="report-meta">覆盖 2026.02.22–02.28 · AI产业深度分析</div>
      <div class="report-tags">
        <span class="tag">Qwen3.5</span>
        <span class="tag">具身智能</span>
        <span class="tag">字节自研芯片</span>
        <span class="tag">阶跃港股IPO</span>
        <span class="tag">阿里云Coding</span>
      </div>
    </a>
    <div class="sentiment-bar">
      <span class="sentiment-label">AI融资</span>
      <div class="bar-track"><div class="bar-fill" style="width:88%;background:linear-gradient(90deg,#6366f1,#8b5cf6)"></div></div>
      <span class="bar-val" style="color:#818cf8">热🔥</span>
    </div>
    <div class="sentiment-bar">
      <span class="sentiment-label">具身智能</span>
      <div class="bar-track"><div class="bar-fill" style="width:82%;background:linear-gradient(90deg,#f59e0b,#f97316)"></div></div>
      <span class="bar-val" style="color:#fbbf24">↑82%</span>
    </div>
    <div class="sentiment-bar">
      <span class="sentiment-label">大模型</span>
      <div class="bar-track"><div class="bar-fill" style="width:95%;background:linear-gradient(90deg,#10b981,#06b6d4)"></div></div>
      <span class="bar-val" style="color:#34d399">↑95%</span>
    </div>
  </div>

  <!-- 加密货币 -->
  <div class="card">
    <div class="card-header">
      <div class="card-title">🌊 加密市场</div>
      <span class="card-badge">实时</span>
    </div>
    <div class="crypto-list">
      {crypto_html}
    </div>
  </div>

  <!-- A股 -->
  <div class="card full">
    <div class="card-header">
      <div class="card-title">📈 A股监控</div>
      <span class="card-badge">上周五收盘</span>
    </div>
    <div class="stock-grid">
      {stock_html}
    </div>
  </div>

  <!-- 面经 -->
  <div class="card full">
    <div class="card-header">
      <div class="card-title">🎓 面经爪 OfferClaw</div>
      <a href="http://localhost:3000" target="_blank" style="font-size:12px;color:var(--accent);text-decoration:none">
        → 打开完整界面
      </a>
    </div>
    <div class="offer-stats">
      <div class="stat-box">
        <div class="stat-num">{total_posts}</div>
        <div class="stat-label">已收录面经</div>
      </div>
      <div class="stat-box">
        <div class="stat-num">{total_companies}</div>
        <div class="stat-label">覆盖公司</div>
      </div>
      <div class="stat-box">
        <div class="stat-num">RAG</div>
        <div class="stat-label">向量检索就绪</div>
      </div>
    </div>
    <div class="post-list">
      {posts_html}
    </div>
  </div>
</div>

<div class="footer">
  Powered by OpenClaw · 数据来源：CoinGecko / A股 / 牛客网
  <div class="quick-links">
    <a href="http://localhost:5000" target="_blank">📈 A股完整图表</a>
    <a href="http://localhost:3000" target="_blank">🎓 面经搜索</a>
    <a href="http://localhost:8000/docs" target="_blank">📡 API文档</a>
    <a href="{feishu_url}" target="_blank">📰 飞书日报</a>
  </div>
</div>

<script>
// 每5分钟自动刷新
setTimeout(() => location.reload(), 5 * 60 * 1000);
</script>
</body>
</html>"""

CRYPTO_COLORS = {
    "bitcoin": ("#f7931a", "₿"),
    "ethereum": ("#627eea", "Ξ"),
    "solana": ("#9945ff", "◎"),
    "binancecoin": ("#f3ba2f", "Ƀ"),
}

def fmt_mcap(v):
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9:  return f"${v/1e9:.1f}B"
    return f"${v/1e6:.0f}M"

def build_html():
    # 加密货币
    cryptos = fetch_crypto()
    crypto_html = ""
    for c in (cryptos if isinstance(cryptos, list) else []):
        cid = c.get("id", "")
        color, icon = CRYPTO_COLORS.get(cid, ("#888", "?"))
        pct = c.get("price_change_percentage_24h", 0) or 0
        pct_cls = "up" if pct > 0 else "down"
        pct_str = f"+{pct:.2f}%" if pct > 0 else f"{pct:.2f}%"
        price = c.get("current_price", 0)
        price_str = f"${price:,.2f}" if price < 10000 else f"${price:,.0f}"
        crypto_html += f"""
        <div class="crypto-item">
          <div class="crypto-left">
            <div class="crypto-icon" style="background:rgba(255,255,255,0.06);color:{color}">{icon}</div>
            <div>
              <div class="crypto-name">{c.get('name','')}</div>
              <div class="crypto-sym">{c.get('symbol','').upper()}</div>
            </div>
          </div>
          <div class="crypto-right">
            <div class="crypto-price">{price_str}</div>
            <div class="crypto-pct {pct_cls}">{pct_str}</div>
            <div class="crypto-mcap">{fmt_mcap(c.get('market_cap',0))}</div>
          </div>
        </div>"""

    # A股
    stocks_raw = fetch_json(f"{ASTOCK_URL}/api/stocks").get("data", [])
    stock_html = ""
    for s in stocks_raw[:8]:
        pct = s.get("change_pct", 0) or 0
        up = pct >= 0
        pct_str = f"+{pct:.2f}%" if up else f"{pct:.2f}%"
        price = s.get("price", 0)
        stock_html += f"""
        <div class="stock-item">
          <div class="stock-name">{s.get('name','')}</div>
          <div class="stock-code">{s.get('code','')}</div>
          <div class="stock-price {'up' if up else 'down'}">¥{price:.2f}</div>
          <span class="stock-chg {'up-bg' if up else 'down-bg'}">{pct_str}</span>
        </div>"""
    if not stock_html:
        stock_html = '<div style="color:#475569;grid-column:1/-1;text-align:center;padding:20px">A股数据加载中...</div>'

    # 面经
    posts_data = fetch_json(f"{OFFERCLAW_URL}/posts?page_size=6")
    posts = posts_data.get("posts", [])
    total_posts = posts_data.get("total", len(posts))
    companies = fetch_json(f"{OFFERCLAW_URL}/companies").get("companies", [])
    total_companies = len(companies)

    co_cls = {"字节跳动": "bytedance", "腾讯": "tencent", "高盛": "goldman"}
    co_emoji = {"字节跳动": "字节", "腾讯": "腾讯", "高盛": "GS"}
    posts_html = ""
    for p in posts[:6]:
        co = p.get("company", "")
        cls = co_cls.get(co, "bytedance")
        label = co_emoji.get(co, co[:2])
        title = p.get("title", "")[:38]
        date = p.get("timestamp", "")[:7]
        posts_html += f"""
        <div class="post-item">
          <span class="post-company {cls}">{label}</span>
          <span class="post-title">{title}</span>
          <span class="post-date">{date}</span>
        </div>"""

    return HTML_TEMPLATE.format(
        updated=datetime.now().strftime("%H:%M:%S"),
        feishu_url=FEISHU_DOC,
        crypto_html=crypto_html,
        stock_html=stock_html,
        posts_html=posts_html or '<div style="color:#475569;padding:20px">面经服务未启动</div>',
        total_posts=total_posts,
        total_companies=total_companies,
    )

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass  # 静默日志
    def do_GET(self):
        if self.path == "/":
            html = build_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(html))
            self.end_headers()
            self.wfile.write(html)
        else:
            self.send_response(404); self.end_headers()

if __name__ == "__main__":
    print(f"🦅 OpenClaw Demo Dashboard")
    print(f"   http://localhost:{PORT}")
    print(f"   Ctrl+C 退出")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
