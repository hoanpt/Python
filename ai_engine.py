"""
=============================================================================
  AI ENGINE — Gemini AI Import & Generate cho Mini Online Judge
=============================================================================
"""

import json


# =============================================================================
# SCHEMA & PROMPTS
# =============================================================================

PROBLEM_SCHEMA = """{
  "title": "TÊN BÀI (VD: ROBOT)",
  "score_points": 2.0,
  "difficulty": "Trung bình",
  "input_filename": "ROBOT.INP",
  "output_filename": "ROBOT.OUT",
  "description": "Mô tả bối cảnh và yêu cầu bài toán (nguyên văn đề thi)",
  "input_format": "Định dạng dữ liệu vào (nguyên văn)",
  "output_format": "Định dạng dữ liệu ra (nguyên văn)",
  "constraints": "Subtask 1 (40%): N <= 100\\nSubtask 2 (60%): N <= 10^5",
  "examples": [
    {"input": "dữ liệu vào ví dụ", "output": "kết quả ví dụ", "explanation": "giải thích"}
  ],
  "testcases": [
    {"input": "tc1 input", "output": "tc1 output"},
    {"input": "tc2 input", "output": "tc2 output"},
    {"input": "tc3 input", "output": "tc3 output"},
    {"input": "tc4 input", "output": "tc4 output"},
    {"input": "tc5 input", "output": "tc5 output"}
  ],
  "source_exam": "Tên kỳ thi nếu biết, hoặc để trống"
}"""

IMPORT_SYSTEM_PROMPT = f"""Ban la chuyen gia doc hieu de thi Tin hoc Viet Nam (HSG, Chuyen Tin lop 9-12).
Nhiem vu: Doc anh de thi (hoac noi dung text) va TACH TUNG BAI TOAN thanh cac JSON doc lap.

QUY TAC BAT BUOC:
1. Moi bai toan trong de thi la 1 JSON rieng biet.
2. Tra ve 1 mang JSON: [{{"bai1"}}, {{"bai2"}}, ...] - KHONG co text ben ngoai, KHONG markdown.
3. Moi phan tu mang theo dung cau truc:
{PROBLEM_SCHEMA}

LUU Y QUAN TRONG:
- testcases: Tao CHINH XAC it nhat 5 testcase (input/output phai khop nhau).
  Bao gom: 2 testcase de, 2 trung binh, 1 corner case.
  Tinh toan output tu input - KHONG duoc sai.
- Trong he thong nay, hoc sinh dung input()/print() (stdin/stdout) thay cho doc/ghi file.
  Nen testcase input/output phai tuong ung voi stdin/stdout.
- difficulty: "De" | "Trung binh" | "Kho" | "Rat kho"
- Giu nguyen ngon ngu tieng Viet trong description, input_format, output_format, constraints."""

GENERATE_SYSTEM_PROMPT = f"""Ban la Chuyen gia Ra de thi Hoc sinh gioi Tin hoc Viet Nam lop 9 voi 20 nam kinh nghiem.
Nhiem vu: Sang tac 1 bai toan MOI chat luong cao de hoc sinh luyen tap hang ngay.

QUY TAC BAT BUOC:
1. Tra ve DUY NHAT 1 chuoi JSON hop le - KHONG co text ben ngoai, KHONG markdown.
2. Cau truc JSON:
{PROBLEM_SCHEMA}

YEU CAU NOI DUNG:
- testcases: It nhat 5 testcase CHINH XAC (input/output phai khop tuyet doi).
- difficulty phu hop voi yeu cau.
- Co subtask ro rang trong constraints.
- Chu de: mang, chuoi, sap xep, tim kiem, QHD co ban, do thi don gian."""


# =============================================================================
# TIỆN ÍCH
# =============================================================================

def _clean_json(raw: str) -> str:
    """Loại bỏ markdown wrapper nếu AI vẫn thêm vào."""
    s = raw.strip()
    if s.startswith("```"):
        lines = s.split("\n")
        s = "\n".join(lines[1:]).rsplit("```", 1)[0].strip()
    return s


def _validate_problem(d: dict, idx: int = 0) -> dict:
    """Validate và chuẩn hóa 1 bài toán từ AI."""
    for k in ("title", "description", "testcases"):
        if k not in d:
            raise ValueError(f"Bai {idx+1}: thieu truong '{k}'")
    if not isinstance(d["testcases"], list) or not d["testcases"]:
        raise ValueError(f"Bai {idx+1}: 'testcases' rong")
    for i, tc in enumerate(d["testcases"]):
        if "input" not in tc or "output" not in tc:
            raise ValueError(f"Bai {idx+1}, testcase {i+1}: thieu input/output")
    return d


# =============================================================================
# AI FUNCTIONS
# =============================================================================

def ai_import_from_text(api_key: str, text_content: str, extra: str = "") -> list:
    """Đọc nội dung text đề thi, trả về list bài toán."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = f"NOI DUNG DE THI:\n{text_content}\n\nYEU CAU BO SUNG: {extra or 'Tach tat ca bai toan trong de thi'}"
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=IMPORT_SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=8192,
        )
    )
    raw = _clean_json(resp.text)
    data = json.loads(raw)
    if isinstance(data, dict):
        data = [data]
    return [_validate_problem(p, i) for i, p in enumerate(data)]


def ai_import_from_images(api_key: str, images_bytes: list, extra: str = "") -> list:
    """Đọc ảnh đề thi (Vision), trả về list bài toán."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    parts = []
    for img_b, mime in images_bytes:
        parts.append(types.Part.from_bytes(data=img_b, mime_type=mime))
    parts.append(types.Part.from_text(
        text=f"Hay doc tat ca cac anh de thi tren va tach tung bai toan.\n"
             f"Yeu cau bo sung: {extra or 'Tach tat ca bai toan'}"
    ))

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=parts,
        config=types.GenerateContentConfig(
            system_instruction=IMPORT_SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=8192,
        )
    )
    raw = _clean_json(resp.text)
    data = json.loads(raw)
    if isinstance(data, dict):
        data = [data]
    return [_validate_problem(p, i) for i, p in enumerate(data)]


def ai_generate_problem(api_key: str, ref_text: str, extra: str) -> dict:
    """AI tự sáng tác 1 bài toán mới."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = (
        f"DE THAM KHAO:\n{ref_text or 'Khong co. Tu sang tac.'}\n\n"
        f"YEU CAU: {extra or 'Ra 1 bai toan ve thuat toan co ban cho hoc sinh gioi lop 9.'}"
    )
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=GENERATE_SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=4096,
        )
    )
    raw = _clean_json(resp.text)
    d = json.loads(raw)
    return _validate_problem(d)


def build_problem_record(d: dict, source: str = "AI Generated") -> dict:
    """Chuẩn hóa dict AI trả về thành record đầy đủ cho database."""
    return {
        "title": d.get("title", "Không có tiêu đề"),
        "score_points": float(d.get("score_points", 1.0)),
        "difficulty": d.get("difficulty", "Trung bình"),
        "input_filename": d.get("input_filename", "BAITAP.INP"),
        "output_filename": d.get("output_filename", "BAITAP.OUT"),
        "description": d.get("description", ""),
        "input_format": d.get("input_format", ""),
        "output_format": d.get("output_format", ""),
        "constraints": d.get("constraints", ""),
        "examples": d.get("examples", []),
        "testcases": d.get("testcases", []),
        "source_exam": d.get("source_exam", ""),
        "tags": d.get("tags", []),
        "source": source,
    }
