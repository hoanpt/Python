"""
=============================================================================
  JUDGE MODULE — Bộ chấm bài tự động (Python & C++)
=============================================================================
"""

import os
import sys
import subprocess
import tempfile

EXEC_TIMEOUT = 2.0  # giây


# =============================================================================
# BẢO MẬT CODE
# =============================================================================

FORBIDDEN_PATTERNS = [
    'import os', 'import sys', 'import subprocess', 'import socket',
    'import shutil', 'import signal', 'import ctypes', 'import multiprocessing',
    'from os', 'from sys', 'from subprocess', 'from socket',
    'from shutil', 'from signal', 'from ctypes', 'from multiprocessing',
    '__import__', 'exec(', 'eval(', 'compile(',
    'open(', 'globals(', 'locals(', 'getattr(',
    'breakpoint(', 'exit(', 'quit(',
]


def check_code_safety(code: str) -> str | None:
    """Kiểm tra code có chứa từ khóa nguy hiểm không. Trả về lý do nếu vi phạm."""
    code_lower = code.lower().replace(' ', '')
    for pattern in FORBIDDEN_PATTERNS:
        pattern_stripped = pattern.replace(' ', '')
        if pattern_stripped.lower() in code_lower:
            return f"Code chứa '{pattern}' — không được phép vì lý do bảo mật."
    return None


# =============================================================================
# THỰC THI CODE
# =============================================================================

def normalize_output(text: str) -> str:
    """Strip từng dòng, bỏ dòng trống cuối — so sánh công tâm."""
    lines = text.strip().splitlines()
    return "\n".join(line.strip() for line in lines)


def _find_cpp_compiler() -> str | None:
    """Tìm compiler C++ trên hệ thống."""
    for cmd in ["g++", "g++.exe", "c++"]:
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def run_code(code: str, inp: str, language: str = "python") -> tuple:
    """Thực thi code học sinh trong subprocess an toàn. Hỗ trợ Python và C++."""
    # Kiểm tra bảo mật trước khi chạy (chỉ Python)
    if language == "python":
        safety_err = check_code_safety(code)
        if safety_err:
            return "ERROR", f"⛔ BẢO MẬT: {safety_err}"

    tmp = None
    exe = None
    try:
        if language == "cpp":
            compiler = _find_cpp_compiler()
            if not compiler:
                return "ERROR", "Không tìm thấy g++ compiler. Cài MinGW hoặc g++ để dùng C++."

            with tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False, encoding="utf-8") as f:
                f.write(code)
                tmp = f.name
            exe = tmp.replace(".cpp", ".exe") if sys.platform == "win32" else tmp.replace(".cpp", "")

            # Compile
            comp = subprocess.run(
                [compiler, tmp, "-o", exe, "-std=c++17", "-O2"],
                capture_output=True, text=True, timeout=15,
                encoding="utf-8", errors="replace"
            )
            if comp.returncode != 0:
                return "ERROR", f"⚠ Compile Error:\n{comp.stderr[:500]}"

            # Run
            r = subprocess.run(
                [exe],
                input=inp, capture_output=True, text=True,
                timeout=EXEC_TIMEOUT, encoding="utf-8", errors="replace"
            )
            return r.stdout, r.stderr
        else:
            # Python
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
                f.write(code)
                tmp = f.name
            r = subprocess.run(
                [sys.executable, tmp],
                input=inp, capture_output=True, text=True,
                timeout=EXEC_TIMEOUT, encoding="utf-8", errors="replace"
            )
            return r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "Chuong trinh chay qua 2 giay"
    except Exception as e:
        return "ERROR", str(e)
    finally:
        for path in [tmp, exe]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass


def judge(code: str, testcases: list, language: str = "python") -> dict:
    """Chấm toàn bộ testcase, trả về score 0-100 và chi tiết."""
    if not testcases:
        return {"score": 0, "details": [], "passed": 0, "total": 0}
    results, passed = [], 0
    for i, tc in enumerate(testcases):
        inp, exp = tc.get("input", ""), tc.get("output", "")
        stdout, stderr = run_code(code, inp, language)
        if stdout == "TIMEOUT":
            status, ok = "TLE", False
        elif stdout == "ERROR":
            status, ok = "ERROR", False
        elif stderr and not stdout.strip():
            status, ok = "RE", False
        else:
            ok = normalize_output(stdout) == normalize_output(exp)
            status = "AC" if ok else "WA"
        if ok:
            passed += 1
        results.append({
            "testcase_id": i + 1,
            "input": inp[:400], "expected": exp[:400],
            "actual": (stdout if stdout not in ("TIMEOUT", "ERROR") else stderr)[:400],
            "status": status, "passed": ok,
            "stderr": stderr[:200] if stderr else ""
        })
    return {
        "score": round(passed / len(testcases) * 100),
        "details": results,
        "passed": passed,
        "total": len(testcases),
    }
