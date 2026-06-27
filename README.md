# Mini Online Judge v3.0 — Chuyên Tin Lớp 9

Hệ thống ôn thi Chuyên Tin lớp 9 với AI hỗ trợ import đề thi và chấm bài tự động.

## Tính năng

- 📸 **Import đề thi từ ảnh** — Gemini Vision đọc ảnh chụp đề → tách từng bài tự động
- ✨ **AI ra đề mới** — Gemini sáng tác bài toán với testcase chuẩn xác
- ⚡ **Chấm bài tự động** — Hỗ trợ Python & C++, so sánh output, tính điểm 0-100
- 👁️ **Nhật ký phụ huynh** — Theo dõi quá trình học tập hàng ngày
- 🔍 **Preview trước khi lưu** — Xem lại kết quả AI trước khi đưa vào bài tập

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite (WAL mode)
- **AI**: Google Gemini 2.5 Flash + Vision
- **Frontend**: Bootstrap 5 + CodeMirror 6
- **Deploy**: Docker + Coolify

## Chạy local

```bash
# Cài dependencies
pip install -r requirements.txt

# Chạy server
python main.py

# Truy cập
# http://localhost:8000/student   — Làm bài
# http://localhost:8000/admin     — Import đề
# http://localhost:8000/parent    — Nhật ký
```

## Deploy với Coolify

1. Push code lên GitHub
2. Trong Coolify → **New Resource** → **Docker**
3. Trỏ vào repo GitHub
4. Coolify tự detect `Dockerfile`
5. Set biến môi trường: `GEMINI_API_KEY=your_key`
6. **Mount volume**: `/app/data` để persist database
7. Deploy!

### Biến môi trường

| Biến | Mô tả | Bắt buộc |
|------|--------|----------|
| `GEMINI_API_KEY` | API key Google Gemini | Không (có thể set trong UI) |

## Cấu trúc project

```
├── main.py              # Entry point
├── database.py          # SQLite CRUD
├── judge.py             # Code execution & grading
├── ai_engine.py         # Gemini AI import/generate
├── templates.py         # CSS + HTML shell
├── routes_home.py       # Trang chủ
├── routes_student.py    # Làm bài + nộp bài
├── routes_admin.py      # Admin panel
├── routes_parent.py     # Nhật ký phụ huynh
├── routes_api.py        # API endpoints
├── Dockerfile           # Docker build
├── docker-compose.yml   # Docker Compose
└── requirements.txt     # Dependencies
```
