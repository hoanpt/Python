"""Routes: Phụ huynh /parent"""

from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from database import get_all_submissions, get_submissions_filtered, get_student_names, get_submission_stats
from templates import page

router = APIRouter()


@router.get("/parent", response_class=HTMLResponse)
async def parent_log(student_name: str = ""):
    filtered = get_submissions_filtered(student_name)
    stats = get_submission_stats(student_name)

    total = stats["total"]
    avg = stats["avg"]
    perf = stats["perfect"]

    names = get_student_names()
    nbtns = '<a href="/parent" class="btn-o btn btn-sm me-1 mb-1">Tất cả</a>'
    for nm in names:
        act = "background:rgba(124,58,237,.2);border-color:var(--purple);color:var(--purple-l);" if nm == student_name else ""
        nbtns += f'<a href="/parent?student_name={nm}" class="btn-o btn btn-sm me-1 mb-1" style="{act}">{nm}</a>'

    log_html = ""
    if not filtered:
        log_html = '<div class="text-center py-5"><div style="font-size:3rem">📭</div><p style="color:var(--muted);margin-top:12px">Chưa có lần nộp bài nào.</p></div>'
    else:
        for s in filtered:
            sc = s.get("score", 0)
            sc_c = "#10b981" if sc == 100 else "#06b6d4" if sc >= 60 else "#f59e0b" if sc >= 30 else "#ef4444"
            try:
                ts = datetime.fromisoformat(s.get("submitted_at", "")).strftime("%d/%m/%Y %H:%M")
            except Exception:
                ts = s.get("submitted_at", "")
            tc_b = "".join(
                f'<span class="sb b{tc["status"].lower()}" style="font-size:.62rem;padding:2px 6px">TC{tc["testcase_id"]} {tc["status"]}</span> '
                for tc in s.get("details", [])
            )
            code_esc = s.get("code", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            eid = s.get("id", "x")
            log_html += f"""
            <div class="log-e fi">
              <div class="log-h" onclick="toggleCode('{eid}')">
                <div class="d-flex align-items-center gap-3">
                  <div style="width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;
                    border:2px solid {sc_c};color:{sc_c};font-weight:800;font-size:1.05rem;flex-shrink:0">{sc}</div>
                  <div>
                    <div style="font-weight:600;font-size:.9rem;color:var(--text)">{s.get('problem_title','?')}</div>
                    <div style="font-size:.78rem;color:var(--text2)">
                      <i class="bi bi-person me-1"></i>{s.get('student_name','?')}
                      &nbsp;·&nbsp;<i class="bi bi-clock me-1"></i>{ts}
                      &nbsp;·&nbsp;{s.get('passed',0)}/{s.get('total',0)} TC
                    </div>
                    <div style="margin-top:4px">{tc_b}</div>
                  </div>
                </div>
                <div style="color:var(--muted);font-size:.78rem;flex-shrink:0">
                  <i class="bi bi-code-slash me-1"></i>Code <i class="bi bi-chevron-down"></i>
                </div>
              </div>
              <div class="log-code" id="code-{eid}">{code_esc}</div>
            </div>"""

    content = f"""
<div class="container" style="max-width:900px;padding:28px 12px 60px">
  <div class="d-flex align-items-center justify-content-between mb-4">
    <div>
      <h2 style="font-weight:700;color:var(--text)">
        <i class="bi bi-eye-fill me-2" style="color:var(--yellow)"></i>Nhật Ký Phụ Huynh
      </h2>
      <p style="color:var(--text2);font-size:.875rem;margin:0">Theo dõi quá trình học tập hàng ngày của con</p>
    </div>
  </div>
  <div class="row g-3 mb-4">
    <div class="col-4"><div class="card-c p-3 text-center">
      <div style="font-size:1.8rem;font-weight:800;color:var(--purple-l)">{total}</div>
      <div style="font-size:.78rem;color:var(--muted)">Lần nộp bài</div>
    </div></div>
    <div class="col-4"><div class="card-c p-3 text-center">
      <div style="font-size:1.8rem;font-weight:800;color:var(--cyan)">{avg}</div>
      <div style="font-size:.78rem;color:var(--muted)">Điểm trung bình</div>
    </div></div>
    <div class="col-4"><div class="card-c p-3 text-center">
      <div style="font-size:1.8rem;font-weight:800;color:var(--green)">{perf}</div>
      <div style="font-size:.78rem;color:var(--muted)">Bài 100 điểm</div>
    </div></div>
  </div>
  {"<div class='mb-4'><label class='fl mb-2'>Lọc học sinh:</label><div>"+nbtns+"</div></div>" if names else ""}
  {log_html}
</div>"""
    return page(content, "parent")
