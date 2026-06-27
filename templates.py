"""
=============================================================================
  TEMPLATES MODULE — CSS, HTML Shell, Badge helpers
=============================================================================
"""

# Nhãn độ khó
DIFFICULTY_COLORS = {
    "Dễ":        ("#10b981", "rgba(16,185,129,.15)"),
    "Trung bình": ("#f59e0b", "rgba(245,158,11,.15)"),
    "Khó":        ("#ef4444", "rgba(239,68,68,.15)"),
    "Rất khó":    ("#9333ea", "rgba(147,51,234,.15)"),
}

CSS = """
<style>
:root{--bg:#0d0f1a;--bg2:#131626;--card:#1a1d2e;--card2:#1f2338;--purple:#7c3aed;--purple-l:#9f5ff5;
  --cyan:#06b6d4;--green:#10b981;--yellow:#f59e0b;--red:#ef4444;--orange:#f97316;
  --text:#e2e8f0;--text2:#94a3b8;--muted:#64748b;--border:#2d3148;
  --grad:linear-gradient(135deg,#7c3aed,#06b6d4);}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;
  background-image:radial-gradient(ellipse at 20% 20%,rgba(124,58,237,.08) 0,transparent 50%),
  radial-gradient(ellipse at 80% 80%,rgba(6,182,212,.06) 0,transparent 50%)}
.topnav{background:rgba(19,22,38,.95);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);
  padding:12px 0;position:sticky;top:0;z-index:999}
.brand{font-size:1.25rem;font-weight:800;background:var(--grad);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;text-decoration:none}
.navlink{color:var(--text2)!important;text-decoration:none;padding:6px 14px!important;border-radius:8px;
  font-weight:500;font-size:.875rem;transition:all .2s}
.navlink:hover,.navlink.active{color:var(--text)!important;background:rgba(124,58,237,.2)}
.card-c{background:linear-gradient(135deg,var(--card),var(--card2));border:1px solid var(--border);
  border-radius:16px;overflow:hidden}
.card-head{background:linear-gradient(135deg,rgba(124,58,237,.15),rgba(6,182,212,.1));
  border-bottom:1px solid var(--border);padding:16px 20px}
.btn-g{background:var(--grad);border:none;color:#fff;font-weight:600;border-radius:10px;
  transition:all .3s;cursor:pointer;text-decoration:none;display:inline-block}
.btn-g:hover{transform:translateY(-1px);box-shadow:0 6px 24px rgba(124,58,237,.4);color:#fff}
.btn-o{background:transparent;border:1px solid var(--border);color:var(--text2);border-radius:10px;
  font-weight:500;transition:all .2s;text-decoration:none;display:inline-block;cursor:pointer}
.btn-o:hover{border-color:var(--purple);color:var(--purple-l);background:rgba(124,58,237,.1)}
.btn-r{background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.3);color:#f87171;
  border-radius:8px;cursor:pointer;font-weight:500;transition:all .2s}
.btn-r:hover{background:rgba(239,68,68,.25)}
.fc{background:rgba(13,15,26,.8)!important;border:1px solid var(--border)!important;
  border-radius:10px!important;color:var(--text)!important;transition:all .2s}
.fc:focus{border-color:var(--purple)!important;box-shadow:0 0 0 3px rgba(124,58,237,.2)!important;
  color:var(--text)!important;outline:none}
.fc::placeholder{color:var(--muted)}
textarea.fc{font-family:'JetBrains Mono',monospace;font-size:.85rem;resize:vertical}
.fl{color:var(--text2);font-size:.85rem;font-weight:500;margin-bottom:6px;display:block}
.sb{padding:3px 9px;border-radius:20px;font-size:.72rem;font-weight:700;letter-spacing:.04em}
.bac{background:rgba(16,185,129,.2);color:#10b981;border:1px solid rgba(16,185,129,.3)}
.bwa{background:rgba(239,68,68,.2);color:#ef4444;border:1px solid rgba(239,68,68,.3)}
.btle{background:rgba(245,158,11,.2);color:#f59e0b;border:1px solid rgba(245,158,11,.3)}
.bre{background:rgba(249,115,22,.2);color:#f97316;border:1px solid rgba(249,115,22,.3)}
.sr{width:72px;height:72px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:1.3rem;font-weight:800;flex-shrink:0}
.s100{background:rgba(16,185,129,.2);border:3px solid #10b981;color:#10b981}
.shi{background:rgba(6,182,212,.2);border:3px solid #06b6d4;color:#06b6d4}
.smi{background:rgba(245,158,11,.2);border:3px solid #f59e0b;color:#f59e0b}
.slo{background:rgba(239,68,68,.2);border:3px solid #ef4444;color:#ef4444}
.pitem{background:var(--card);border:1px solid var(--border);border-radius:12px;
  padding:14px 18px;margin-bottom:8px;transition:all .2s;display:flex;
  align-items:center;gap:14px;text-decoration:none;color:inherit}
.pitem:hover{border-color:var(--purple);background:var(--card2);color:inherit;text-decoration:none}
.exam-section{margin-bottom:18px}
.exam-label{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
  color:var(--purple-l);margin-bottom:6px;display:flex;align-items:center;gap:6px}
.exam-content{background:rgba(13,15,26,.5);border:1px solid var(--border);border-radius:10px;
  padding:14px 16px;line-height:1.75;font-size:.9rem;color:var(--text);white-space:pre-wrap}
.exam-io{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.ex-table{width:100%;border-collapse:collapse;font-size:.82rem}
.ex-table th{background:rgba(124,58,237,.15);color:var(--purple-l);padding:7px 10px;
  text-align:left;font-weight:600;font-size:.75rem;border:1px solid var(--border)}
.ex-table td{padding:7px 10px;border:1px solid var(--border);color:var(--text);
  font-family:'JetBrains Mono',monospace;vertical-align:top}
.ex-table .expl-col{font-family:'Inter',sans-serif;color:var(--text2);font-size:.8rem}
.constraint-box{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.25);
  border-radius:10px;padding:12px 16px;font-size:.85rem;line-height:1.8;color:var(--text)}
.code-ed{font-family:'JetBrains Mono',monospace!important;font-size:.875rem;line-height:1.6;
  background:#0d1117!important;border:1px solid var(--border)!important;border-radius:12px!important;
  color:#e6edf3!important;padding:14px!important}
.code-ed:focus{border-color:var(--purple)!important;box-shadow:0 0 0 3px rgba(124,58,237,.15)!important}
.tct{width:100%;border-collapse:separate;border-spacing:0 5px;font-size:.82rem}
.tcr td{background:var(--card);padding:9px 12px;
  border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
.tcr td:first-child{border-left:1px solid var(--border);border-radius:8px 0 0 8px}
.tcr td:last-child{border-right:1px solid var(--border);border-radius:0 8px 8px 0}
.tcr.ac td{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.05)}
.tcr.wa td{border-color:rgba(239,68,68,.3);background:rgba(239,68,68,.05)}
.tcr.tle td{border-color:rgba(245,158,11,.3);background:rgba(245,158,11,.05)}
.tcr.re td{border-color:rgba(249,115,22,.3);background:rgba(249,115,22,.05)}
.prog{height:5px;background:var(--border);border-radius:3px;overflow:hidden}
.prog-b{height:100%;background:var(--grad);border-radius:3px;transition:width .6s}
.a-ok{background:rgba(16,185,129,.15);border:1px solid rgba(16,185,129,.3);color:#34d399;
  border-radius:12px;padding:12px 16px;font-size:.9rem}
.a-err{background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.3);color:#f87171;
  border-radius:12px;padding:12px 16px;font-size:.9rem}
.ai-sec{background:linear-gradient(135deg,rgba(124,58,237,.08),rgba(6,182,212,.06));
  border:1px solid rgba(124,58,237,.25);border-radius:20px;padding:24px;position:relative;overflow:hidden}
.ai-sec::before{content:'✨';position:absolute;top:-20px;right:-10px;font-size:5rem;opacity:.07;pointer-events:none}
.import-sec{background:linear-gradient(135deg,rgba(6,182,212,.08),rgba(16,185,129,.06));
  border:1px solid rgba(6,182,212,.25);border-radius:20px;padding:24px;position:relative;overflow:hidden}
.import-sec::before{content:'📄';position:absolute;top:-20px;right:-10px;font-size:5rem;opacity:.07;pointer-events:none}
.ai-badge{display:inline-flex;align-items:center;gap:6px;padding:3px 11px;border-radius:20px;
  font-size:.78rem;font-weight:600;margin-bottom:14px}
.ab-ai{background:rgba(124,58,237,.2);border:1px solid rgba(124,58,237,.4);color:var(--purple-l)}
.ab-import{background:rgba(6,182,212,.2);border:1px solid rgba(6,182,212,.4);color:var(--cyan)}
.dropzone{border:2px dashed var(--border);border-radius:14px;padding:28px;text-align:center;
  transition:all .3s;cursor:pointer;background:rgba(13,15,26,.4)}
.dropzone:hover,.dropzone.drag-over{border-color:var(--cyan);background:rgba(6,182,212,.06)}
.tab-bar{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:20px}
.tab-btn{padding:8px 18px;border-radius:10px 10px 0 0;font-size:.875rem;font-weight:500;
  color:var(--text2);background:transparent;border:none;cursor:pointer;transition:all .2s;
  border-bottom:2px solid transparent;margin-bottom:-1px}
.tab-btn.active{color:var(--text);border-bottom-color:var(--purple);background:rgba(124,58,237,.1)}
.tab-panel{display:none}.tab-panel.active{display:block}
.log-e{background:var(--card);border:1px solid var(--border);border-radius:14px;
  margin-bottom:14px;overflow:hidden;transition:all .2s}
.log-e:hover{border-color:rgba(124,58,237,.35)}
.log-h{padding:14px 18px;display:flex;align-items:center;justify-content:space-between;
  cursor:pointer;background:linear-gradient(135deg,rgba(26,29,46,.8),rgba(31,35,56,.8))}
.log-code{background:#0d1117;padding:14px;font-family:'JetBrains Mono',monospace;
  font-size:.8rem;line-height:1.6;overflow-x:auto;border-top:1px solid var(--border);
  color:#e6edf3;white-space:pre;display:none}
.spin{width:20px;height:20px;border:2.5px solid rgba(124,58,237,.2);border-top-color:var(--purple);
  border-radius:50%;animation:sp .8s linear infinite;display:inline-block;vertical-align:middle}
@keyframes sp{to{transform:rotate(360deg)}}
.fi{animation:fi .35s ease-in}
@keyframes fi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
footer{border-top:1px solid var(--border);padding:20px 0;margin-top:60px;text-align:center}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--purple)}
</style>"""

HTML_SHELL = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Mini Online Judge - On thi Chuyen Tin lop 9">
<title>{page_title} | Mini OJ</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
{css}
{extra_head}
</head>
<body>
<nav class="topnav">
  <div class="container d-flex align-items-center gap-3">
    <a href="/" class="brand"><i class="bi bi-code-slash"></i> OJ Chuyên Tin</a>
    <div class="d-flex gap-1 ms-auto">
      <a href="/" class="navlink {h}"><i class="bi bi-house-fill me-1"></i>Trang Chủ</a>
      <a href="/student" class="navlink {s}"><i class="bi bi-person-fill me-1"></i>Học Sinh</a>
      <a href="/admin" class="navlink {a}"><i class="bi bi-shield-fill-check me-1"></i>Admin</a>
      <a href="/parent" class="navlink {p}"><i class="bi bi-eye-fill me-1"></i>Phụ Huynh</a>
    </div>
  </div>
</nav>
{content}
<footer><p style="color:var(--muted);font-size:.82rem;margin:0">
  <i class="bi bi-cpu me-1"></i>Mini OJ — Chuyên Tin Lớp 9 v3.0
  &nbsp;|&nbsp; Powered by <span style="color:var(--purple-l)">Google Gemini AI</span>
  &nbsp;|&nbsp; Python &amp; C++
</p></footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
function toggleCode(id){{const e=document.getElementById('code-'+id);if(e)e.style.display=e.style.display==='none'?'block':'none';}}
function switchTab(name){{
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.toggle('active',p.id==='tab-'+name));
}}
</script>
</body>
</html>"""


def page(content: str, active: str = "home", extra_head: str = "") -> str:
    titles = {"home": "Trang Chủ", "student": "Làm Bài", "admin": "Admin", "parent": "Nhật Ký"}
    return HTML_SHELL.format(
        page_title=titles.get(active, "Mini OJ"),
        css=CSS,
        extra_head=extra_head,
        h="active" if active == "home" else "",
        s="active" if active == "student" else "",
        a="active" if active == "admin" else "",
        p="active" if active == "parent" else "",
        content=content,
    )


def diff_badge(d: str) -> str:
    c, bg = DIFFICULTY_COLORS.get(d, ("#94a3b8", "rgba(100,116,139,.15)"))
    return f'<span class="sb" style="background:{bg};color:{c};border:1px solid {c}40">{d}</span>'


def source_badge(s: str) -> str:
    if s == "AI Generated":
        return '<span class="sb" style="background:rgba(124,58,237,.2);color:var(--purple-l);border:1px solid rgba(124,58,237,.3);font-size:.65rem">✨AI</span>'
    if s == "Imported":
        return '<span class="sb" style="background:rgba(6,182,212,.2);color:var(--cyan);border:1px solid rgba(6,182,212,.3);font-size:.65rem">📄Import</span>'
    return ''
