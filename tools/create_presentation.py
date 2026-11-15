# -*- coding: utf-8 -*-
"""
Script tạo bộ slide thuyết trình chuyên nghiệp 16:9 (slide_thuyet_trinh.pptx)
dành cho buổi bảo vệ đồ án tốt nghiệp / báo cáo học thuật môn Tối ưu phần mềm di động.
Tích hợp:
- Chuẩn tỷ lệ màn hình rộng 16:9 (13.333 x 7.5 inches).
- Bố cục học thuật hiện đại, thẻ card đồ họa, bảng số liệu đối chiếu.
- Gắn trực tiếp 10 đồ thị thực nghiệm 300 DPI và ảnh chụp Stack Monitor HUD.
- Đầy đủ Speaker Notes (Lời thoại thuyết trình) cho từng slide, khớp nối trực tiếp với live_demo.md.
"""

import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# HẰNG SỐ MÀU SẮC & PHÔNG CHỮ CHUẨN HỌC THUẬT (ACADEMIC PALETTE)
# ==============================================================================
COLOR_BG_LIGHT     = RGBColor(0xF8, 0xFA, 0xFC)  # Slate 50
COLOR_CARD_BG      = RGBColor(0xFF, 0xFF, 0xFF)  # White
COLOR_CARD_BORDER  = RGBColor(0xCB, 0xD5, 0xE1)  # Slate 300
COLOR_NAVY_DARK    = RGBColor(0x0F, 0x17, 0x2A)  # Slate 900
COLOR_NAVY_BLUE    = RGBColor(0x1E, 0x3A, 0x8A)  # Blue 900
COLOR_PRIMARY_BLUE = RGBColor(0x25, 0x63, 0xEB)  # Blue 600
COLOR_CYAN_ACCENT  = RGBColor(0x02, 0x84, 0xC7)  # Sky 600
COLOR_GREEN_EMERALD= RGBColor(0x05, 0x96, 0x69)  # Emerald 600
COLOR_AMBER_WARN   = RGBColor(0xD9, 0x77, 0x06)  # Amber 600
COLOR_RED_ALERT    = RGBColor(0xDC, 0x26, 0x26)  # Red 600
COLOR_TEXT_MAIN    = RGBColor(0x1E, 0x29, 0x3B)  # Slate 800
COLOR_TEXT_MUTED   = RGBColor(0x64, 0x74, 0x8B)  # Slate 500

FONT_NAME_TITLE = "Segoe UI"
FONT_NAME_BODY  = "Segoe UI"

def set_slide_background_color(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text=""):
    # Header banner
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
    top_bar.line.fill.background()

    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.9))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    if category_text:
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = FONT_NAME_TITLE
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_PRIMARY_BLUE
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]

    p_title.text = title_text
    p_title.font.name = FONT_NAME_TITLE
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_NAVY_DARK

def add_card(slide, left, top, width, height, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card

def add_card_content(slide, left, top, width, height, title="", items=None, title_color=COLOR_NAVY_BLUE):
    add_card(slide, left, top, width, height)
    tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(height - 0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    if title:
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_NAME_TITLE
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = title_color
        p_t.space_after = Pt(8)

    if items:
        for idx, it in enumerate(items):
            p = tf.add_paragraph() if (title or idx > 0) else tf.paragraphs[0]
            p.text = it
            p.font.name = FONT_NAME_BODY
            p.font.size = Pt(11.5)
            p.font.color.rgb = COLOR_TEXT_MAIN
            p.space_after = Pt(6)

def add_speaker_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

# ==============================================================================
# HÀM XÂY DỰNG TOÀN BỘ 18 SLIDE
# ==============================================================================
def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --------------------------------------------------------------------------
    # SLIDE 1: TRANG TIÊU ĐỀ (TITLE SLIDE)
    # --------------------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide1, COLOR_NAVY_DARK)

    # Accent decorative bars
    accent_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.18), Inches(3.2))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
    accent_bar.line.fill.background()

    tb = slide1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(11.2), Inches(3.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "HỌC VIỆN KỸ THUẬT MẬT MÃ — KHOA CÔNG NGHỆ THÔNG TIN"
    p0.font.name = FONT_NAME_TITLE
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_CYAN_ACCENT
    p0.space_after = Pt(12)

    p1 = tf.add_paragraph()
    p1.text = "BỘ LẬP LỊCH TÁC VỤ THÍCH ỨNG TẦNG ỨNG DỤNG\nCHO NỀN TẢNG FLUTTER"
    p1.font.name = FONT_NAME_TITLE
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p1.space_after = Pt(12)

    p2 = tf.add_paragraph()
    p2.text = "Tối ưu hóa Đa mục tiêu giữa Độ mượt mà Giao diện và Thông lượng Xử lý Nền"
    p2.font.name = FONT_NAME_BODY
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)

    # Info card at bottom
    add_card(slide1, 1.2, 5.2, 10.9, 1.4, bg_color=RGBColor(0x1E, 0x29, 0x3B), border_color=RGBColor(0x33, 0x41, 0x55))
    tb_info = slide1.shapes.add_textbox(Inches(1.5), Inches(5.35), Inches(10.3), Inches(1.1))
    tf_info = tb_info.text_frame
    p_gv = tf_info.paragraphs[0]
    p_gv.text = "Giáo viên hướng dẫn: ThS. Lê Bá Cường"
    p_gv.font.bold = True
    p_gv.font.size = Pt(12)
    p_gv.font.color.rgb = COLOR_CYAN_ACCENT

    p_sv = tf_info.add_paragraph()
    p_sv.text = "Sinh viên thực hiện: Nguyễn Văn Nghĩa · Dương Công Hai · Cao Đình Nguyên · Nguyễn Huy Hoàng (Lớp L01)"
    p_sv.font.size = Pt(12)
    p_sv.font.color.rgb = RGBColor(0xF1, 0xF5, 0xF9)

    add_speaker_notes(slide1, 
        "Kính thưa Thầy Cô và Hội đồng đánh giá. Hôm nay nhóm chúng em xin được báo cáo đề tài nghiên cứu: "
        "'Bộ lập lịch tác vụ thích ứng tầng ứng dụng cho nền tảng Flutter - Tối ưu hóa đa mục tiêu giữa độ mượt giao diện và thông lượng xử lý nền'. "
        "Bài báo cáo sẽ đi từ nghịch lý căn bản của hệ điều hành, mô hình hóa toán học, kiến trúc 5 phân lớp và các kiểm chứng thực nghiệm chuẩn tắc trên phần cứng thật."
    )

    # --------------------------------------------------------------------------
    # SLIDE 2: BỐI CẢNH NGHIÊN CỨU & NGHỊCH LÝ HỆ ĐIỀU HÀNH
    # --------------------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide2, COLOR_BG_LIGHT)
    add_header(slide2, "Bối Cảnh Nghiên Cứu & Nghịch Lý Hệ Điều Hành", "1. Đặt Vấn Đề")

    add_card_content(slide2, 0.8, 1.5, 5.6, 5.3, 
        title="Thực Trạng Phần Cứng Di Động", 
        items=[
            "• Vi xử lý đa nhân (Octa-core SoC): Kiến trúc big.LITTLE / DynamIQ kết hợp giữa nhân hiệu năng cao và nhân tiết kiệm điện.",
            "• Màn hình tần số quét cao (60 Hz - 120 Hz): Ngân sách thời gian dựng hình bị siết chặt còn 16.67 ms (60Hz) hoặc 8.33 ms (120Hz).",
            "• Ứng dụng di động ngày càng nặng: Đồng thời gánh vác tương tác vuốt chạm phức tạp và các tác vụ nền đồ sộ (giải nén tập tin, giải mã đồ họa, mã hóa dữ liệu)."
        ],
        title_color=COLOR_NAVY_BLUE
    )

    add_card_content(slide2, 6.8, 1.5, 5.7, 5.3, 
        title="Nghịch Lý 'Bất Cân Xứng Nhận Thức' (Semantic Blindness)", 
        items=[
            "• Hệ điều hành chia sẻ CPU theo nguyên tắc 'công bằng toán học' (nhân Linux CFS - Completely Fair Scheduler).",
            "• Nhân hệ điều hành HOÀN TOÀN MÙ NGỮ NGHĨA đối với trải nghiệm người dùng:",
            "   - HĐH coi luồng cuộn danh sách và luồng giải nén nền 10.000 dòng Excel là NGANG HÀNG NHAU.",
            "   - Một độ trễ 5ms trên giao diện sẽ gây giật lag trực giác, trong khi việc trễ 500ms ở tiến trình nền không gây ảnh hưởng.",
            "• Hệ quả tất yếu: Khi ứng dụng đẩy tính toán ra đa luồng không kiểm soát, các luồng nền tranh chấp CPU/Bus, phá vỡ nhịp Vsync và làm sập độ mượt của màn hình."
        ],
        title_color=COLOR_RED_ALERT
    )

    add_speaker_notes(slide2,
        "Điểm mấu chốt đầu tiên là Nghịch lý Bất cân xứng nhận thức. Hệ điều hành Android chia CPU rất công bằng, "
        "nhưng nó 'mù' về mặt ngữ nghĩa: nó không biết luồng nào đang phục vụ ngón tay người dùng vuốt màn hình, "
        "luồng nào đang đọc file ngầm. Vì vậy, tầng ứng dụng không thể phó mặc cho hệ điều hành mà bắt buộc phải tự xây dựng bộ lập lịch thông minh cho riêng mình."
    )

    # --------------------------------------------------------------------------
    # SLIDE 3: BA HIỆN TƯỢNG TIÊU CỰC VÀ MINH CHỨNG THỰC TIỄN
    # --------------------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide3, COLOR_BG_LIGHT)
    add_header(slide3, "Ba Hiện Tượng Tiêu Cực Cản Trở Trải Nghiệm Người Dùng", "1. Đặt Vấn Đề")

    add_card_content(slide3, 0.8, 1.5, 3.6, 5.3, 
        title="1. Giật Lag Giao Diện (Jank)", 
        items=[
            "• Vượt ngân sách Vsync (16.67ms hoặc 8.33ms).",
            "• Bỏ lỡ khung hình (Frame Drop) hoặc nghiêm trọng hơn là đóng băng giao diện (Frozen Frame > 700ms).",
            "• Thao tác chạm bị khựng, hoạt ảnh loading dừng hẳn, gây ức chế tâm lý tương tác (HCI)."
        ],
        title_color=COLOR_RED_ALERT
    )

    add_card_content(slide3, 4.8, 1.5, 3.6, 5.3, 
        title="2. Bóp Xung Nhiệt (Thermal Throttling)", 
        items=[
            "• Các luồng nền chạy tối đa công suất làm nhiệt độ SoC tăng vọt (> 42°C - 45°C).",
            "• Cơ chế điều tần phần cứng (DVFS) cưỡng bức hạ một nửa xung nhịp CPU/GPU.",
            "• Toàn bộ ứng dụng bị kéo chậm dây chuyền, ngay cả thao tác cuộn nhẹ cũng bị giật."
        ],
        title_color=COLOR_AMBER_WARN
    )

    add_card_content(slide3, 8.8, 1.5, 3.7, 5.3, 
        title="3. Hao Tổn Năng Lượng & Nghẽn Bộ Nhớ", 
        items=[
            "• Theo Định luật Amdahl, tăng luồng vô tội vạ không tăng tốc vô hạn do bị nghẽn bus bộ nhớ.",
            "• Tranh chấp bộ nhớ đệm (Cache Thrashing) giữa các lõi CPU.",
            "• Thiết bị luôn hoạt động ở công suất đỉnh (Peak Power), gây hao pin nhanh mà không tăng hiệu năng."
        ],
        title_color=COLOR_CYAN_ACCENT
    )

    add_speaker_notes(slide3,
        "Ba hiện tượng này xuất hiện liên tục trong thực tế: từ việc giật lag giao diện (Jank), bóp xung do nhiệt "
        "khiến toàn máy chậm lại, đến việc hao tổn pin vô ích do tranh chấp bộ nhớ đệm theo định luật Amdahl. "
        "Khảo sát trên các ứng dụng bán hàng POS và thư viện ảnh cho thấy việc phân tích Excel hay giải mã ảnh nền làm đóng băng giao diện tới vài giây."
    )

    # --------------------------------------------------------------------------
    # SLIDE 4: MÔ HÌNH HÓA TOÁN HỌC BÀI TOÁN TỐI ƯU (MOOP)
    # --------------------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide4, COLOR_BG_LIGHT)
    add_header(slide4, "Mô Hình Hóa Toán Học Bài Toán Tối Ưu Đa Mục Tiêu (MOOP)", "2. Cơ Sở Khoa Học")

    add_card_content(slide4, 0.8, 1.5, 5.6, 5.3, 
        title="Véc-tơ Hàm Mục Tiêu Cần Tối Thiểu Hóa", 
        items=[
            "Phát biểu bài toán tối ưu đa mục tiêu tại thời điểm t:",
            "       min F(x) = [ f_jank(x),  f_latency(x),  f_overhead(x) ]^T",
            "",
            "• f_jank(x) = Pr(T_frame > T_budget): Tỷ lệ khung hình vượt ngân sách thời gian thực Vsync.",
            "• f_latency(x) = L_critical^(p95): Phân vị thứ 95 của độ trễ hoàn thành tác vụ khẩn cấp (Critical Tasks).",
            "• f_overhead(x) = E[tau_dispatch]: Kỳ vọng chi phí phụ tải điều phối và truyền thông điệp liên tiến trình (IPC)."
        ],
        title_color=COLOR_NAVY_BLUE
    )

    add_card_content(slide4, 6.8, 1.5, 5.7, 5.3, 
        title="Hệ Ràng Buộc Cứng và Mềm (Constraints)", 
        items=[
            "1. Ràng buộc Ngân sách Thời gian thực (Hard Frame Deadline):",
            "       T_frame <= 16.67 ms (60Hz) hoặc <= 8.33 ms (120Hz)",
            "       f_jank <= 2.0% và không có khung hình đóng băng > 700 ms.",
            "",
            "2. Ràng buộc Độ trễ Tương tác Con người (HCI Constraint):",
            "       L_critical^(p95) < 100 ms (ngưỡng phản hồi tức thì).",
            "",
            "3. Ràng buộc Đánh đổi Thông lượng Xử lý Nền (Throughput Trade-off):",
            "       Makespan(Adaptive) <= 1.30 * Makespan(FIFO)  (chậm tối đa 25-30%).",
            "",
            "4. Ràng buộc Công bằng (Starvation-Free): Không bỏ đói tác vụ nền."
        ],
        title_color=COLOR_GREEN_EMERALD
    )

    add_speaker_notes(slide4,
        "Đây là slide quan trọng thể hiện nền tảng học thuật của đề tài: Bài toán lập lịch được phát biểu là "
        "Bài toán Tối ưu hóa Đa mục tiêu (MOOP). Ta không tối ưu cảm tính mà giải quyết đồng thời 3 mục tiêu: "
        "giảm tỷ lệ rớt frame, giảm độ trễ tác vụ khẩn cấp, và tối thiểu phụ tải điều phối, dưới 4 ràng buộc thời gian thực ngặt nghèo."
    )

    # --------------------------------------------------------------------------
    # SLIDE 5: KIẾN TRÚC TỔNG THỂ HỆ THỐNG 5 PHÂN LỚP
    # --------------------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide5, COLOR_BG_LIGHT)
    add_header(slide5, "Kiến Trúc Tổng Thể Hệ Thống Lập Lịch Thích Ứng", "3. Thiết Kế Kiến Trúc")

    layers = [
        ("Tầng 1: Giao Diện Người Dùng (UI Layer)", "Main Isolate đơn luồng, quản lý cây Widget, lắng nghe thao tác chạm và phát yêu cầu vẽ hình."),
        ("Tầng 2: Giám Sát & Điều Khiển (Controller Layer)", "Quản lý chu trình thực nghiệm, kết nối Stack Monitor HUD hiển thị số liệu thời gian thực."),
        ("Tầng 3: Bộ Lập Lịch Thích Ứng Cốt Lõi (Scheduling Core)", "Hàng đợi phân tầng O(1), bộ tính Aging, bộ điều khiển AIMD, máy trạng thái FSA và Backpressure."),
        ("Tầng 4: Hồ Chứa Worker Nền Dài Hạn (Worker Pool Layer)", "W Worker Isolates sống lâu, giao tiếp hai chiều qua cổng SendPort/ReceivePort không sao chép."),
        ("Tầng 5: Tín Hiệu Cảm Biến Nền Tảng (Hardware Signals)", "FrameSignal (Persistent Callback) đo Vsync và MethodChannel đọc nhiệt độ/pin từ Android.")
    ]

    for idx, (l_title, l_desc) in enumerate(layers):
        y = 1.45 + idx * 1.05
        add_card(slide5, 0.8, y, 11.7, 0.95, bg_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER)
        # Colored badge on left
        badge = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(0.15), Inches(0.95))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_PRIMARY_BLUE if idx == 2 else (COLOR_CYAN_ACCENT if idx < 2 else COLOR_GREEN_EMERALD)
        badge.line.fill.background()

        tb = slide5.shapes.add_textbox(Inches(1.15), Inches(y + 0.1), Inches(11.2), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = l_title
        p_t.font.name = FONT_NAME_TITLE
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY_DARK

        p_d = tf.add_paragraph()
        p_d.text = l_desc
        p_d.font.name = FONT_NAME_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_TEXT_MUTED

    add_speaker_notes(slide5,
        "Kiến trúc hệ thống được phân lớp nghiêm ngặt thành 5 tầng. Trọng tâm là Tầng 3 - Bộ lập lịch thích ứng cốt lõi "
        "đóng vai trò 'bộ não' điều phối giữa luồng UI ở Tầng 1 và đội ngũ Worker Isolates ở Tầng 4, liên tục nhận tín hiệu phản hồi từ Tầng 5."
    )

    # --------------------------------------------------------------------------
    # SLIDE 6: HÀNG ĐỢI PHÂN CẤP O(1) & ĐỊNH LÝ CHỐNG BỎ ĐÓI
    # --------------------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide6, COLOR_BG_LIGHT)
    add_header(slide6, "Hàng Đợi Phân Tầng O(1) & Định Lý Chống Bỏ Đói (P2)", "3. Thiết Kế Kỹ Thuật")

    add_card_content(slide6, 0.8, 1.5, 5.6, 5.3, 
        title="Cấu Trúc Hàng Đợi 3 Làn O(1)", 
        items=[
            "• Phân loại 3 mức ưu tiên ngữ nghĩa:",
            "   - Critical (rank = 0): Thao tác chạm cần phản hồi < 100 ms.",
            "   - Visible (rank = 1): Tải dữ liệu vùng màn hình sắp cuộn tới.",
            "   - Background (rank = 2): Tính toán nặng ngầm (Excel, đồng bộ).",
            "",
            "• Cấu trúc 3 hàng đợi hai đầu (Deque) riêng biệt:",
            "   - Trong mỗi làn, tác vụ tự sắp xếp theo thứ tự đến (FIFO).",
            "   - Thuật toán chọn việc chỉ so sánh tối đa 3 đầu hàng.",
            "   - Độ phức tạp thời gian đạt mức tối ưu tuyệt đối: T = O(1).",
            "   - Hoạt động ổn định ngay cả khi hàng đợi có hàng nghìn tác vụ."
        ],
        title_color=COLOR_NAVY_BLUE
    )

    add_card_content(slide6, 6.8, 1.5, 5.7, 5.3, 
        title="Thuật Toán Aging & Định Lý Chống Bỏ Đói", 
        items=[
            "• Hàm chấm điểm ưu tiên hiệu dụng:",
            "       Score(i, t) = Rank(p_i) * tau_aging - (t - t_submit(i))",
            "   (Hằng số lão hóa tau_aging = 3000 ms; điểm càng nhỏ càng ưu tiên).",
            "",
            "• Định lý 3.1 (Tính Khả Hoàn Hữu Hạn):",
            "   Với mọi tác vụ nền t_bg, khi thời gian chờ tích lũy đạt:",
            "       t - t_0 >= 2 * tau_aging = 6000 ms (6 giây)",
            "   thì Score(t_bg, t) <= 0, vượt qua quyền ưu tiên của mọi tác vụ Critical mới đến.",
            "",
            "• Hệ quả: Đảm bảo về mặt toán học 100% tác vụ nền không bao giờ bị bỏ đói vô hạn (Zero Starvation)."
        ],
        title_color=COLOR_GREEN_EMERALD
    )

    add_speaker_notes(slide6,
        "Ở chính sách P2, nhóm áp dụng hai cơ chế toán học quan trọng: Hàng đợi 3 làn đạt độ phức tạp O(1) giúp Main Isolate "
        "chọn việc cực nhanh, và công thức Aging tính điểm thâm niên. Chúng em đã chứng minh bằng toán học rằng sau đúng 6 giây, "
        "tác vụ nền chắc chắn được chạy, triệt tiêu hoàn toàn nguy cơ Starvation."
    )

    # --------------------------------------------------------------------------
    # SLIDE 7: PHÂN MẢNH HỢP TÁC (CHUNK) & ĐIỂM NHƯỜNG LUỒNG
    # --------------------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide7, COLOR_BG_LIGHT)
    add_header(slide7, "Kỹ Thuật Phân Mảnh Hợp Tác Đa Nhiệm (P3)", "3. Thiết Kế Kỹ Thuật")

    add_card_content(slide7, 0.8, 1.5, 5.6, 5.3, 
        title="Giải Quyết Rào Cản Bất Khả Ngắt của Isolate", 
        items=[
            "• Rào cản cốt lõi của Dart VM:",
            "   - Isolate không hỗ trợ cơ chế ngắt cưỡng bức (Preemption).",
            "   - Worker đang chạy dở tác vụ nặng 1000ms thì không thể dừng ngang.",
            "",
            "• Giải pháp: Phân mảnh hợp tác (Cooperative Chunking):",
            "   - Băm nhỏ tác vụ thành chuỗi phân mảnh ngắn danh định: Delta t_chunk approx 80 ms.",
            "   - Máy trạng thái theo dõi: RemainingIters = TotalIters - DoneIters.",
            "   - Ranh giới giữa hai phân mảnh thiết lập Điểm Nhường Luồng (Yield Point Y).",
            "   - Tại điểm Y: Tác vụ Critical xuất hiện sẽ lập tức cướp worker để chen ngang thực thi!"
        ],
        title_color=COLOR_NAVY_BLUE
    )

    add_card_content(slide7, 6.8, 1.5, 5.7, 5.3, 
        title="Hiện Thực Phân Mảnh Trên Tác Vụ Ảnh 24MP", 
        items=[
            "• Thách thức thực tế: Xử lý 80 ảnh DSLR 24MP (6016x4016, 6-12MB/ảnh).",
            "• Giải pháp phân mảnh truy cập ngẫu nhiên (RandomAccessFile):",
            "   1. Header Chunk: Đọc 4 KB đầu tiên phân tích JPEG SOI/SOF, trích xuất kích thước ảnh mà không nạp bitmap.",
            "   2. Data Chunks: Mỗi chunk dịch con trỏ file, chỉ đọc tối đa 256 KB dữ liệu nhị phân, tính toán histogram 256 mức.",
            "   3. Đóng luồng an toàn: Khối lệnh try/finally giải phóng tài nguyên hệ điều hành ngay khi kết thúc chunk.",
            "",
            "• Đạt đồng thời 2 mục tiêu: Tái hiện đúng tải I/O thực tế và triệt tiêu nguy cơ tràn RAM (OOM)."
        ],
        title_color=COLOR_CYAN_ACCENT
    )

    add_speaker_notes(slide7,
        "Rào cản lớn nhất của Dart Isolate là không thể ép ngắt giữa chừng. Kỹ thuật Cooperative Chunking băm nhỏ tác vụ thành các lát 80ms. "
        "Cứ hết một lát là một Yield Point để việc Critical chen ngang. Nhóm đã hiện thực hóa kỹ thuật này trực tiếp trên tác vụ đọc file ảnh thật 24MP "
        "bằng cách cắt lát đọc đĩa 256KB, vừa tạo tải I/O thật vừa chống tràn RAM."
    )

    # --------------------------------------------------------------------------
    # SLIDE 8: CRITICAL WORKER RESERVE & FRAME YIELDING
    # --------------------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide8, COLOR_BG_LIGHT)
    add_header(slide8, "Dự Trữ Worker Chuyên Biệt ($P_{3r}$) & Nhường Nhịp Dựng Hình ($P_3$)", "3. Thiết Kế Kỹ Thuật")

    add_card_content(slide8, 0.8, 1.5, 5.6, 5.3, 
        title="Dự Trữ Worker Chuyên Biệt ($P_{3r}$)", 
        items=[
            "• Vấn đề: Dù có Chunking, ở thời điểm bão tải, cả W worker đều có thể đang chạy dở chunk nền.",
            "• Quy tắc ràng buộc cấp phát thép:",
            "       N_non_critical(t) <= min( N_cap(t), W_total - 1 )",
            "",
            "• Luôn bảo toàn ít nhất 1 Worker dự phòng độc quyền cho tác vụ Critical.",
            "• Kết quả thực nghiệm:",
            "   - Chỉ dùng Chunking (P3c): Critical latency vẫn còn ~44.8 giây.",
            "   - Bổ sung Ghế Reserve (P3r): Độ trễ lập tức giảm gần 1.000 lần xuống còn 49.0 ms (< 100ms)!"
        ],
        title_color=COLOR_GREEN_EMERALD
    )

    add_card_content(slide8, 6.8, 1.5, 5.7, 5.3, 
        title="Cơ Chế Nhường Nhịp Dựng Hình (Frame Yielding)", 
        items=[
            "• Cảm biến FrameSignal (Persistent Callback):",
            "   - Đo lường khoảng cách khung hình g(t) trên cửa sổ 30 frame.",
            "",
            "• Bộ điều khiển nhường luồng trễ ngưỡng (Hysteresis):",
            "   - Bật nhường luồng (State_busy = 1 / ● YIELDING): Khi g_p95 > 20 ms (lỡ nhịp Vsync 16.67ms).",
            "   - Hủy nhường luồng: Chỉ khi g_p95 hạ sâu dưới 16 ms (0.8 * 20ms).",
            "",
            "• Hành động điều phối: Tạm dừng phát sinh phân mảnh Background, nhường 100% CPU cho luồng UI và GPU.",
            "• Trần hoãn (Defer Cap = 8s): Không hoãn việc nền quá 8 giây."
        ],
        title_color=COLOR_AMBER_WARN
    )

    add_speaker_notes(slide8,
        "Hai đóng góp then chốt của P3: Thứ nhất là Critical Worker Reserve - luôn khóa trống 1 ghế VIP trong pool. "
        "Số liệu thực nghiệm chứng minh kỹ thuật này kéo giảm độ trễ chạm từ 44 giây xuống 49 mili-giây. "
        "Thứ hai là Frame Yielding - khi cảm biến thấy khung hình trễ nhịp 20ms, đèn YIELDING bật sáng hoãn ngay việc nền để cứu UI."
    )

    # --------------------------------------------------------------------------
    # SLIDE 9: ĐIỀU KHIỂN PHẢN HỒI THÍCH ỨNG AIMD & BACKPRESSURE (P4)
    # --------------------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide9, COLOR_BG_LIGHT)
    add_header(slide9, "Điều Khiển Thích Ứng AIMD & Giảm Tải Ngược Backpressure (P4)", "3. Thiết Kế Kỹ Thuật")

    add_card_content(slide9, 0.8, 1.5, 5.6, 5.3, 
        title="Thuật Toán Phản Hồi Thích Ứng AIMD", 
        items=[
            "• Động học điều khiển vòng kín (Epoch 500ms):",
            "   - Pha Phanh Khẩn Cấp (Multiplicative Decrease):",
            "       Khi g_p95 > 20 ms => Workers = max(1, floor(Workers * 0.5))",
            "       Cắt giảm ngay 50% worker nền giải phóng CPU (ổ khóa vàng 🔒).",
            "   - Pha Tăng Trưởng Thận Trọng (Additive Increase):",
            "       Khi g_p95 <= 16 ms => Workers = min(W_max, Workers + 1)",
            "       Tăng từ từ từng worker một khi giao diện ổn định.",
            "",
            "• Nguyên lý miễn trừ: Tác vụ Critical hoàn toàn không bị giới hạn bởi trần worker của AIMD."
        ],
        title_color=COLOR_NAVY_BLUE
    )

    add_card_content(slide9, 6.8, 1.5, 5.7, 5.3, 
        title="Định Luật Little & Giảm Tải Ngược Backpressure", 
        items=[
            "• Cân bằng hàng đợi theo Định luật Little: E[L] = lambda * E[W].",
            "   Khi tải đến bùng nổ, hàng đợi tăng vô hạn gây tràn RAM sập app (OOM).",
            "",
            "• Cơ chế Xả Tải Có Chọn Lọc (Selective Load Shedding):",
            "   - Ngưỡng an toàn: L_threshold = max(20, W_total * 10).",
            "   - Tuyệt đối KHÔNG BAO GIỜ hủy tác vụ Critical.",
            "   - Loại bỏ các tác vụ Background quá hạn thị giác (Stale Work Elimination) khi người dùng đã cuộn qua.",
            "",
            "• Máy trạng thái nhiệt/pin (FSA): Normal -> Conserve -> Critical với trễ Hysteresis 5 giây chống chập chờn."
        ],
        title_color=COLOR_RED_ALERT
    )

    add_speaker_notes(slide9,
        "Ở chính sách tối cao P4, hệ thống trang bị thuật toán AIMD: khi máy chớm trễ nhịp 20ms, thuật toán lập tức cắt giảm 50% worker "
        "để phanh khẩn cấp cứu UI. Đồng thời, theo Định luật Little, khi hàng đợi quá tải, cơ chế Backpressure chủ động xả tải các việc nền cũ hết hạn "
        "để bảo vệ RAM và không bao giờ hủy việc Critical."
    )

    # --------------------------------------------------------------------------
    # SLIDE 10: MA TRẬN ĐỐI CHIẾU 5 CHÍNH SÁCH LẬP LỊCH
    # --------------------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide10, COLOR_BG_LIGHT)
    add_header(slide10, "Ma Trận Đối Chiếu Khoa Học 5 Chính Sách Lập Lịch", "3. Thiết Kế Kiến Trúc")

    # Add table
    rows_p = [
        ["P0: Main Isolate", "Main Isolate (Luồng UI)", "FIFO đơn cấp", "Tuần tự hóa Event Loop", "Tê liệt hoàn toàn khi có tính toán nặng"],
        ["P1: Pool Tĩnh FIFO", "Worker Pool tĩnh (W Isolate)", "FIFO đơn cấp", "Tái sử dụng Isolate, IPC SendPort", "Không thích ứng; nghẽn đầu hàng và tranh chấp CFS"],
        ["P2: Ưu tiên & Aging", "Worker Pool tĩnh (W Isolate)", "Hàng đợi 3 mức O(1)", "Thuật toán Aging thâm niên Score(i,t)", "Bảo đảm toán học không bỏ đói (Starvation-Free)"],
        ["P3: Phân mảnh & Nhường", "Worker Pool tĩnh (W Isolate)", "3 mức + Ghế Reserve", "Chunking 80ms, Yielding theo Vsync", "Nhường nhịp khung hình khi khoảng cách frame > 20ms"],
        ["P4: Thích ứng Toàn diện", "Worker Pool động tự co giãn", "3 mức + Backpressure", "AIMD (+1 / ×0.5), Stale Load Shedding", "Máy trạng thái FSA 3 chế độ kèm trễ Hysteresis 5s"]
    ]

    tbl_shape = slide10.shapes.add_table(6, 5, Inches(0.8), Inches(1.6), Inches(11.73), Inches(5.1))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.2)
    tbl.columns[1].width = Inches(2.3)
    tbl.columns[2].width = Inches(2.0)
    tbl.columns[3].width = Inches(2.6)
    tbl.columns[4].width = Inches(2.63)

    headers = ["Chính sách", "Không gian Thực thi", "Hàng đợi", "Kỹ thuật Cốt lõi", "Cơ chế Thích ứng Môi trường"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_NAVY_BLUE
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_NAME_TITLE
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        p.alignment = PP_ALIGN.CENTER

    for r_idx, r_data in enumerate(rows_p):
        for c_idx, val in enumerate(r_data):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0xF1, 0xF5, 0xF9) if r_idx % 2 == 1 else RGBColor(0xFF, 0xFF, 0xFF)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_NAME_BODY
            p.font.size = Pt(10.5)
            p.font.color.rgb = COLOR_TEXT_MAIN
            if c_idx == 0:
                p.font.bold = True

    add_speaker_notes(slide10,
        "Bảng ma trận này tóm tắt trọn vẹn sự tiến hóa kiến trúc từ P0 đến P4. P0 phơi bày vấn đề đơn luồng; "
        "P1 dùng pool nhưng mắc lỗi FIFO; P2 giải quyết thứ tự nhưng thiếu điểm nhường; P3 là bước đột phá kết hợp "
        "Chunking và Worker Reserve; và P4 là giải pháp hoàn chỉnh với AIMD và Backpressure tự lái."
    )

    # --------------------------------------------------------------------------
    # SLIDE 11: THIẾT LẬP THỰC NGHIỆM CHUẨN HÓA
    # --------------------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide11, COLOR_BG_LIGHT)
    add_header(slide11, "Thiết Lập Môi Trường Thực Nghiệm Chuẩn Hóa", "4. Thực Nghiệm Định Lượng")

    add_card_content(slide11, 0.8, 1.5, 5.6, 5.3, 
        title="Hai Thế Hệ Thiết Bị Thử Nghiệm", 
        items=[
            "• Thiết bị 1 (Phổ thông Giá rẻ — Baseline Device):",
            "   - Model: Samsung Galaxy A04e (SM-A042F).",
            "   - SoC: MediaTek Helio P35 (8 nhân Cortex-A53, 2.3 GHz).",
            "   - RAM: 2 GB (khả dụng ~700 MB) — Android 14.",
            "   - Màn hình: Chuẩn 60 Hz (Ngân sách Vsync: 16.67 ms).",
            "",
            "• Thiết bị 2 (Tầm trung Thế hệ mới — Cross-device):",
            "   - Model: Xiaomi Redmi Note 13.",
            "   - SoC: MediaTek Helio G99 (2 nhân A76 + 6 nhân A55).",
            "   - RAM: 6 GB — Android 15.",
            "   - Màn hình: Tần số quét cao 120 Hz (Ngân sách Vsync: 8.33 ms)."
        ],
        title_color=COLOR_NAVY_BLUE
    )

    add_card_content(slide11, 6.8, 1.5, 5.7, 5.3, 
        title="Quy Trình Đo Lường & Phương Pháp Thống Kê", 
        items=[
            "• Chế độ biên dịch: Profile AOT mode (Ahead-of-Time compilation) tắt hoàn toàn debug assertions.",
            "",
            "• Chu trình chuẩn hóa tự động hóa:",
            "   - Nghỉ ổn định thiết bị (10s) -> Làm nóng Warm-up (10s không ghi nhận) -> Đo chính thức (60s) -> Xuất CSV & Metadata nhiệt/pin -> Nghỉ nguội giữa các run.",
            "",
            "• Phương pháp xử lý dữ liệu:",
            "   - Sử dụng Trung vị (Median), Khoảng tứ phân vị (IQR) và Phân vị p95 do dữ liệu lệch đuôi dài.",
            "   - Kiểm định giả thuyết phi tham số Mann-Whitney U test với mức ý nghĩa chuẩn alpha = 0.05."
        ],
        title_color=COLOR_GREEN_EMERALD
    )

    add_speaker_notes(slide11,
        "Về phương pháp luận thực nghiệm: Toàn bộ số liệu đều được đo lường tự động trên phần cứng thật gồm hai thái cực: "
        "máy yếu Samsung Galaxy A04e chip Helio P35 RAM 2GB màn 60Hz, và máy mạnh Redmi Note 13 màn 120Hz ngân sách chỉ 8.33ms. "
        "Mọi kết luận đều được bảo đảm bằng kiểm định thống kê phi tham số Mann-Whitney U."
    )

    # --------------------------------------------------------------------------
    # SLIDE 12: KIỂM CHỨNG GIẢ THUYẾT H1 & H3 (KỊCH BẢN TẢI BÃO HÒA S1)
    # --------------------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide12, COLOR_BG_LIGHT)
    add_header(slide12, "Kiểm Chứng Giả Thuyết H1 & H3 Trên Kịch Bản Bão Hòa S1", "4. Thực Nghiệm Định Lượng")

    # Add 2 images side-by-side
    img1 = "figures/fig1_s1_tradeoff.png"
    img4 = "figures/fig4_ablation_s1.png"
    if os.path.exists(img1):
        slide12.shapes.add_picture(img1, Inches(0.8), Inches(1.5), width=Inches(5.7))
    if os.path.exists(img4):
        slide12.shapes.add_picture(img4, Inches(6.8), Inches(1.5), width=Inches(5.7))

    # Bottom summary card
    add_card(slide12, 0.8, 5.5, 11.7, 1.6, bg_color=COLOR_CARD_BG, border_color=COLOR_PRIMARY_BLUE)
    tb_res = slide12.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.3), Inches(1.4))
    tf_res = tb_res.text_frame
    tf_res.word_wrap = True
    p_h1 = tf_res.paragraphs[0]
    p_h1.text = "• CHẤP NHẬN H1 (P0 vs P1): P0 rớt 90.8% frame, giao diện tê liệt (gap p95 = 419ms). Chuyển sang P1 giảm rớt xuống 23.2% (U = 16.0, p = 0.014)."
    p_h1.font.bold = True
    p_h1.font.size = Pt(11)
    p_h1.font.color.rgb = COLOR_TEXT_MAIN

    p_h3 = tf_res.add_paragraph()
    p_h3.text = "• CHẤP NHẬN H3 (P1 vs P3): P3 đưa tỷ lệ rớt frame về 0.8% (mượt ngang baseline không tải 0.9%), kéo giảm độ trễ Critical từ 35.4 giây xuống 31.0 ms (nhanh hơn 1.140 lần, U = 16.0, p = 0.014)."
    p_h3.font.bold = True
    p_h3.font.size = Pt(11)
    p_h3.font.color.rgb = COLOR_GREEN_EMERALD

    p_abl = tf_res.add_paragraph()
    p_abl.text = "• Phân rã Ablation: Chunking (P3c) giải quyết triệt để rớt frame (22.2% -> 0.8%); Ghế dự phòng Reserve (P3r) giải quyết độ trễ Critical (44.8s -> 49ms)."
    p_abl.font.size = Pt(10.5)
    p_abl.font.color.rgb = COLOR_TEXT_MUTED

    add_speaker_notes(slide12,
        "Kết quả Kịch bản S1 ủng hộ mạnh mẽ hai giả thuyết H1 và H3. Biểu đồ bên trái chỉ ra sự đánh đổi Pareto: P0 tê liệt, "
        "P1 giảm rớt frame nhưng độ trễ Critical vẫn vọt lên 35 giây. P3 nằm ở góc tối ưu hoàn hảo: rớt frame chỉ 0.8% và Critical chỉ 31ms. "
        "Biểu đồ bên phải bóc tách Ablation chứng minh vai trò then chốt của Chunking và Ghế Reserve."
    )

    # --------------------------------------------------------------------------
    # SLIDE 13: KIỂM CHỨNG GIẢ THUYẾT H4 (KỊCH BẢN TẢI BIẾN ĐỘNG S2)
    # --------------------------------------------------------------------------
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide13, COLOR_BG_LIGHT)
    add_header(slide13, "Kiểm Chứng Giả Thuyết H4 Trên Kịch Bản Tải Biến Động S2", "4. Thực Nghiệm Định Lượng")

    img2 = "figures/fig2_s2_comparison.png"
    img3 = "figures/fig3_timeline_frames.png"
    if os.path.exists(img2):
        slide13.shapes.add_picture(img2, Inches(0.8), Inches(1.5), width=Inches(6.2))
    if os.path.exists(img3):
        slide13.shapes.add_picture(img3, Inches(7.2), Inches(1.5), width=Inches(5.3))

    add_card(slide13, 0.8, 5.5, 11.7, 1.6, bg_color=COLOR_CARD_BG, border_color=COLOR_GREEN_EMERALD)
    tb_s2 = slide13.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.3), Inches(1.4))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True
    p_s2_1 = tf_s2.paragraphs[0]
    p_s2_1.text = "• CHẤP NHẬN H4 (P4 vs P3): Dưới tải bậc thang tăng vọt đến 2.0x, AIMD phanh worker giúp P4 giảm jank hơn 3 lần so với P3 (từ 24.8% xuống 8.0%, p = 0.050)."
    p_s2_1.font.bold = True
    p_s2_1.font.size = Pt(11)
    p_s2_1.font.color.rgb = COLOR_TEXT_MAIN

    p_s2_2 = tf_s2.add_paragraph()
    p_s2_2.text = "• Bảo toàn Độ trễ Critical 28.0 ms: Nhờ quy tắc miễn trừ, tác vụ tương tác ở P4 đạt phản hồi nhanh nhất toàn diện (nhanh hơn P1 169 lần)."
    p_s2_2.font.bold = True
    p_s2_2.font.size = Pt(11)
    p_s2_2.font.color.rgb = COLOR_PRIMARY_BLUE

    p_s2_3 = tf_s2.add_paragraph()
    p_s2_3.text = "• Rút ngắn Makespan gần 10 giây: Cơ chế Backpressure loại bỏ 1.990 tác vụ nền hết hạn, chống tràn RAM và giúp hoàn thành sớm ở 67.8 giây."
    p_s2_3.font.size = Pt(10.5)
    p_s2_3.font.color.rgb = COLOR_TEXT_MUTED

    add_speaker_notes(slide13,
        "Ở kịch bản tải bậc thang S2, giả thuyết H4 được khẳng định: Khi tải tăng vọt 2.0x, P3 bị giật tới 24.8% do cố duy trì 8 worker. "
        "Thuật toán AIMD của P4 phanh worker giúp giảm jank 3 lần xuống 8.0%, đưa độ trễ Critical về 28ms kỷ lục, "
        "và cơ chế xả tải Backpressure loại bỏ các tác vụ quá hạn giúp ứng dụng hoàn thành sớm hơn 10 giây."
    )

    # --------------------------------------------------------------------------
    # SLIDE 14: KHÁI QUÁT HÓA LIÊN THIẾT BỊ & TÁC VỤ ẢNH 24MP
    # --------------------------------------------------------------------------
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide14, COLOR_BG_LIGHT)
    add_header(slide14, "Đánh Giá Khái Quát Hóa Liên Thiết Bị & Tác Vụ Ảnh Thật", "4. Thực Nghiệm Định Lượng")

    img5 = "figures/fig5_cross_device_comparison.png"
    img6 = "figures/fig6_s_image_real_workload.png"
    if os.path.exists(img5):
        slide14.shapes.add_picture(img5, Inches(0.8), Inches(1.5), width=Inches(5.7))
    if os.path.exists(img6):
        slide14.shapes.add_picture(img6, Inches(6.8), Inches(1.5), width=Inches(5.7))

    add_card(slide14, 0.8, 5.5, 11.7, 1.6, bg_color=COLOR_CARD_BG, border_color=COLOR_CYAN_ACCENT)
    tb_c = slide14.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.3), Inches(1.4))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p_c1 = tf_c.paragraphs[0]
    p_c1.text = "• Khái quát hóa Màn hình 120Hz (Redmi Note 13): Ngân sách siết chặt 8.33ms. P1 rớt tới 61.6% frame; P3 duy trì 1.21% rớt frame (ngang baseline 1.19%) và P4 dập tắt jank về 0.03%, giảm trễ Critical 2.180 lần."
    p_c1.font.bold = True
    p_c1.font.size = Pt(11)
    p_c1.font.color.rgb = COLOR_TEXT_MAIN

    p_c2 = tf_c.add_paragraph()
    p_c2.text = "• Tác vụ Ảnh thật 24MP (s_image): P4 đạt 510 frames (tiệm cận baseline không tải 550 frames), giảm frame p95 từ 747ms xuống 154ms, và hạ Critical từ 35.7 giây xuống 286 ms (nhanh hơn 125 lần)."
    p_c2.font.bold = True
    p_c2.font.size = Pt(11)
    p_c2.font.color.rgb = COLOR_GREEN_EMERALD

    add_speaker_notes(slide14,
        "Hai kiểm chứng thực tế quan trọng: Thứ nhất, khi đưa lên màn hình 120Hz của Redmi Note 13 với ngân sách chỉ 8.33ms, "
        "P3 và P4 vẫn mượt mà tuyệt đối, bác bỏ nguy cơ overfitting trên một thiết bị. Thứ hai, thực nghiệm trên 80 ảnh DSLR 24MP "
        "chứng minh P4 giảm độ trễ chạm 125 lần và phục hồi số frame tiệm cận mức không tải."
    )

    # --------------------------------------------------------------------------
    # SLIDE 15: MINH CHỨNG TRỰC QUAN THỜI GIAN THỰC QUA HUD
    # --------------------------------------------------------------------------
    slide15 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide15, COLOR_BG_LIGHT)
    add_header(slide15, "Minh Chứng Trực Quan Thời Gian Thực Qua Stack Monitor HUD", "4. Thực Nghiệm Định Lượng")

    # Add 3 HUD screenshots
    hud0 = "figures/hud_v2_p0.png"
    hud3 = "figures/hud_v2_p3.png"
    hud4 = "figures/hud_v2_p4.png"
    if os.path.exists(hud0):
        slide15.shapes.add_picture(hud0, Inches(0.8), Inches(1.5), height=Inches(4.6))
    if os.path.exists(hud3):
        slide15.shapes.add_picture(hud3, Inches(4.8), Inches(1.5), height=Inches(4.6))
    if os.path.exists(hud4):
        slide15.shapes.add_picture(hud4, Inches(8.8), Inches(1.5), height=Inches(4.6))

    add_card(slide15, 0.8, 6.25, 3.6, 0.9, bg_color=RGBColor(0xFE, 0xF2, 0xF2), border_color=COLOR_RED_ALERT)
    tb_h0 = slide15.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(3.4), Inches(0.8))
    tb_h0.text_frame.word_wrap = True
    p_h0 = tb_h0.text_frame.paragraphs[0]
    p_h0.text = "P0: 10 FPS · Miss 84.3%\n40 cột đỏ vọt vạch 16.7ms · Đơ spinner"
    p_h0.font.size = Pt(10)
    p_h0.font.bold = True
    p_h0.font.color.rgb = COLOR_RED_ALERT

    add_card(slide15, 4.8, 6.25, 3.6, 0.9, bg_color=RGBColor(0xEC, 0xFD, 0xF5), border_color=COLOR_GREEN_EMERALD)
    tb_h3 = slide15.shapes.add_textbox(Inches(4.9), Inches(6.3), Inches(3.4), Inches(0.8))
    tb_h3.text_frame.word_wrap = True
    p_h3 = tb_h3.text_frame.paragraphs[0]
    p_h3.text = "P3: 60 FPS · ● YIELDING\nCột xanh dưới vạch 16.7ms · Frame 7.6ms"
    p_h3.font.size = Pt(10)
    p_h3.font.bold = True
    p_h3.font.color.rgb = COLOR_GREEN_EMERALD

    add_card(slide15, 8.8, 6.25, 3.7, 0.9, bg_color=RGBColor(0xEE, 0xF2, 0xFF), border_color=COLOR_PRIMARY_BLUE)
    tb_h4 = slide15.shapes.add_textbox(Inches(8.9), Inches(6.3), Inches(3.5), Inches(0.8))
    tb_h4.text_frame.word_wrap = True
    p_h4 = tb_h4.text_frame.paragraphs[0]
    p_h4.text = "P4: 60 FPS · Khóa 3 worker 🔒\nDrop 938 task cứu RAM · Crit 85ms"
    p_h4.font.size = Pt(10)
    p_h4.font.bold = True
    p_h4.font.color.rgb = COLOR_PRIMARY_BLUE

    add_speaker_notes(slide15,
        "Để Thầy Cô quan sát trực quan nhất, nhóm phát triển bảng HUD kính mờ hiển thị trực tiếp: "
        "Bên trái là P0 bị sập xuống 10 FPS, 40 cột đỏ rực vượt ngân sách; Ở giữa là P3 với đèn vàng YIELDING bật sáng, "
        "toàn bộ cột xanh ngọc dưới vạch 16.7ms; Bên phải là P4 dưới tải 16x tự động khóa 3 worker hiện ổ khóa vàng và xả tải 938 task."
    )

    # --------------------------------------------------------------------------
    # SLIDE 16: [SÂN KHẤU CHUYỂN TIẾP] LIVE DEMO TRỰC TIẾP
    # --------------------------------------------------------------------------
    slide16 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide16, COLOR_NAVY_DARK)

    top_badge = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.5), Inches(0.8), Inches(4.333), Inches(0.5))
    top_badge.fill.solid()
    top_badge.fill.fore_color.rgb = COLOR_PRIMARY_BLUE
    top_badge.line.fill.background()
    p_tb = top_badge.text_frame.paragraphs[0]
    p_tb.text = "THỰC NGHIỆM TRỰC TIẾP TRÊN THIẾT BỊ"
    p_tb.font.name = FONT_NAME_TITLE
    p_tb.font.size = Pt(12)
    p_tb.font.bold = True
    p_tb.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p_tb.alignment = PP_ALIGN.CENTER

    tb_live = slide16.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.3), Inches(1.2))
    tf_live = tb_live.text_frame
    p_lt = tf_live.paragraphs[0]
    p_lt.text = "CHUYỂN SANG SÂN KHẤU LIVE DEMO (SPLIT-SCREEN)"
    p_lt.font.name = FONT_NAME_TITLE
    p_lt.font.size = Pt(26)
    p_lt.font.bold = True
    p_lt.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p_lt.alignment = PP_ALIGN.CENTER

    demo_steps = [
        ("Phím 1: P0 (Main Isolate)", "Phơi bày thảm họa đơn luồng: Vòng xoay đơ khựng, FPS tụt còn 10, biểu đồ 40 cột đỏ rực."),
        ("Phím 2: P1 (Fixed Pool FIFO)", "Hết đơ cứng >700ms nhưng nghẽn đầu hàng FIFO khiến tác vụ chạm Critical trễ hàng chục giây."),
        ("Phím 3: P3 (Chunk + Yield)", "Bước ngoặt hiệu năng: Đèn YIELDING bật sáng, biểu đồ hạ thành cột xanh 60 FPS, Frame time 7.6ms."),
        ("Phím 4: P4 (AIMD + Backpressure)", "Tải bùng nổ 16x: AIMD khóa 3 worker (1/1 khóa 3), xả tải Drop cứu RAM, giữ vững 60 FPS và Crit 85ms.")
    ]

    for idx, (d_title, d_desc) in enumerate(demo_steps):
        y = 2.9 + idx * 1.05
        add_card(slide16, 1.2, y, 10.9, 0.92, bg_color=RGBColor(0x1E, 0x29, 0x3B), border_color=RGBColor(0x33, 0x41, 0x55))
        badge = slide16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(y), Inches(0.15), Inches(0.92))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_RED_ALERT if idx == 0 else (COLOR_AMBER_WARN if idx == 1 else (COLOR_GREEN_EMERALD if idx == 2 else COLOR_PRIMARY_BLUE))
        badge.line.fill.background()

        tb = slide16.shapes.add_textbox(Inches(1.5), Inches(y + 0.08), Inches(10.4), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = d_title
        p_t.font.name = FONT_NAME_TITLE
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_CYAN_ACCENT

        p_d = tf.add_paragraph()
        p_d.text = d_desc
        p_d.font.name = FONT_NAME_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)

    add_speaker_notes(slide16,
        "[ĐÂY LÀ ĐIỂM CHUYỂN SANG MÀN HÌNH LIVE DEMO - THỜI LƯỢNG 3-4 PHÚT]\n"
        "Em xin phép chuyển sang cửa sổ Live Demo trực tiếp ngay trên thiết bị qua công cụ demo.bat. "
        "Em sẽ lần lượt bấm 4 phím: Phím 1 (P0), Phím 2 (P1), Phím 3 (P3) và Phím 4 (P4) để Thầy Cô tận mắt nhìn thấy "
        "bằng chứng hoạt động của từng kỹ thuật và sự thay đổi tức thì của các chỉ số trên Stack Monitor HUD."
    )

    # --------------------------------------------------------------------------
    # SLIDE 17: KẾT LUẬN & ĐÓNG GÓP CHÍNH
    # --------------------------------------------------------------------------
    slide17 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide17, COLOR_BG_LIGHT)
    add_header(slide17, "Kết Luận & Các Đóng Góp Chính Của Đề Tài", "5. Kết Luận")

    add_card_content(slide17, 0.8, 1.5, 5.6, 5.3, 
        title="Các Đóng Góp Khoa Học Cốt Lõi", 
        items=[
            "1. Mô hình hóa Toán học Bài toán Lập lịch Đa mục tiêu:",
            "   - Chỉ rõ nghịch lý 'mù ngữ nghĩa' của nhân Linux CFS.",
            "   - Chứng minh toán học Định lý Chống Bỏ Đói (Starvation-Free Theorem) thông qua giải thuật Aging.",
            "",
            "2. Đột phá Kiến trúc Bộ Lập lịch Thích ứng 5 Cấp độ:",
            "   - Giải quyết triệt để tính bất khả ngắt của Dart Isolate bằng Cooperative Chunking (80ms).",
            "   - Thiết lập cơ chế Critical Worker Reserve bảo vệ thao tác chạm.",
            "   - Ứng dụng điều khiển thích ứng AIMD vòng kín kết hợp xả tải Backpressure và máy trạng thái nhiệt/pin.",
            "",
            "3. Chi phí Phụ tải Vi mô Cực Thấp (Microbenchmark E3):",
            "   - Độ trễ điều phối IPC p50 chỉ 0.34 ms (~2.0% ngân sách frame 16.7ms)."
        ],
        title_color=COLOR_NAVY_BLUE
    )

    add_card_content(slide17, 6.8, 1.5, 5.7, 5.3, 
        title="Đóng Góp Thực Tiễn & Hướng Phát Triển", 
        items=[
            "• Bộ Dữ Liệu Thực Nghiệm Chuẩn Mực:",
            "   - Kiểm chứng trên phần cứng thật (Galaxy A04e 60Hz và Redmi Note 13 120Hz).",
            "   - Xác nhận bằng kiểm định phi tham số Mann-Whitney U (p < 0.05): Rớt frame giảm từ 23.2% xuống 0.8%, độ trễ Critical giảm từ 35.4s xuống 28ms (nhanh hơn 1.200 lần).",
            "",
            "• Kiểm chứng Tác vụ Đa Phương tiện Thực tế:",
            "   - Hoạt động ổn định trên bộ 80 ảnh DSLR 24MP và Stack Monitor HUD.",
            "",
            "• Hướng Nghiên Cứu Tiếp Theo:",
            "   1. Đóng gói thành package mã nguồn mở độc lập trên pub.dev.",
            "   2. Ứng dụng TinyML trên NPU di động để dự đoán tải động."
        ],
        title_color=COLOR_GREEN_EMERALD
    )

    add_speaker_notes(slide17,
        "Tóm lại, đề tài đã giải quyết thành công bài toán tối ưu hóa đa mục tiêu bằng kiến trúc bộ lập lịch thích ứng. "
        "Chúng em đã mang lại cả đóng góp về mặt lý thuyết mô hình hóa toán học, lẫn đóng góp thực nghiệm vững chắc trên phần cứng thật "
        "với chi phí phụ tải điều phối chỉ chiếm 2% ngân sách khung hình."
    )

    # --------------------------------------------------------------------------
    # SLIDE 18: LỜI CẢM ƠN & PHIÊN PHẢN BIỆN Q&A
    # --------------------------------------------------------------------------
    slide18 = prs.slides.add_slide(blank_layout)
    set_slide_background_color(slide18, COLOR_NAVY_DARK)

    tb_qa = slide18.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.3), Inches(2.2))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True

    p_thx = tf_qa.paragraphs[0]
    p_thx.text = "XIN TRÂN TRỌNG CẢM ƠN THẦY CÔ VÀ HỘI ĐỒNG!"
    p_thx.font.name = FONT_NAME_TITLE
    p_thx.font.size = Pt(28)
    p_thx.font.bold = True
    p_thx.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    p_thx.alignment = PP_ALIGN.CENTER
    p_thx.space_after = Pt(16)

    p_qa = tf_qa.add_paragraph()
    p_qa.text = "PHIÊN THẢO LUẬN & TRẢ LỜI CÂU HỎI PHẢN BIỆN (Q&A)"
    p_qa.font.name = FONT_NAME_BODY
    p_qa.font.size = Pt(18)
    p_qa.font.bold = True
    p_qa.font.color.rgb = COLOR_CYAN_ACCENT
    p_qa.alignment = PP_ALIGN.CENTER

    add_card(slide18, 2.0, 4.6, 9.3, 1.8, bg_color=RGBColor(0x1E, 0x29, 0x3B), border_color=RGBColor(0x33, 0x41, 0x55))
    tb_hint = slide18.shapes.add_textbox(Inches(2.2), Inches(4.75), Inches(8.9), Inches(1.5))
    tf_hint = tb_hint.text_frame
    tf_hint.word_wrap = True
    p_h = tf_hint.paragraphs[0]
    p_h.text = "Nhóm đã chuẩn bị sẵn sàng dữ liệu và phân tích chuyên sâu cho các chủ đề:"
    p_h.font.size = Pt(12)
    p_h.font.bold = True
    p_h.font.color.rgb = COLOR_CYAN_ACCENT
    p_h.space_after = Pt(6)

    hints = [
        "• Hàm mục tiêu & Hệ ràng buộc MOOP · Chi phí IPC và phụ tải điều phối microbenchmark",
        "• Tại sao Scheduler tầng ứng dụng ưu việt hơn 'nice' của Linux CFS · Cơ sở toán học chọn chunk 80ms",
        "• Tính hợp lệ của xả tải Backpressure Stale Work · Ứng xử với thư viện nguyên khối FFI C/C++"
    ]
    for h in hints:
        p_it = tf_hint.add_paragraph()
        p_it.text = h
        p_it.font.size = Pt(11)
        p_it.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)

    add_speaker_notes(slide18,
        "Em xin chân thành cảm ơn Quý Thầy Cô và Hội đồng đã chú ý lắng nghe bài thuyết trình của nhóm. "
        "Chúng em rất mong nhận được những đóng góp quý báu và xin sẵn sàng lắng nghe, trả lời các câu hỏi phản biện từ Hội đồng ạ."
    )

    out_file = "slide_thuyet_trinh.pptx"
    prs.save(out_file)
    print(f"Đã lưu thành công bộ slide thuyết trình tại: {out_file}")

if __name__ == '__main__':
    build_presentation()
