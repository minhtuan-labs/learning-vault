"""
Trích xuất số liệu BCTC từ PDF: PyMuPDF (text) hoặc Claude Vision (PDF scan).
Kết quả mong đợi: JSON { "report_type": "...", "metrics": [...] }.
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

MIN_AVG_CHARS_PER_PAGE = 80
MAX_TEXT_CHARS = 120_000
MAX_VISION_PAGES = 15
RENDER_DPI = 120

SYSTEM_PROMPT_VI = """Bạn là chuyên gia kế toán Việt Nam, chuyên đọc báo cáo tài chính doanh nghiệp.
Nhiệm vụ: trích xuất các chỉ số tài chính chính từ nội dung được cung cấp (text hoặc hình ảnh trang báo cáo).

Quy tắc:
- Trả về ĐÚNG một JSON hợp lệ, không markdown, không giải thích ngoài JSON.
- Cấu trúc bắt buộc:
{
  "report_type": "KQKD",
  "metrics": [
    {"name": "Tên chỉ tiêu tiếng Việt", "value": 123456.78, "unit": "triệu VND"},
    ...
  ]
}
- report_type phải là một trong: KQKD, CDKT, LCTT, TM, CBTT (suy luận từ nội dung nếu có thể, mặc định KQKD nếu không chắc).
- value là số (float), không dùng chuỗi; bỏ qua chỉ tiêu không đọc được số.
- unit mặc định "triệu VND" nếu báo cáo ghi triệu đồng; giữ đúng đơn vị nếu có trong tài liệu.
- Ưu tiên các chỉ tiêu cấp 1: Doanh thu thuần, Lợi nhuận trước thuế, Lợi nhuận sau thuế, Tài sản ngắn hạn, Nợ phải trả, Vốn chủ sở hữu, Lưu chuyển tiền thuần từ hoạt động kinh doanh, v.v. tùy loại báo cáo.
"""


def _avg_chars_per_page(doc: fitz.Document) -> float:
    n = len(doc)
    if n == 0:
        return 0.0
    total = sum(len(page.get_text() or "") for page in doc)
    return total / n


def _extract_full_text(doc: fitz.Document) -> str:
    parts: list[str] = []
    for page in doc:
        parts.append(page.get_text() or "")
    text = "\n".join(parts).strip()
    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]
    return text


def _pages_to_png_base64(doc: fitz.Document, max_pages: int) -> list[tuple[int, str]]:
    """Trả về list (page_index_1based, base64_png)."""
    out: list[tuple[int, str]] = []
    for i in range(min(len(doc), max_pages)):
        page = doc[i]
        pix = page.get_pixmap(dpi=RENDER_DPI, alpha=False)
        png = pix.tobytes("png")
        b64 = base64.standard_b64encode(png).decode("ascii")
        out.append((i + 1, b64))
    return out


def _parse_json_from_assistant_text(text: str) -> dict[str, Any]:
    text = text.strip()
    m = re.search(r"\{[\s\S]*\}\s*$", text)
    if m:
        text = m.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
        if fence:
            return json.loads(fence.group(1).strip())
        raise ValueError("Không parse được JSON từ phản hồi AI.") from None


def _call_claude(
    *,
    api_key: str,
    model: str,
    user_content: list[dict[str, Any]],
) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    selected_model = model.strip() or "claude-sonnet-4-6"
    try:
        message = client.messages.create(
            model=selected_model,
            max_tokens=8192,
            system=SYSTEM_PROMPT_VI,
            messages=[{"role": "user", "content": user_content}],
        )
    except Exception as e:
        err = str(e)
        is_missing_model = "not_found_error" in err and "model" in err.lower()
        fallback_model = "claude-sonnet-4-6"
        if is_missing_model and selected_model != fallback_model:
            message = client.messages.create(
                model=fallback_model,
                max_tokens=8192,
                system=SYSTEM_PROMPT_VI,
                messages=[{"role": "user", "content": user_content}],
            )
        else:
            raise
    blocks = message.content
    text_parts: list[str] = []
    for block in blocks:
        if block.type == "text":
            text_parts.append(block.text)
    combined = "\n".join(text_parts)
    return _parse_json_from_assistant_text(combined)


def extract_financial_json_from_pdf(
    pdf_path: str | Path,
    *,
    api_key: str,
    model: str,
    default_report_type: str = "KQKD",
) -> dict[str, Any]:
    """
    Đọc PDF và gọi Claude để trả về dict có keys: report_type, metrics (list name/value/unit).
    """
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(str(path))

    doc = fitz.open(path)
    try:
        avg = _avg_chars_per_page(doc)
        use_vision = avg < MIN_AVG_CHARS_PER_PAGE

        if use_vision:
            pages = _pages_to_png_base64(doc, MAX_VISION_PAGES)
            content: list[dict[str, Any]] = [
                {
                    "type": "text",
                    "text": (
                        f"Đây là {len(pages)} trang đầu của báo cáo tài chính dạng scan (ảnh). "
                        f"Loại báo cáo gợi ý từ ngữ cảnh: {default_report_type}. "
                        "Hãy trích xuất JSON theo hướng dẫn hệ thống."
                    ),
                }
            ]
            for page_no, b64 in pages:
                content.append({"type": "text", "text": f"--- Trang {page_no} ---"})
                content.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": b64,
                        },
                    }
                )
        else:
            body = _extract_full_text(doc)
            content = [
                {
                    "type": "text",
                    "text": (
                        "Dưới đây là nội dung text trích từ PDF báo cáo tài chính. "
                        f"Loại báo cáo gợi ý: {default_report_type}.\n\n"
                        f"{body}"
                    ),
                }
            ]

        result = _call_claude(api_key=api_key, model=model, user_content=content)
        if "report_type" not in result or "metrics" not in result:
            raise ValueError("JSON thiếu report_type hoặc metrics.")
        if not isinstance(result["metrics"], list):
            raise ValueError("metrics phải là mảng.")
        return result
    finally:
        doc.close()


def normalize_metrics(raw: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Chuẩn hoá metrics về list dict có keys name, value, unit."""
    rt = str(raw.get("report_type", "KQKD")).upper()
    metrics_out: list[dict[str, Any]] = []
    for item in raw["metrics"]:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        value = item.get("value")
        unit = item.get("unit") or "triệu VND"
        if name is None or value is None:
            continue
        try:
            fv = float(value)
        except (TypeError, ValueError):
            continue
        metrics_out.append({"name": str(name).strip(), "value": fv, "unit": str(unit)})
    return rt, metrics_out
