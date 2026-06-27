"""Routes: Trang chủ /"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from database import get_stats
from templates import page

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home():
    stats = get_stats()
    content = f"""
<div class="container" style="padding:60px 12px 40px">
  <div class="text-center mb-5">
    <div class="ai-badge ab-import mb-3"><i class="bi bi-stars"></i> Google Gemini AI · Vision</div>
    <h1 style="font-size:2.6rem;font-weight:800;background:var(--grad);-webkit-background-clip:text;
      -webkit-text-fill-color:transparent;background-clip:text;line-height:1.2;margin-bottom:14px">
      Mini Online Judge<br>Chuyên Tin Lớp 9
    </h1>
    <p style="color:var(--text2);font-size:1rem;max-width:560px;margin:0 auto">
      Import đề thi từ ảnh chụp → AI tách từng bài → Bé làm từng ngày → Phụ huynh theo dõi.
    </p>
    <div class="d-flex gap-3 justify-content-center mt-4 flex-wrap">
      <a href="/student" class="btn-g btn px-5 py-2"><i class="bi bi-play-fill me-2"></i>Vào Làm Bài</a>
      <a href="/admin" class="btn-o btn px-4 py-2"><i class="bi bi-upload me-2"></i>Import Đề Thi</a>
    </div>
  </div>
  <div class="row g-3 mb-5" style="max-width:700px;margin:0 auto">
    <div class="col-4"><div class="card-c p-4 text-center">
      <div style="font-size:2.2rem;font-weight:800;color:var(--purple-l)">{stats['problems']}</div>
      <div style="color:var(--text2);font-size:.82rem;margin-top:4px"><i class="bi bi-file-text me-1"></i>Bài Tập</div>
    </div></div>
    <div class="col-4"><div class="card-c p-4 text-center">
      <div style="font-size:2.2rem;font-weight:800;color:var(--cyan)">{stats['submissions']}</div>
      <div style="color:var(--text2);font-size:.82rem;margin-top:4px"><i class="bi bi-send me-1"></i>Lần Nộp</div>
    </div></div>
    <div class="col-4"><div class="card-c p-4 text-center">
      <div style="font-size:2.2rem;font-weight:800;color:var(--green)">{stats['perfect']}</div>
      <div style="color:var(--text2);font-size:.82rem;margin-top:4px"><i class="bi bi-trophy me-1"></i>Bài 100đ</div>
    </div></div>
  </div>
  <div class="row g-4" style="max-width:900px;margin:0 auto">
    <div class="col-md-3"><div class="card-c p-4 h-100">
      <div style="font-size:1.6rem;margin-bottom:10px">📸</div>
      <h6 style="font-weight:600;margin-bottom:6px">Import Đề Thi</h6>
      <p style="color:var(--text2);font-size:.82rem;margin:0">Upload ảnh chụp đề → AI đọc và tách từng bài tự động.</p>
    </div></div>
    <div class="col-md-3"><div class="card-c p-4 h-100">
      <div style="font-size:1.6rem;margin-bottom:10px">✨</div>
      <h6 style="font-weight:600;margin-bottom:6px">AI Ra Đề Mới</h6>
      <p style="color:var(--text2);font-size:.82rem;margin:0">AI tự sáng tác bài dựa trên yêu cầu và đề tham khảo.</p>
    </div></div>
    <div class="col-md-3"><div class="card-c p-4 h-100">
      <div style="font-size:1.6rem;margin-bottom:10px">⚡</div>
      <h6 style="font-weight:600;margin-bottom:6px">Chấm Tự Động</h6>
      <p style="color:var(--text2);font-size:.82rem;margin:0">Chạy code trong sandbox, so sánh đáp án, tính điểm 0-100.</p>
    </div></div>
    <div class="col-md-3"><div class="card-c p-4 h-100">
      <div style="font-size:1.6rem;margin-bottom:10px">👁️</div>
      <h6 style="font-weight:600;margin-bottom:6px">Nhật Ký Bố/Mẹ</h6>
      <p style="color:var(--text2);font-size:.82rem;margin:0">Xem điểm, thời gian và code bé đã viết mỗi ngày.</p>
    </div></div>
  </div>
</div>"""
    return page(content, "home")
