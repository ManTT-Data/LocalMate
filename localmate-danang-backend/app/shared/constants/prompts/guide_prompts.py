"""Prompts for Guide Agent."""

GUIDE_FUN_FACT_PROMPT = """Tạo một fun fact thú vị về địa điểm "{place_name}" ở Đà Nẵng.

Thông tin địa điểm:
- Tên: {place_name}
- Loại: {category}
- Mô tả: {description}

Yêu cầu:
- 1-2 câu
- Tiếng Việt
- Thông tin độc đáo, ít người biết
- Chỉ trả về fact, không giải thích"""

GUIDE_LOCAL_TIPS_PROMPT = """Tạo 3 tips địa phương cho du khách tại "{place_name}" ở Đà Nẵng.

Thông tin địa điểm:
- Tên: {place_name}
- Loại: {category}
- Rating: {rating}
- Mô tả: {description}

Yêu cầu:
- Mỗi tip 1 câu ngắn gọn
- Tiếng Việt
- Thực tế, hữu ích
- Trả về dạng danh sách, mỗi dòng 1 tip, bắt đầu bằng "-"
"""

GUIDE_FULL_CONTENT_PROMPT = """Tạo nội dung hướng dẫn đầy đủ cho địa điểm du lịch.

Thông tin địa điểm:
- ID: {place_id}
- Tên: {place_name}
- Loại: {category}
- Rating: {rating}/5
- Mô tả: {description}

Yêu cầu trả về JSON với format sau (chỉ trả về JSON):
{{
    "fun_fact": "1-2 câu fun fact thú vị",
    "tips": ["tip 1", "tip 2", "tip 3"],
    "best_time_to_visit": "thời gian tốt nhất để đến",
    "suggested_duration": "thời gian tham quan đề xuất",
    "highlights": ["điểm nổi bật 1", "điểm nổi bật 2"]
}}"""
