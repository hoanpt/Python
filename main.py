"""
=============================================================================
  MINI ONLINE JUDGE v3.0 — Hệ thống ôn thi Chuyên Tin lớp 9
=============================================================================
  AI Library : google-genai (Gemini 2.5 Flash + Vision)
  Database   : SQLite (data/oj.db)
  Tính năng  :
    - Import đề thi từ ảnh (Gemini Vision) hoặc file text
    - Tách từng bài riêng để bé làm hàng ngày
    - Hiển thị đúng chuẩn đề thi thật (subtask, ví dụ, ràng buộc)
    - Chấm bài tự động (Python & C++) + nhật ký phụ huynh
  Chạy       : python main.py
=============================================================================
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes_home import router as home_router
from routes_student import router as student_router
from routes_admin import router as admin_router
from routes_parent import router as parent_router
from routes_api import router as api_router

# =============================================================================
# APP INITIALIZATION
# =============================================================================


@asynccontextmanager
async def lifespan(app):
    """Khởi tạo database khi server start."""
    init_db()
    yield


app = FastAPI(title="Mini OJ - Chuyen Tin Lop 9 v3", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(home_router)
app.include_router(student_router)
app.include_router(admin_router)
app.include_router(parent_router)
app.include_router(api_router)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    # Init DB trước khi chạy (cho trường hợp chạy trực tiếp)
    init_db()

    print("=" * 56)
    print("  MINI OJ v3.0 - Chuyen Tin Lop 9")
    print("  Database: SQLite (data/oj.db)")
    print("=" * 56)
    print("  http://localhost:8000/student   - Hoc sinh")
    print("  http://localhost:8000/admin     - Admin + Import")
    print("  http://localhost:8000/parent    - Phu huynh")
    print("  http://localhost:8000/health    - Health check")
    print("=" * 56)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
