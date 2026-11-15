# -*- coding: utf-8 -*-
"""
Script xây dựng toàn bộ Chương 3, Chương 4, Chương 5 và Tài liệu tham khảo
chèn trực tiếp vào file báo cáo bc.docx, bao gồm đầy đủ bảng biểu số liệu,
công thức toán học, phân tích chuyên sâu và các hình ảnh đồ thị thực nghiệm 300 DPI.
"""

import os
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

DOC_IN = 'bc_backup.docx'
DOC_OUT = 'bc.docx'

def setup_paragraph(p, space_before=60, space_after=60, line_spacing=288, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    sp = parse_xml(f'<w:spacing {nsdecls("w")} w:before="{space_before}" w:after="{space_after}" w:line="{line_spacing}" w:lineRule="auto"/>')
    pPr.append(sp)

def add_h1(doc, text):
    p = doc.add_paragraph(text, style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="360" w:after="160" w:line="288" w:lineRule="auto"/>'))
    return p

def add_h2(doc, text):
    p = doc.add_paragraph(text, style='Heading 2')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="240" w:after="100" w:line="288" w:lineRule="auto"/>'))
    return p

def add_h3(doc, text):
    p = doc.add_paragraph(text, style='Style1')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = RGBColor(0, 0, 0)
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:spacing {nsdecls("w")} w:before="160" w:after="80" w:line="288" w:lineRule="auto"/>'))
    return p

def add_p(doc, text, bold_prefix='', italic_prefix='', bullet=False):
    style_name = 'List Paragraph' if bullet else 'Normal'
    p = doc.add_paragraph(style=style_name)
    setup_paragraph(p, space_before=60, space_after=60, line_spacing=288,
                    align=WD_ALIGN_PARAGRAPH.LEFT if bullet else WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Times New Roman'
        r_bold.font.size = Pt(13)
        r_bold.font.bold = True
        r_bold.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        
    if italic_prefix:
        r_it = p.add_run(italic_prefix)
        r_it.font.name = 'Times New Roman'
        r_it.font.size = Pt(13)
        r_it.font.italic = True
        r_it.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    r_text = p.add_run(text)
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(13)
    r_text.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    return p

def add_formula(doc, formula_text, label=''):
    p = doc.add_paragraph(style='Normal')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setup_paragraph(p, space_before=120, space_after=120, line_spacing=288, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run(formula_text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.italic = True
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
    if label:
        r_lbl = p.add_run(f'   ({label})')
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(13)
        r_lbl.font.bold = True
    return p

def add_callout(doc, text, bold_title='> Nhận xét quan trọng: '):
    p = doc.add_paragraph(style='Normal')
    setup_paragraph(p, space_before=100, space_after=100, line_spacing=288, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'''
        <w:pBdr {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="12" w:color="1E88E5"/>
        </w:pBdr>
    ''')
    pPr.append(pBdr)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F4F8FA"/>')
    pPr.append(shd)

    r_title = p.add_run(bold_title)
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(12.5)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    r_text = p.add_run(text)
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(12.5)
    r_text.font.italic = True
    r_text.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    return p

def add_styled_table(doc, headers, data, col_widths=None, caption=''):
    if caption:
        p_cap = doc.add_paragraph(style='Normal')
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        setup_paragraph(p_cap, space_before=140, space_after=60, line_spacing=240, align=WD_ALIGN_PARAGRAPH.CENTER)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(12)
        r_cap.font.bold = True
        r_cap.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    tblBorders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="12" w:space="0" w:color="222222"/>
            <w:bottom w:val="single" w:sz="12" w:space="0" w:color="222222"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tbl._tbl.tblPr.append(tblBorders)

    hdr_row = tbl.rows[0]
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EBF2F7"/>')
        cell._tc.get_or_add_tcPr().append(shd)
        
        tcMar = parse_xml(f'''
            <w:tcMar {nsdecls("w")}>
                <w:top w:w="120" w:type="dxa"/>
                <w:bottom w:w="120" w:type="dxa"/>
                <w:left w:w="140" w:type="dxa"/>
                <w:right w:w="140" w:type="dxa"/>
            </w:tcMar>
        ''')
        cell._tc.get_or_add_tcPr().append(tcMar)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        setup_paragraph(p, space_before=40, space_after=40, line_spacing=240, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(heading)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x0A, 0x25, 0x40)

    for r_idx, row_data in enumerate(data):
        row = tbl.rows[r_idx + 1]
        bg_color = "F9FBFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
            cell._tc.get_or_add_tcPr().append(shd)

            tcMar = parse_xml(f'''
                <w:tcMar {nsdecls("w")}>
                    <w:top w:w="80" w:type="dxa"/>
                    <w:bottom w:w="80" w:type="dxa"/>
                    <w:left w:w="140" w:type="dxa"/>
                    <w:right w:w="140" w:type="dxa"/>
                </w:tcMar>
            ''')
            cell._tc.get_or_add_tcPr().append(tcMar)

            p = cell.paragraphs[0]
            val_str = str(val)
            align = WD_ALIGN_PARAGRAPH.CENTER if (c_idx > 0 and len(val_str) <= 25) else WD_ALIGN_PARAGRAPH.LEFT
            setup_paragraph(p, space_before=30, space_after=30, line_spacing=240, align=align)
            r = p.add_run(val_str)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)
            if "P4" in val_str or "0.8%" in val_str or "31.0 ms" in val_str or "28.0 ms" in val_str:
                r.font.bold = True
            r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    if col_widths:
        for row in tbl.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)

    p_after = doc.add_paragraph(style='Normal')
    setup_paragraph(p_after, space_before=0, space_after=100, line_spacing=240)
    return tbl

def add_figure(doc, img_path, caption, width_inches=6.0):
    if not os.path.exists(img_path):
        print(f"Warning: Figure not found at {img_path}")
        return None
    p_img = doc.add_paragraph(style='Normal')
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setup_paragraph(p_img, space_before=140, space_after=60, line_spacing=240, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph(style='Normal')
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    setup_paragraph(p_cap, space_before=40, space_after=140, line_spacing=240, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(11)
    r_cap.font.italic = True
    r_cap.font.bold = True
    r_cap.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    return p_img

def build_thesis_content(doc):
    print("Bắt đầu chèn Chương 3, 4, 5 và Tài liệu tham khảo...")

    # =========================================================================
    # CHƯƠNG 3
    # =========================================================================
    add_h1(doc, "CHƯƠNG 3: THIẾT KẾ VÀ HIỆN THỰC BỘ LẬP LỊCH TÁC VỤ THÍCH ỨNG")
    
    add_p(doc, "Dựa trên nền tảng lý thuyết và các rào cản nền tảng đã phân tích ở Chương 2, Chương này trình bày chi tiết về kiến trúc, nguyên lý thiết kế và quy trình hiện thực của Bộ lập lịch tác vụ thích ứng tầng ứng dụng (Adaptive Application-Level Task Scheduler). Hệ thống được thiết kế theo hướng module hóa chặt chẽ, cho phép phân tách rạch ròi vai trò của từng kỹ thuật tối ưu hóa và tích hợp thông suốt vào môi trường thực thi của nền tảng Flutter.")

    add_h2(doc, "3.1. Kiến trúc Tổng thể Hệ thống Lập lịch Tầng Ứng dụng")
    
    add_h3(doc, "3.1.1. Mô hình Phân lớp Kiến trúc")
    add_p(doc, "Hệ thống bộ lập lịch được tổ chức thành 5 phân lớp chức năng rõ ràng, hoạt động phối hợp để đưa ra các quyết định điều phối tài nguyên tối ưu nhất tại thời gian thực:")
    add_p(doc, "Tầng Giao diện Người dùng (UI Layer): Bao gồm luồng chính của ứng dụng Flutter (Main Isolate), nơi quản lý cây widget, lắng nghe sự kiện vuốt chạm của người dùng và thực thi chu trình dựng hình 60 Hz hoặc 120 Hz. Luồng này đòi hỏi quyền ưu tiên tài nguyên CPU cao nhất để duy trì ngân sách thời gian khung hình ngặt nghèo (16.67 ms hoặc 8.33 ms).", bold_prefix="• Tầng 1 — ", bullet=True)
    add_p(doc, "Tầng Giám sát và Điều khiển (Controller & Monitor Layer): Lớp giao tiếp trung gian (RunController) quản lý trạng thái thực nghiệm, kết nối đồng thời với Stack Monitor HUD để trực quan hóa hiệu năng theo thời gian thực và ghi nhận dữ liệu đo lường chi tiết.", bold_prefix="• Tầng 2 — ", bullet=True)
    add_p(doc, "Tầng Bộ Lập Lịch Trung Tâm (Scheduling Engine Layer): 'Bộ não điều phối' cốt lõi của ứng dụng (Scheduler interface và các dẫn xuất P0, P1, P2, P3, P4). Lớp này sở hữu hàng đợi ưu tiên 3 mức (TaskQueue), bộ đếm tuổi tác vụ (Aging Calculator), bộ điều khiển phản hồi thích ứng (AimdController), máy trạng thái suy giảm (ModeMachine) và cơ chế giảm tải ngược (Backpressure).", bold_prefix="• Tầng 3 — ", bullet=True)
    add_p(doc, "Tầng Hồ chứa Worker Nền (Worker Pool Layer): Tập hợp các Worker Isolate sống lâu dài hạn (Long-running Worker Pool) được khởi tạo trước và quản lý vòng đời độc lập. Tầng này chịu trách nhiệm nhận các lát cắt công việc (chunks) từ bộ lập lịch thông qua các cổng SendPort/ReceivePort, thực thi tính toán và gửi trả tín hiệu hoàn tất.", bold_prefix="• Tầng 4 — ", bullet=True)
    add_p(doc, "Tầng Cảm biến và Tín hiệu Nền tảng (Hardware & Platform Signals): Giao tiếp trực tiếp với Flutter Engine thông qua SchedulerBinding để trích xuất tín hiệu thời gian khung hình (FrameSignal), đồng thời kết nối xuống hệ điều hành Android thông qua MethodChannel để đọc nhiệt độ pin và dung lượng pin thời gian thực.", bold_prefix="• Tầng 5 — ", bullet=True)

    add_h3(doc, "3.1.2. Vòng đời và Đường ống Xử lý Tác vụ (Task Lifecycle Pipeline)")
    add_p(doc, "Quy trình điều phối một tác vụ trong kiến trúc được chuẩn hóa qua 6 giai đoạn nối tiếp:")
    add_p(doc, "Tiếp nhận và Phân loại (Submission): Tác vụ được gửi vào hàm submit(Task t). Tại đây, nếu hệ thống đang chịu quá tải hoặc máy quá nhiệt, cơ chế Backpressure sẽ quyết định cho phép tác vụ đi tiếp hay kích hoạt xả tải (Drop).", bold_prefix="1. ", bullet=True)
    add_p(doc, "Xếp hàng Đa mức (Enqueueing): Tác vụ được phân bổ vào đúng ngăn hàng đợi tương ứng với mức ưu tiên (Critical, Visible hoặc Background).", bold_prefix="2. ", bullet=True)
    add_p(doc, "Tính toán Độ ưu tiên Động (Dynamic Priority & Aging): Khi một worker rảnh, bộ lập lịch quét các đầu hàng đợi, tính toán điểm số thâm niên để chọn ra tác vụ xứng đáng nhất.", bold_prefix="3. ", bullet=True)
    add_p(doc, "Băm nhỏ và Phân phát (Chunking & Dispatch): Nếu tác vụ có kích thước lớn, nó được cắt thành một lát nhỏ (chunk) tương ứng thời gian chunkMs (80 ms) và đẩy xuống cổng SendPort của worker.", bold_prefix="4. ", bullet=True)
    add_p(doc, "Thực thi Cô lập (Isolated Execution): Worker tính toán lát cắt trong không gian bộ nhớ riêng biệt mà không làm gián đoạn luồng UI.", bold_prefix="5. ", bullet=True)
    add_p(doc, "Báo cáo Điểm Nhường (Yield Point & Re-entry): Khi hoàn thành chunk, worker báo về Main Isolate. Nếu tác vụ còn phần việc dở dang, phần còn lại được đưa trở lại đầu hàng đợi để nhường cơ hội cho các tác vụ khẩn cấp chen ngang.", bold_prefix="6. ", bullet=True)

    add_h2(doc, "3.2. Mô hình Tác vụ và Hàng đợi Ưu tiên Đa mức kèm Kỹ thuật Aging (P2)")
    
    add_h3(doc, "3.2.1. Phân loại Mức độ Ưu tiên Tác vụ")
    add_p(doc, "Khác với các hệ thống Isolate thông thường vốn coi mọi tác vụ đều đồng nhất, đề tài phân định rõ ràng 3 lớp ưu tiên nghiệp vụ dựa trên yêu cầu tương tác của con người:")
    add_p(doc, "Mức Critical (Khẩn cấp - Điểm cơ sở rank = 0): Các tác vụ phát sinh trực tiếp từ thao tác chạm của người dùng (ví dụ: bấm nút mở chi tiết sản phẩm, xác nhận in hóa đơn, chạm chuyển màn hình). Mục tiêu thiết kế là phản hồi tức thì với độ trễ Crit p95 < 100 ms.", bold_prefix="• ", bullet=True)
    add_p(doc, "Mức Visible (Hiển thị trước - Điểm cơ sở rank = 1): Các tác vụ chuẩn bị dữ liệu cho vùng màn hình người dùng sắp cuộn tới (ví dụ: giải mã ảnh thu nhỏ của các hàng kế tiếp trong danh sách). Tác vụ này cần hoàn tất sớm nhưng không được quyền chiếm đoạt tài nguyên của tác vụ Critical.", bold_prefix="• ", bullet=True)
    add_p(doc, "Mức Background (Chạy ngầm - Điểm cơ sở rank = 2): Các tác vụ nặng, kéo dài và không đòi hỏi phản hồi thị giác ngay lập tức (ví dụ: phân tích tập tin Excel 10.000 dòng, đồng bộ giao dịch lên máy chủ đám mây, băm chỉ mục tìm kiếm nội bộ).", bold_prefix="• ", bullet=True)

    add_h3(doc, "3.2.2. Cấu trúc Hàng đợi 3 Làn với Độ phức tạp O(1)")
    add_p(doc, "Để đảm bảo chi phí điều phối tại Main Isolate luôn ở mức tối thiểu, lớp TaskQueue được thiết kế bằng 3 hàng đợi hai đầu độc lập (Queue<Task>) tương ứng với 3 mức ưu tiên. Vì trong nội bộ mỗi làn, các tác vụ được sắp xếp tự nhiên theo thời gian đến (FIFO), thuật toán chọn tác vụ tiếp theo (popNext) chỉ cần so sánh tối đa 3 phần tử đứng đầu của 3 làn. Do đó, độ phức tạp thuật toán luôn đạt mức tối ưu tuyệt đối:")
    add_formula(doc, "T_{select} = O(1)", "3.1")
    add_p(doc, "Đặc tính này cực kỳ quan trọng đối với môi trường di động: ngay cả khi hàng đợi tích tụ hàng nghìn tác vụ lúc hệ thống quá tải, chi phí lựa chọn tác vụ vẫn chỉ tốn vài phần triệu giây (micro-giây), hoàn toàn không gây áp lực lên Main Isolate.")

    add_h3(doc, "3.2.3. Giải thuật Aging Chống Bỏ đói (Zero Starvation)")
    add_p(doc, "Nếu áp dụng cơ chế ưu tiên tuyệt đối (Strict Priority), khi người dùng lướt màn hình liên tục sinh ra các tác vụ Critical và Visible, các tác vụ Background sẽ bị kẹt vĩnh viễn trong hàng đợi, dẫn đến hiện tượng 'chết đói' (Starvation). Để khắc phục, đề tài cài đặt thuật toán Aging tính điểm ưu tiên hiệu dụng theo thời gian thực:")
    add_formula(doc, "Score(t) = (Rank(t) × agingMs) - WaitTime(t)", "3.2")
    add_p(doc, "Trong đó:")
    add_p(doc, "Rank(t) nhận giá trị 0 đối với Critical, 1 đối với Visible, và 2 đối với Background.", bold_prefix="• ", bullet=True)
    add_p(doc, "agingMs là hệ số thâm niên, được thiết lập mặc định là 3000 ms (3 giây).", bold_prefix="• ", bullet=True)
    add_p(doc, "WaitTime(t) là thời gian tác vụ đã phải nằm chờ trong hàng đợi tính bằng mili-giây.", bold_prefix="• ", bullet=True)
    add_p(doc, "Thuật toán quy ước tác vụ có Score nhỏ nhất sẽ giành chiến thắng để lấy worker thực thi. Khi vừa nộp vào hàng đợi (WaitTime = 0), tác vụ Critical có Score = 0, Visible có Score = 3000, Background có Score = 6000 (Critical được chọn trước). Tuy nhiên, nếu một tác vụ Background phải đợi quá 3 giây, Score của nó giảm xuống dưới 3000 (vượt qua Visible mới đến); nếu đợi quá 6 giây, Score của nó tụt xuống dưới 0 (vượt qua cả Critical mới đến). Cơ chế này đảm bảo về mặt toán học rằng mọi tác vụ nền đều chắc chắn được thực thi sau một khoảng thời gian chờ hữu hạn.")

    add_h2(doc, "3.3. Cơ chế Đa nhiệm Hợp tác và Kỹ thuật Chunking (P3)")
    
    add_h3(doc, "3.3.1. Rào cản Bất khả Ngắt của Isolate và Giải pháp Hợp tác")
    add_p(doc, "Như đã chỉ ra ở Mục 2.1.2, Dart Isolate không hỗ trợ cơ chế ngắt cưỡng bức (Preemption) từ bên ngoài. Nếu một tác vụ tính toán nặng 1000 ms được giao cho worker, worker đó sẽ bị khóa cứng trong 1000 ms mà không có cách nào tạm dừng nó lại. Nếu toàn bộ các worker trong pool đều đang bận thực thi các tác vụ nền dài, tác vụ Critical dù đứng đầu hàng đợi ưu tiên vẫn phải chờ đợi hàng chục giây (nghẽn đầu hàng).")
    add_p(doc, "Để phá vỡ rào cản này, hệ thống áp dụng kỹ thuật Đa nhiệm Hợp tác (Cooperative Multitasking) thông qua giải pháp Chunking: biến một tác vụ khổng lồ thành một chuỗi các bước tính toán nhỏ (lát cắt công việc) có độ dài xấp xỉ chunkMs (80 ms).")

    add_h3(doc, "3.3.2. Thiết kế Máy Trạng thái Tác vụ và Điểm Nhường Luồng (Yield Point)")
    add_p(doc, "Mỗi Task sở hữu một máy trạng thái theo dõi tiến độ công việc:")
    add_formula(doc, "RemainingIters = TotalIters - DoneIters", "3.3")
    add_p(doc, "Tại mỗi vòng lặp điều phối, Scheduler chỉ trích xuất một khối lượng tính toán tương ứng:")
    add_formula(doc, "ChunkIters = min(RemainingIters, chunkMs × ItersPerMs)", "3.4")
    add_p(doc, "Khi worker hoàn thành xong ChunkIters, nó gửi thông điệp báo cáo hoàn tất (onDone) về cho Scheduler tại Main Isolate. Ranh giới giữa hai chunk liên tiếp chính là Điểm Nhường Luồng (Yield Point). Tại thời điểm này, Scheduler cộng dồn DoneIters và kiểm tra nếu tác vụ còn dang dở, nó đưa phần việc còn lại trở lại đầu hàng đợi (addFront). Nếu trong tích tắc đó có một tác vụ Critical vừa xuất hiện, tác vụ Critical sẽ lập tức chiếm lấy worker rảnh, giúp thời gian phản hồi tương tác được cải thiện ngoạn mục.")

    add_h3(doc, "3.3.3. Hiện thực Chunking trên Tác vụ I/O Đọc Ảnh Thực tế")
    add_p(doc, "Để kiểm chứng khả năng áp dụng trong thực tế, đề tài cài đặt cơ chế Chunking trực tiếp trên tác vụ đọc và phân tích ảnh JPEG kích thước lớn (độ phân giải 24 Megapixel, 6016×4016 pixel, dung lượng 6–12 MB/ảnh) trong module image_workload.dart:")
    add_p(doc, "Phân tách Header và Metadata: Ở chunk đầu tiên (chunkOffset = 0), worker mở file ảnh bằng RandomAccessFile, đọc lát 4 KB đầu tiên để phân tích các marker JPEG SOI (0xFFD8) và SOF0/SOF2 (0xFFC0/0xFFC2) nhằm trích xuất kích thước ảnh gốc mà không cần giải mã toàn bộ file.", bold_prefix="• ", bullet=True)
    add_p(doc, "Đọc Lát Cắt Dữ liệu Nhị phân Có Giới hạn: Ở các chunk tiếp theo, worker dịch chuyển con trỏ file (seek) đến vị trí tương ứng với tiến độ và chỉ đọc một lát dữ liệu tối đa 256 KB (_maxChunkBytes).", bold_prefix="• ", bullet=True)
    add_p(doc, "Xử lý Khối Điểm ảnh: Tiến hành tính toán Histogram 256 mức và tính toán năng lượng khối điểm ảnh trên lát dữ liệu vừa đọc.", bold_prefix="• ", bullet=True)
    add_p(doc, "Đóng File An toàn: Toàn bộ quá trình đọc đĩa được bọc trong khối lệnh try/finally để giải phóng tài nguyên hệ điều hành ngay khi kết thúc chunk.", bold_prefix="• ", bullet=True)
    add_p(doc, "Cách tiếp cận này vừa tái hiện chính xác tải nhập/xuất đĩa (Disk I/O) và tính toán CPU thực tế của các ứng dụng đa phương tiện, vừa triệt tiêu hoàn toàn nguy cơ tràn bộ nhớ RAM (OOM Crash) khi giải mã ảnh độ phân giải cao.")

    add_h2(doc, "3.4. Kỹ thuật Critical Worker Reserve — Ghế Dự phòng VIP (P3r)")
    add_p(doc, "Một phát hiện cốt lõi từ thực nghiệm của đề tài là: nếu chỉ áp dụng Chunking đơn thuần (P3c), trong thời điểm bão tải, toàn bộ các worker trong pool đều có thể đang chạy dở các chunk của tác vụ nền. Khi người dùng chạm màn hình, tác vụ Critical vẫn phải chờ cho đến khi chunk nền đầu tiên kết thúc. Trên chip di động yếu, việc chờ đợi một chu kỳ chunk cộng với độ trễ truyền thông điệp IPC vẫn có thể làm trễ thao tác.")
    add_p(doc, "Để triệt tiêu hoàn toàn nguy cơ này, kỹ thuật Critical Worker Reserve quy định một ràng buộc thép trong hàm phân phát tác vụ (_eligible):")
    add_formula(doc, "RunningNonCritical \le \min(CurrentWorkerCap, W - 1)", "3.5")
    add_p(doc, "Quy tắc này đảm bảo rằng trong một pool gồm W worker, các tác vụ thông thường (Visible và Background) chỉ được phép sử dụng tối đa W - 1 worker. Luôn luôn có ít nhất 1 worker dự phòng ở trạng thái sẵn sàng để phục vụ ngay lập tức khi tác vụ Critical xuất hiện. Nhờ chiếc ghế dự phòng này, độ trễ tương tác chạm của người dùng được bảo vệ tuyệt đối ngay cả khi hệ thống đang chịu tải nặng nhất.")

    add_h2(doc, "3.5. Đồng bộ Nhịp Vsync và Kỹ thuật Frame Yielding (P3)")
    
    add_h3(doc, "3.5.1. Giám sát Khoảng cách Khung hình Tức thời với FrameSignal")
    add_p(doc, "Để bộ lập lịch biết được giao diện người dùng có đang mượt mà hay bắt đầu bị giật lag, module FrameSignal được gắn trực tiếp vào Flutter Engine thông qua hàm lắng nghe SchedulerBinding.instance.addPersistentFrameCallback. Module này duy trì một cửa sổ trượt gồm 30 khung hình gần nhất, liên tục tính toán phân vị xấu nhất p95 của khoảng cách giữa hai khung hình liên tiếp (gapP95Ms). Điểm độc đáo của cơ chế này là nó tính toán cả thời gian đang bị treo của khung hình hiện tại, cho phép phát hiện sự cố giật lag ngay trong tích tắc mà không cần chờ khung hình kết thúc.")

    add_h3(doc, "3.5.2. Thuật toán Nhường Khung hình có Vùng đệm Trễ (Hysteresis Frame Yielding)")
    add_p(doc, "Định kỳ mỗi 100 ms, bộ lập lịch kiểm tra tín hiệu gapP95Ms và điều khiển cờ trạng thái UI bận (_busy) theo cơ chế trễ kép:")
    add_p(doc, "Kích hoạt Nhường luồng: Nếu gapP95Ms > yieldMs (mặc định 20 ms đối với màn hình 60 Hz), chứng tỏ luồng UI đã bị lỡ nhịp Vsync chuẩn 16.67 ms. Bộ lập lịch lập tức bật cờ _busy = true (trên giao diện hiển thị huy hiệu ● YIELDING). Khi cờ này bật, toàn bộ các tác vụ Background bị tạm hoãn cấp phát worker mới, nhường toàn bộ năng lực tính toán của CPU cho luồng UI và luồng Raster.", bold_prefix="• ", bullet=True)
    add_p(doc, "Hủy trạng thái Nhường luồng: Chỉ khi gapP95Ms hạ sâu xuống dưới 0.8 × yieldMs (16 ms), chứng tỏ giao diện đã thực sự mượt mà trở lại, cờ _busy mới được hạ xuống false.", bold_prefix="• ", bullet=True)
    add_p(doc, "Chống bỏ đói khi nhường (Defer Cap): Để tránh trường hợp giao diện cuộn liên tục làm tác vụ nền bị hoãn vô hạn, bộ lập lịch thiết lập trần hoãn deferCapMs = 8000 ms (8 giây). Một tác vụ nền nếu đã bị hoãn quá 8 giây sẽ được quyền vượt qua rào cản nhường luồng để thực thi.")

    add_h2(doc, "3.6. Thuật toán Điều khiển Phản hồi Thích ứng AIMD (P4)")
    
    add_h3(doc, "3.6.1. Nguyên lý Điều hòa Tắc nghẽn CPU")
    add_p(doc, "Khi ứng dụng đối mặt với các đợt bùng nổ tải dữ liệu đột ngột (Kịch bản S2), việc duy trì số lượng worker cố định ở mức cao sẽ dẫn đến hiện tượng tranh chấp tài nguyên bộ nhớ đệm (Cache Thrashing) và nghẽn băng thông bus dữ liệu, kéo sập độ mượt của màn hình. Để giải quyết, đề tài áp dụng thuật toán kinh điển trong kiểm soát tắc nghẽn mạng: Additive Increase / Multiplicative Decrease (AIMD).")

    add_h3(doc, "3.6.2. Hiện thực Bộ Điều khiển AimdController")
    add_p(doc, "Lớp AimdController hoạt động theo từng chu kỳ đánh giá cố định (pacingMs = 500 ms) nhằm cho phép hệ thống ổn định trước khi đưa ra quyết định co giãn tiếp theo:")
    add_p(doc, "Khi khoảng cách khung hình vượt ngưỡng mục tiêu (gapP95Ms > targetGapMs = 20 ms), hệ thống kích hoạt cơ chế Giảm Nhân (Multiplicative Decrease):", bold_prefix="• Pha Phanh Khẩn Cấp: ")
    add_formula(doc, "Workers(t) = \max(MinWorkers, Workers(t) \times 0.5)", "3.6")
    add_p(doc, "Số lượng worker nền được cắt giảm ngay lập tức một nửa, giải phóng 50% tài nguyên CPU để cứu vãn nhịp dựng hình kế tiếp.")
    add_p(doc, "Khi khoảng cách khung hình duy trì ở mức mượt mà (gapP95Ms \le targetGapMs × 0.8 = 16 ms), hệ thống kích hoạt cơ chế Tăng Cộng (Additive Increase):", bold_prefix="• Pha Tăng Trưởng Thận Trọng: ")
    add_formula(doc, "Workers(t) = \min(MaxWorkers, Workers(t) + 1.0)", "3.7")
    add_p(doc, "Worker được mở rộng từ từ từng đơn vị một để tận dụng năng lực tính toán còn nhàn rỗi.")

    add_h3(doc, "3.6.3. Quy tắc Miễn nhiễm cho Tác vụ Khẩn cấp")
    add_p(doc, "Một nguyên lý then chốt trong thiết kế P4 của đề tài là: Trần giới hạn worker của AIMD chỉ áp dụng đối với các tác vụ thông thường (Visible và Background). Riêng tác vụ Critical được quyền vượt trần AIMD để sử dụng bất kỳ worker nhàn rỗi nào trong pool. Thiết kế này bảo vệ tuyệt đối độ trễ tương tác của người dùng, không để thuật toán co worker vô tình làm chậm các thao tác khẩn cấp.")

    add_h2(doc, "3.7. Cơ chế Áp lực Ngược (Backpressure) và Xả Tải Chủ Động (P4)")
    
    add_h3(doc, "3.7.1. Cơ sở Toán học từ Định luật Little")
    add_p(doc, "Theo Định luật Little trong lý thuyết hàng đợi:")
    add_formula(doc, "L = \lambda \times W", "3.8")
    add_p(doc, "Trong đó L là số lượng tác vụ tích tụ trong hàng đợi, \lambda là tốc độ tác vụ mới phát sinh, và W là thời gian trung bình một tác vụ lưu lại trong hệ thống. Khi tốc độ tác vụ gửi đến \lambda vượt quá năng lực xử lý cực đại của phần cứng trong một khoảng thời gian dài, hàng đợi L sẽ tăng trưởng không giới hạn, dẫn đến việc cạn kiệt bộ nhớ RAM và làm sập ứng dụng (Out-Of-Memory Crash).")

    add_h3(doc, "3.7.2. Chính sách Loại bỏ Tác vụ Hết hạn (Stale Work Elimination)")
    add_p(doc, "Để đảm bảo ứng dụng không bao giờ bị tràn RAM khi tải bùng nổ, P4Scheduler cài đặt cơ chế xả tải có chọn lọc ngay tại cửa vào submit():")
    add_formula(doc, "QueueThreshold = \max(20, W \times 10)", "3.9")
    add_p(doc, "Khi số lượng tác vụ đang xếp hàng vượt quá QueueThreshold (ví dụ 40 hoặc 80 tác vụ), bộ lập lịch kích hoạt luật xả tải:")
    add_p(doc, "Tuyệt đối không bao giờ hủy tác vụ Critical: Mọi thao tác chạm của người dùng luôn được đảm bảo thực thi 100%.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Xả tải tác vụ Background dồn ứ: Các tác vụ nền cũ đã hết hạn thị giác (ví dụ yêu cầu giải mã ảnh của một trang danh sách mà người dùng đã cuộn lướt qua từ lâu) được chủ động đánh dấu hủy (t.dropped = true), giải phóng ngay lập tức mà không đưa vào hàng đợi.", bold_prefix="2. ", bullet=True)
    add_p(doc, "Nhờ cơ chế xả tải thông minh này, ứng dụng bảo vệ trọn vẹn dung lượng RAM và rút ngắn đáng kể tổng thời gian hoàn thành kịch bản (Makespan).")

    add_h2(doc, "3.8. Máy Trạng thái Suy giảm Thích ứng Môi trường (P4)")
    
    add_h3(doc, "3.8.1. Thu thập Tín hiệu Nhiệt độ và Pin từ Android Native")
    add_p(doc, "Thông qua lớp DeviceSignalSource giao tiếp với Android Kotlin qua MethodChannel('com.example.optimize/device_signals'), bộ lập lịch liên tục lấy mẫu hai chỉ số phần cứng quan trọng:")
    add_p(doc, "Nhiệt độ pin (Battery Temperature): Đọc từ BatteryManager.EXTRA_TEMPERATURE theo thời gian thực.", bold_prefix="• ", bullet=True)
    add_p(doc, "Mức pin còn lại (Battery Level): Đọc phần trăm dung lượng pin hiện tại.", bold_prefix="• ", bullet=True)

    add_h3(doc, "3.8.2. Ba Chế độ Suy giảm và Cơ chế Trễ Hysteresis")
    add_p(doc, "Máy trạng thái (ModeMachine) điều khiển ứng dụng vận hành qua 3 chế độ suy giảm linh hoạt:")
    add_p(doc, "Chế độ Bình thường (Normal Mode - Nhiệt độ < 38°C và Pin > 20%): Hệ thống hoạt động với toàn bộ công suất và số worker do AIMD quyết định.", bold_prefix="• ", bullet=True)
    add_p(doc, "Chế độ Tiết kiệm (Conserve Mode - Nhiệt độ ≥ 38°C hoặc Pin ≤ 20%): Thiết bị bắt đầu ấm lên hoặc pin yếu; bộ lập lịch chủ động cắt bớt 25% trần worker tối đa (cap = cap × 0.75) và nhân đôi thời gian hoãn của tác vụ nền để giảm phát nhiệt.", bold_prefix="• ", bullet=True)
    add_p(doc, "Chế độ Nguy cấp (Critical Mode - Nhiệt độ ≥ 42°C hoặc Pin ≤ 10%): Thiết bị đứng trước nguy cơ bị hệ điều hành bóp xung nhịp (Thermal Throttling) hoặc sập nguồn; bộ lập lịch khóa cứng trần worker về mức 1 worker tối thiểu và tự động loại bỏ mọi tác vụ nền mới đến.", bold_prefix="• ", bullet=True)
    add_p(doc, "Đặc biệt, để ngăn chặn hiện tượng rung giật chuyển trạng thái (flapping / chattering) khi nhiệt độ dao động quanh ngưỡng 38°C, ModeMachine thiết lập thời gian trễ hysteresisMs = 5000 ms (5 giây). Tín hiệu phần cứng mới phải duy trì ổn định liên tục qua ngưỡng trong tối thiểu 5 giây thì máy trạng thái mới chính thức kích hoạt chuyển chế độ.")

    add_h2(doc, "3.9. Tổng hợp Đối chiếu Kiến trúc 5 Chính sách Lập lịch (P0 -> P4)")
    add_p(doc, "Bảng 3.1 tổng hợp sự tiến hóa về mặt kiến trúc và các cơ chế kỹ thuật tương ứng qua 5 chính sách lập lịch được cài đặt và đánh giá trong đề tài:")

    headers_p = ["Chính sách", "Không gian Thực thi", "Cấu trúc Hàng đợi", "Kỹ thuật Điều phối Cốt lõi", "Cơ chế Thích ứng Môi trường"]
    data_p = [
        ["P0: Main Isolate", "Main Isolate (Luồng UI đơn)", "Hàng đợi tuần tự FIFO đơn giản", "Chạy tuần tự, chia sẻ Event Loop", "Không có (Tê liệt khi có tính toán nặng)"],
        ["P1: Fixed Pool", "Worker Pool tĩnh (W Isolate sống lâu)", "Hàng đợi FIFO đơn cấp", "Tái sử dụng Isolate, giao tiếp SendPort", "Không có (Tranh chấp CPU, nghẽn đầu hàng)"],
        ["P2: Priority+Aging", "Worker Pool tĩnh (W Isolate sống lâu)", "Hàng đợi 3 mức O(1) (Crit/Vis/Bg)", "Aging tăng điểm theo thời gian chờ hữu hạn", "Chống bỏ đói tác vụ nền (Zero Starvation)"],
        ["P3: Chunk+Yield", "Worker Pool tĩnh (W Isolate sống lâu)", "Hàng đợi 3 mức O(1) + Ghế Reserve", "Cooperative Chunking 80ms, Frame Yielding", "Nhường luồng khi khoảng cách frame > 20ms"],
        ["P4: Adaptive AIMD", "Worker Pool động tự co giãn", "Hàng đợi 3 mức + Backpressure", "AIMD (+1 / ×0.5), Load Shedding Stale Work", "Máy trạng thái 3 chế độ + Trễ Hysteresis 5s"]
    ]
    add_styled_table(doc, headers_p, data_p, col_widths=[1.2, 1.4, 1.3, 1.6, 1.5], caption="Bảng 3.1: Ma trận so sánh tính năng kỹ thuật của 5 chính sách lập lịch P0 - P4")

    # =========================================================================
    # CHƯƠNG 4
    # =========================================================================
    add_h1(doc, "CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ ĐÓNG GÓP")
    
    add_p(doc, "Chương này trình bày toàn bộ các kết quả đo lường thực nghiệm thu được từ quá trình chạy thử nghiệm khắt khe trên các thiết bị phần cứng thật, phân tích thống kê định lượng và kiểm chứng 4 giả thuyết nghiên cứu khoa học cốt lõi (H1 đến H4) của đề tài.")

    add_h2(doc, "4.1. Thiết lập Môi trường và Phương pháp Đo lường Chuẩn hóa")
    
    add_h3(doc, "4.1.1. Thiết bị Phần cứng và Môi trường Đo lường")
    add_p(doc, "Các thực nghiệm chính thức được thực hiện trên hai thiết bị đại diện cho hai phân khúc phần cứng phổ biến trên thị trường:")
    add_p(doc, "Thiết bị Phổ thông Giá rẻ (Baseline Device): Samsung Galaxy A04e (Model SM-A042F), trang bị vi xử lý MediaTek Helio P35 (8 nhân Cortex-A53: 4 nhân 2.3 GHz + 4 nhân 1.8 GHz), RAM 2 GB, hệ điều hành Android 14 (One UI Core 6.0), màn hình chuẩn 60 Hz (ngân sách khung hình 16.67 ms).", bold_prefix="• Thiết bị 1: ", bullet=True)
    add_p(doc, "Thiết bị Tầm trung Thế hệ mới (High-end Cross-Device): Xiaomi Redmi Note 13, vi xử lý MediaTek Helio G99 (8 nhân: 2 nhân hiệu năng cao Cortex-A76 2.2 GHz + 6 nhân tiết kiệm điện Cortex-A55 2.0 GHz), RAM 6 GB, hệ điều hành Android 15, màn hình tần số quét cao 120 Hz với ngân sách khung hình ngặt nghèo chỉ 8.33 ms.", bold_prefix="• Thiết bị 2: ", bullet=True)
    add_p(doc, "Chế độ Biên dịch Chuẩn mực: Toàn bộ các bản dựng thử nghiệm đều được biên dịch ở chế độ Profile Mode (Ahead-Of-Time compilation - AOT), tắt hoàn toàn các bộ kiểm tra gỡ lỗi (debug assertions) để phản ánh chính xác hiệu năng khi ứng dụng phát hành thực tế.", bold_prefix="• ", bullet=True)

    add_h3(doc, "4.1.2. Kịch bản Thực nghiệm")
    add_p(doc, "Nghiên cứu thiết kế 3 kịch bản thực nghiệm mô phỏng toàn diện các tình huống tải trong thực tế:")
    add_p(doc, "Kịch bản Tải Đều Bão hòa (Scenario S1): Đẩy tải tác vụ nền liên tục với hệ số tải cao (L = 64 trên A04e, L = 256 trên Note 13), kèm theo 5 tác vụ Critical xuất hiện ngẫu nhiên. Kịch bản này nhằm khảo sát khả năng duy trì độ mượt và kiểm tra hiện tượng nghẽn đầu hàng khi tài nguyên tính toán bị bão hòa hoàn toàn.", bold_prefix="• Kịch bản S1: ", bullet=True)
    add_p(doc, "Kịch bản Tải Bậc thang Biến động (Scenario S2): Tải tác vụ nền tăng dần qua 4 bậc thang thời gian trong 60 giây (0.25x -> 0.5x -> 1.0x -> 2.0x), đan xen 8 tác vụ Critical. Kịch bản này thử thách khả năng thích ứng động của thuật toán AIMD và cơ chế xả tải Backpressure khi tải bùng nổ.", bold_prefix="• Kịch bản S2: ", bullet=True)
    add_p(doc, "Kịch bản Tác vụ Ảnh Thực tế (Scenario s_image): Tải thực thi giải mã nhị phân, đọc đĩa ngẫu nhiên và tính toán ma trận histogram trên tập 80 bức ảnh chụp DSLR 24 Megapixel thật, kết hợp hiển thị lưới cuộn ảnh 3 cột trên giao diện.", bold_prefix="• Kịch bản s_image: ", bullet=True)

    add_h3(doc, "4.1.3. Phương pháp Đo lường và Kiểm định Thống kê")
    add_p(doc, "Để đảm bảo tính khách quan khoa học, mỗi phép đo đều tuân thủ quy trình chuẩn hóa: Nghỉ ổn định thiết bị (10s) -> Chạy làm nóng (Warmup 10s không tính) -> Đo chính thức (60s) -> Xuất dữ liệu CSV và Metadata nhiệt độ/pin -> Nghỉ nguội giữa các lần đo. Do các chỉ số độ trễ phân phối lệch (skewed distribution), toàn bộ báo cáo sử dụng Trung vị (Median), Khoảng tứ phân vị (IQR) và khoảng biến thiên [Min - Max]. Mọi so sánh giả thuyết đều được kiểm định bằng phương pháp phi tham số Mann-Whitney U test ở mức ý nghĩa thống kê chuẩn alpha = 0.05.")

    add_h2(doc, "4.2. Kiểm chứng Giả thuyết H1: Nghẽn Main Isolate và Hiệu quả của WorkerPool (P0 vs P1)")
    add_p(doc, "Giả thuyết H1: Việc thực thi các tác vụ tính toán nặng trên Main Isolate (P0) sẽ làm tê liệt vòng lặp dựng hình của giao diện; chuyển tác vụ ra WorkerPool Isolate (P1) sẽ khôi phục khả năng dựng frame mượt mà.", italic_prefix="Phát biểu Giả thuyết: ")
    add_p(doc, "Kết quả thực nghiệm trên Samsung Galaxy A04e ở Kịch bản S1 (L = 64, W = 8, C = 80, n = 4 mỗi chính sách):")
    add_p(doc, "Chính sách P0 (Main Isolate): Tỷ lệ khung hình bị bỏ rơi (Missed Frame) lên tới 90.8% [91–91%], khoảng cách giữa các khung hình dựng được kéo dài tới 419.3 ms (tốc độ hiển thị thực tế rớt xuống dưới 3 FPS, vòng xoay giao diện bị đóng băng hoàn toàn). Độ trễ tác vụ khẩn cấp trung vị là 68,483 ms (~68.5 giây) và thời gian chờ của tác vụ nền lên tới 81,719 ms.", bold_prefix="• ", bullet=True)
    add_p(doc, "Chính sách P1 (WorkerPool FIFO): Khi chuyển toàn bộ tác vụ ra 8 worker isolates chạy nền, tỷ lệ Missed Frame lập tức giảm mạnh xuống 23.2% [22–24%], khoảng cách khung hình p95 rút ngắn về 48.2 ms, và tỷ lệ hoàn thành tác vụ tăng từ 16.6% lên 86.5%.", bold_prefix="• ", bullet=True)
    add_callout(doc, "Kiểm định phi tham số Mann-Whitney U giữa P0 và P1 về tỷ lệ Missed Frame xác nhận sự khác biệt vượt trội có ý nghĩa thống kê rất cao (U = 16.0, p = 0.014 < 0.05). Kết luận: CHẤP NHẬN GIẢ THUYẾT H1. Việc chuyển đổi tác vụ nặng ra Isolate nền là điều kiện tiên quyết bắt buộc để cứu vãn vòng lặp giao diện.", bold_title="> Kiểm định Thống kê & Kết luận H1: ")

    add_h2(doc, "4.3. Kiểm chứng Giả thuyết H2: Giới hạn của Pool FIFO Cố định Dưới Tải Cao (P1)")
    add_p(doc, "Giả thuyết H2: Trong môi trường phần cứng hạn chế (8 nhân Cortex-A53), việc tăng số worker Isolate trong một pool FIFO cố định không giải quyết được hiện tượng nghẽn đầu hàng (Head-of-Line Blocking) khi tải bão hòa, đồng thời gây gia tăng tranh chấp CPU với UI thread.", italic_prefix="Phát biểu Giả thuyết: ")
    add_p(doc, "Kết quả thực nghiệm khảo sát mở rộng số worker từ W = 4, W = 6 đến W = 8 trên P1:")
    add_p(doc, "Ở mức tải trung bình (L = 32), việc tăng worker từ W = 6 lên W = 8 giúp giảm độ trễ critical từ 131 ms xuống 36 ms do hệ thống còn nhân CPU nhàn rỗi.", bold_prefix="• ", bullet=True)
    add_p(doc, "Tuy nhiên, khi tải vượt ngưỡng bão hòa (L = 64): Ngay cả khi cấp tối đa 8 worker, P1 vẫn để xảy ra 23.2% missed frames. Do hàng đợi tuân theo cơ chế FIFO không phân biệt độ ưu tiên, tác vụ Critical phải xếp sau hàng trăm tác vụ nền khổng lồ, khiến độ trễ Critical p95 vọt lên tới 35,356 ms (hơn 35 giây!).", bold_prefix="• ", bullet=True)
    add_callout(doc, "Kết luận: ỦNG HỘ GIẢ THUYẾT H2. Tăng số lượng worker trong cơ chế FIFO chỉ có tác dụng khi tải chưa bão hòa; một khi hệ thống quá tải, pool cố định hoàn toàn thất bại trong việc bảo vệ độ trễ tương tác của người dùng và gây nhiễu luồng UI do tranh chấp bộ lập lịch CFS.", bold_title="> Kết luận Giả thuyết H2: ")

    add_h2(doc, "4.4. Kiểm chứng Giả thuyết H3: Vai trò của Ưu tiên, Chunking, Reserve và Nhường Frame (P1 -> P2 -> P3)")
    add_p(doc, "Giả thuyết H3: Cơ chế hàng đợi ưu tiên kèm aging (P2), kết hợp chia nhỏ tác vụ (chunking), dành riêng worker dự phòng và chủ động nhường frame (P3) sẽ triệt tiêu độ trễ critical và đưa tỷ lệ rớt frame về mức tương đương baseline không tải.", italic_prefix="Phát biểu Giả thuyết: ")
    add_p(doc, "Bảng 4.1 trình bày kết quả đối đầu chi tiết giữa các chính sách trên kịch bản tải bão hòa S1 (Samsung A04e, L = 64, W = 8, C = 80, n = 4 mỗi chính sách):")

    headers_s1 = ["Chính sách", "Missed Frame (%)", "Jank Frame (%)", "Frame Gap p95 (ms)", "Critical Latency p95", "Tỷ lệ Hoàn thành"]
    data_s1 = [
        ["NONE (Baseline)", "0.9% [1–1%]", "2.2% [0–3%]", "18.3 ms", "– (Không tải)", "–"],
        ["P0 (Main Isolate)", "90.8% [91–91%]", "0.0% (Tê liệt)", "419.3 ms", "68,483 ms (~68.5s)", "16.6%"],
        ["P1 (FIFO Pool)", "23.2% [22–24%]", "9.9% [9–11%]", "48.2 ms", "35,356 ms (~35.4s)", "86.5%"],
        ["P2 (Priority+Aging)", "22.4% [21–24%]", "10.0% [9–10%]", "42.9 ms", "22,760 ms (~22.8s)", "90.4%"],
        ["P3 (Chunk+Yield)", "0.8% [1–1%]", "17.0% [16–19%]", "18.2 ms", "31.0 ms [28–35 ms]", "77.1%"]
    ]
    add_styled_table(doc, headers_s1, data_s1, col_widths=[1.5, 1.2, 1.1, 1.3, 1.4, 1.1], caption="Bảng 4.1: So sánh hiệu năng các chính sách lập lịch trên kịch bản tải bão hòa S1 (Samsung Galaxy A04e)")

    add_h3(doc, "4.4.1. Phân rã Đóng góp Kiến trúc (Ablation Study)")
    add_p(doc, "Để bóc tách chính xác giá trị của từng kỹ thuật trong bước nhảy vọt từ P1 lên P3, nghiên cứu tiến hành phân rã kiến trúc qua 4 biến thể:")
    add_p(doc, "P2 (Ưu tiên đơn thuần): Độ trễ critical giảm từ 35.4s xuống 22.8s (giảm 36%, p = 0.014), nhưng vẫn ở mức hàng chục giây vì 8 worker đang bận chạy dở tác vụ nền không thể ngắt giữa chừng.", bold_prefix="1. ", bullet=True)
    add_p(doc, "P3c (Bổ sung Chunking 80ms): Cắt nhỏ tác vụ giúp worker liên tục nhả việc sau mỗi 80ms. Tỷ lệ rớt frame lập tức giảm sốc từ 22.2% xuống 0.8% (mượt ngang baseline không tải!).", bold_prefix="2. ", bullet=True)
    add_p(doc, "P3r (Bổ sung Critical Reserve): Dành riêng 1 worker cho tương tác chạm. Ngay lập tức độ trễ Critical giảm gần 1.000 lần, từ 44.8 giây xuống còn 49.0 ms (< 100 ms).", bold_prefix="3. ", bullet=True)
    add_p(doc, "P3 Hoàn chỉnh (Bổ sung Frame Yielding): Khi nhịp frame trễ, tạm dừng việc nền để nhường CPU cho UI. Độ trễ Critical đạt mức tối ưu tuyệt đối: 31.0 ms.", bold_prefix="4. ", bullet=True)

    add_figure(doc, "figures/fig1_s1_tradeoff.png", "Hình 4.1: Biểu đồ phân tán đánh đổi giữa Tỷ lệ Missed Frame và Độ trễ Critical p95 trên Kịch bản S1", width_inches=6.0)
    add_figure(doc, "figures/fig4_ablation_s1.png", "Hình 4.2: Biểu đồ phân rã đóng góp của từng thành phần kiến trúc (Ablation Study)", width_inches=6.0)

    add_callout(doc, "Kiểm định Mann-Whitney U giữa P1 và P3 xác nhận: Tỷ lệ Missed Frame giảm từ 23.2% xuống 0.8% (U = 16.0, p = 0.014); Độ trễ Critical giảm từ 35.4 giây xuống 31.0 ms (nhanh hơn 1.140 lần, U = 16.0, p = 0.014). Kết luận: CHẤP NHẬN GIẢ THUYẾT H3.", bold_title="> Kiểm định Thống kê & Kết luận H3: ")

    add_h2(doc, "4.5. Kiểm chứng Giả thuyết H4: Thích ứng Động AIMD và Backpressure Trên Kịch bản S2 (P4 vs P3)")
    add_p(doc, "Giả thuyết H4: Khi chịu tải biến động và tăng đột biến (Kịch bản S2: 4 bậc thang từ 0.25x đến 2.0x), thuật toán AIMD co/giãn worker động kết hợp Backpressure (load shedding) sẽ giúp loại bỏ hiện tượng jank UI do nghẽn CPU, đồng thời rút ngắn makespan nhờ hủy bỏ các tác vụ nền dồn ứ.", italic_prefix="Phát biểu Giả thuyết: ")
    add_p(doc, "Bảng 4.2 đối chiếu kết quả đo lường kịch bản tải bậc thang S2 giữa P1, P3 và P4 trên Samsung Galaxy A04e (L = 32, W = 8, C = 80, n = 3 mỗi chính sách):")

    headers_s2 = ["Chỉ số Đánh giá", "P1 (FIFO)", "P3 (Chunk+Priority)", "P4 (AIMD+Backpressure)", "Đánh giá So sánh (P4 vs P3)"]
    data_s2 = [
        ["Missed Frame (%)", "5.1% [5–5%]", "0.7% [1–1%]", "0.8% [1–1%]", "Ngang nhau, duy trì mượt mà ~60 FPS"],
        ["Jank Frame (%)", "4.8% [4–8%]", "24.8% [18–26%]", "8.0% [0–10%]", "P4 giảm jank hơn 3 lần (U = 9.0, p = 0.050)"],
        ["Critical Latency p95", "4,744.0 ms", "34.0 ms", "28.0 ms [27–30 ms]", "Nhanh nhất toàn diện (nhanh hơn P1 169 lần)"],
        ["Makespan (Tổng thời gian)", "67,839 ms", "77,736 ms", "67,865 ms", "P4 hoàn thành sớm hơn P3 gần 10 giây"],
        ["Tác vụ Nền bị hủy (Dropped)", "0", "0", "1,990 tasks", "Backpressure chủ động loại bỏ task ứ đọng"]
    ]
    add_styled_table(doc, headers_s2, data_s2, col_widths=[1.6, 1.2, 1.4, 1.5, 1.8], caption="Bảng 4.2: So sánh hiệu năng trên kịch bản tải bậc thang tăng dần S2 (Samsung Galaxy A04e)")

    add_p(doc, "Phân tích cơ chế vượt trội của P4:")
    add_p(doc, "Dập tắt Jank Frame ở Tải Đỉnh: Ở pha 4 (tải đỉnh 2.0x), P3 vẫn cố chấp duy trì 8 worker làm việc hết công suất khiến CPU bị nghẽn bus và tranh chấp dữ dội với GPU, đẩy tỷ lệ Jank của P3 lên 24.8%. Ngược lại, AIMD của P4 nhận diện độ trễ khung hình tăng và phanh gấp số worker xuống 1–2 worker, giúp Jank giảm hơn 3 lần xuống chỉ còn 8.0% (có run đạt mức lý tưởng 0.25%).", bold_prefix="• ", bullet=True)
    add_p(doc, "Bảo toàn Độ trễ Critical 28.0 ms: Nhờ quy tắc cô lập Critical khỏi trần AIMD, tác vụ khẩn cấp luôn chiếm dụng ngay worker rảnh rỗi mà không bị ảnh hưởng bởi việc co worker nền.", bold_prefix="• ", bullet=True)
    add_p(doc, "Chống Tràn RAM nhờ Load Shedding: Ở tải đỉnh 2.0x, P4 loại bỏ 1.990 tác vụ nền hết hạn, cứu ứng dụng khỏi nguy cơ tràn RAM OOM và rút ngắn Makespan gần 10 giây.", bold_prefix="• ", bullet=True)

    add_figure(doc, "figures/fig2_s2_comparison.png", "Hình 4.3: So sánh 4 chỉ số hiệu năng cốt lõi giữa P1, P3 và P4 trên Kịch bản tải bậc thang S2", width_inches=6.0)
    add_figure(doc, "figures/fig3_timeline_frames.png", "Hình 4.4: Dòng thời gian phân bố thời gian khung hình (Frame Duration Timeline) trong 60 giây của kịch bản S2", width_inches=6.0)

    add_callout(doc, "Kết luận: CHẤP NHẬN GIẢ THUYẾT H4. Thuật toán AIMD kết hợp Backpressure là mô hình tối ưu toàn diện cho thiết bị di động phân khúc giá rẻ khi phải đương đầu với các đợt bùng nổ tải dữ liệu nghiêm trọng.", bold_title="> Kết luận Giả thuyết H4: ")

    add_h2(doc, "4.6. Đo lường Phụ tải (Overhead) của Bộ Lập lịch (Microbenchmark E3)")
    add_p(doc, "Một nghi vấn thường gặp là việc liên tục băm nhỏ tác vụ, xếp hàng ưu tiên và giao tiếp qua cổng Isolate Port có sinh ra phụ tải (Overhead) làm chậm chính Main Isolate hay không. Để trả lời định lượng, đề tài xây dựng bài kiểm chuẩn độc lập Microbenchmark E3 (trong file test/overhead_bench_test.dart) đo lường độ trễ khứ hồi trên 200 lượt điều phối tác vụ:")
    add_p(doc, "Độ trễ Điều phối Khứ hồi Trung vị (Dispatch Latency p50): 0.34 ms (345 micro-giây).", bold_prefix="• ", bullet=True)
    add_p(doc, "Độ trễ Điều phối Khứ hồi Phân vị p95: 0.47 ms (467 micro-giây).", bold_prefix="• ", bullet=True)
    add_p(doc, "Độ trễ Điều phối Khứ hồi Phân vị p99: 0.73 ms (730 micro-giây).", bold_prefix="• ", bullet=True)
    add_p(doc, "So với ngân sách thời gian 16.67 ms của một khung hình 60 Hz, tổng chi phí điều phối của bộ lập lịch chỉ chiếm vỏn vẹn ~2.0% ngân sách frame. Đây là một con số hoàn toàn vô hình đối với cảm nhận thị giác của mắt người, khẳng định rằng lợi ích mang lại từ bộ lập lịch vượt trội gấp hàng trăm lần so với chi phí tính toán bỏ ra.")

    add_h2(doc, "4.7. Đánh giá Khả năng Khái quát hóa Liên Thiết bị (Cross-Device Evaluation)")
    add_p(doc, "Để chứng minh bộ lập lịch không bị 'học vẹt' hay quá khớp (overfitting) trên một con chip duy nhất, đề tài mở rộng toàn bộ ma trận thực nghiệm sang thiết bị tầm trung Xiaomi Redmi Note 13 sở hữu chip Helio G99 mạnh gấp 4 lần và màn hình 120 Hz với ngân sách khung hình cực kỳ ngặt nghèo (8.33 ms).")
    add_p(doc, "Bảng 4.3 đối chiếu kết quả thực nghiệm giữa hai thế hệ phần cứng:")

    headers_cross = ["Thiết bị & Kịch bản", "Chính sách", "Missed Frame (%)", "Jank Frame (%)", "Critical Latency p95", "Ghi chú Hiệu năng"]
    data_cross = [
        ["Galaxy A04e (60Hz)\nKịch bản S1 (L=64)", "P1 (FIFO)\nP3 (Chunk+Yield)\nP4 (AIMD+BP)", "23.2%\n0.8%\n0.8%", "9.9%\n17.0%\n8.0%", "35,356 ms\n31.0 ms\n28.0 ms", "P3/P4 mượt ngang baseline\nP4 giảm jank vượt trội"],
        ["Redmi Note 13 (120Hz)\nKịch bản S1 (L=256)", "P1 (FIFO)\nP2 (Pri+Aging)\nP3 (Chunk+Yield)", "61.6%\n59.6%\n1.21%", "34.7%\n32.1%\n0.12%", "63,278 ms (~63.3s)\n39,351 ms\n29.0 ms", "P1 rớt hơn 61% frame 120Hz\nP3 giảm trễ hơn 2.180 lần!"],
        ["Redmi Note 13 (120Hz)\nKịch bản S2 (L=128)", "P1 (FIFO)\nP3 (Chunk+Yield)\nP4 (AIMD+BP)", "33.5%\n1.19%\n1.22%", "13.2%\n0.14%\n0.03%", "33,501 ms (~33.5s)\n29.0 ms\n25.0 ms", "P4 jank gần như triệt tiêu (0.03%)\nHoàn thành sớm hơn 30.6 giây"]
    ]
    add_styled_table(doc, headers_cross, data_cross, col_widths=[1.8, 1.4, 1.2, 1.1, 1.4, 1.6], caption="Bảng 4.3: Đối chiếu hiệu năng đa nền tảng giữa Samsung Galaxy A04e (60Hz) và Xiaomi Redmi Note 13 (120Hz)")

    add_figure(doc, "figures/fig5_cross_device_comparison.png", "Hình 4.5: So sánh đối đầu hiệu năng giữa hai thế hệ thiết bị: Galaxy A04e (60Hz) và Redmi Note 13 (120Hz)", width_inches=6.0)

    add_callout(doc, "Kết quả khẳng định: Cơ chế FIFO thông thường (P1) thất bại trên cả máy mạnh màn 120Hz (rớt tới 61.6% frame và trễ hơn 1 phút). Ngược lại, giải pháp P3 và P4 thể hiện tính khái quát hóa xuất sắc: trên màn hình 120Hz khắt khe (ngân sách 8.33 ms), P3 vẫn giữ tỷ lệ rớt frame ở mức lý tưởng 1.21% (ngang baseline không tải 1.19%), và P4 dập tắt jank xuống mức kỷ lục 0.03%, đưa độ trễ Critical về 25.0 ms.", bold_title="> Nhận xét Khái quát hóa Liên Thiết bị: ")

    add_h2(doc, "4.8. Thực nghiệm Tác vụ Ảnh Thực tế (s_image) Trên Bộ 80 Ảnh DSLR 24MP")
    add_p(doc, "Để bác bỏ hoàn toàn nghi vấn cho rằng giải pháp chỉ hiệu quả trên các vòng lặp tính toán CPU giả lập (synthetic burn), đề tài tiến hành thực nghiệm kịch bản s_image trên bộ dữ liệu gồm 80 bức ảnh chụp DSLR nguyên bản (độ phân giải 6016×4016, 24MP, dung lượng 5.85–12.48 MB/ảnh) được nạp trực tiếp vào bộ nhớ ứng dụng.")
    add_p(doc, "Giao diện PhotoGrid đồng thời hiển thị lưới cuộn 3 cột nạp 80 ảnh thu nhỏ (thumbnail cacheWidth: 240) cuộn tự động ở tốc độ cao (1000 px/s). Các worker Isolate chạy nền liên tục mở file, phân tích header JPEG và tính toán histogram 256 mức theo cơ chế chunking lát cắt 256 KB. Bảng 4.4 tổng hợp kết quả 12 lượt đo chuẩn tắc trên máy ảo emulator-5554 (L = 16, W = 4, C = 80, 30s, n = 2 mỗi chính sách):")

    headers_img = ["Chính sách", "Tổng Frame Dựng", "Missed Frame (%)", "Frame p95 (ms)", "Raster p95 (ms)", "Critical Latency p95", "Tác vụ Hoàn thành"]
    data_img = [
        ["NONE (Baseline)", "550 frames", "69.5%", "142.8 ms", "73.0 ms", "– (Không tải)", "–"],
        ["P0 (Main Isolate)", "120 frames", "93.4%", "747.4 ms", "101.2 ms", "35,683 ms (~35.7s)", "29.1% (Tê liệt)"],
        ["P1 (FIFO Pool)", "385 frames", "78.6%", "248.2 ms", "123.5 ms", "26,589 ms (~26.6s)", "34.9%"],
        ["P2 (Priority+Aging)", "358 frames", "80.1%", "254.9 ms", "135.4 ms", "29,412 ms (~29.4s)", "41.1%"],
        ["P3 (Chunk+Yield)", "364 frames", "79.8%", "290.6 ms", "154.9 ms", "506.0 ms (Nhanh hơn 52x)", "31.9%"],
        ["P4 (AIMD+BP)", "510 frames", "71.6%", "154.5 ms", "80.4 ms", "286.0 ms (Nhanh hơn 93x)", "76.4%"]
    ]
    add_styled_table(doc, headers_img, data_img, col_widths=[1.5, 1.1, 1.2, 1.2, 1.2, 1.4, 1.2], caption="Bảng 4.4: Kết quả thực nghiệm kịch bản xử lý ảnh thật 24MP s_image kết hợp lưới cuộn ảnh UI")

    add_figure(doc, "figures/fig6_s_image_real_workload.png", "Hình 4.6: So sánh hiệu năng các chính sách trên kịch bản tác vụ ảnh thực tế s_image", width_inches=6.0)
    add_figure(doc, "figures/app_screen_80.png", "Hình 4.7: Giao diện ứng dụng thực nghiệm hiển thị lưới 80 ảnh DSLR thật kết hợp vòng xoay đo jank và Stack Monitor HUD", width_inches=4.0)

    add_callout(doc, "Kết quả thực nghiệm trên ảnh thật khẳng định: P4 đạt tới 510 frames (tiệm cận mức nền không tải 550 frames của GPU giả lập), giảm độ trễ khung hình p95 từ 747.4 ms ở P0 xuống 154.5 ms, và hạ độ trễ tương tác chạm Critical từ 35.7 giây xuống chỉ còn 286 ms (nhanh hơn 125 lần so với P0 và 93 lần so với P1), đồng thời tăng tỷ lệ hoàn thành tác vụ lên 76.4%.", bold_title="> Đánh giá Thực nghiệm Ảnh Thực tế: ")

    add_h2(doc, "4.9. Minh chứng Trực quan Thời Gian Thực qua Stack Monitor HUD")
    add_p(doc, "Để cung cấp bằng chứng trực quan không thể chối cãi phục vụ cho các buổi báo cáo trực tiếp, đề tài phát triển bảng điều khiển Stack Monitor HUD v2 hiển thị lớp kính mờ ngay trên đỉnh ứng dụng, phản ánh chính xác các thông số hoạt động của bộ lập lịch:")
    add_p(doc, "Bằng chứng về sự Thất bại của P0: Hình 4.8 ghi lại tình trạng tê liệt của P0. Đồng hồ FPS tụt xuống chỉ còn 10 FPS, tỷ lệ bỏ lỡ Miss vọt lên 84.3%, thời gian khung hình báo đỏ 66.7 ms (p95 lên tới 250.0 ms), biểu đồ 40 cột đỏ rực vượt quá vạch ngân sách 16.7 ms, và vòng xoay góc phải bị khựng cứng.", bold_prefix="• Minh chứng 1 (P0): ", bullet=True)
    add_p(doc, "Bằng chứng về Bước ngoặt Mượt mà của P3: Hình 4.9 minh chứng huy hiệu màu vàng ● YIELDING bật sáng, báo hiệu bộ lập lịch đang chủ động nhường luồng cho UI. Tốc độ khung hình đạt chuẩn 60 FPS, Frame Time giảm sâu xuống 7.6 ms (p95 đạt 12.1 ms), và biểu đồ sparkline tụt hẳn xuống thành các cột xanh ngọc lục bảo gọn ghẽ dưới vạch đỏ 16.7 ms.", bold_prefix="• Minh chứng 2 (P3): ", bullet=True)
    add_p(doc, "Bằng chứng về Năng lực Tự Thích ứng của P4: Hình 4.10 ghi lại khoảnh khắc tải bùng nổ 16x. Thuật toán AIMD tự động khóa chặt 3 worker (hiển thị rõ 3 ổ khóa vàng 🔒 cùng dòng 1/1 (AIMD khóa 3)), ô xả tải báo Drop: 938 tác vụ nền dư thừa. Nhờ sự điều tiết linh hoạt này, giao diện vẫn giữ trọn 60 FPS và tác vụ Critical đạt mức xanh lý tưởng: 85 ms (< 100 ms).", bold_prefix="• Minh chứng 3 (P4): ", bullet=True)

    add_figure(doc, "figures/hud_v2_p0.png", "Hình 4.8: Ảnh chụp Stack Monitor HUD ở chính sách P0 - Giao diện tê liệt, 10 FPS, 40 cột đỏ vượt ngân sách 16.7ms", width_inches=4.2)
    add_figure(doc, "figures/hud_v2_p3.png", "Hình 4.9: Ảnh chụp Stack Monitor HUD ở chính sách P3 - Bật cờ YIELDING, 60 FPS mượt mà, toàn bộ cột xanh dưới vạch 16.7ms", width_inches=4.2)
    add_figure(doc, "figures/hud_v2_p4.png", "Hình 4.10: Ảnh chụp Stack Monitor HUD ở chính sách P4 - Tự động khóa 3 worker (1/1 AIMD khóa 3), xả tải Drop 938 task, giữ vững 60 FPS và Crit p95 = 85ms", width_inches=4.2)

    # =========================================================================
    # CHƯƠNG 5
    # =========================================================================
    add_h1(doc, "CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    
    add_h2(doc, "5.1. Các Đóng góp Chính của Đề tài")
    add_p(doc, "Đề tài đã giải quyết trọn vẹn bài toán tối ưu hóa đa mục tiêu giữa độ mượt giao diện (UI UX) và thông lượng xử lý nền trên nền tảng di động Flutter, đạt được các đóng góp khoa học và thực tiễn nổi bật sau:")
    add_p(doc, "Mô hình hóa Khoa học Bài toán Lập lịch Tầng Ứng dụng: Chỉ ra nghịch lý 'bất cân xứng nhận thức' (Semantic Blindness) của hệ điều hành và chứng minh rằng tầng ứng dụng bắt buộc phải chủ động tự điều phối tài nguyên thay vì phó mặc cho kernel CFS.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Phát triển Kiến trúc Bộ Lập lịch Thích ứng Đa cấp độ: Hiện thực hóa thành công chuỗi 5 chính sách (P0 đến P4) với 6 kỹ thuật cốt lõi: Hàng đợi ưu tiên 3 mức O(1), Thuật toán Aging chống bỏ đói, Cooperative Chunking băm nhỏ tác vụ giải quyết rào cản bất khả ngắt của Isolate, Critical Worker Reserve bảo vệ thao tác người dùng, Frame Yielding nhường nhịp Vsync, và Điều khiển phản hồi thích ứng AIMD kết hợp máy trạng thái suy giảm môi trường.", bold_prefix="2. ", bullet=True)
    add_p(doc, "Bộ Dữ liệu Thực nghiệm Chuẩn mực trên Phần cứng Thật: Xây dựng hệ thống đo lường tự động hóa, thu thập hàng trăm lượt đo chuẩn tắc trên thiết bị thật (Samsung Galaxy A04e và Xiaomi Redmi Note 13), chứng minh bằng kiểm định thống kê Mann-Whitney U (p < 0.05) rằng giải pháp giúp giảm tỷ lệ rớt frame từ 23.2% xuống 0.8%, kéo giảm độ trễ tương tác từ hơn 35 giây xuống còn 28.0 ms (nhanh hơn 1.200 lần) với chi phí phụ tải điều phối chỉ chiếm ~2.0% ngân sách frame.", bold_prefix="3. ", bullet=True)
    add_p(doc, "Kiểm chứng Thực tế trên Tác vụ Ảnh 24MP và Công cụ Trực quan HUD: Chứng minh tính khả thi trên tập 80 bức ảnh DSLR kích thước lớn và cung cấp công cụ Stack Monitor HUD theo thời gian thực phục vụ quan sát minh bạch.", bold_prefix="4. ", bullet=True)

    add_h2(doc, "5.2. Những Hạn chế Còn Tồn tại")
    add_p(doc, "Bên cạnh các thành quả đạt được, đề tài còn ghi nhận một số hạn chế khách quan:")
    add_p(doc, "Giới hạn của Mô hình Đa nhiệm Hợp tác: Giải pháp Chunking đòi hỏi mã nguồn Dart phải được phân rã thành các bước lặp. Đối với các thư viện native C/C++ nguyên khối gọi qua Dart FFI mà không hỗ trợ callback tiến độ, hệ thống chưa thể ngắt giữa chừng mà phải dựa hoàn toàn vào cơ chế Worker Reserve và khóa trần AIMD.", bold_prefix="• ", bullet=True)
    add_p(doc, "Giới hạn Truy cập Cảm biến Tầng Sâu: Việc thu thập chỉ số tiêu thụ năng lượng (mW) chi tiết của từng nhân CPU đòi hỏi quyền truy cập root vào hệ thống tệp tin /sys/class/power_supply, vốn không khả dụng trên các thiết bị thương mại của người dùng thông thường.", bold_prefix="• ", bullet=True)

    add_h2(doc, "5.3. Hướng Nghiên cứu và Phát triển Tiếp theo")
    add_p(doc, "Từ những nền tảng vững chắc đã thiết lập, hướng phát triển tiếp theo của đề tài bao gồm:")
    add_p(doc, "Đóng gói Thư viện Mã Nguồn Mở: Hoàn thiện API và phát hành bộ lập lịch thành một package độc lập trên hệ sinh thái pub.dev để cộng đồng lập trình viên Flutter có thể dễ dàng tích hợp vào các dự án thương mại.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Nghiên cứu Dự đoán Tải Thông minh: Ứng dụng các mô hình học máy siêu nhẹ (TinyML) chạy trên bộ gia tốc NPU di động để dự đoán trước khối lượng công việc của tác vụ và tự động đề xuất kích thước chunk tối ưu theo thời gian thực.", bold_prefix="2. ", bullet=True)
    add_p(doc, "Hỗ trợ Mở rộng Đa Nền tảng: Đưa các cơ chế tín hiệu thích ứng mở rộng sang nền tảng iOS (thông qua Apple Metal và Thermal State API) và nền tảng Web (Web Workers).", bold_prefix="3. ", bullet=True)

    # =========================================================================
    # TÀI LIỆU THAM KHẢO
    # =========================================================================
    add_h1(doc, "TÀI LIỆU THAM KHẢO")
    
    refs = [
        "[1] Google Flutter Team, \"Flutter architectural overview: The engine, framework, and rendering pipeline,\" Flutter Documentation, 2024. [Online]. Available: https://docs.flutter.dev/resources/architectural-overview.",
        "[2] Dart Language Team, \"Concurrency in Dart: Isolates and Event Loops,\" Dart Language Guide, 2024. [Online]. Available: https://dart.dev/language/concurrency.",
        "[3] Android Open Source Project, \"Completely Fair Scheduler (CFS) and Energy-Aware Scheduling (EAS) in Android,\" Android Core Technologies Documentation, 2023.",
        "[4] Android Developers, \"Profile your app performance with FrameTiming and dumpsys gfxinfo,\" Android Performance Guides, 2024.",
        "[5] V. Jacobson, \"Congestion avoidance and control,\" in ACM SIGCOMM Computer Communication Review, vol. 18, no. 4, pp. 314–329, 1988.",
        "[6] J. D. C. Little, \"A proof for the queuing formula: L = λW,\" Operations Research, vol. 9, no. 3, pp. 383–387, 1961.",
        "[7] G. M. Amdahl, \"Validity of the single processor approach to achieving large scale computing capabilities,\" in AFIPS Conference Proceedings, vol. 30, pp. 483–485, 1967.",
        "[8] Apple Inc., \"Energy Efficiency Guide for iOS Apps: Managing Quality of Service (QoS),\" Apple Developer Documentation, 2022.",
        "[9] React Team, \"Inside React Scheduler: Cooperative multitasking and time slicing in modern user interfaces,\" Meta Open Source, 2023.",
        "[10] H. B. Mann and D. R. Whitney, \"On a test of whether one of two random variables is stochastically larger than the other,\" The Annals of Mathematical Statistics, vol. 18, no. 1, pp. 50–60, 1947."
    ]
    for r in refs:
        add_p(doc, r, bullet=False)

    print("Hoàn tất chèn toàn bộ nội dung học thuật!")

def update_table_of_contents_and_settings(doc_path):
    print("Cập nhật cờ updateFields trong settings.xml...")
    import zipfile
    import tempfile
    
    temp_dir = tempfile.mkdtemp()
    temp_zip = os.path.join(temp_dir, 'temp.docx')
    shutil.copyfile(doc_path, temp_zip)
    
    extract_dir = os.path.join(temp_dir, 'extracted')
    with zipfile.ZipFile(temp_zip, 'r') as z:
        z.extractall(extract_dir)
        
    settings_file = os.path.join(extract_dir, 'word', 'settings.xml')
    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'w:updateFields' not in content:
            # Thêm <w:updateFields w:val="true"/> vào settings.xml
            idx = content.find('</w:settings>')
            if idx != -1:
                new_content = content[:idx] + '<w:updateFields xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="true"/>' + content[idx:]
                with open(settings_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("Đã thêm w:updateFields thành công vào settings.xml!")

    # Đóng gói lại thành docx hoàn chỉnh
    shutil.make_archive(os.path.join(temp_dir, 'new_doc'), 'zip', extract_dir)
    shutil.move(os.path.join(temp_dir, 'new_doc.zip'), doc_path)
    shutil.rmtree(temp_dir)
    print("Đã đóng gói tài liệu Word hoàn chỉnh:", doc_path)

def main():
    print("Bắt đầu xử lý file docx...")
    if not os.path.exists(DOC_IN):
        shutil.copyfile('bc.docx', DOC_IN)
        
    doc = docx.Document(DOC_IN)
    build_thesis_content(doc)
    doc.save(DOC_OUT)
    print("Đã lưu bản nháp tại:", DOC_OUT)
    
    update_table_of_contents_and_settings(DOC_OUT)
    print("HOÀN TẤT TOÀN BỘ QUÁ TRÌNH!")

if __name__ == '__main__':
    main()
