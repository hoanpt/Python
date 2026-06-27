"""Routes: Học sinh /student/*"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import HTMLResponse

from database import get_all_problems, get_problem, add_submission
from judge import judge
from templates import page, diff_badge, source_badge

router = APIRouter()


@router.get("/student", response_class=HTMLResponse)
async def student_list():
    probs = get_all_problems()

    if not probs:
        body = """<div class="text-center py-5">
          <div style="font-size:3rem">📭</div>
          <p style="color:var(--muted);margin-top:12px">Chưa có bài tập nào.<br>
          Admin hãy import đề thi hoặc dùng AI ra đề.</p>
          <a href="/admin" class="btn-o btn mt-3"><i class="bi bi-upload me-1"></i>Import Đề Thi</a>
        </div>"""
    else:
        grouped = {}
        for p in probs:
            key = p.get("source_exam", "") or "Bài Tập Tổng Hợp"
            grouped.setdefault(key, []).append(p)

        body = ""
        for exam_name, items in grouped.items():
            body += f"""
            <div class="mb-4">
              <div style="font-size:.75rem;color:var(--muted);font-weight:600;text-transform:uppercase;
                letter-spacing:.08em;margin-bottom:10px;padding-left:4px">
                <i class="bi bi-collection me-1"></i>{exam_name}
              </div>"""
            for i, p in enumerate(items):
                tc = len(p.get("testcases", []))
                sc = p.get("score_points", 0)
                sc_str = f"{sc:.1f}đ" if sc else ""
                inp_f = p.get("input_filename", "")
                body += f"""
              <a href="/student/solve/{p['id']}" class="pitem">
                <div style="width:34px;height:34px;border-radius:9px;background:rgba(124,58,237,.2);
                  display:flex;align-items:center;justify-content:center;font-weight:700;
                  color:var(--purple-l);font-size:.82rem;flex-shrink:0">{i+1}</div>
                <div class="flex-grow-1">
                  <div style="font-weight:600;color:var(--text);display:flex;align-items:center;gap:7px;flex-wrap:wrap">
                    {p.get('title','?')}
                    {source_badge(p.get('source',''))}
                    {diff_badge(p.get('difficulty','Trung bình'))}
                    {"<span class='sb' style='background:rgba(245,158,11,.15);color:var(--yellow);border:1px solid rgba(245,158,11,.3);font-size:.65rem'>"+sc_str+"</span>" if sc_str else ""}
                  </div>
                  <div style="font-size:.78rem;color:var(--muted);margin-top:3px">
                    {"<i class='bi bi-file-earmark-text me-1'></i>"+inp_f+" &nbsp;·&nbsp;" if inp_f else ""}
                    <i class="bi bi-list-check me-1"></i>{tc} testcase
                    &nbsp;·&nbsp;<i class="bi bi-hourglass me-1"></i>Timeout 2s
                  </div>
                </div>
                <i class="bi bi-arrow-right-circle" style="color:var(--muted)"></i>
              </a>"""
            body += "</div>"

    content = f"""
<div class="container" style="max-width:800px;padding:36px 12px 60px">
  <div class="d-flex align-items-center justify-content-between mb-4">
    <div>
      <h2 style="font-weight:700;color:var(--text)">
        <i class="bi bi-collection-fill me-2" style="color:var(--purple-l)"></i>Danh Sách Bài Tập
      </h2>
      <p style="color:var(--text2);font-size:.875rem;margin:0">Chọn bài để bắt đầu luyện tập</p>
    </div>
    <a href="/parent" class="btn-o btn btn-sm py-1"><i class="bi bi-clock-history me-1"></i>Nhật Ký</a>
  </div>
  {body}
</div>"""
    return page(content, "student")


@router.get("/student/solve/{pid}", response_class=HTMLResponse)
async def student_solve(pid: str):
    """Trang làm bài — hiển thị đúng chuẩn đề thi thật."""
    p = get_problem(pid)
    if not p:
        raise HTTPException(404, "Khong tim thay bai")

    title = p.get("title", "")
    desc = p.get("description", "")
    inp_fmt = p.get("input_format", "")
    out_fmt = p.get("output_format", "")
    const = p.get("constraints", "")
    examples = p.get("examples", [])
    inp_f = p.get("input_filename", "")
    out_f = p.get("output_filename", "")
    sc_pts = p.get("score_points", "")
    src_ex = p.get("source_exam", "")
    tc_cnt = len(p.get("testcases", []))

    has_expl = any(e.get("explanation") for e in examples)
    ex_rows = ""
    for e in examples:
        ex_rows += f"""<tr>
          <td style="white-space:pre">{e.get('input','')}</td>
          <td style="white-space:pre">{e.get('output','')}</td>
          {"<td class='expl-col'>"+e.get('explanation','')+"</td>" if has_expl else ""}
        </tr>"""
    ex_table = f"""
    <div class="exam-section">
      <div class="exam-label"><i class="bi bi-table"></i>VÍ DỤ</div>
      <div style="overflow-x:auto;border-radius:10px;border:1px solid var(--border)">
        <table class="ex-table">
          <thead><tr>
            <th>{inp_f or 'INPUT'}</th>
            <th>{out_f or 'OUTPUT'}</th>
            {"<th>GIẢI THÍCH</th>" if has_expl else ""}
          </tr></thead>
          <tbody>{ex_rows}</tbody>
        </table>
      </div>
    </div>""" if examples else ""

    note_html = f"""
    <div style="background:rgba(245,158,11,.1);border:1px solid rgba(245,158,11,.25);
      border-radius:8px;padding:10px 14px;font-size:.8rem;color:var(--yellow);margin-top:10px">
      <i class="bi bi-info-circle me-1"></i>
      <strong>Lưu ý:</strong> Đề gốc dùng file <code>{inp_f}</code>/<code>{out_f}</code>.
      Trong hệ thống này dùng <code>input()</code> / <code>print()</code> (stdin/stdout).
    </div>""" if inp_f else ""

    content = f"""
<div class="container" style="max-width:1080px;padding:24px 12px 60px">
  <div class="mb-3">
    <a href="/student" style="color:var(--muted);text-decoration:none;font-size:.85rem">
      <i class="bi bi-arrow-left me-1"></i>Quay lại danh sách
    </a>
  </div>
  <div style="background:linear-gradient(135deg,rgba(124,58,237,.12),rgba(6,182,212,.08));
    border:1px solid rgba(124,58,237,.25);border-radius:16px;padding:18px 22px;margin-bottom:20px">
    <div class="d-flex align-items-start justify-content-between flex-wrap gap-3">
      <div>
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px">
          <h3 style="font-weight:800;color:var(--text);margin:0">Bài {title}</h3>
          {diff_badge(p.get('difficulty','Trung bình'))}
          {"<span class='sb' style='background:rgba(245,158,11,.2);color:var(--yellow);border:1px solid rgba(245,158,11,.3)'>"+str(sc_pts)+"đ</span>" if sc_pts else ""}
        </div>
        <div style="font-size:.82rem;color:var(--muted)">
          {"<i class='bi bi-file-earmark-arrow-in me-1'></i>"+inp_f+" &nbsp;→&nbsp; <i class='bi bi-file-earmark-arrow-out me-1'></i>"+out_f+"&nbsp;&nbsp;·&nbsp;&nbsp;" if inp_f else ""}
          {"<i class='bi bi-journal-text me-1'></i>"+src_ex+"&nbsp;&nbsp;·&nbsp;&nbsp;" if src_ex else ""}
          <i class="bi bi-list-check me-1"></i>{tc_cnt} testcase &nbsp;·&nbsp; <i class="bi bi-hourglass me-1"></i>Timeout 2s
        </div>
      </div>
      <a href="/student" class="btn-o btn btn-sm py-1"><i class="bi bi-grid me-1"></i>Tất cả bài</a>
    </div>
  </div>
  <div class="row g-4">
    <div class="col-lg-5">
      <div class="card-c" style="height:fit-content;position:sticky;top:70px;max-height:85vh;overflow-y:auto">
        <div class="card-head">
          <span style="font-weight:600;color:var(--text);font-size:.9rem">
            <i class="bi bi-file-text me-2" style="color:var(--cyan)"></i>Đề Bài
          </span>
        </div>
        <div class="p-4">
          <div class="exam-section">
            <div class="exam-label"><i class="bi bi-text-paragraph"></i>MÔ TẢ BÀI TOÁN</div>
            <div class="exam-content">{desc}</div>
          </div>
          <div class="exam-section">
            <div class="exam-label"><i class="bi bi-arrow-left-right"></i>ĐỊNH DẠNG DỮ LIỆU</div>
            <div class="exam-io">
              <div>
                <div style="font-size:.72rem;color:var(--cyan);font-weight:600;margin-bottom:5px">DỮ LIỆU VÀO</div>
                <div class="exam-content" style="font-size:.82rem">{inp_fmt or "—"}</div>
              </div>
              <div>
                <div style="font-size:.72rem;color:var(--green);font-weight:600;margin-bottom:5px">DỮ LIỆU RA</div>
                <div class="exam-content" style="font-size:.82rem">{out_fmt or "—"}</div>
              </div>
            </div>
          </div>
          {ex_table}
          {"<div class='exam-section'><div class='exam-label'><i class='bi bi-shield-check'></i>RÀNG BUỘC (SUBTASK)</div><div class='constraint-box'>"+const+"</div></div>" if const else ""}
        </div>
      </div>
    </div>
    <div class="col-lg-7">
      <div class="card-c">
        <div class="card-head d-flex align-items-center justify-content-between">
          <span style="font-weight:600;color:var(--text);font-size:.9rem">
            <i class="bi bi-code-slash me-2" style="color:var(--cyan)"></i>Code Editor
          </span>
          <div class="d-flex align-items-center gap-2">
            <select id="langSelect" onchange="changeLang(this.value)"
              style="background:rgba(13,15,26,.8);color:var(--cyan);border:1px solid var(--border);
              border-radius:8px;padding:3px 10px;font-size:.78rem;font-weight:600;cursor:pointer">
              <option value="python" selected>🐍 Python 3</option>
              <option value="cpp">⚡ C++ 17</option>
            </select>
            <button onclick="clearCode()" class="btn-o btn btn-sm" style="padding:3px 10px;font-size:.78rem">
              <i class="bi bi-trash me-1"></i>Xóa
            </button>
          </div>
        </div>
        <div class="p-4">
          {note_html}
          <form method="POST" action="/student/submit/{pid}" id="submitForm" style="margin-top:12px">
            <div class="mb-3">
              <label class="fl">Tên học sinh</label>
              <input type="text" name="student_name" class="form-control fc"
                placeholder="Ví dụ: Nguyễn Văn An" required
                style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
            </div>
            <input type="hidden" name="language" id="langInput" value="python">
            <div class="mb-3">
              <label class="fl" id="codeLangLabel">Code Python</label>
              <div id="cmEditorWrap" style="border-radius:12px;overflow:hidden;border:1px solid var(--border);
                min-height:360px;background:#0d1117"></div>
              <textarea name="code" id="codeEd" class="code-ed form-control" rows="18"
                placeholder="# Viết code Python tại đây&#10;# Dùng input() để đọc dữ liệu&#10;# Dùng print() để in kết quả&#10;&#10;n = int(input())&#10;..." required
                style="display:none"></textarea>
            </div>
            <button type="submit" class="btn-g btn w-100 py-2" id="subBtn" style="font-size:.95rem">
              <i class="bi bi-send-fill me-2"></i>Nộp Bài &amp; Chấm Điểm
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>

<script type="module">
import {{EditorView, basicSetup}} from 'https://cdn.jsdelivr.net/npm/codemirror@6.65.7/+esm';
import {{python}} from 'https://cdn.jsdelivr.net/npm/@codemirror/lang-python@6.1.6/+esm';
import {{cpp}} from 'https://cdn.jsdelivr.net/npm/@codemirror/lang-cpp@6.0.2/+esm';
import {{oneDark}} from 'https://cdn.jsdelivr.net/npm/@codemirror/theme-one-dark@6.1.2/+esm';
import {{EditorState}} from 'https://cdn.jsdelivr.net/npm/@codemirror/state@6.4.1/+esm';
import {{keymap, indentWithTab}} from 'https://cdn.jsdelivr.net/npm/@codemirror/view@6.26.3/+esm';

const KEY = 'code_{pid}';
const LANG_KEY = 'lang_{pid}';
const wrap = document.getElementById('cmEditorWrap');
const ta = document.getElementById('codeEd');
const langSel = document.getElementById('langSelect');
const langInp = document.getElementById('langInput');
const langLabel = document.getElementById('codeLangLabel');

const savedLang = localStorage.getItem(LANG_KEY) || 'python';
langSel.value = savedLang;
langInp.value = savedLang;
langLabel.textContent = savedLang === 'cpp' ? 'Code C++' : 'Code Python';

const savedCode = localStorage.getItem(KEY) || '';

function getLangExt(lang) {{
  return lang === 'cpp' ? cpp() : python();
}}

function createExtensions(lang) {{
  return [
    basicSetup, oneDark, getLangExt(lang),
    keymap.of([indentWithTab]),
    EditorView.updateListener.of(update => {{
      if (update.docChanged) {{
        const code = view.state.doc.toString();
        localStorage.setItem(KEY, code);
        ta.value = code;
      }}
    }}),
    EditorView.theme({{
      '&': {{ fontSize: '14px', minHeight: '360px' }},
      '.cm-content': {{ fontFamily: "'JetBrains Mono', monospace", padding: '10px 0' }},
      '.cm-gutters': {{ background: '#0d1117', borderRight: '1px solid #2d3148' }},
      '.cm-scroller': {{ minHeight: '360px' }},
    }}),
  ];
}}

let view = new EditorView({{
  state: EditorState.create({{ doc: savedCode, extensions: createExtensions(savedLang) }}),
  parent: wrap,
}});
ta.value = savedCode;

window.changeLang = function(lang) {{
  langInp.value = lang;
  langLabel.textContent = lang === 'cpp' ? 'Code C++' : 'Code Python';
  localStorage.setItem(LANG_KEY, lang);
  const code = view.state.doc.toString();
  view.destroy();
  view = new EditorView({{
    state: EditorState.create({{ doc: code, extensions: createExtensions(lang) }}),
    parent: wrap,
  }});
  ta.value = code;
}};

window.clearCode = function() {{
  if (confirm('Xóa toàn bộ code?')) {{
    view.dispatch({{ changes: {{ from: 0, to: view.state.doc.length, insert: '' }} }});
    localStorage.removeItem(KEY);
    ta.value = '';
  }}
}};

document.getElementById('submitForm').addEventListener('submit', function() {{
  ta.value = view.state.doc.toString();
  const b = document.getElementById('subBtn');
  b.innerHTML = '<span class="spin me-2"></span>Đang chấm bài...';
  b.disabled = true;
}});
</script>"""
    return page(content, "student")


@router.post("/student/submit/{pid}", response_class=HTMLResponse)
async def student_submit(pid: str, code: str = Form(...), student_name: str = Form(""), language: str = Form("python")):
    p = get_problem(pid)
    if not p:
        raise HTTPException(404, "Khong tim thay bai")

    result = judge(code, p.get("testcases", []), language)
    score = result["score"]
    lang_label = "C++" if language == "cpp" else "Python"

    add_submission({
        "problem_id": pid,
        "problem_title": p.get("title", ""),
        "student_name": student_name.strip() or "Ẩn danh",
        "code": code,
        "language": language,
        "score": score,
        "details": result.get("details", []),
        "passed": result.get("passed", 0),
        "total": result.get("total", 0),
    })

    if score == 100:
        sr, msg = "s100", "🎉 Xuất sắc! Bài làm hoàn hảo!"
    elif score >= 60:
        sr, msg = "shi", "👍 Khá tốt! Cố gắng hơn nữa nhé."
    elif score >= 30:
        sr, msg = "smi", "💪 Cần cải thiện thêm."
    else:
        sr, msg = "slo", "❌ Chưa đúng. Xem lại đề và thử lại!"

    tc_rows = ""
    for tc in result.get("details", []):
        st = tc["status"]
        rc = st.lower()
        st_txt = {"AC": "Accepted ✓", "WA": "Wrong Answer", "TLE": "Time Limit", "RE": "Runtime Error", "ERROR": "Error"}.get(st, st)
        def sh(x, n=70):
            return (x[:n] + "…") if len(x) > n else x
        act = tc.get("actual", "")
        if st == "TLE":
            act = "⏱ Quá 2 giây"
        elif st == "RE":
            act = "💥 " + tc.get("stderr", "RE")[:70]
        tc_rows += f"""<tr class="tcr {rc}">
          <td style="width:55px;font-weight:600;color:var(--text2)">TC#{tc['testcase_id']}</td>
          <td><span class="sb b{rc}">{st_txt}</span></td>
          <td style="color:var(--text2);font-family:'JetBrains Mono',monospace;font-size:.78rem">{sh(tc.get('input',''))}</td>
          <td style="color:var(--green);font-family:'JetBrains Mono',monospace;font-size:.78rem">{sh(tc.get('expected',''))}</td>
          <td style="color:{'#34d399' if tc['passed'] else '#f87171'};font-family:'JetBrains Mono',monospace;font-size:.78rem">{sh(act)}</td>
        </tr>"""

    content = f"""
<div class="container" style="max-width:960px;padding:24px 12px 60px">
  <div class="mb-3">
    <a href="/student/solve/{pid}" style="color:var(--muted);text-decoration:none;font-size:.85rem">
      <i class="bi bi-arrow-left me-1"></i>Quay lại làm bài
    </a>
  </div>
  <div class="card-c p-4 mb-4 fi">
    <div class="d-flex align-items-center gap-4 flex-wrap">
      <div class="sr {sr}">{score}</div>
      <div class="flex-grow-1">
        <h4 style="font-weight:700;margin:0 0 4px;color:var(--text)">{msg}</h4>
        <p style="color:var(--text2);margin:0 0 10px;font-size:.875rem">
          {p.get('title','')} &nbsp;·&nbsp; <strong style="color:var(--text)">{student_name or 'Ẩn danh'}</strong>
          &nbsp;·&nbsp; <span style="color:var(--cyan);font-size:.82rem">{lang_label}</span>
        </p>
        <div class="prog"><div class="prog-b" style="width:{score}%"></div></div>
        <div style="font-size:.78rem;color:var(--muted);margin-top:5px">{result.get('passed',0)}/{result.get('total',0)} testcase passed</div>
      </div>
    </div>
  </div>
  <div class="card-c fi">
    <div class="card-head"><h6 style="margin:0;font-weight:600;color:var(--text)">
      <i class="bi bi-table me-2" style="color:var(--cyan)"></i>Chi Tiết Testcase
    </h6></div>
    <div class="p-4" style="overflow-x:auto">
      <table class="tct">
        <thead><tr>
          <th style="color:var(--muted);font-size:.78rem;font-weight:500;padding:0 0 8px">TC</th>
          <th style="color:var(--muted);font-size:.78rem;font-weight:500;padding:0 0 8px">Kết quả</th>
          <th style="color:var(--muted);font-size:.78rem;font-weight:500;padding:0 0 8px">Input</th>
          <th style="color:var(--muted);font-size:.78rem;font-weight:500;padding:0 0 8px">Expected</th>
          <th style="color:var(--muted);font-size:.78rem;font-weight:500;padding:0 0 8px">Actual</th>
        </tr></thead>
        <tbody>{tc_rows}</tbody>
      </table>
    </div>
  </div>
  <div class="mt-4 d-flex gap-3 flex-wrap">
    <a href="/student/solve/{pid}" class="btn-g btn py-2 px-4"><i class="bi bi-arrow-repeat me-2"></i>Làm Lại</a>
    <a href="/student" class="btn-o btn py-2 px-4"><i class="bi bi-collection me-2"></i>Chọn Bài Khác</a>
    <a href="/parent" class="btn-o btn py-2 px-4"><i class="bi bi-clock-history me-2"></i>Xem Nhật Ký</a>
  </div>
</div>"""
    return page(content, "student")
