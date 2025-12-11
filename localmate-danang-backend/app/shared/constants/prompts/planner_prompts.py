"""Prompts for Planner Agent."""

ITINERARY_TITLE_PROMPT = """Tạo tiêu đề hấp dẫn cho lịch trình du lịch Đà Nẵng.

Thông tin:
- Số ngày: {duration_days}
- Sở thích: {interests}

Yêu cầu:
- Dưới 10 từ
- Tiếng Việt
- Hấp dẫn, gợi cảm xúc

Chỉ trả về tiêu đề, không giải thích."""

STOP_DESCRIPTION_PROMPT = """Viết mô tả ngắn cho điểm dừng trong lịch trình du lịch.

Địa điểm: {place_name}
Loại: {category}
Thành phố: Đà Nẵng

Yêu cầu:
- 1-2 câu
- Tiếng Việt
- Nêu điểm đặc sắc

Chỉ trả về mô tả."""

DAILY_SUMMARY_PROMPT = """Tạo tóm tắt cho ngày {day_index} của lịch trình.

Các điểm dừng:
{stops}

Viết tóm tắt ngắn gọn (1-2 câu) về trải nghiệm trong ngày."""

FULL_ITINERARY_SUMMARY_PROMPT = """Tạo mô tả tổng quan cho lịch trình du lịch.

Thông tin:
- Tiêu đề: {title}
- Số ngày: {total_days}
- Các địa điểm: {places}

Viết mô tả tổng quan hấp dẫn (2-3 câu)."""
