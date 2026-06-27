"""
=============================================================================
  DATABASE MODULE — SQLite CRUD cho Mini Online Judge
=============================================================================
"""

import sqlite3
import json
import uuid
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH  = DATA_DIR / "oj.db"

# Legacy JSON files (for migration)
_LEGACY_PROBLEMS  = BASE_DIR / "problems.json"
_LEGACY_SUBS      = BASE_DIR / "submissions.json"
_LEGACY_CONFIG    = BASE_DIR / "config.json"

# Preview cache (ephemeral)
PREVIEW_FILE = DATA_DIR / "_preview_cache.json"


def _get_conn() -> sqlite3.Connection:
    """Tạo connection SQLite với Row factory."""
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Tạo tables nếu chưa có, migrate data cũ nếu phát hiện."""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS problems (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            score_points REAL DEFAULT 1.0,
            difficulty TEXT DEFAULT 'Trung bình',
            input_filename TEXT DEFAULT '',
            output_filename TEXT DEFAULT '',
            description TEXT DEFAULT '',
            input_format TEXT DEFAULT '',
            output_format TEXT DEFAULT '',
            constraints TEXT DEFAULT '',
            examples TEXT DEFAULT '[]',
            testcases TEXT DEFAULT '[]',
            source_exam TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            source TEXT DEFAULT 'Manual',
            created_at TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            problem_id TEXT,
            problem_title TEXT,
            student_name TEXT DEFAULT 'Ẩn danh',
            code TEXT,
            language TEXT DEFAULT 'python',
            score INTEGER DEFAULT 0,
            details TEXT DEFAULT '[]',
            passed INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            submitted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    conn.commit()
    conn.close()

    # Migrate legacy JSON data if exists
    _migrate_from_json()

    # Tạo bài mẫu nếu DB rỗng
    if not get_all_problems():
        _insert_sample_problem()


def _load_legacy_json(fp: Path, default):
    if not fp.exists():
        return default
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _migrate_from_json():
    """Migrate dữ liệu từ JSON files cũ sang SQLite."""
    migrated = False

    # Migrate problems
    if _LEGACY_PROBLEMS.exists():
        old_probs = _load_legacy_json(_LEGACY_PROBLEMS, [])
        if old_probs:
            conn = _get_conn()
            for p in old_probs:
                try:
                    conn.execute("""
                        INSERT OR IGNORE INTO problems
                        (id, title, score_points, difficulty, input_filename, output_filename,
                         description, input_format, output_format, constraints, examples,
                         testcases, source_exam, tags, source, created_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        p.get("id", str(uuid.uuid4())[:8]),
                        p.get("title", ""),
                        float(p.get("score_points", 1.0)),
                        p.get("difficulty", "Trung bình"),
                        p.get("input_filename", ""),
                        p.get("output_filename", ""),
                        p.get("description", ""),
                        p.get("input_format", ""),
                        p.get("output_format", ""),
                        p.get("constraints", ""),
                        json.dumps(p.get("examples", []), ensure_ascii=False),
                        json.dumps(p.get("testcases", []), ensure_ascii=False),
                        p.get("source_exam", ""),
                        json.dumps(p.get("tags", []), ensure_ascii=False),
                        p.get("source", "Manual"),
                        p.get("created_at", datetime.now().isoformat()),
                    ))
                except Exception:
                    pass
            conn.commit()
            conn.close()
        _LEGACY_PROBLEMS.rename(_LEGACY_PROBLEMS.with_suffix(".json.bak"))
        migrated = True
        print(f"[MIGRATE] problems.json -> SQLite ({len(old_probs)} bai)")

    # Migrate submissions
    if _LEGACY_SUBS.exists():
        old_subs = _load_legacy_json(_LEGACY_SUBS, [])
        if old_subs:
            conn = _get_conn()
            for s in old_subs:
                try:
                    conn.execute("""
                        INSERT OR IGNORE INTO submissions
                        (id, problem_id, problem_title, student_name, code, language,
                         score, details, passed, total, submitted_at)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        s.get("id", str(uuid.uuid4())[:8]),
                        s.get("problem_id", ""),
                        s.get("problem_title", ""),
                        s.get("student_name", "Ẩn danh"),
                        s.get("code", ""),
                        s.get("language", "python"),
                        int(s.get("score", 0)),
                        json.dumps(s.get("details", []), ensure_ascii=False),
                        int(s.get("passed", 0)),
                        int(s.get("total", 0)),
                        s.get("submitted_at", datetime.now().isoformat()),
                    ))
                except Exception:
                    pass
            conn.commit()
            conn.close()
        _LEGACY_SUBS.rename(_LEGACY_SUBS.with_suffix(".json.bak"))
        migrated = True
        print(f"[MIGRATE] submissions.json -> SQLite ({len(old_subs)} bai nop)")

    # Migrate config
    if _LEGACY_CONFIG.exists():
        old_cfg = _load_legacy_json(_LEGACY_CONFIG, {})
        if old_cfg.get("api_key"):
            set_config_value("api_key", old_cfg["api_key"])
        _LEGACY_CONFIG.rename(_LEGACY_CONFIG.with_suffix(".json.bak"))
        migrated = True
        print("[MIGRATE] config.json -> SQLite")

    if migrated:
        print("[MIGRATE] Done. Old files renamed to .bak")


def _insert_sample_problem():
    """Tạo bài ROBOT mẫu."""
    add_problem({
        "id": "sample01",
        "title": "ROBOT",
        "score_points": 2.0,
        "difficulty": "Trung bình",
        "input_filename": "ROBOT.INP",
        "output_filename": "ROBOT.OUT",
        "description": (
            "Cho một xâu S có độ dài N ký tự, ghi lại hành trình di chuyển của một Robot trên "
            "lưới các ô vuông. Trong xâu S chứa các ký tự U, D, L, R tương ứng với các hướng "
            "di chuyển, mỗi lần di chuyển một ô vuông với: U - lên trên, D - xuống dưới, "
            "L - sang trái, R - sang phải.\n\n"
            "Yêu cầu: Hãy tìm tọa độ của Robot khi kết thúc hành trình, biết rằng ban đầu "
            "Robot xuất phát tại tọa độ (0, 0)."
        ),
        "input_format": "Dòng thứ nhất chứa số nguyên dương N (N ≤ 10^5).\nDòng thứ hai chứa xâu S.",
        "output_format": "Ghi ra hai số nguyên dương x và y cách nhau một ký tự trống, là tọa độ của Robot khi kết thúc hành trình.",
        "constraints": "Subtask 1 (40%): N ≤ 100\nSubtask 2 (60%): N ≤ 10^5",
        "examples": [
            {"input": "9\nUULLDRDRR", "output": "0 -1",
             "explanation": "Robot di chuyển lên 2, trái 2, xuống 1, phải 1, xuống 1, phải 2 → (0, -1)"}
        ],
        "testcases": [
            {"input": "9\nUULLDRDRR", "output": "0 -1"},
            {"input": "4\nUDLR", "output": "0 0"},
            {"input": "5\nUUUUU", "output": "0 5"},
            {"input": "6\nRRRRRR", "output": "6 0"},
            {"input": "8\nUURRDDLL", "output": "0 0"},
        ],
        "source_exam": "KỲ THI CHỌN HSG TP ĐÀ NẴNG 2025-2026",
        "tags": ["string", "simulation"],
        "source": "Sample",
    })
    print("[OK] Created sample problem ROBOT in SQLite")


# =============================================================================
# CRUD: PROBLEMS
# =============================================================================

def _row_to_problem(row: sqlite3.Row) -> dict:
    """Convert SQLite Row to problem dict, parsing JSON fields."""
    d = dict(row)
    for k in ("examples", "testcases", "tags"):
        if k in d and isinstance(d[k], str):
            try:
                d[k] = json.loads(d[k])
            except (json.JSONDecodeError, TypeError):
                d[k] = []
    return d


def get_all_problems() -> list:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM problems ORDER BY created_at DESC").fetchall()
    conn.close()
    return [_row_to_problem(r) for r in rows]


def get_problem(pid: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM problems WHERE id=?", (pid,)).fetchone()
    conn.close()
    return _row_to_problem(row) if row else None


def add_problem(data: dict) -> str:
    pid = data.get("id") or str(uuid.uuid4())[:8]
    now = data.get("created_at") or datetime.now().isoformat()
    conn = _get_conn()
    conn.execute("""
        INSERT INTO problems
        (id, title, score_points, difficulty, input_filename, output_filename,
         description, input_format, output_format, constraints, examples,
         testcases, source_exam, tags, source, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        pid,
        data.get("title", "Không có tiêu đề"),
        float(data.get("score_points", 1.0)),
        data.get("difficulty", "Trung bình"),
        data.get("input_filename", ""),
        data.get("output_filename", ""),
        data.get("description", ""),
        data.get("input_format", ""),
        data.get("output_format", ""),
        data.get("constraints", ""),
        json.dumps(data.get("examples", []), ensure_ascii=False),
        json.dumps(data.get("testcases", []), ensure_ascii=False),
        data.get("source_exam", ""),
        json.dumps(data.get("tags", []), ensure_ascii=False),
        data.get("source", "Manual"),
        now,
    ))
    conn.commit()
    conn.close()
    return pid


def update_problem(pid: str, data: dict) -> bool:
    conn = _get_conn()
    conn.execute("""
        UPDATE problems SET
            title=?, score_points=?, difficulty=?, input_filename=?, output_filename=?,
            description=?, input_format=?, output_format=?, constraints=?,
            examples=?, testcases=?, source_exam=?, updated_at=?
        WHERE id=?
    """, (
        data.get("title", ""),
        float(data.get("score_points", 1.0)),
        data.get("difficulty", "Trung bình"),
        data.get("input_filename", ""),
        data.get("output_filename", ""),
        data.get("description", ""),
        data.get("input_format", ""),
        data.get("output_format", ""),
        data.get("constraints", ""),
        json.dumps(data.get("examples", []), ensure_ascii=False),
        json.dumps(data.get("testcases", []), ensure_ascii=False),
        data.get("source_exam", ""),
        datetime.now().isoformat(),
        pid,
    ))
    conn.commit()
    affected = conn.total_changes
    conn.close()
    return affected > 0


def delete_problem(pid: str) -> bool:
    conn = _get_conn()
    conn.execute("DELETE FROM problems WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return True


# =============================================================================
# CRUD: SUBMISSIONS
# =============================================================================

def _row_to_submission(row: sqlite3.Row) -> dict:
    d = dict(row)
    if "details" in d and isinstance(d["details"], str):
        try:
            d["details"] = json.loads(d["details"])
        except (json.JSONDecodeError, TypeError):
            d["details"] = []
    return d


def get_all_submissions() -> list:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM submissions ORDER BY submitted_at DESC").fetchall()
    conn.close()
    return [_row_to_submission(r) for r in rows]


def get_submissions_filtered(student_name: str = "") -> list:
    conn = _get_conn()
    if student_name.strip():
        rows = conn.execute(
            "SELECT * FROM submissions WHERE LOWER(student_name) LIKE ? ORDER BY submitted_at DESC",
            (f"%{student_name.strip().lower()}%",)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM submissions ORDER BY submitted_at DESC").fetchall()
    conn.close()
    return [_row_to_submission(r) for r in rows]


def add_submission(data: dict) -> str:
    sid = data.get("id") or str(uuid.uuid4())[:8]
    conn = _get_conn()
    conn.execute("""
        INSERT INTO submissions
        (id, problem_id, problem_title, student_name, code, language,
         score, details, passed, total, submitted_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        sid,
        data.get("problem_id", ""),
        data.get("problem_title", ""),
        data.get("student_name", "Ẩn danh"),
        data.get("code", ""),
        data.get("language", "python"),
        int(data.get("score", 0)),
        json.dumps(data.get("details", []), ensure_ascii=False),
        int(data.get("passed", 0)),
        int(data.get("total", 0)),
        data.get("submitted_at") or datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()
    return sid


def get_student_names() -> list:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT DISTINCT student_name FROM submissions ORDER BY student_name"
    ).fetchall()
    conn.close()
    return [r["student_name"] for r in rows]


# =============================================================================
# CONFIG
# =============================================================================

def get_api_key() -> str:
    """Lấy API key — ưu tiên env var."""
    env = os.environ.get("GEMINI_API_KEY", "")
    if env:
        return env
    conn = _get_conn()
    row = conn.execute("SELECT value FROM config WHERE key='api_key'").fetchone()
    conn.close()
    return row["value"] if row else ""


def set_api_key(key: str):
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES ('api_key', ?)",
        (key,)
    )
    conn.commit()
    conn.close()


def get_config_value(key: str, default: str = "") -> str:
    conn = _get_conn()
    row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_config_value(key: str, value: str):
    conn = _get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()


# =============================================================================
# PREVIEW CACHE (ephemeral JSON)
# =============================================================================

def save_preview(data: list):
    DATA_DIR.mkdir(exist_ok=True)
    with open(PREVIEW_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_preview() -> list:
    if not PREVIEW_FILE.exists():
        return []
    try:
        with open(PREVIEW_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def clear_preview():
    if PREVIEW_FILE.exists():
        PREVIEW_FILE.unlink()


# =============================================================================
# STATS (cho trang chủ / parent)
# =============================================================================

def get_stats() -> dict:
    conn = _get_conn()
    prob_count = conn.execute("SELECT COUNT(*) as c FROM problems").fetchone()["c"]
    sub_count = conn.execute("SELECT COUNT(*) as c FROM submissions").fetchone()["c"]
    perf_count = conn.execute("SELECT COUNT(*) as c FROM submissions WHERE score=100").fetchone()["c"]
    conn.close()
    return {"problems": prob_count, "submissions": sub_count, "perfect": perf_count}


def get_submission_stats(student_name: str = "") -> dict:
    subs = get_submissions_filtered(student_name)
    total = len(subs)
    avg = round(sum(s.get("score", 0) for s in subs) / total) if total else 0
    perf = sum(1 for s in subs if s.get("score", 0) == 100)
    return {"total": total, "avg": avg, "perfect": perf}
