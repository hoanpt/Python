"""Routes: Admin /admin/*"""

import json
from typing import List

from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse

from database import (
    get_all_problems, get_problem, add_problem, update_problem, delete_problem,
    get_api_key, set_api_key, save_preview, load_preview, clear_preview,
)
from ai_engine import (
    ai_import_from_text, ai_import_from_images, ai_generate_problem, build_problem_record,
)
from templates import page, diff_badge, source_badge

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(msg: str = "", msg_type: str = "", tab: str = "import"):
    probs = get_all_problems()
    ak = get_api_key()
    masked = (ak[:8] + "..." + ak[-4:]) if len(ak) > 12 else (ak or "Chưa cấu hình")

    alert_html = ""
    if msg:
        cls = "a-ok" if msg_type == "success" else "a-err"
        ico = "bi-check-circle-fill" if msg_type == "success" else "bi-exclamation-triangle-fill"
        alert_html = f'<div class="{cls} mb-4 fi"><i class="bi {ico} me-2"></i>{msg}</div>'

    plist = ""
    for i, p in enumerate(probs):
        tc = len(p.get("testcases", []))
        plist += f"""
        <div class="d-flex align-items-center gap-3 p-3" style="border-bottom:1px solid var(--border)">
          <div style="width:28px;height:28px;border-radius:7px;background:rgba(124,58,237,.2);
            display:flex;align-items:center;justify-content:center;font-weight:700;
            color:var(--purple-l);font-size:.75rem;flex-shrink:0">#{i+1}</div>
          <div class="flex-grow-1" style="min-width:0">
            <div style="font-weight:600;font-size:.85rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
              {source_badge(p.get('source',''))} {p.get('title','?')}
            </div>
            <div style="font-size:.72rem;color:var(--muted)">{diff_badge(p.get('difficulty','?'))} {tc}TC &middot; ID:{p['id']}</div>
          </div>
          <div class="d-flex gap-1">
            <a href="/admin/edit/{p['id']}" class="btn-o btn btn-sm" style="padding:3px 9px;font-size:.75rem"
              title="Sửa bài"><i class="bi bi-pencil"></i></a>
            <form method="POST" action="/admin/delete/{p['id']}" style="margin:0">
              <button type="submit" class="btn-r btn btn-sm" style="padding:3px 9px;font-size:.75rem"
                onclick="return confirm('Xóa bài này?')"><i class="bi bi-trash"></i></button>
            </form>
          </div>
        </div>"""
    if not plist:
        plist = '<div class="p-4 text-center" style="color:var(--muted);font-size:.85rem"><i class="bi bi-inbox me-2"></i>Chưa có bài tập nào.</div>'

    t_imp = "active" if tab == "import" else ""
    t_ai = "active" if tab == "ai" else ""
    t_man = "active" if tab == "manual" else ""

    content = f"""
<div class="container" style="max-width:1140px;padding:28px 12px 60px">
  {alert_html}
  <h2 style="font-weight:700;color:var(--text);margin-bottom:24px">
    <i class="bi bi-shield-fill-check me-2" style="color:var(--purple-l)"></i>Bảng Điều Khiển Admin
  </h2>

  <!-- API KEY -->
  <div class="card-c mb-4">
    <div class="card-head">
      <span style="font-weight:600;color:var(--text);font-size:.9rem">
        <i class="bi bi-key-fill me-2" style="color:var(--yellow)"></i>Cấu Hình Gemini API Key
      </span>
    </div>
    <div class="p-4">
      <p style="color:var(--text2);font-size:.82rem;margin-bottom:10px">
        Key hiện tại: <code style="color:var(--cyan)">{masked}</code>
        &nbsp;·&nbsp; Hoặc đặt biến môi trường <code>GEMINI_API_KEY</code>
      </p>
      <form method="POST" action="/admin/set-api-key" class="d-flex gap-2">
        <input type="password" name="api_key" class="form-control fc flex-grow-1"
          placeholder="Nhập Gemini API Key mới..."
          style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
        <button type="submit" class="btn-g btn" style="white-space:nowrap;padding:8px 20px">
          <i class="bi bi-floppy me-1"></i>Lưu
        </button>
      </form>
      <a href="https://aistudio.google.com/apikey" target="_blank"
        style="color:var(--purple-l);font-size:.78rem;text-decoration:none;display:inline-block;margin-top:8px">
        <i class="bi bi-box-arrow-up-right me-1"></i>Lấy API Key miễn phí tại Google AI Studio
      </a>
    </div>
  </div>

  <div class="row g-4">
    <!-- CỘT TRÁI: Tabs -->
    <div class="col-lg-7">
      <div class="card-c">
        <div class="card-head">
          <div class="tab-bar" style="margin-bottom:0;border-bottom:none">
            <button class="tab-btn {t_imp}" data-tab="import" onclick="switchTab('import')">
              <i class="bi bi-upload me-1"></i>Import Đề Thi
            </button>
            <button class="tab-btn {t_ai}" data-tab="ai" onclick="switchTab('ai')">
              <i class="bi bi-stars me-1"></i>AI Ra Đề Mới
            </button>
            <button class="tab-btn {t_man}" data-tab="manual" onclick="switchTab('manual')">
              <i class="bi bi-plus me-1"></i>Thêm Thủ Công
            </button>
          </div>
        </div>
        <div class="p-4">

          <!-- TAB: IMPORT ĐỀ THI -->
          <div class="tab-panel {t_imp}" id="tab-import">
            <div class="import-sec">
              <div class="ai-badge ab-import"><i class="bi bi-upload"></i>Gemini Vision · Đọc Ảnh Đề Thi</div>
              <h5 style="font-weight:700;color:var(--text);margin-bottom:6px">Import Đề Thi → Tách Từng Bài</h5>
              <p style="color:var(--text2);font-size:.82rem;margin-bottom:20px">
                Upload ảnh chụp đề thi (nhiều trang) hoặc file text. AI sẽ đọc và tự động
                tách <strong style="color:var(--text)">từng bài toán</strong> thành bài tập riêng lẻ
                với testcase đầy đủ.
              </p>
              <form method="POST" action="/admin/import-exam" enctype="multipart/form-data" id="importForm">
                <div class="mb-3">
                  <label class="fl"><i class="bi bi-images me-1"></i>Upload ảnh đề thi (JPG/PNG, nhiều trang)</label>
                  <div class="dropzone" id="dropzone" onclick="document.getElementById('imgInput').click()">
                    <input type="file" name="images" id="imgInput" multiple accept="image/*,.txt,.md"
                      style="display:none" onchange="updateFileList(this)">
                    <div id="dropzoneContent">
                      <i class="bi bi-cloud-upload" style="font-size:2rem;color:var(--cyan);display:block;margin-bottom:8px"></i>
                      <div style="color:var(--text);font-weight:500;font-size:.9rem">Nhấn để chọn ảnh hoặc kéo thả vào đây</div>
                      <div style="color:var(--muted);font-size:.8rem;margin-top:4px">Hỗ trợ: JPG, PNG (nhiều trang), TXT, MD</div>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="fl">Hoặc paste nội dung đề thi dạng text</label>
                  <textarea name="text_content" id="importText" class="form-control fc" rows="5"
                    placeholder="Paste nội dung đề thi vào đây (nếu không upload ảnh)..."></textarea>
                </div>
                <div class="mb-3">
                  <label class="fl"><i class="bi bi-chat-dots me-1"></i>Yêu cầu bổ sung (tùy chọn)</label>
                  <input type="text" name="extra" class="form-control fc"
                    placeholder="VD: Chỉ lấy bài 1 và bài 3, tạo 7 testcase mỗi bài...">
                </div>
                <button type="submit" class="btn-g btn w-100 py-2" id="importBtn" style="font-size:.95rem">
                  <i class="bi bi-magic me-2"></i>AI Đọc & Tách Bài Tập
                </button>
              </form>
            </div>
          </div>

          <!-- TAB: AI RA ĐỀ MỚI -->
          <div class="tab-panel {t_ai}" id="tab-ai">
            <div class="ai-sec">
              <div class="ai-badge ab-ai"><i class="bi bi-stars"></i>Gemini 2.5 Flash · Sáng Tác</div>
              <h5 style="font-weight:700;color:var(--text);margin-bottom:6px">AI Tự Sáng Tác Bài Tập Mới</h5>
              <p style="color:var(--text2);font-size:.82rem;margin-bottom:20px">
                AI sẽ sáng tác 1 bài toán mới hoàn chỉnh với subtask, testcase chuẩn xác.
              </p>
              <form method="POST" action="/admin/ai-generate" id="aiForm">
                <div class="mb-3">
                  <label class="fl"><i class="bi bi-file-text me-1"></i>Đề tham khảo (tùy chọn)</label>
                  <textarea name="ref_text" class="form-control fc" rows="6"
                    placeholder="Paste đề thi tham khảo để AI học hỏi phong cách, hoặc bỏ trống..."></textarea>
                </div>
                <div class="mb-3">
                  <label class="fl"><i class="bi bi-chat-dots me-1"></i>Yêu cầu cho AI</label>
                  <input type="text" name="extra" class="form-control fc"
                    placeholder="VD: Bài về mảng 2 chiều độ khó trung bình, có subtask...">
                </div>
                <div class="mb-3">
                  <label class="fl"><i class="bi bi-bar-chart me-1"></i>Độ khó</label>
                  <select name="difficulty" class="form-select fc"
                    style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px;border:1px solid var(--border)">
                    <option value="Dễ">Dễ</option>
                    <option value="Trung bình" selected>Trung bình</option>
                    <option value="Khó">Khó</option>
                    <option value="Rất khó">Rất khó</option>
                  </select>
                </div>
                <button type="submit" class="btn-g btn w-100 py-2" id="aiBtn" style="font-size:.95rem">
                  <i class="bi bi-lightning-fill me-2"></i>AI Sáng Tác Bài Tập
                </button>
              </form>
            </div>
          </div>

          <!-- TAB: THỦ CÔNG -->
          <div class="tab-panel {t_man}" id="tab-manual">
            <h6 style="font-weight:600;color:var(--text);margin-bottom:16px">
              <i class="bi bi-plus-circle me-2" style="color:var(--green)"></i>Thêm Bài Tập Thủ Công
            </h6>
            <form method="POST" action="/admin/add-problem">
              <div class="row g-3 mb-3">
                <div class="col-8">
                  <label class="fl">Tên bài toán</label>
                  <input type="text" name="title" class="form-control fc"
                    placeholder="VD: ROBOT" required
                    style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
                </div>
                <div class="col-4">
                  <label class="fl">Điểm</label>
                  <input type="number" name="score_points" class="form-control fc" value="2" step="0.5" min="0" max="10"
                    style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
                </div>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label class="fl">File Input (VD: ROBOT.INP)</label>
                  <input type="text" name="input_filename" class="form-control fc" placeholder="BAITAP.INP"
                    style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
                </div>
                <div class="col-6">
                  <label class="fl">File Output (VD: ROBOT.OUT)</label>
                  <input type="text" name="output_filename" class="form-control fc" placeholder="BAITAP.OUT"
                    style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
                </div>
              </div>
              <div class="mb-3">
                <label class="fl">Nguồn (kỳ thi)</label>
                <input type="text" name="source_exam" class="form-control fc"
                  placeholder="VD: KỲ THI HSG TP ĐÀ NẴNG 2025-2026"
                  style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
              </div>
              <div class="mb-3">
                <label class="fl">Mô tả đề bài</label>
                <textarea name="description" class="form-control fc" rows="4"
                  placeholder="Mô tả bối cảnh bài toán và yêu cầu..." required></textarea>
              </div>
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label class="fl">Định dạng dữ liệu vào</label>
                  <textarea name="input_format" class="form-control fc" rows="3" placeholder="Dòng 1: N..."></textarea>
                </div>
                <div class="col-6">
                  <label class="fl">Định dạng dữ liệu ra</label>
                  <textarea name="output_format" class="form-control fc" rows="3" placeholder="Ghi ra số nguyên..."></textarea>
                </div>
              </div>
              <div class="mb-3">
                <label class="fl">Ràng buộc / Subtask</label>
                <textarea name="constraints" class="form-control fc" rows="3"
                  placeholder="Subtask 1 (40%): N <= 100&#10;Subtask 2 (60%): N <= 10^5"></textarea>
              </div>
              <div class="mb-3">
                <label class="fl">Testcases (JSON Array)</label>
                <textarea name="testcases_json" class="form-control fc" rows="5"
                  placeholder='[{{"input":"10&#10;UULLDRDRR","output":"0 -1"}},{{"input":"5&#10;UUUUU","output":"0 5"}}]'
                  required></textarea>
              </div>
              <div class="mb-3">
                <label class="fl">Độ khó</label>
                <select name="difficulty" class="form-select fc"
                  style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px;border:1px solid var(--border)">
                  <option>Dễ</option><option selected>Trung bình</option><option>Khó</option><option>Rất khó</option>
                </select>
              </div>
              <button type="submit" class="btn-o btn w-100 py-2">
                <i class="bi bi-plus-lg me-2"></i>Thêm Bài Tập
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- CỘT PHẢI: Danh sách bài -->
    <div class="col-lg-5">
      <div class="card-c" style="position:sticky;top:70px">
        <div class="card-head d-flex align-items-center justify-content-between">
          <span style="font-weight:600;color:var(--text);font-size:.9rem">
            <i class="bi bi-collection me-2" style="color:var(--cyan)"></i>Bài Tập ({len(probs)})
          </span>
          <a href="/student" class="btn-o btn btn-sm py-1"><i class="bi bi-eye me-1"></i>Xem</a>
        </div>
        <div style="max-height:620px;overflow-y:auto">{plist}</div>
      </div>
    </div>
  </div>
</div>

<script>
// Tab mặc định
document.addEventListener('DOMContentLoaded',()=>{{
  const activeTab = '{tab}';
  switchTab(activeTab);
}});

// Drag & drop
const dz=document.getElementById('dropzone');
if(dz){{
  dz.addEventListener('dragover',e=>{{e.preventDefault();dz.classList.add('drag-over');}});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag-over'));
  dz.addEventListener('drop',e=>{{
    e.preventDefault();dz.classList.remove('drag-over');
    const inp=document.getElementById('imgInput');
    const dt=new DataTransfer();
    [...e.dataTransfer.files].forEach(f=>dt.items.add(f));
    inp.files=dt.files;updateFileList(inp);
  }});
}}

function updateFileList(inp){{
  const files=[...inp.files];
  const el=document.getElementById('dropzoneContent');
  if(files.length>0){{
    el.innerHTML='<i class="bi bi-check-circle" style="font-size:1.8rem;color:var(--green);display:block;margin-bottom:6px"></i>'
      +'<div style="color:var(--text);font-weight:600">'+files.length+' file đã chọn</div>'
      +'<div style="color:var(--muted);font-size:.78rem;margin-top:4px">'+files.map(f=>f.name).join(', ')+'</div>';
  }}
}}

// Loading states
document.getElementById('importForm')?.addEventListener('submit',function(){{
  const b=document.getElementById('importBtn');
  b.innerHTML='<span class="spin me-2"></span>AI đang đọc đề thi... (20-40 giây)';b.disabled=true;
}});
document.getElementById('aiForm')?.addEventListener('submit',function(){{
  const b=document.getElementById('aiBtn');
  b.innerHTML='<span class="spin me-2"></span>AI đang sáng tác... (15-30 giây)';b.disabled=true;
}});
</script>"""
    return page(content, "admin")


@router.post("/admin/set-api-key")
async def admin_set_key(api_key: str = Form(...)):
    try:
        set_api_key(api_key.strip())
        return RedirectResponse("/admin?msg=Đã+lưu+API+Key&msg_type=success&tab=import", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin?msg=Lỗi:{str(e)[:50]}&msg_type=error&tab=import", status_code=303)


@router.post("/admin/import-exam")
async def admin_import(
    images: List[UploadFile] = File(default=[]),
    text_content: str = Form(""),
    extra: str = Form(""),
):
    """Import đề thi từ ảnh hoặc text → AI tách từng bài → PREVIEW trước khi lưu."""
    api_key = get_api_key()
    if not api_key:
        return RedirectResponse(
            "/admin?msg=Chưa+có+API+Key!+Nhập+Gemini+API+Key+trước.&msg_type=error&tab=import",
            status_code=303
        )

    try:
        from google import genai  # kiểm tra thư viện
    except ImportError:
        return RedirectResponse(
            "/admin?msg=Thiếu+thư+viện+google-genai.+Chạy:+pip+install+google-genai&msg_type=error&tab=import",
            status_code=303
        )

    try:
        extracted_problems = []

        valid_images = [img for img in images if img and img.filename]
        if valid_images:
            imgs_data = []
            for img in valid_images:
                data = await img.read()
                if data:
                    mime = img.content_type or "image/jpeg"
                    if mime in ("text/plain", "text/markdown") or img.filename.endswith((".txt", ".md")):
                        text_content += "\n" + data.decode("utf-8", errors="replace")
                    else:
                        imgs_data.append((data, mime))

            if imgs_data:
                extracted_problems = ai_import_from_images(api_key, imgs_data, extra)

        if not extracted_problems and text_content.strip():
            extracted_problems = ai_import_from_text(api_key, text_content.strip(), extra)

        if not extracted_problems:
            return RedirectResponse(
                "/admin?msg=Không+có+dữ+liệu+để+import.+Upload+ảnh+hoặc+paste+text.&msg_type=error&tab=import",
                status_code=303
            )

        save_preview(extracted_problems)
        n = len(extracted_problems)
        return RedirectResponse(f"/admin/preview-import?n={n}", status_code=303)

    except json.JSONDecodeError as e:
        msg = str(e)[:80].replace(" ", "+")
        return RedirectResponse(f"/admin?msg=AI+trả+về+JSON+sai+(thử+lại):+{msg}&msg_type=error&tab=import", status_code=303)
    except ValueError as e:
        msg = str(e)[:80].replace(" ", "+")
        return RedirectResponse(f"/admin?msg=Dữ+liệu+thiếu+trường:+{msg}&msg_type=error&tab=import", status_code=303)
    except Exception as e:
        msg = str(e)[:100].replace(" ", "+").replace("&", "va")
        return RedirectResponse(f"/admin?msg=Lỗi:+{msg}&msg_type=error&tab=import", status_code=303)


@router.get("/admin/preview-import", response_class=HTMLResponse)
async def admin_preview_import():
    """Trang preview bài tập đã import — cho admin xem trước khi lưu."""
    preview_data = load_preview()
    if not preview_data:
        return RedirectResponse("/admin?msg=Không+có+dữ+liệu+preview.&msg_type=error&tab=import", status_code=303)

    cards_html = ""
    for i, d in enumerate(preview_data):
        title = d.get("title", "?")
        desc = d.get("description", "")[:200]
        diff = d.get("difficulty", "Trung bình")
        tc_count = len(d.get("testcases", []))
        score = d.get("score_points", 0)
        inp_f = d.get("input_filename", "")
        out_f = d.get("output_filename", "")
        const = d.get("constraints", "")[:120]
        examples = d.get("examples", [])

        ex_html = ""
        for ex in examples[:2]:
            ex_html += f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">
              <div style="background:rgba(13,15,26,.5);border:1px solid var(--border);border-radius:8px;padding:8px;font-family:'JetBrains Mono',monospace;font-size:.78rem;white-space:pre;color:var(--cyan)">{ex.get('input','')[:100]}</div>
              <div style="background:rgba(13,15,26,.5);border:1px solid var(--border);border-radius:8px;padding:8px;font-family:'JetBrains Mono',monospace;font-size:.78rem;white-space:pre;color:var(--green)">{ex.get('output','')[:100]}</div>
            </div>"""

        tc_preview = ""
        for j, tc in enumerate(d.get("testcases", [])[:3]):
            tc_preview += f"""<div style="font-size:.72rem;color:var(--muted);margin-top:4px">
              TC#{j+1}: <code style="color:var(--cyan)">{tc.get('input','')[:40]}</code> → <code style="color:var(--green)">{tc.get('output','')[:40]}</code>
            </div>"""
        if tc_count > 3:
            tc_preview += f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">... +{tc_count-3} testcase khác</div>'

        cards_html += f"""
        <div class="card-c mb-4 fi">
          <div class="card-head d-flex align-items-center justify-content-between">
            <div class="d-flex align-items-center gap-3">
              <div style="width:36px;height:36px;border-radius:10px;background:rgba(6,182,212,.2);
                display:flex;align-items:center;justify-content:center;font-weight:800;
                color:var(--cyan);font-size:.9rem;flex-shrink:0">#{i+1}</div>
              <div>
                <div style="font-weight:700;color:var(--text);font-size:1rem">{title}</div>
                <div style="font-size:.78rem;color:var(--muted)">
                  {diff_badge(diff)}
                  {"<span style='margin-left:6px;color:var(--yellow);font-size:.72rem'>"+str(score)+"đ</span>" if score else ""}
                  {"&nbsp;·&nbsp;<code style='font-size:.72rem'>"+inp_f+" → "+out_f+"</code>" if inp_f else ""}
                  &nbsp;·&nbsp;{tc_count} testcase
                </div>
              </div>
            </div>
          </div>
          <div class="p-4">
            <div class="exam-section">
              <div class="exam-label"><i class="bi bi-text-paragraph"></i>MÔ TẢ</div>
              <div class="exam-content" style="font-size:.85rem;max-height:120px;overflow-y:auto">{desc}{"..." if len(d.get("description","")) > 200 else ""}</div>
            </div>
            {"<div class='exam-section'><div class='exam-label'><i class='bi bi-shield-check'></i>RÀNG BUỘC</div><div class='constraint-box' style='font-size:.82rem'>"+const+"</div></div>" if const else ""}
            {"<div class='exam-section'><div class='exam-label'><i class='bi bi-table'></i>VÍ DỤ</div>"+ex_html+"</div>" if ex_html else ""}
            <div class="exam-section">
              <div class="exam-label"><i class="bi bi-list-check"></i>TESTCASE PREVIEW</div>
              {tc_preview}
            </div>
          </div>
        </div>"""

    content = f"""
<div class="container" style="max-width:960px;padding:28px 12px 60px">
  <div class="mb-3">
    <a href="/admin" style="color:var(--muted);text-decoration:none;font-size:.85rem">
      <i class="bi bi-arrow-left me-1"></i>Quay lại Admin
    </a>
  </div>

  <div style="background:linear-gradient(135deg,rgba(6,182,212,.1),rgba(16,185,129,.08));
    border:1px solid rgba(6,182,212,.25);border-radius:16px;padding:20px 24px;margin-bottom:24px">
    <div class="d-flex align-items-center gap-3 flex-wrap">
      <div style="font-size:2rem">🔍</div>
      <div class="flex-grow-1">
        <h4 style="font-weight:700;color:var(--text);margin:0 0 4px">Preview Import — {len(preview_data)} Bài Tập</h4>
        <p style="color:var(--text2);font-size:.85rem;margin:0">
          Kiểm tra kết quả AI trước khi lưu. Nhấn <strong style="color:var(--green)">Xác Nhận</strong> để lưu hoặc
          <strong style="color:var(--red)">Hủy</strong> để thử lại.
        </p>
      </div>
      <div class="d-flex gap-2">
        <form method="POST" action="/admin/confirm-import" style="margin:0">
          <button type="submit" class="btn-g btn px-4 py-2" style="font-size:.95rem">
            <i class="bi bi-check-lg me-2"></i>Xác Nhận & Lưu
          </button>
        </form>
        <a href="/admin?msg=Đã+hủy+preview&msg_type=error&tab=import" class="btn-r btn px-3 py-2" style="font-size:.9rem;text-decoration:none;display:flex;align-items:center">
          <i class="bi bi-x-lg me-1"></i>Hủy
        </a>
      </div>
    </div>
  </div>

  {cards_html}

  <div class="d-flex gap-3 mt-4">
    <form method="POST" action="/admin/confirm-import" style="margin:0;flex:1">
      <button type="submit" class="btn-g btn w-100 py-2" style="font-size:.95rem">
        <i class="bi bi-check-lg me-2"></i>Xác Nhận Lưu {len(preview_data)} Bài
      </button>
    </form>
    <a href="/admin?tab=import" class="btn-o btn py-2 px-4" style="text-decoration:none;display:flex;align-items:center">
      <i class="bi bi-arrow-left me-1"></i>Quay lại
    </a>
  </div>
</div>"""
    return page(content, "admin")


@router.post("/admin/confirm-import")
async def admin_confirm_import():
    """Xác nhận lưu bài tập từ preview vào database."""
    preview_data = load_preview()
    if not preview_data:
        return RedirectResponse("/admin?msg=Không+có+dữ+liệu+để+lưu.&msg_type=error&tab=import", status_code=303)

    for d in preview_data:
        add_problem(build_problem_record(d, "Imported"))
    clear_preview()

    n = len(preview_data)
    titles = ", ".join(d.get("title", "?") for d in preview_data[:3])
    if n > 3:
        titles += f"... (+{n-3} bài)"
    return RedirectResponse(
        f"/admin?msg=Import+thành+công+{n}+bài:+{titles.replace(' ','+')}&msg_type=success&tab=import",
        status_code=303
    )


@router.post("/admin/ai-generate")
async def admin_ai_gen(
    ref_text: str = Form(""),
    extra: str = Form(""),
    difficulty: str = Form("Trung bình"),
):
    """AI sáng tác 1 bài toán mới."""
    api_key = get_api_key()
    if not api_key:
        return RedirectResponse("/admin?msg=Chưa+có+API+Key&msg_type=error&tab=ai", status_code=303)
    try:
        full_extra = f"Do kho: {difficulty}. {extra}"
        d = ai_generate_problem(api_key, ref_text, full_extra)
        d["difficulty"] = difficulty
        add_problem(build_problem_record(d, "AI Generated"))
        title = d.get("title", "?")[:40].replace(" ", "+")
        return RedirectResponse(f"/admin?msg=AI+tạo+xong:+{title}&msg_type=success&tab=ai", status_code=303)
    except json.JSONDecodeError:
        return RedirectResponse("/admin?msg=JSON+sai+(thử+lại)&msg_type=error&tab=ai", status_code=303)
    except ValueError as e:
        return RedirectResponse(f"/admin?msg={str(e)[:70].replace(' ','+')}&msg_type=error&tab=ai", status_code=303)
    except Exception as e:
        msg = str(e)[:80].replace(" ", "+").replace("&", "va")
        return RedirectResponse(f"/admin?msg=Lỗi+AI:+{msg}&msg_type=error&tab=ai", status_code=303)


@router.post("/admin/add-problem")
async def admin_add(
    title: str = Form(...),
    description: str = Form(...),
    testcases_json: str = Form(...),
    score_points: float = Form(2.0),
    input_filename: str = Form(""),
    output_filename: str = Form(""),
    input_format: str = Form(""),
    output_format: str = Form(""),
    constraints: str = Form(""),
    source_exam: str = Form(""),
    difficulty: str = Form("Trung bình"),
):
    try:
        tcs = json.loads(testcases_json)
        if not isinstance(tcs, list):
            raise ValueError("Phải là array JSON")
        add_problem({
            "title": title, "score_points": score_points, "difficulty": difficulty,
            "input_filename": input_filename, "output_filename": output_filename,
            "description": description, "input_format": input_format,
            "output_format": output_format, "constraints": constraints,
            "examples": [], "testcases": tcs,
            "source_exam": source_exam, "tags": [], "source": "Manual",
        })
        return RedirectResponse("/admin?msg=Thêm+bài+thành+công&msg_type=success&tab=manual", status_code=303)
    except json.JSONDecodeError:
        return RedirectResponse("/admin?msg=JSON+testcase+sai!&msg_type=error&tab=manual", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/admin?msg={str(e)[:60].replace(' ','+')}&msg_type=error&tab=manual", status_code=303)


@router.post("/admin/delete/{pid}")
async def admin_delete(pid: str):
    delete_problem(pid)
    return RedirectResponse("/admin?msg=Đã+xóa+bài&msg_type=success&tab=import", status_code=303)


@router.get("/admin/edit/{pid}", response_class=HTMLResponse)
async def admin_edit_page(pid: str):
    """Trang chỉnh sửa bài tập."""
    p = get_problem(pid)
    if not p:
        raise HTTPException(404, "Khong tim thay bai")

    tc_json = json.dumps(p.get("testcases", []), ensure_ascii=False, indent=2)
    ex_json = json.dumps(p.get("examples", []), ensure_ascii=False, indent=2)
    tc_json_esc = tc_json.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    ex_json_esc = ex_json.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    desc_esc = p.get("description", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    inp_fmt_esc = p.get("input_format", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out_fmt_esc = p.get("output_format", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    const_esc = p.get("constraints", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    diff_opts = ""
    for d in ["Dễ", "Trung bình", "Khó", "Rất khó"]:
        sel = "selected" if p.get("difficulty") == d else ""
        diff_opts += f'<option value="{d}" {sel}>{d}</option>'

    content = f"""
<div class="container" style="max-width:900px;padding:28px 12px 60px">
  <div class="mb-3">
    <a href="/admin" style="color:var(--muted);text-decoration:none;font-size:.85rem">
      <i class="bi bi-arrow-left me-1"></i>Quay lại Admin
    </a>
  </div>
  <div class="card-c">
    <div class="card-head">
      <h5 style="margin:0;font-weight:700;color:var(--text)">
        <i class="bi bi-pencil-square me-2" style="color:var(--yellow)"></i>Chỉnh Sửa Bài: {p.get('title','?')}
      </h5>
    </div>
    <div class="p-4">
      <form method="POST" action="/admin/edit/{pid}">
        <div class="row g-3 mb-3">
          <div class="col-7">
            <label class="fl">Tên bài toán</label>
            <input type="text" name="title" class="form-control fc" value="{p.get('title','')}" required
              style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
          </div>
          <div class="col-2">
            <label class="fl">Điểm</label>
            <input type="number" name="score_points" class="form-control fc" value="{p.get('score_points',2)}" step="0.5" min="0" max="10"
              style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
          </div>
          <div class="col-3">
            <label class="fl">Độ khó</label>
            <select name="difficulty" class="form-select fc"
              style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px;border:1px solid var(--border)">
              {diff_opts}
            </select>
          </div>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-4">
            <label class="fl">File Input</label>
            <input type="text" name="input_filename" class="form-control fc" value="{p.get('input_filename','')}"
              style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
          </div>
          <div class="col-4">
            <label class="fl">File Output</label>
            <input type="text" name="output_filename" class="form-control fc" value="{p.get('output_filename','')}"
              style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
          </div>
          <div class="col-4">
            <label class="fl">Nguồn (kỳ thi)</label>
            <input type="text" name="source_exam" class="form-control fc" value="{p.get('source_exam','')}"
              style="background:rgba(13,15,26,.8);color:var(--text);border-radius:10px">
          </div>
        </div>
        <div class="mb-3">
          <label class="fl">Mô tả đề bài</label>
          <textarea name="description" class="form-control fc" rows="5" required>{desc_esc}</textarea>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-6">
            <label class="fl">Định dạng dữ liệu vào</label>
            <textarea name="input_format" class="form-control fc" rows="3">{inp_fmt_esc}</textarea>
          </div>
          <div class="col-6">
            <label class="fl">Định dạng dữ liệu ra</label>
            <textarea name="output_format" class="form-control fc" rows="3">{out_fmt_esc}</textarea>
          </div>
        </div>
        <div class="mb-3">
          <label class="fl">Ràng buộc / Subtask</label>
          <textarea name="constraints" class="form-control fc" rows="3">{const_esc}</textarea>
        </div>
        <div class="mb-3">
          <label class="fl"><i class="bi bi-table me-1"></i>Ví dụ (JSON Array)</label>
          <textarea name="examples_json" class="form-control fc" rows="4"
            style="font-family:'JetBrains Mono',monospace;font-size:.82rem">{ex_json_esc}</textarea>
          <div style="font-size:.72rem;color:var(--muted);margin-top:4px">
            Format: [{{"input":"...","output":"...","explanation":"..."}}]
          </div>
        </div>
        <div class="mb-3">
          <label class="fl"><i class="bi bi-list-check me-1"></i>Testcases (JSON Array) — {len(p.get('testcases',[]))} testcase hiện tại</label>
          <textarea name="testcases_json" class="form-control fc" rows="8" required
            style="font-family:'JetBrains Mono',monospace;font-size:.82rem">{tc_json_esc}</textarea>
          <div style="font-size:.72rem;color:var(--muted);margin-top:4px">
            Format: [{{"input":"...","output":"..."}}]
          </div>
        </div>
        <div class="d-flex gap-3">
          <button type="submit" class="btn-g btn flex-grow-1 py-2" style="font-size:.95rem">
            <i class="bi bi-check-lg me-2"></i>Lưu Thay Đổi
          </button>
          <a href="/admin" class="btn-o btn py-2 px-4">Hủy</a>
        </div>
      </form>
    </div>
  </div>
</div>"""
    return page(content, "admin")


@router.post("/admin/edit/{pid}")
async def admin_edit_save(
    pid: str,
    title: str = Form(...),
    description: str = Form(...),
    testcases_json: str = Form(...),
    score_points: float = Form(2.0),
    input_filename: str = Form(""),
    output_filename: str = Form(""),
    input_format: str = Form(""),
    output_format: str = Form(""),
    constraints: str = Form(""),
    source_exam: str = Form(""),
    difficulty: str = Form("Trung bình"),
    examples_json: str = Form("[]"),
):
    """Lưu chỉnh sửa bài tập."""
    try:
        tcs = json.loads(testcases_json)
        if not isinstance(tcs, list):
            raise ValueError("testcases phải là JSON array")
        try:
            examples = json.loads(examples_json) if examples_json.strip() else []
        except json.JSONDecodeError:
            examples = []

        update_problem(pid, {
            "title": title, "description": description,
            "testcases": tcs, "score_points": score_points,
            "input_filename": input_filename, "output_filename": output_filename,
            "input_format": input_format, "output_format": output_format,
            "constraints": constraints, "source_exam": source_exam,
            "difficulty": difficulty, "examples": examples,
        })
        t = title[:30].replace(' ', '+')
        return RedirectResponse(f"/admin?msg=Đã+cập+nhật+bài+{t}&msg_type=success", status_code=303)
    except json.JSONDecodeError:
        return RedirectResponse(f"/admin/edit/{pid}?msg=JSON+testcase+sai!&msg_type=error", status_code=303)
    except Exception as e:
        msg = str(e)[:60].replace(' ', '+')
        return RedirectResponse(f"/admin/edit/{pid}?msg=Lỗi:+{msg}&msg_type=error", status_code=303)
