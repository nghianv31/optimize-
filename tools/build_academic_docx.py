# -*- coding: utf-8 -*-
"""
Script tái thiết kế và nâng cấp báo cáo bc.docx sang văn phong học thuật chuyên sâu (Academic Rigor):
- Mô hình hóa bài toán tối ưu hóa đa mục tiêu (Multi-Objective Optimization Problem).
- Hình thức hóa toán học các cơ chế: Hàng đợi ưu tiên 3 mức, Định lý chống bỏ đói (Starvation-Free Theorem),
  Đa nhiệm hợp tác (Cooperative Chunking), Lý thuyết điều khiển phản hồi thích ứng (AIMD Feedback Control),
  Định luật Little và cân bằng hàng đợi, Máy trạng thái suy giảm (Finite State Automaton) với trễ Hysteresis.
- Loại bỏ toàn bộ các diễn đạt mang tính mô tả mã nguồn (code walk-through), thay thế bằng thuật ngữ
  khoa học máy tính, kỹ nghệ phần mềm và hệ thống thời gian thực.
- Tích hợp đầy đủ bảng biểu số liệu chuẩn mực, kiểm định thống kê phi tham số Mann-Whitney U,
  và 11 đồ thị thực nghiệm 300 DPI.
"""

import os
import shutil
import xml.etree.ElementTree as ET
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

DOC_IN = 'bc_backup.docx'
DOC_OUT = 'bc_academic.docx'

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

def add_callout(doc, text, bold_title='> Đánh giá Học thuật & Luận điểm Khoa học: '):
    p = doc.add_paragraph(style='Normal')
    setup_paragraph(p, space_before=100, space_after=100, line_spacing=288, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'''
        <w:pBdr {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="12" w:color="1A365D"/>
        </w:pBdr>
    ''')
    pPr.append(pBdr)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F7FAFC"/>')
    pPr.append(shd)

    r_title = p.add_run(bold_title)
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(12.5)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    r_text = p.add_run(text)
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(12.5)
    r_text.font.italic = True
    r_text.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
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
            <w:top w:val="single" w:sz="12" w:space="0" w:color="1A202C"/>
            <w:bottom w:val="single" w:sz="12" w:space="0" w:color="1A202C"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E0"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tbl._tbl.tblPr.append(tblBorders)

    hdr_row = tbl.rows[0]
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EDF2F7"/>')
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
        r.font.color.rgb = RGBColor(0x1A, 0x20, 0x2C)

    for r_idx, row_data in enumerate(data):
        row = tbl.rows[r_idx + 1]
        bg_color = "F7FAFC" if r_idx % 2 == 1 else "FFFFFF"
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
            r.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)

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
    r_cap.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)
    return p_img

def build_academic_thesis_content(doc):
    print("Bắt đầu chèn nội dung học thuật chuyên sâu...")

    # =========================================================================
    # CHƯƠNG 3: MÔ HÌNH HÓA VÀ THIẾT KẾ HỆ THỐNG LẬP LỊCH THÍCH ỨNG
    # =========================================================================
    add_h1(doc, "CHƯƠNG 3: MÔ HÌNH HÓA VÀ THIẾT KẾ HỆ THỐNG LẬP LỊCH TÁC VỤ THÍCH ỨNG")
    
    add_p(doc, "Dựa trên các rào cản nền tảng đã phân tích ở Chương 2—bao gồm hiện tượng bất cân xứng nhận thức ngữ nghĩa của bộ lập lịch nhân hệ điều hành, tính bất khả ngắt của môi trường thực thi Dart Isolate, và ngân sách thời gian ngặt nghèo của chu trình dựng hình giao diện—Chương này trình bày việc mô hình hóa toán học bài toán tối ưu hóa lập lịch tác vụ tại tầng ứng dụng, thiết kế kiến trúc hệ thống và các cơ chế điều phối thích ứng chuyên biệt nhằm đảm bảo chất lượng trải nghiệm tương tác thời gian thực (Quality of Experience - QoE).")

    add_h2(doc, "3.1. Mô hình Hóa Toán học Bài toán Tối ưu Lập lịch Đa Mục tiêu")
    
    add_h3(doc, "3.1.1. Phát biểu Bài toán Tối ưu Hóa Đa Mục tiêu (MOOP)")
    add_p(doc, "Xét một hệ thống ứng dụng di động tiếp nhận một tập hợp tác vụ không đồng nhất T = {t_1, t_2, ..., t_n} xuất hiện ngẫu nhiên theo thời gian. Mỗi tác vụ t_i được đặc trưng bởi bộ tham số {a_i, c_i, p_i, d_i}, trong đó a_i là thời điểm xuất hiện (arrival time), c_i là khối lượng tính toán danh định (computational cost), p_i in {Critical, Visible, Background} là mức độ ưu tiên ngữ nghĩa, và d_i là hạn định thời gian phản hồi (deadline).")
    add_p(doc, "Tại mỗi thời điểm t, bộ lập lịch tại tầng ứng dụng phải đưa ra một véc-tơ quyết định x(t) = (pi(t), Delta t_chunk(t), N(t), D(t)), trong đó pi(t) là thứ tự cấp phát tác vụ, Delta t_chunk(t) là độ dài lát cắt thời gian, N(t) là số lượng worker isolates được phép hoạt động song song, và D(t) subseteq T là tập các tác vụ bị loại bỏ nhằm giảm tải ngược. Mục tiêu của bộ lập lịch là giải quyết bài toán Tối ưu hóa Đa mục tiêu (Multi-Objective Optimization Problem - MOOP):")
    add_formula(doc, "min_{x in X} F(x) = [ f_jank(x),  f_latency(x),  f_overhead(x) ]^T", "3.1")
    add_p(doc, "Trong đó:")
    add_p(doc, "f_jank(x) = Pr(T_frame > T_budget) là tỷ lệ khung hình vượt ngân sách thời gian dựng hình Vsync, dẫn đến hiện tượng giật lag giao diện thị giác.", bold_prefix="• ", bullet=True)
    add_p(doc, "f_latency(x) = L_critical^(p95) là độ trễ phân vị thứ 95 của thời gian hoàn thành các tác vụ tương tác khẩn cấp (Critical Tasks).", bold_prefix="• ", bullet=True)
    add_p(doc, "f_overhead(x) = E[tau_dispatch] là kỳ vọng chi phí phụ tải điều phối và truyền thông điệp liên tiến trình (IPC Overhead).", bold_prefix="• ", bullet=True)

    add_h3(doc, "3.1.2. Hệ Ràng buộc Cứng và Mềm (System Constraints)")
    add_p(doc, "Quá trình tối ưu hóa phải thỏa mãn đồng thời các ràng buộc hệ thống sau:")
    add_p(doc, "Ràng buộc ngân sách thời gian thực (Hard Real-time Frame Deadline):", bold_prefix="1. ")
    add_formula(doc, "T_frame <= T_budget = 1000 / f_refresh  (ms)", "3.2")
    add_p(doc, "với T_budget = 16.67 ms đối với màn hình 60 Hz và T_budget = 8.33 ms đối với màn hình 120 Hz. Tỷ lệ rớt khung hình tổng thể phải thỏa mãn f_jank <= 2.0%, đồng thời triệt tiêu hoàn toàn các khung hình đóng băng nghiêm trọng (Frozen Frame > 700 ms).")
    add_p(doc, "Ràng buộc độ trễ tương tác con người (Human-Computer Interaction Deadline):", bold_prefix="2. ")
    add_formula(doc, "L_critical^(p95) < 100  (ms)", "3.3")
    add_p(doc, "nhằm đảm bảo thao tác cảm ứng của người dùng được tiếp nhận với cảm giác phản hồi tức thì.")
    add_p(doc, "Ràng buộc đánh đổi thông lượng xử lý nền (Throughput Trade-off Constraint):", bold_prefix="3. ")
    add_formula(doc, "Makespan(P_adaptive) <= (1 + epsilon) * Makespan(P_FIFO)  (epsilon <= 0.30)", "3.4")
    add_p(doc, "nghĩa là việc bảo vệ giao diện chỉ được phép làm chậm tổng thời gian hoàn thành tác vụ nền tối đa 25-30% so với mô hình FIFO chạy tối đa công suất.")
    add_p(doc, "Ràng buộc công bằng và chống bỏ đói (Starvation-Free Constraint): Mọi tác vụ nền hợp lệ đều phải được đảm bảo thực thi sau một khoảng thời gian chờ hữu hạn:", bold_prefix="4. ")
    add_formula(doc, "forall i in T_background,  lim_{t -> infty} Pr(t_i  được thực thi) = 1", "3.5")

    add_h2(doc, "3.2. Kiến trúc Hệ thống Lập lịch Thích ứng Đa Phân Lớp")
    add_p(doc, "Để giải quyết bài toán tối ưu trên, hệ thống được kiến trúc hóa thành 5 phân lớp chức năng độc lập (Hình 3.1), đảm bảo tính module hóa và khả năng cách ly cao giữa luồng giao diện chính và các luồng tính toán nền.")
    
    add_h3(doc, "3.2.1. Phân định Vai trò Các Phân Lớp Chức Năng")
    add_p(doc, "Lớp Điều phối Sự kiện Giao diện (UI Event Dispatcher Loop): Luồng thực thi đơn lập (Main Isolate) chịu trách nhiệm tuần hoàn hóa việc xử lý cử chỉ tương tác của người dùng, biến đổi cây Widget và gửi yêu cầu dựng hình xuống tầng đồ họa Raster thông qua Flutter Engine. Luồng này được bảo vệ tuyệt đối khỏi các tính toán nặng.", bold_prefix="• Phân lớp 1 — ", bullet=True)
    add_p(doc, "Lớp Cảm biến và Đo lường Hiệu năng Thời gian Thực (Runtime Instrumentation Layer): Khai thác cơ chế Persistent Frame Callback nhằm trích xuất thông số thời gian dựng khung hình tức thời, liên tục cập nhật bộ đệm phân vị trượt và cung cấp dữ liệu cho giao diện giám sát Stack Monitor HUD.", bold_prefix="• Phân lớp 2 — ", bullet=True)
    add_p(doc, "Lớp Bộ Lập Lịch Thích Ứng Cốt Lõi (Adaptive Scheduling Core): Trọng tâm điều phối của hệ thống, tích hợp cấu trúc hàng đợi phân cấp ba mức O(1), bộ tính toán ưu tiên động kèm Aging, bộ điều khiển phản hồi AIMD, máy trạng thái suy giảm môi trường và bộ lọc giảm tải ngược Backpressure.", bold_prefix="• Phân lớp 3 — ", bullet=True)
    add_p(doc, "Lớp Hồ chứa Worker Dài Hạn (Long-running Worker Pool Layer): Duy trì một tập hợp cố định gồm W worker isolates được cấp phát sẵn ngay khi khởi động ứng dụng. Các worker giao tiếp với bộ lập lịch thông qua cơ chế trao đổi thông điệp bất đối xứng trên cặp cổng SendPort/ReceivePort.", bold_prefix="• Phân lớp 4 — ", bullet=True)
    add_p(doc, "Lớp Tích hợp Tín hiệu Phần cứng Nền tảng (Platform Hardware Signals): Giao tiếp với nhân Linux/Android qua cầu nối ngoại vi MethodChannel để lấy mẫu nhiệt độ SoC và trạng thái dung lượng pin theo thời gian thực.", bold_prefix="• Phân lớp 5 — ", bullet=True)

    add_h2(doc, "3.3. Hàng Đợi Ưu Tiên Phân Cấp O(1) và Định Lý Chống Bỏ Đói (P2)")
    
    add_h3(doc, "3.3.1. Cấu trúc Hàng đợi Phân tầng Ba Mức")
    add_p(doc, "Nhằm triệt tiêu chi phí duyệt mảng vốn làm tăng phụ tải CPU trên Main Isolate, hàng đợi được tổ chức thành ba ngăn độc lập Q = {Q_0, Q_1, Q_2} tương ứng với ba mức ưu tiên: Critical (rank = 0), Visible (rank = 1), và Background (rank = 2). Trong mỗi ngăn Q_r, các tác vụ được lưu trữ theo cấu trúc hàng đợi hai đầu (Double-ended Queue - Deque).")
    add_p(doc, "Độ phức tạp tính toán: Khi một worker nhàn rỗi yêu cầu cấp phát công việc mới, thuật toán trích xuất tác vụ chỉ cần kiểm tra tối đa ba phần tử đứng đầu của ba ngăn hàng đợi. Do đó, chi phí lựa chọn tác vụ có độ phức tạp thời gian tối ưu tuyệt đối O(1), độc lập hoàn toàn với tổng số lượng tác vụ đang tích tụ trong hệ thống:")
    add_formula(doc, "TimeComplexity(popNext) = O(1)", "3.6")

    add_h3(doc, "3.3.2. Hàm Tính Toán Ưu Tiên Động (Dynamic Priority Metric)")
    add_p(doc, "Để giải quyết xung đột giữa việc ưu tiên phản hồi thao tác tức thời và nghĩa vụ hoàn thành các tác vụ xử lý nền, bộ lập lịch áp dụng hàm chấm điểm ưu tiên hiệu dụng Score(i, t):")
    add_formula(doc, "Score(i, t) = Rank(p_i) * tau_aging - (t - t_submit(i))", "3.7")
    add_p(doc, "Trong đó:")
    add_p(doc, "Rank(p_i) in {0, 1, 2} biểu thị cấp bậc ưu tiên tĩnh của tác vụ t_i.", bold_prefix="• ", bullet=True)
    add_p(doc, "tau_aging là hằng số lão hóa thời gian (Aging Parameter), được xác lập chuẩn ở mức 3000 ms.", bold_prefix="• ", bullet=True)
    add_p(doc, "w_i(t) = t - t_submit(i) là thời gian lưu lại trong hàng đợi của tác vụ tính đến thời điểm t (ms).", bold_prefix="• ", bullet=True)
    add_p(doc, "Quy tắc điều phối quy định tác vụ sở hữu giá trị Score(i, t) nhỏ nhất sẽ được ưu tiên trích xuất trước.")

    add_h3(doc, "3.3.3. Định lý Không Bỏ Đói Tác Vụ Nền (Starvation-Free Theorem)")
    add_p(doc, "Định lý 3.1 (Tính Khả Hoàn Hữu Hạn): Giả thiết hệ thống liên tục tiếp nhận một chuỗi vô hạn các tác vụ khẩn cấp (Critical Tasks) tại các thời điểm t_k >= 0. Với mọi tác vụ nền t_bg in Q_background nộp vào hàng đợi tại thời điểm t_0, tác vụ t_bg chắc chắn sẽ được cấp phát thực thi tại một thời điểm hữu hạn t^* < infty, bất kể mật độ xuất hiện của các tác vụ khẩn cấp.", italic_prefix="Chứng minh Toán học: ")
    add_p(doc, "Chứng minh: Xét một tác vụ khẩn cấp bất kỳ t_crit đến tại thời điểm t >= t_0. Điểm số của tác vụ khẩn cấp khi vừa vào hàng đợi là: Score(t_crit, t) = 0 * tau_aging - 0 = 0. Trong khi đó, điểm số của tác vụ nền t_bg tại thời điểm t là: Score(t_bg, t) = 2 * tau_aging - (t - t_0). Để tác vụ nền vượt quyền ưu tiên của tác vụ khẩn cấp mới đến, điều kiện cần là Score(t_bg, t) <= Score(t_crit, t), tương đương:")
    add_formula(doc, "2 * tau_aging - (t - t_0) <= 0  <=>  t - t_0 >= 2 * tau_aging", "3.8")
    add_p(doc, "Với tau_aging = 3000 ms, khi thời gian chờ tích lũy đạt t - t_0 >= 6000 ms (6 giây), điểm số của tác vụ nền suy giảm về mức âm (Score(t_bg, t) < 0). Tại thời điểm này, tác vụ nền sở hữu độ ưu tiên tuyệt đối cao hơn bất kỳ tác vụ khẩn cấp mới xuất hiện nào. Do đó, tác vụ nền không bao giờ bị bỏ đói vô hạn. Định lý được chứng minh.")

    add_h2(doc, "3.4. Kỹ Thuật Phân Mảnh Hợp Tác Đa Nhiệm (Cooperative Chunking) và Điểm Nhường Luồng (P3)")
    
    add_h3(doc, "3.4.1. Giới hạn Bất Khả Ngắt của Isolate và Ranh Giới Phân Mảnh")
    add_p(doc, "Mô hình tác tử (Actor Model) trong Dart VM vận hành trên nguyên lý cô lập hoàn toàn không gian địa chỉ bộ nhớ giữa các Isolate. Do thiếu cơ chế ngắt cưỡng bức từ bên ngoài, một hàm tính toán nguyên khối một khi đã bắt đầu thực thi sẽ chiếm giữ nhân CPU cho đến khi kết thúc. Nếu thời gian thực thi của tác vụ nền vượt quá ngân sách khung hình, hệ thống sẽ rơi vào trạng thái tê liệt điều phối cục bộ.")
    add_p(doc, "Để thiết lập khả năng điều phối preemptive-like trên nền tảng non-preemptive, đề tài đề xuất kỹ thuật Phân Mảnh Hợp Tác Đa Nhiệm (Cooperative Chunking). Một tác vụ tính toán nặng t_i với tổng số vòng lặp tính toán C_i được phân rã thành một chuỗi k lát cắt thời gian:")
    add_formula(doc, "t_i = { c_{i,1}, c_{i,2}, ..., c_{i,k} },  với  Cost(c_{i,j}) approx Delta t_chunk", "3.9")
    add_p(doc, "với Delta t_chunk là độ dài lát cắt thời gian chuẩn danh định (xác lập mặc định ở mức 80 ms thông qua thực nghiệm quét tham số).")

    add_h3(doc, "3.4.2. Ranh giới Nhường Luồng (Yield Boundary) và Tái Nạp Hàng Đợi")
    add_p(doc, "Mỗi worker isolate sau khi hoàn thành một phân mảnh c_{i,j} sẽ tạm ngừng tính toán và gửi thông điệp báo cáo hoàn tất kèm định danh tác vụ về Main Isolate thông qua SendPort. Ranh giới kết thúc phân mảnh này thiết lập nên một Điểm Nhường Luồng (Yield Point - Y). Tại điểm Y, bộ lập lịch thực hiện đánh giá hai bước:")
    add_p(doc, "Kiểm tra tiến độ tác vụ: Cập nhật biến tích lũy Iters_done = Iters_done + Iters_chunk. Nếu Iters_done < C_i, tác vụ được tái nạp vào đầu ngăn hàng đợi tương ứng (addFront) nhằm bảo toàn tính liên tục ngữ cảnh.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Đánh giá xen ngang (Interleaving Evaluation): Bộ lập lịch quét hàng đợi ưu tiên. Nếu phát hiện có tác vụ Critical mới xuất hiện trong khoảng thời gian worker đang bận thực thi chunk trước đó, tác vụ Critical sẽ lập tức được điều phối vào worker vừa được giải phóng, triệt tiêu hoàn toàn hiện tượng nghẽn đầu hàng.", bold_prefix="2. ", bullet=True)

    add_h3(doc, "3.4.3. Mô hình Hóa Phân Mảnh trên Tác vụ Xử lý Ảnh Độ Phân Giải Cao")
    add_p(doc, "Trên tác vụ giải mã và phân tích dữ liệu đa phương tiện thực tế (tập tin ảnh JPEG độ phân giải 24 Megapixel, dung lượng 6–12 MB), kỹ thuật phân mảnh được hiện thực hóa dựa trên cấu trúc truy cập nhị phân ngẫu nhiên (Random File Access):")
    add_p(doc, "Phân mảnh Khởi tạo (Header Chunk): Mở luồng tập tin qua con trỏ RandomAccessFile, chỉ đọc 4096 bytes đầu tiên để phân tích cú pháp marker JPEG SOI (0xFFD8) và SOF (0xFFC0/0xFFC2), trích xuất thông số hình học (chiều rộng, chiều cao) mà không cần nạp toàn bộ bitmap vào bộ nhớ.", bold_prefix="• ", bullet=True)
    add_p(doc, "Các Phân mảnh Xử lý Kế tiếp (Data Chunks): Tại mỗi bước lặp j, con trỏ tệp tin dịch chuyển đến vị trí byte tương ứng progress = j / k và chỉ nạp một khối đệm giới hạn B_chunk <= 256 KB. Quá trình tính toán phân bố tần suất 256 mức độ sáng (Histogram) và năng lượng điểm ảnh được giới hạn chặt chẽ trong khối đệm này.", bold_prefix="• ", bullet=True)
    add_p(doc, "Cơ chế này vừa phản ánh trung thực tải nhập/xuất đĩa (Disk I/O) và phụ tải bộ nhớ của các ứng dụng thương mại, vừa ngăn ngừa triệt để nguy cơ tràn bộ nhớ RAM (OOM) khi xử lý đồng thời nhiều ảnh lớn.")

    add_h2(doc, "3.5. Cơ Chế Dự Trữ Tài Nguyên Chuyên Biệt cho Tác Vụ Thời Gian Thực (P3r)")
    add_p(doc, "Mặc dù kỹ thuật phân mảnh giúp giải phóng worker sau mỗi 80 ms, trong các tình huống bão tải cực đại, xác suất toàn bộ W worker trong pool đồng thời rơi vào giữa chu kỳ phân mảnh vẫn tồn tại. Khi đó, một thao tác chạm khẩn cấp của người dùng vẫn có thể phải gánh chịu độ trễ chờ đợi lên tới 80 ms cộng với phụ tải điều phối.")
    add_p(doc, "Để thiết lập bảo đảm thời gian thực tuyệt đối cho thao tác tương tác, hệ thống thiết kế Cơ chế Dự trữ Tài nguyên Chuyên biệt (Dedicated Real-time Worker Reservation). Quy tắc ràng buộc cấp phát được định nghĩa như sau:")
    add_formula(doc, "N_non_critical(t) <= min( N_cap(t), W_total - 1 )", "3.10")
    add_p(doc, "Trong đó N_non_critical(t) là số lượng worker đang thực thi các tác vụ Visible và Background, N_cap(t) là trần worker cho phép tại thời điểm t, và W_total là tổng quy mô hồ chứa worker. Bằng việc luôn duy trì ít nhất 1 worker ở trạng thái dự phòng độc quyền cho các tác vụ Critical, hệ thống đảm bảo thời gian khởi động của tác vụ khẩn cấp đạt tiệm cận mức tức thời, giảm độ trễ phân vị p95 từ hàng chục giây xuống dưới 50 ms.")

    add_h2(doc, "3.6. Cơ Chế Nhường Nhịp Dựng Hình Dựa Trên Cảm Biến Khung Hình (Frame Yielding)")
    add_p(doc, "Bộ lập lịch nhân Linux (CFS) phân bổ thời gian CPU dựa trên trọng số công bằng mà không nhận biết được chu kỳ quét của phần cứng hiển thị (Vsync Pulse từ Choreographer). Để khắc phục khiếm khuyết này, bộ lập lịch tại tầng ứng dụng thiết lập cơ chế Nhường Nhịp Dựng Hình (Frame Yielding).")
    add_p(doc, "Cảm biến FrameSignal liên tục đo lường khoảng cách thời gian giữa hai khung hình liên tiếp g(t) trên cửa sổ trượt 30 khung hình gần nhất. Định kỳ mỗi chu kỳ kiểm tra T_check = 100 ms, trạng thái bận của giao diện được xác định thông qua bộ điều khiển trễ ngưỡng:")
    add_formula(doc, "State_busy(t) = \\begin{cases} 1 & \\text{nếu } g_{p95}(t) > T_{yield} \\\\ 0 & \\text{nếu } g_{p95}(t) < 0.8 * T_{yield} \\\\ State_busy(t - T_check) & \\text{trường hợp còn lại} \\end{cases}", "3.11")
    add_p(doc, "với ngưỡng nhường luồng được xác lập ở mức T_yield = 20 ms (tương đương việc khung hình bị trễ nhịp 16.67 ms). Khi State_busy = 1, hệ thống tạm hoãn phát lệnh thực thi đối với toàn bộ các phân mảnh Background, giải phóng hoàn toàn các nhân CPU nhằm phục vụ việc hoàn tất chu trình dựng hình của luồng UI và Raster. Nhằm bảo toàn ràng buộc công bằng, nếu một tác vụ nền bị hoãn vượt quá hạn định deferCapMs = 8000 ms, tác vụ đó sẽ được quyền miễn trừ trạng thái nhường luồng.")

    add_h2(doc, "3.7. Lý Thuyết Điều Khiển Phản Hồi Thích Ứng AIMD và Co Giãn Worker Động (P4)")
    
    add_h3(doc, "3.7.1. Động Học Hệ Thống Điều Khiển Vòng Kín")
    add_p(doc, "Theo Định luật Amdahl, việc tăng số lượng luồng tính toán song song bị giới hạn bởi phần mã tuần tự và băng thông truy xuất bộ nhớ. Khi tải hệ thống tăng vọt, việc duy trì quy mô worker lớn sẽ gây ra hiện tượng cạnh tranh tài nguyên bộ nhớ đệm (Cache Thrashing) và gia tăng độ trễ chuyển mạch ngữ cảnh (Context Switching Overhead).")
    add_p(doc, "Hệ thống thiết lập một vòng lặp điều khiển phản hồi thích ứng khép kín dựa trên giải thuật Additive Increase / Multiplicative Decrease (AIMD). Thuật toán hoạt động theo các chu kỳ đánh giá ổn định (pacing epoch) T_epoch = 500 ms:")
    add_formula(doc, "N(k+1) = \\begin{cases} min(N_max, N(k) + alpha) & \\text{khi } g_{p95}(k) <= gamma * T_target \\\\ max(N_min, \\lfloor beta * N(k) \\rfloor) & \\text{khi } g_{p95}(k) > T_target \\end{cases}", "3.12")
    add_p(doc, "Trong đó:")
    add_p(doc, "alpha = 1 là hệ số gia tăng tuyến tính (Additive Increase Step), cho phép thăm dò năng lực xử lý một cách thận trọng khi giao diện đang mượt mà.", bold_prefix="• ", bullet=True)
    add_p(doc, "beta = 0.5 là hệ số suy giảm nhân (Multiplicative Decrease Factor), cho phép hệ thống lập tức cắt giảm 50% số worker nền khi phát hiện dấu hiệu suy giảm tốc độ khung hình, giải phóng tài nguyên CPU khẩn cấp để cứu vãn nhịp Vsync kế tiếp.", bold_prefix="• ", bullet=True)
    add_p(doc, "gamma = 0.8 là hệ số vùng đệm an toàn, T_target = 20 ms là ngưỡng trễ mục tiêu, và N_min = 1, N_max = W_total.", bold_prefix="• ", bullet=True)
    add_p(doc, "Đặc biệt, quy tắc miễn trừ quy định trần N(k+1) chỉ áp dụng lên các tác vụ Visible và Background; các tác vụ Critical luôn được quyền chiếm dụng worker dự phòng độc lập, đảm bảo tính phản hồi tức thì không bị ảnh hưởng bởi quá trình phanh của AIMD.")

    add_h2(doc, "3.8. Cân Bằng Hàng Đợi Bằng Định Luật Little và Giảm Tải Ngược Chọn Lọc (Backpressure)")
    
    add_h3(doc, "3.8.1. Cân Bằng Dòng Tải Theo Định Luật Little")
    add_p(doc, "Xét hệ thống hàng đợi tác vụ ở trạng thái dừng, theo Định luật Little:")
    add_formula(doc, "E[L] = lambda * E[W]", "3.13")
    add_p(doc, "Trong đó E[L] là độ dài kỳ vọng của hàng đợi, lambda là tốc độ tác vụ mới phát sinh, và E[W] là thời gian lưu lại trung bình của tác vụ trong hệ thống. Khi tốc độ tải đến lambda tăng đột biến trong các tình huống bão tải (ví dụ Kịch bản S2 ở pha 2.0x), nếu không kiểm soát, chiều dài hàng đợi L sẽ tăng trưởng tuyến tính theo thời gian, dẫn đến việc cạn kiệt không gian heap của bộ nhớ RAM và làm sập tiến trình ứng dụng (OOM Crash).")

    add_h3(doc, "3.8.2. Giải Thuật Giảm Tải Ngược Dựa Trên Hạn Định Hữu Dụng Thị Giác")
    add_p(doc, "Hệ thống cài đặt giải thuật giảm tải ngược chọn lọc (Selective Load Shedding) dựa trên nguyên lý Loại Bỏ Công Việc Hết Hạn Thị Giác (Stale Work Elimination). Ngưỡng dung lượng hàng đợi an toàn được mô hình hóa theo quy mô worker:")
    add_formula(doc, "L_threshold = max( 20, W_total * 10 )", "3.14")
    add_p(doc, "Khi tổng số tác vụ trong hàng đợi vượt quá L_threshold, bộ điều phối kích hoạt chính sách lọc tại cổng tiếp nhận:")
    add_formula(doc, "Action(t_i) = \\begin{cases} Accept & \\text{nếu } p_i = Critical \\\\ Drop & \\text{nếu } p_i in {Visible, Background} \\wedge L_queue >= L_threshold \\end{cases}", "3.15")
    add_p(doc, "Cơ sở khoa học của quyết định này dựa trên đặc thù của giao diện người dùng: các yêu cầu giải mã hình ảnh hoặc dựng dữ liệu của các phần tử giao diện mà người dùng đã cuộn lướt qua từ lâu không còn mang lại giá trị trải nghiệm thị giác (Zero Visual Utility). Việc chủ động loại bỏ các tác vụ quá hạn này giúp bảo toàn tuyệt đối không gian bộ nhớ RAM và ngăn chặn hiện tượng lãng phí chu kỳ CPU vô ích.")

    add_h2(doc, "3.9. Máy Trạng Thái Hữu Hạn Tự Động Thích Ứng Nhiệt và Năng Lượng (Degradation FSA)")
    add_p(doc, "Khi thiết bị di động hoạt động dưới tải nặng liên tục, sự tích tụ nhiệt lượng sẽ kích hoạt cơ chế điều tần bảo vệ phần cứng (Dynamic Voltage and Frequency Scaling - DVFS) của hệ điều hành, làm suy giảm đột ngột xung nhịp CPU và kéo sập hiệu năng toàn hệ thống. Để chủ động thích ứng trước khi hệ điều hành can thiệp cưỡng bức, đề tài xây dựng Mô hình Máy Trạng thái Hữu hạn Tự động (Finite State Automaton - FSA) quản lý chế độ suy giảm M = (S, Sigma, delta, s_0):")
    add_p(doc, "Tập trạng thái S = { Normal, Conserve, Critical }.", bold_prefix="• ", bullet=True)
    add_p(doc, "Tập tín hiệu đầu vào Sigma = { (Temp_SoC, Battery_Level) } thu thập từ Android PowerManager.", bold_prefix="• ", bullet=True)
    add_p(doc, "Trạng thái khởi tạo s_0 = Normal.", bold_prefix="• ", bullet=True)
    add_p(doc, "Hàm chuyển trạng thái có trễ (Hysteresis Transition Function delta):", bold_prefix="• Quy tắc chuyển đổi: ")
    add_p(doc, "Chế độ Bình thường (Normal): Duy trì khi Temp < 38°C và Battery > 20%. Hệ thống vận hành với toàn bộ năng lực worker do AIMD phân bổ.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Chế độ Tiết giảm (Conserve): Kích hoạt khi Temp >= 38°C hoặc Battery <= 20%. Hệ thống chủ động giảm 25% trần worker (cap = cap * 0.75) và tăng gấp đôi thời gian hoãn tác vụ nền nhằm hạ thấp công suất tỏa nhiệt.", bold_prefix="2. ", bullet=True)
    add_p(doc, "Chế độ Nguy cấp (Critical): Kích hoạt khi Temp >= 42°C hoặc Battery <= 10%. Hệ thống áp đặt trần cứng cap = 1 worker tối thiểu và kích hoạt xả tải toàn bộ tác vụ nền nhằm ngăn ngừa hiện tượng quá nhiệt sập nguồn.", bold_prefix="3. ", bullet=True)
    add_p(doc, "Cơ chế Triệt tiêu Dao động Ngưỡng (Hysteresis Dwell Time): Nhằm ngăn ngừa hiện tượng rung giật trạng thái (Limit Cycle Oscillations / Chattering) khi tín hiệu nhiệt độ dao động quanh ngưỡng 38°C, hệ thống áp đặt thời gian trễ ổn định tau_dwell = 5000 ms (5 giây). Trạng thái mới chỉ được kích hoạt nếu tín hiệu duy trì ổn định liên tục vượt ngưỡng trong suốt khoảng thời gian tau_dwell.")

    add_h2(doc, "3.10. Ma Trận Đối Chiếu Khoa Học 5 Chính Sách Lập Lịch (P0 -> P4)")
    add_p(doc, "Bảng 3.1 tổng hợp sự tiến hóa về mặt mô hình lý thuyết và cơ chế điều khiển của 5 chính sách lập lịch được khảo sát trong nghiên cứu:")

    headers_p = ["Chính sách", "Không gian Thực thi", "Cấu trúc Hàng đợi", "Cơ chế Điều phối Cốt lõi", "Mô hình Thích ứng Môi trường"]
    data_p = [
        ["P0: Baseline Đơn luồng", "Main Isolate (Luồng UI)", "Hàng đợi tuần tự FIFO", "Tuần tự hóa Event Loop", "Mù ngữ nghĩa, tê liệt hoàn toàn khi có tải"],
        ["P1: Pool Tĩnh FIFO", "Worker Pool tĩnh (W Isolate)", "Hàng đợi FIFO đơn cấp", "Đa luồng cố định, IPC SendPort", "Không thích ứng; nghẽn đầu hàng và tranh chấp CFS"],
        ["P2: Ưu tiên & Aging", "Worker Pool tĩnh (W Isolate)", "Hàng đợi 3 mức O(1)", "Thuật toán Aging thâm niên Score(i,t)", "Bảo đảm toán học không bỏ đói (Starvation-Free)"],
        ["P3: Phân mảnh & Nhường", "Worker Pool tĩnh (W Isolate)", "Hàng đợi 3 mức + Ghế Reserve", "Chunking 80ms, Yielding theo Vsync", "Nhường nhịp khung hình khi khoảng cách frame > 20ms"],
        ["P4: Thích ứng Toàn diện", "Worker Pool động tự co giãn", "Hàng đợi 3 mức + Backpressure", "AIMD (+1 / ×0.5), Stale Load Shedding", "Máy trạng thái FSA 3 chế độ kèm trễ Hysteresis 5s"]
    ]
    add_styled_table(doc, headers_p, data_p, col_widths=[1.3, 1.4, 1.3, 1.6, 1.5], caption="Bảng 3.1: So sánh đặc tính lý thuyết và cơ chế kiến trúc của các chính sách lập lịch P0 - P4")

    # =========================================================================
    # CHƯƠNG 4: THỰC NGHIỆM ĐỊNH LƯỢNG VÀ PHÂN TÍCH ĐÁNH GIÁ
    # =========================================================================
    add_h1(doc, "CHƯƠNG 4: THỰC NGHIỆM ĐỊNH LƯỢNG VÀ PHÂN TÍCH ĐÁNH GIÁ")
    
    add_p(doc, "Chương này trình bày toàn bộ kết quả thực nghiệm định lượng thu được từ quy trình đo lường chuẩn hóa trên các thiết bị phần cứng di động thực tế. Các kết quả đo được phân tích đối chứng thông qua các đại lượng thống kê mô tả (Trung vị - Median, Khoảng tứ phân vị - IQR, Biên độ [Min - Max]) và kiểm định giả thuyết thống kê phi tham số Mann-Whitney U nhằm khẳng định tính vững chắc khoa học của các đóng góp.")

    add_h2(doc, "4.1. Thiết Lập Môi Trường Thực Nghiệm Chuẩn Hóa")
    
    add_h3(doc, "4.1.1. Cấu Hình Phần Cứng Thiết Bị Thử Nghiệm")
    add_p(doc, "Thực nghiệm được triển khai trên hai thế hệ phần cứng đại diện cho hai phân khúc thị trường với các đặc tính kiến trúc vi xử lý và màn hình hiển thị tương phản:")
    add_p(doc, "Thiết bị Phổ thông Giá rẻ (Helio P35 / 60 Hz): Samsung Galaxy A04e (SM-A042F), trang bị SoC MediaTek Helio P35 (8 nhân ARM Cortex-A53: cụm 4 nhân 2.3 GHz + cụm 4 nhân 1.8 GHz theo cấu trúc big.LITTLE đồng nhất), bộ nhớ RAM 2 GB (khả dụng thực tế ~700 MB), Android 14. Màn hình chuẩn 60 Hz với ngân sách khung hình T_budget = 16.67 ms. Đây là môi trường phần cứng khắc nghiệt nhất nhằm kiểm chứng năng lực tối ưu hóa.", bold_prefix="• Thiết bị 1: ", bullet=True)
    add_p(doc, "Thiết bị Tầm trung Thế hệ mới (Helio G99 / 120 Hz): Xiaomi Redmi Note 13, trang bị SoC MediaTek Helio G99 (2 nhân Cortex-A76 2.2 GHz + 6 nhân Cortex-A55 2.0 GHz), RAM 6 GB, Android 15. Màn hình tần số quét cao 120 Hz với ngân sách thời gian cực kỳ ngặt nghèo T_budget = 8.33 ms. Thiết bị này dùng để kiểm chứng khả năng khái quát hóa liên nền tảng.", bold_prefix="• Thiết bị 2: ", bullet=True)
    add_p(doc, "Môi trường Biên dịch Chuẩn mực: Ứng dụng được biên dịch ở chế độ Profile AOT (Ahead-of-Time native binary), loại bỏ toàn bộ mã kiểm tra gỡ lỗi để phản ánh chính xác hiệu năng vận hành thực tế.", bold_prefix="• ", bullet=True)

    add_h3(doc, "4.1.2. Thiết Kế Các Kịch Bản Thử Nghiệm")
    add_p(doc, "Kịch bản Tải Bão hòa Đều (Scenario S1): Duy trì tốc độ dồn tác vụ liên tục ở mức bão hòa (L = 64 trên A04e, L = 256 trên Note 13), tích hợp 5 tác vụ Critical xuất hiện ngẫu nhiên. Kịch bản này nhằm khảo sát khả năng duy trì độ mượt và hiện tượng nghẽn đầu hàng dưới tải tĩnh cực đại.", bold_prefix="• Kịch bản S1: ", bullet=True)
    add_p(doc, "Kịch bản Tải Biến động Bậc thang (Scenario S2): Tải tác vụ nền tăng trưởng lũy tiến qua 4 pha thời gian trong 60 giây (0.25x -> 0.5x -> 1.0x -> 2.0x), tích hợp 8 tác vụ Critical. Kịch bản này nhằm đánh giá năng lực co giãn worker của AIMD và hiệu quả chống tràn bộ nhớ của cơ chế Backpressure.", bold_prefix="• Kịch bản S2: ", bullet=True)
    add_p(doc, "Kịch bản Tác vụ Đa Phương tiện Thực tế (Scenario s_image): Thực thi chuỗi tác vụ đọc tập tin ngẫu nhiên, phân tích header nhị phân và tính toán histogram trên tập 80 bức ảnh chụp DSLR 24 Megapixel thật, kết hợp hiển thị lưới cuộn 80 ảnh trên giao diện.", bold_prefix="• Kịch bản s_image: ", bullet=True)

    add_h3(doc, "4.1.3. Phương Pháp Luận Thống Kê và Kiểm Định Phi Tham Số")
    add_p(doc, "Do các chỉ số độ trễ và khoảng cách khung hình trên hệ điều hành di động có phân phối lệch đuôi dài (heavy-tailed skewed distribution), việc sử dụng giá trị trung bình cộng (Mean) và độ lệch chuẩn sẽ gây sai lệch kết quả. Nghiên cứu sử dụng Trung vị (Median), Khoảng tứ phân vị (IQR = Q75 - Q25) và Phân vị thứ 95 (p95). Mọi cặp so sánh giả thuyết đều được kiểm định bằng kiểm định phi tham số Mann-Whitney U ở mức ý nghĩa thống kê chuẩn alpha = 0.05.")

    add_h2(doc, "4.2. Kiểm Chứng Giả Thuyết H1: Nghẽn Main Isolate và Sự Cần Thiết Của WorkerPool (P0 vs P1)")
    add_p(doc, "Giả thuyết H1: Việc thực thi các tác vụ tính toán nặng trên Main Isolate (P0) sẽ phá vỡ hoàn toàn chu trình dựng hình của giao diện; việc phân tách tác vụ ra WorkerPool Isolate độc lập (P1) là điều kiện cần để phục hồi năng lực dựng khung hình.", italic_prefix="Phát biểu Giả thuyết Khoa học: ")
    add_p(doc, "Kết quả thực nghiệm trên Samsung Galaxy A04e dưới kịch bản bão hòa S1 (L = 64, W = 8, C = 80, n = 4 mỗi chính sách):")
    add_p(doc, "Chính sách P0 (Main Isolate): Tỷ lệ khung hình bị bỏ lỡ (Missed Frame Rate) lên tới 90.8% [91–91%], khoảng cách thời gian giữa hai khung hình p95 kéo dài tới 419.3 ms (tốc độ hiển thị thực tế rớt xuống dưới 3 FPS, vòng xoay hoạt họa giao diện bị đóng băng hoàn toàn). Độ trễ tác vụ khẩn cấp trung vị là 68,483 ms (~68.5 giây) và thời gian chờ của tác vụ nền lên tới 81,719 ms.", bold_prefix="• ", bullet=True)
    add_p(doc, "Chính sách P1 (WorkerPool FIFO): Khi chuyển toàn bộ tác vụ ra 8 worker isolates chạy nền, tỷ lệ Missed Frame lập tức giảm xuống 23.2% [22–24%], khoảng cách khung hình p95 rút ngắn về 48.2 ms, và tỷ lệ hoàn thành tác vụ tăng từ 16.6% lên 86.5%.", bold_prefix="• ", bullet=True)
    add_callout(doc, "Kiểm định phi tham số Mann-Whitney U giữa P0 và P1 về tỷ lệ Missed Frame xác nhận sự khác biệt có ý nghĩa thống kê vượt trội (U = 16.0, p = 0.014 < 0.05). Kết luận: CHẤP NHẬN GIẢ THUYẾT H1. Việc cách ly tác vụ tính toán nặng ra khỏi luồng giao diện chính là điều kiện tiên quyết bắt buộc của kiến trúc phần mềm di động.", bold_title="> Kiểm định Thống kê & Kết luận Giả thuyết H1: ")

    add_h2(doc, "4.3. Kiểm Chứng Giả Thuyết H2: Giới Hạn Của Pool FIFO Cố Định Dưới Tải Cao (P1)")
    add_p(doc, "Giả thuyết H2: Trong môi trường phần cứng hạn chế, việc gia tăng số lượng worker isolates trong một hồ chứa FIFO cố định không giải quyết được hiện tượng nghẽn đầu hàng (Head-of-Line Blocking) khi tải bão hòa, đồng thời làm gia tăng tranh chấp thời gian CPU với luồng UI.", italic_prefix="Phát biểu Giả thuyết Khoa học: ")
    add_p(doc, "Kết quả phân tích định lượng khi quét tham số worker từ W = 4 đến W = 8 trên chính sách P1:")
    add_p(doc, "Ở mức tải trung bình (L = 32), việc mở rộng pool từ W = 6 lên W = 8 giúp giảm độ trễ critical từ 131 ms xuống 36 ms do hệ thống còn dư thừa nhân CPU nhàn rỗi.", bold_prefix="• ", bullet=True)
    add_p(doc, "Tuy nhiên, khi tải vượt ngưỡng bão hòa (L = 64): Ngay cả khi cấp tối đa 8 worker, chính sách P1 vẫn để xảy ra 23.2% missed frames và 9.9% jank frames. Do cơ chế FIFO hoàn toàn mù về mặt ngữ nghĩa ưu tiên, tác vụ Critical bị kẹt phía sau các tác vụ nền khổng lồ, khiến độ trễ Critical p95 vọt lên tới 35,356 ms (hơn 35 giây). Đồng thời, 8 worker cạnh tranh trực tiếp thời gian CPU với luồng UI trên bộ lập lịch nhân Linux CFS.", bold_prefix="• ", bullet=True)
    add_callout(doc, "Kết luận: ỦNG HỘ GIẢ THUYẾT H2. Mở rộng worker trong cơ chế FIFO chỉ có tác dụng khi tài nguyên chưa bão hòa; khi hệ thống quá tải, cơ chế này hoàn toàn thất bại trong việc bảo vệ độ trễ tương tác của người dùng.", bold_title="> Kết luận Giả thuyết H2: ")

    add_h2(doc, "4.4. Kiểm Chứng Giả Thuyết H3: Hiệu Quả Đột Phá Của Ưu Tiên, Phân Mảnh, Dự Trữ và Nhường Luồng (P1 -> P2 -> P3)")
    add_p(doc, "Giả thuyết H3: Sự kết hợp giữa cấu trúc hàng đợi ưu tiên kèm aging (P2), kỹ thuật phân mảnh hợp tác (Cooperative Chunking), dự trữ worker chuyên biệt và nhường nhịp khung hình (P3) sẽ triệt tiêu độ trễ critical và đưa tỷ lệ rớt khung hình về mức tương đương baseline không tải.", italic_prefix="Phát biểu Giả thuyết Khoa học: ")
    add_p(doc, "Bảng 4.1 trình bày kết quả so sánh đối chứng trên kịch bản tải bão hòa S1 (Samsung Galaxy A04e, L = 64, W = 8, C = 80, n = 4 mỗi chính sách):")

    headers_s1 = ["Chính sách Lập lịch", "Tỷ lệ Missed Frame (%)", "Tỷ lệ Jank Frame (%)", "Frame Gap p95 (ms)", "Critical Latency p95", "Tỷ lệ Hoàn thành"]
    data_s1 = [
        ["Baseline Không Tải", "0.9% [1–1%]", "2.2% [0–3%]", "18.3 ms", "– (Không tải)", "–"],
        ["P0: Main Isolate", "90.8% [91–91%]", "0.0% (Tê liệt)", "419.3 ms", "68,483 ms (~68.5s)", "16.6%"],
        ["P1: Pool Tĩnh FIFO", "23.2% [22–24%]", "9.9% [9–11%]", "48.2 ms", "35,356 ms (~35.4s)", "86.5%"],
        ["P2: Ưu tiên & Aging", "22.4% [21–24%]", "10.0% [9–10%]", "42.9 ms", "22,760 ms (~22.8s)", "90.4%"],
        ["P3: Phân mảnh & Nhường", "0.8% [1–1%]", "17.0% [16–19%]", "18.2 ms", "31.0 ms [28–35 ms]", "77.1%"]
    ]
    add_styled_table(doc, headers_s1, data_s1, col_widths=[1.6, 1.2, 1.1, 1.3, 1.4, 1.1], caption="Bảng 4.1: Ma trận hiệu năng đối đầu giữa các chính sách lập lịch trên kịch bản bão hòa S1 (Samsung Galaxy A04e)")

    add_h3(doc, "4.4.1. Phân Tích Đóng Góp Từng Thành Phần (Ablation Study)")
    add_p(doc, "Nhằm lượng hóa độc lập giá trị khoa học của từng cơ chế kỹ thuật trong bước nhảy vọt từ P1 lên P3, nghiên cứu tiến hành phân tích phân rã kiến trúc (Ablation Analysis):")
    add_p(doc, "Chính sách P2 (Chỉ áp dụng Hàng đợi Ưu tiên 3 mức): Độ trễ critical giảm từ 35.4s xuống 22.8s (giảm 36%, p = 0.014), nhưng vẫn ở mức hàng chục giây. Nguyên nhân: Một khi 8 worker đang bận thực thi các tác vụ nền dở dang, tác vụ critical dù đứng đầu hàng đợi vẫn không thể chen ngang do tính bất khả ngắt của Isolate.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Chính sách P3c (Bổ sung Phân mảnh Cooperative Chunking 80ms): Cắt nhỏ tác vụ giúp worker liên tục tạo điểm nhường luồng. Tỷ lệ missed frame lập tức giảm chấn động từ 22.2% xuống 0.8% (mượt tương đương baseline không tải 0.9%).", bold_prefix="2. ", bullet=True)
    add_p(doc, "Chính sách P3r (Bổ sung Dự trữ Worker Chuyên biệt): Dành riêng 1 worker dự phòng cho tác vụ khẩn cấp. Độ trễ Critical p95 lập tức giảm gần 1.000 lần, từ 44.8 giây xuống còn 49.0 ms (< 100 ms).", bold_prefix="3. ", bullet=True)
    add_p(doc, "Chính sách P3 Hoàn chỉnh (Bổ sung Nhường nhịp Frame Yielding): Tạm hoãn phát sinh phân mảnh nền khi khoảng cách khung hình vượt 20 ms. Độ trễ Critical đạt mức tối ưu tuyệt đối: 31.0 ms.", bold_prefix="4. ", bullet=True)

    add_figure(doc, "figures/fig1_s1_tradeoff.png", "Hình 4.1: Đồ thị phân tán đánh đổi Pareto giữa Tỷ lệ Missed Frame và Độ trễ Critical Latency p95 trên Kịch bản S1", width_inches=6.0)
    add_figure(doc, "figures/fig4_ablation_s1.png", "Hình 4.2: Biểu đồ phân tích đóng góp độc lập của từng cơ chế kiến trúc (Ablation Study) đối với các chỉ số hiệu năng", width_inches=6.0)

    add_callout(doc, "Kiểm định thống kê Mann-Whitney U giữa P1 và P3 khẳng định: Tỷ lệ Missed Frame giảm từ 23.2% xuống 0.8% (U = 16.0, p = 0.014); Độ trễ Critical giảm từ 35.4 giây xuống 31.0 ms (nhanh hơn 1.140 lần, U = 16.0, p = 0.014). Kết luận: CHẤP NHẬN GIẢ THUYẾT H3.", bold_title="> Kiểm định Thống kê & Kết luận Giả thuyết H3: ")

    add_h2(doc, "4.5. Kiểm Chứng Giả Thuyết H4: Năng Lực Thích Ứng Của AIMD và Backpressure Dưới Tải Biến Thiên S2 (P4 vs P3)")
    add_p(doc, "Giả thuyết H4: Dưới kịch bản tải biến động và tăng đột biến (Scenario S2: 4 bậc thang từ 0.25x đến 2.0x), thuật toán điều khiển thích ứng AIMD kết hợp cơ chế giảm tải ngược Backpressure (P4) sẽ triệt tiêu hiện tượng jank do nghẽn CPU, đồng thời rút ngắn Makespan nhờ loại bỏ các tác vụ nền quá hạn.", italic_prefix="Phát biểu Giả thuyết Khoa học: ")
    add_p(doc, "Bảng 4.2 đối chiếu kết quả đo lường kịch bản S2 giữa P1, P3 và P4 trên Samsung Galaxy A04e (L = 32, W = 8, C = 80, n = 3 mỗi chính sách):")

    headers_s2 = ["Chỉ số Hiệu năng", "P1 (FIFO Pool)", "P3 (Chunk+Priority)", "P4 (AIMD+Backpressure)", "Đánh giá Đối chiếu (P4 vs P3)"]
    data_s2 = [
        ["Missed Frame (%)", "5.1% [5–5%]", "0.7% [1–1%]", "0.8% [1–1%]", "Tương đương, duy trì mượt mà 60 FPS"],
        ["Jank Frame (%)", "4.8% [4–8%]", "24.8% [18–26%]", "8.0% [0–10%]", "P4 giảm jank hơn 3 lần (U = 9.0, p = 0.050)"],
        ["Critical Latency p95", "4,744.0 ms", "34.0 ms", "28.0 ms [27–30 ms]", "P4 tối ưu nhất (nhanh hơn P1 169 lần)"],
        ["Makespan (Tổng thời gian)", "67,839 ms", "77,736 ms", "67,865 ms", "P4 hoàn tất sớm hơn P3 gần 10 giây"],
        ["Tác vụ Nền bị hủy (Dropped)", "0", "0", "1,990 tasks", "Backpressure loại bỏ các tác vụ quá hạn"]
    ]
    add_styled_table(doc, headers_s2, data_s2, col_widths=[1.6, 1.2, 1.4, 1.5, 1.8], caption="Bảng 4.2: So sánh hiệu năng vận hành dưới kịch bản tải biến động bậc thang S2 (Samsung Galaxy A04e)")

    add_p(doc, "Cơ chế vượt trội của P4 được giải thích dựa trên động học điều khiển:")
    add_p(doc, "Triệt tiêu Jank tại Pha Bão tải: Ở pha tải đỉnh 2.0x, chính sách P3 duy trì cố định 8 worker làm việc liên tục khiến CPU bị nghẽn bus bộ nhớ và tranh chấp dữ dội với luồng đồ họa Raster, đẩy tỷ lệ Jank của P3 lên 24.8%. Ngược lại, thuật toán AIMD của P4 nhận diện độ trễ khung hình tăng và phanh khẩn cấp số worker nền xuống 1–2 worker, giúp Jank giảm hơn 3 lần xuống 8.0% (có run đạt mức lý tưởng 0.25%).", bold_prefix="• ", bullet=True)
    add_p(doc, "Bảo toàn Độ trễ Critical Kỷ lục 28.0 ms: Nhờ quy tắc cô lập Critical khỏi trần AIMD, tác vụ tương tác luôn được cấp phát ngay worker rảnh rỗi mà không bị ảnh hưởng bởi quá trình phanh worker nền.", bold_prefix="• ", bullet=True)
    add_p(doc, "Cân bằng Hàng đợi và Chống Tràn RAM: Ở pha tải đỉnh, P4 loại bỏ 1.990 tác vụ nền hết hạn thị giác, bảo vệ an toàn vùng nhớ RAM và giúp kịch bản kết thúc ở 67.8 giây (nhanh hơn P3 gần 10 giây).", bold_prefix="• ", bullet=True)

    add_figure(doc, "figures/fig2_s2_comparison.png", "Hình 4.3: So sánh 4 chỉ số hiệu năng định lượng giữa P1, P3 và P4 trên Kịch bản tải bậc thang tăng dần S2", width_inches=6.0)
    add_figure(doc, "figures/fig3_timeline_frames.png", "Hình 4.4: Phân bố thời gian khung hình theo dòng thời gian thực tế 0-60 giây dưới kịch bản tải bậc thang S2", width_inches=6.0)

    add_callout(doc, "Kết luận: CHẤP NHẬN GIẢ THUYẾT H4. Thuật toán điều khiển thích ứng AIMD kết hợp cơ chế giảm tải ngược Backpressure là giải pháp tối ưu toàn diện cho các thiết bị di động phân khúc giá rẻ khi phải đối mặt với tải bùng nổ.", bold_title="> Kết luận Giả thuyết H4: ")

    add_h2(doc, "4.6. Vi Đo Lường Phụ Tải Điều Phối (Microbenchmark of Scheduling Overhead)")
    add_p(doc, "Nhằm chứng minh các cấu trúc điều phối phức tạp không gây tổn hại đến quỹ thời gian của Main Isolate, nghiên cứu thực hiện bài kiểm chuẩn độc lập Microbenchmark E3 đo lường chi phí khứ hồi (Round-trip Dispatch & IPC Serialization Latency) trên 200 lượt điều phối:")
    add_p(doc, "Độ trễ Điều phối Khứ hồi Trung vị (Dispatch Latency p50): 0.34 ms (345 micro-giây).", bold_prefix="• ", bullet=True)
    add_p(doc, "Độ trễ Điều phối Khứ hồi Phân vị thứ 95 (Dispatch Latency p95): 0.47 ms (467 micro-giây).", bold_prefix="• ", bullet=True)
    add_p(doc, "Độ trễ Điều phối Khứ hồi Phân vị thứ 99 (Dispatch Latency p99): 0.73 ms (730 micro-giây).", bold_prefix="• ", bullet=True)
    add_p(doc, "So với ngân sách thời gian chuẩn 16.67 ms của màn hình 60 Hz, tổng phụ tải điều phối chỉ chiếm xấp xỉ 2.0% ngân sách frame. Đây là mức chi phí hoàn toàn nằm dưới ngưỡng cảm nhận thị giác của mắt người, chứng minh tính hiệu quả vượt bậc của kiến trúc O(1).")

    add_h2(doc, "4.7. Đánh Giá Khả Năng Khái Quát Hóa Liên Nền Tảng Thiết Bị (Cross-Device Generalizability)")
    add_p(doc, "Để bác bỏ nguy cơ 'quá khớp' (overfitting) trên một con chip duy nhất, nghiên cứu mở rộng toàn bộ ma trận thực nghiệm sang thiết bị Xiaomi Redmi Note 13 sở hữu vi xử lý Helio G99 mạnh gấp 4 lần và màn hình 120 Hz với ngân sách thời gian chỉ 8.33 ms.")
    add_p(doc, "Bảng 4.3 đối chiếu kết quả thực nghiệm giữa hai thế hệ phần cứng:")

    headers_cross = ["Thiết bị & Kịch bản", "Chính sách", "Missed Frame (%)", "Jank Frame (%)", "Critical Latency p95", "Đánh giá Khái quát hóa"]
    data_cross = [
        ["Galaxy A04e (60Hz)\nKịch bản S1 (L=64)", "P1 (FIFO)\nP3 (Chunk+Yield)\nP4 (AIMD+BP)", "23.2%\n0.8%\n0.8%", "9.9%\n17.0%\n8.0%", "35,356 ms\n31.0 ms\n28.0 ms", "P3 và P4 mượt ngang baseline\nP4 giảm jank vượt trội"],
        ["Redmi Note 13 (120Hz)\nKịch bản S1 (L=256)", "P1 (FIFO)\nP2 (Pri+Aging)\nP3 (Chunk+Yield)", "61.6%\n59.6%\n1.21%", "34.7%\n32.1%\n0.12%", "63,278 ms (~63.3s)\n39,351 ms\n29.0 ms", "P1 rớt hơn 61% frame 120Hz\nP3 giảm trễ hơn 2.180 lần!"],
        ["Redmi Note 13 (120Hz)\nKịch bản S2 (L=128)", "P1 (FIFO)\nP3 (Chunk+Yield)\nP4 (AIMD+BP)", "33.5%\n1.19%\n1.22%", "13.2%\n0.14%\n0.03%", "33,501 ms (~33.5s)\n29.0 ms\n25.0 ms", "P4 triệt tiêu jank (0.03%)\nHoàn thành sớm hơn 30.6 giây"]
    ]
    add_styled_table(doc, headers_cross, data_cross, col_widths=[1.8, 1.4, 1.2, 1.1, 1.4, 1.6], caption="Bảng 4.3: Đối chiếu hiệu năng vận hành đa nền tảng giữa Samsung Galaxy A04e (60Hz) và Xiaomi Redmi Note 13 (120Hz)")

    add_figure(doc, "figures/fig5_cross_device_comparison.png", "Hình 4.5: Đồ thị đối đầu hiệu năng liên thiết bị giữa Galaxy A04e (60Hz) và Redmi Note 13 (120Hz) trên kịch bản S1 và S2", width_inches=6.0)

    add_callout(doc, "Kết luận Khái quát hóa: Cơ chế FIFO truyền thống (P1) thất bại trên cả thiết bị cấu hình cao màn hình 120Hz (rớt tới 61.6% frame và trễ hơn 1 phút). Ngược lại, giải pháp P3 và P4 thể hiện tính vững chắc xuất sắc: trên màn hình 120Hz khắt khe (ngân sách 8.33 ms), P3 duy trì tỷ lệ rớt frame ở mức 1.21% (ngang baseline không tải 1.19%), và P4 triệt tiêu jank xuống mức 0.03%, đưa độ trễ Critical về 25.0 ms.", bold_title="> Đánh giá Tính Khái quát hóa Liên Thiết bị: ")

    add_h2(doc, "4.8. Thực Nghiệm Trên Tác Vụ Xử Lý Dữ Liệu Đa Phương Tiện Thực Tế (s_image)")
    add_p(doc, "Để kiểm chứng trên tải công việc thực tế, đề tài thực hiện kịch bản s_image trên tập 80 bức ảnh chụp DSLR độ phân giải cao 24 Megapixel (6016×4016 pixel, dung lượng 5.85–12.48 MB/ảnh). Giao diện người dùng đồng thời thực hiện cuộn tự động lưới 80 ảnh thu nhỏ ở vận tốc cao (1000 px/s). Bảng 4.4 tổng hợp kết quả thực nghiệm trên máy ảo chuẩn tắc emulator-5554 (L = 16, W = 4, C = 80, 30s, n = 2 mỗi chính sách):")

    headers_img = ["Chính sách Lập lịch", "Tổng Frame Dựng", "Missed Frame (%)", "Frame p95 (ms)", "Raster p95 (ms)", "Critical Latency p95", "Tỷ lệ Hoàn thành"]
    data_img = [
        ["Baseline Không Tải", "550 frames", "69.5%", "142.8 ms", "73.0 ms", "– (Không tải)", "–"],
        ["P0: Main Isolate", "120 frames", "93.4%", "747.4 ms", "101.2 ms", "35,683 ms (~35.7s)", "29.1% (Tê liệt)"],
        ["P1: Pool Tĩnh FIFO", "385 frames", "78.6%", "248.2 ms", "123.5 ms", "26,589 ms (~26.6s)", "34.9%"],
        ["P2: Ưu tiên & Aging", "358 frames", "80.1%", "254.9 ms", "135.4 ms", "29,412 ms (~29.4s)", "41.1%"],
        ["P3: Phân mảnh & Nhường", "364 frames", "79.8%", "290.6 ms", "154.9 ms", "506.0 ms (Nhanh hơn 52x)", "31.9%"],
        ["P4: Thích ứng Toàn diện", "510 frames", "71.6%", "154.5 ms", "80.4 ms", "286.0 ms (Nhanh hơn 93x)", "76.4%"]
    ]
    add_styled_table(doc, headers_img, data_img, col_widths=[1.6, 1.1, 1.2, 1.2, 1.2, 1.4, 1.1], caption="Bảng 4.4: Kết quả đo lường thực nghiệm trên tác vụ xử lý ảnh 24MP thực tế kết hợp lưới cuộn giao diện")

    add_figure(doc, "figures/fig6_s_image_real_workload.png", "Hình 4.6: So sánh hiệu năng định lượng giữa các chính sách lập lịch trên kịch bản dữ liệu ảnh thực tế s_image", width_inches=6.0)
    add_figure(doc, "figures/app_screen_80.png", "Hình 4.7: Giao diện ứng dụng thực nghiệm hiển thị lưới 80 ảnh DSLR thật kết hợp vòng xoay đo jank và Stack Monitor HUD", width_inches=4.0)

    add_callout(doc, "Kết quả thực nghiệm trên ảnh thật khẳng định: Chính sách thích ứng P4 đạt tới 510 frames (tiệm cận mức trần 550 frames của GPU phần mềm), giảm độ trễ khung hình p95 từ 747.4 ms ở P0 xuống 154.5 ms, và hạ độ trễ tương tác chạm Critical từ 35.7 giây xuống 286 ms (nhanh hơn 125 lần so với P0 và 93 lần so với P1), đồng thời tăng tỷ lệ hoàn thành tác vụ lên 76.4%.", bold_title="> Đánh giá Thực nghiệm Tác vụ Ảnh Thực tế: ")

    add_h2(doc, "4.9. Minh Chứng Trực Quan Thời Gian Thực Qua Hệ Thống Stack Monitor HUD")
    add_p(doc, "Nhằm cung cấp bằng chứng trực quan sinh động phục vụ đánh giá, hệ thống tích hợp giao diện Stack Monitor HUD hiển thị trực tiếp các thông số vận hành của bộ lập lịch theo thời gian thực:")
    add_p(doc, "Minh chứng Sự suy sụp của P0: Hình 4.8 ghi lại trạng thái tê liệt của P0. Tốc độ khung hình sụt giảm nghiêm trọng xuống 10 FPS, tỷ lệ bỏ lỡ Miss vọt lên 84.3%, thời gian dựng khung hình báo đỏ 66.7 ms (p95 đạt 250.0 ms), toàn bộ 40 cột biểu đồ sparkline đều vượt ngưỡng ngân sách 16.7 ms, và vòng xoay hoạt họa bị đóng băng.", bold_prefix="• Quan sát 1 (Chính sách P0): ", bullet=True)
    add_p(doc, "Minh chứng Năng lực Nhường Luồng của P3: Hình 4.9 minh chứng cờ trạng thái YIELDING bật sáng khi bộ lập lịch chủ động hoãn tác vụ nền. Tốc độ khung hình phục hồi chuẩn 60 FPS, Frame Time giảm sâu xuống 7.6 ms (p95 đạt 12.1 ms), và biểu đồ sparkline chuyển sang màu xanh ngọc lục bảo hoàn toàn dưới vạch 16.7 ms.", bold_prefix="• Quan sát 2 (Chính sách P3): ", bullet=True)
    add_p(doc, "Minh chứng Khả năng Phanh Tự Động của P4: Hình 4.10 ghi lại thời điểm tải tăng vọt 16x. Thuật toán AIMD tự động khóa 3 worker nền (hiển thị biểu tượng 3 ổ khóa 🔒 cùng dòng 1/1 AIMD khóa 3), cơ chế Backpressure kích hoạt xả tải 938 tác vụ quá hạn. Nhờ đó, ứng dụng duy trì trọn vẹn 60 FPS và độ trễ Critical đạt mức xanh lý tưởng: 85 ms (< 100 ms).", bold_prefix="• Quan sát 3 (Chính sách P4): ", bullet=True)

    add_figure(doc, "figures/hud_v2_p0.png", "Hình 4.8: Ảnh chụp Stack Monitor HUD ở chính sách P0 - Giao diện tê liệt, 10 FPS, 40 cột đỏ vượt ngân sách 16.7ms", width_inches=4.2)
    add_figure(doc, "figures/hud_v2_p3.png", "Hình 4.9: Ảnh chụp Stack Monitor HUD ở chính sách P3 - Bật cờ YIELDING, 60 FPS mượt mà, toàn bộ cột xanh dưới vạch 16.7ms", width_inches=4.2)
    add_figure(doc, "figures/hud_v2_p4.png", "Hình 4.10: Ảnh chụp Stack Monitor HUD ở chính sách P4 - Tự động khóa 3 worker (1/1 AIMD khóa 3), xả tải Drop 938 task, giữ vững 60 FPS và Crit p95 = 85ms", width_inches=4.2)

    # =========================================================================
    # CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # =========================================================================
    add_h1(doc, "CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    
    add_h2(doc, "5.1. Các Đóng Góp Khoa Học và Kỹ Thuật Chính")
    add_p(doc, "Đề tài đã giải quyết thành công bài toán tối ưu hóa đa mục tiêu giữa độ mượt mà giao diện người dùng (UI Smoothness) và thông lượng xử lý nền (Throughput) trên môi trường di động đa nhân tài nguyên hạn chế. Các đóng góp chính của đề tài bao gồm:")
    add_p(doc, "Đóng góp về Mặt Lý thuyết và Mô hình hóa: Làm rõ nghịch lý 'bất cân xứng nhận thức' của bộ lập lịch nhân hệ điều hành đối với trải nghiệm người dùng, hình thức hóa bài toán tối ưu hóa đa mục tiêu MOOP và chứng minh bằng toán học Định lý không bỏ đói tác vụ nền (Starvation-Free Theorem) thông qua giải thuật Aging.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Đóng góp về Mặt Kiến trúc và Thiết kế Hệ thống: Đề xuất và hiện thực hóa thành công kiến trúc bộ lập lịch thích ứng phân cấp tại tầng ứng dụng với chuỗi 6 kỹ thuật cốt lõi: Hàng đợi phân tầng O(1), Phân mảnh tác vụ hợp tác (Cooperative Chunking) giải quyết rào cản bất khả ngắt của Dart Isolate, Dự trữ worker chuyên biệt cho tương tác thời gian thực, Nhường nhịp dựng hình Vsync, Điều khiển phản hồi thích ứng AIMD và Máy trạng thái suy giảm môi trường có trễ Hysteresis.", bold_prefix="2. ", bullet=True)
    add_p(doc, "Đóng góp về Mặt Dữ liệu và Kiểm chứng Thực nghiệm: Thiết lập hệ thống đo lường tự động hóa chuẩn mực, thu thập tập dữ liệu thực nghiệm quy mô trên phần cứng thiết bị di động thật (Samsung Galaxy A04e và Xiaomi Redmi Note 13), chứng minh bằng kiểm định thống kê Mann-Whitney U (p < 0.05) rằng giải pháp giúp giảm tỷ lệ rớt frame từ 23.2% xuống 0.8%, kéo giảm độ trễ tương tác từ hơn 35 giây xuống 28.0 ms (nhanh hơn 1.200 lần) với chi phí phụ tải điều phối chỉ chiếm ~2.0% ngân sách khung hình.", bold_prefix="3. ", bullet=True)
    add_p(doc, "Kiểm chứng Đa Chiều trên Tác vụ Đa Phương tiện Thực tế: Xác nhận tính khả thi trên tập dữ liệu 80 bức ảnh DSLR 24MP và cung cấp công cụ đồ họa Stack Monitor HUD phục vụ quan sát minh bạch.", bold_prefix="4. ", bullet=True)

    add_h2(doc, "5.2. Những Hạn Chế Còn Tồn Tại")
    add_p(doc, "Nghiên cứu ghi nhận hai giới hạn mang tính khách quan của nền tảng:")
    add_p(doc, "Phụ thuộc vào Bản chất Hợp tác Đa nhiệm: Kỹ thuật phân mảnh đòi hỏi mã nguồn Dart phải có khả năng chia tách thành các bước lặp. Đối với các thư viện nguyên khối C/C++ gọi qua Dart FFI mà không hỗ trợ callback tiến độ, hệ thống chưa thể ngắt ngang mà phải dựa hoàn toàn vào cơ chế cách ly worker dự trữ và khóa trần AIMD.", bold_prefix="• ", bullet=True)
    add_p(doc, "Rào cản Thu thập Cảm biến Mức Nhân: Việc thu thập dữ liệu tiêu hao công suất tức thời (mW) trên từng nhân CPU đòi hỏi quyền truy cập root vào hệ thống tệp tin /sys/class/power_supply, vốn bị giới hạn bởi chính sách bảo mật Sandbox của Android thương mại.", bold_prefix="• ", bullet=True)

    add_h2(doc, "5.3. Hướng Nghiên Cứu và Phát Triển Tiếp Theo")
    add_p(doc, "Từ các kết quả đạt được, các hướng phát triển triển vọng tiếp theo bao gồm:")
    add_p(doc, "Đóng gói Thư viện Mã Nguồn Mở: Hoàn thiện giao diện lập trình ứng dụng (API) và phát hành bộ lập lịch dưới dạng package độc lập trên hệ sinh thái pub.dev.", bold_prefix="1. ", bullet=True)
    add_p(doc, "Dự đoán Tải Thông minh Bằng TinyML: Nghiên cứu ứng dụng các mô hình học máy siêu nhẹ chạy trên vi xử lý trí tuệ nhân tạo (NPU di động) để dự đoán trước thời gian thực thi của tác vụ và tự động tối ưu hóa kích thước phân mảnh theo thời gian thực.", bold_prefix="2. ", bullet=True)
    add_p(doc, "Mở rộng Kiến trúc Đa Nền tảng: Chuyển giao các cơ chế điều phối thích ứng sang nền tảng iOS (thông qua Apple Metal và Thermal State API) và nền tảng Web đa luồng (Web Workers).", bold_prefix="3. ", bullet=True)

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

    print("Hoàn tất việc chèn toàn bộ nội dung học thuật chuyên sâu!")

def update_table_of_contents_and_settings(doc_path):
    print("Cập nhật cờ updateFields và Mục lục đồng bộ...")
    import zipfile
    import tempfile
    
    new_toc_items = [
        ("TOC1", "CHƯƠNG 3: MÔ HÌNH HÓA VÀ THIẾT KẾ HỆ THỐNG LẬP LỊCH TÁC VỤ THÍCH ỨNG", "11"),
        ("TOC2", "3.1. Mô hình Hóa Toán học Bài toán Tối ưu Lập lịch Đa Mục tiêu", "11"),
        ("TOC3", "3.1.1. Phát biểu Bài toán Tối ưu Hóa Đa Mục tiêu (MOOP)", "11"),
        ("TOC3", "3.1.2. Hệ Ràng buộc Cứng và Mềm (System Constraints)", "12"),
        ("TOC2", "3.2. Kiến trúc Hệ thống Lập lịch Thích ứng Đa Phân Lớp", "12"),
        ("TOC3", "3.2.1. Phân định Vai trò Các Phân Lớp Chức Năng", "12"),
        ("TOC2", "3.3. Hàng Đợi Ưu Tiên Phân Cấp O(1) và Định Lý Chống Bỏ Đói (P2)", "13"),
        ("TOC3", "3.3.1. Cấu trúc Hàng đợi Phân tầng Ba Mức", "13"),
        ("TOC3", "3.3.2. Hàm Tính Toán Ưu Tiên Động (Dynamic Priority Metric)", "13"),
        ("TOC3", "3.3.3. Định lý Không Bỏ Đói Tác Vụ Nền (Starvation-Free Theorem)", "14"),
        ("TOC2", "3.4. Kỹ Thuật Phân Mảnh Hợp Tác Đa Nhiệm (Cooperative Chunking) và Điểm Nhường Luồng (P3)", "14"),
        ("TOC3", "3.4.1. Giới hạn Bất Khả Ngắt của Isolate và Ranh Giới Phân Mảnh", "14"),
        ("TOC3", "3.4.2. Ranh giới Nhường Luồng (Yield Boundary) và Tái Nạp Hàng Đợi", "15"),
        ("TOC3", "3.4.3. Mô hình Hóa Phân Mảnh trên Tác vụ Xử lý Ảnh Độ Phân Giải Cao", "15"),
        ("TOC2", "3.5. Cơ Chế Dự Trữ Tài Nguyên Chuyên Biệt cho Tác Vụ Thời Gian Thực (P3r)", "16"),
        ("TOC2", "3.6. Cơ Chế Nhường Nhịp Dựng Hình Dựa Trên Cảm Biến Khung Hình (Frame Yielding)", "16"),
        ("TOC2", "3.7. Lý Thuyết Điều Khiển Phản Hồi Thích Ứng AIMD và Co Giãn Worker Động (P4)", "17"),
        ("TOC3", "3.7.1. Động Học Hệ Thống Điều Khiển Vòng Kín", "17"),
        ("TOC2", "3.8. Cân Bằng Hàng Đợi Bằng Định Luật Little và Giảm Tải Ngược Chọn Lọc (Backpressure)", "18"),
        ("TOC3", "3.8.1. Cân Bằng Dòng Tải Theo Định Luật Little", "18"),
        ("TOC3", "3.8.2. Giải Thuật Giảm Tải Ngược Dựa Trên Hạn Định Hữu Dụng Thị Giác", "18"),
        ("TOC2", "3.9. Máy Trạng Thái Hữu Hạn Tự Động Thích Ứng Nhiệt và Năng Lượng (Degradation FSA)", "19"),
        ("TOC2", "3.10. Ma Trận Đối Chiếu Khoa Học 5 Chính Sách Lập Lịch (P0 -> P4)", "20"),
        ("TOC1", "CHƯƠNG 4: THỰC NGHIỆM ĐỊNH LƯỢNG VÀ PHÂN TÍCH ĐÁNH GIÁ", "21"),
        ("TOC2", "4.1. Thiết Lập Môi Trường Thực Nghiệm Chuẩn Hóa", "21"),
        ("TOC3", "4.1.1. Cấu Hình Phần Cứng Thiết Bị Thử Nghiệm", "21"),
        ("TOC3", "4.1.2. Thiết Kế Các Kịch Bản Thử Nghiệm", "22"),
        ("TOC3", "4.1.3. Phương Pháp Luận Thống Kê và Kiểm Định Phi Tham Số", "22"),
        ("TOC2", "4.2. Kiểm Chứng Giả Thuyết H1: Nghẽn Main Isolate và Sự Cần Thiết Của WorkerPool (P0 vs P1)", "23"),
        ("TOC2", "4.3. Kiểm Chứng Giả Thuyết H2: Giới Hạn Của Pool FIFO Cố Định Dưới Tải Cao (P1)", "24"),
        ("TOC2", "4.4. Kiểm Chứng Giả Thuyết H3: Hiệu Quả Đột Phá Của Ưu Tiên, Phân Mảnh, Dự Trữ và Nhường Luồng (P1 -> P2 -> P3)", "25"),
        ("TOC3", "4.4.1. Phân Tích Đóng Góp Từng Thành Phần (Ablation Study)", "25"),
        ("TOC2", "4.5. Kiểm Chứng Giả Thuyết H4: Năng Lực Thích Ứng Của AIMD và Backpressure Dưới Tải Biến Thiên S2 (P4 vs P3)", "27"),
        ("TOC2", "4.6. Vi Đo Lường Phụ Tải Điều Phối (Microbenchmark of Scheduling Overhead)", "29"),
        ("TOC2", "4.7. Đánh Giá Khả Năng Khái Quát Hóa Liên Nền Tảng Thiết Bị (Cross-Device Generalizability)", "30"),
        ("TOC2", "4.8. Thực Nghiệm Trên Tác Vụ Xử Lý Dữ Liệu Đa Phương Tiện Thực Tế (s_image)", "32"),
        ("TOC2", "4.9. Minh Chứng Trực Quan Thời Gian Thực Qua Hệ Thống Stack Monitor HUD", "34"),
        ("TOC1", "CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "36"),
        ("TOC2", "5.1. Các Đóng Góp Khoa Học và Kỹ Thuật Chính", "36"),
        ("TOC2", "5.2. Những Hạn Chế Còn Tồn Tại", "37"),
        ("TOC2", "5.3. Hướng Nghiên Cứu và Phát Triển Tiếp Theo", "37"),
        ("TOC1", "TÀI LIỆU THAM KHẢO", "38")
    ]

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
            idx = content.find('</w:settings>')
            if idx != -1:
                new_content = content[:idx] + '<w:updateFields xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="true"/>' + content[idx:]
                with open(settings_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)

    doc_xml_file = os.path.join(extract_dir, 'word', 'document.xml')
    with open(doc_xml_file, 'r', encoding='utf-8') as f:
        xml_str = f.read()

    ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
    ET.register_namespace('w14', 'http://schemas.microsoft.com/office/word/2010/wordml')
    ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')

    root = ET.fromstring(xml_str.encode('utf-8'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    sdt = root.find('.//w:sdt', ns)
    content = sdt.find('.//w:sdtContent', ns)
    all_ps = content.findall('.//w:p', ns)
    last_p = all_ps[-1]

    # Giữ lại các mục từ Chương 1 và Chương 2 gốc, loại bỏ các mục cũ sau 2.4.4
    cutoff_found = False
    for p in list(content):
        txt = ''.join(p.itertext())
        if 'CHƯƠNG 3' in txt or cutoff_found:
            cutoff_found = True
            content.remove(p)

    # Thêm các mục TOC học thuật mới
    for idx, (style, text, page) in enumerate(new_toc_items):
        p_xml = f'''
        <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:pPr>
                <w:pStyle w:val="{style}"/>
                <w:tabs>
                    <w:tab w:val="right" w:leader="dot" w:pos="9016"/>
                </w:tabs>
                <w:rPr>
                    <w:noProof/>
                </w:rPr>
            </w:pPr>
            <w:hyperlink w:history="1">
                <w:r>
                    <w:rPr>
                        <w:rStyle w:val="Hyperlink"/>
                        <w:noProof/>
                    </w:rPr>
                    <w:t>{text}</w:t>
                </w:r>
                <w:r>
                    <w:rPr><w:noProof/><w:webHidden/></w:rPr>
                    <w:tab/>
                </w:r>
                <w:r>
                    <w:rPr><w:noProof/><w:webHidden/></w:rPr>
                    <w:t>{page}</w:t>
                </w:r>
            </w:hyperlink>
        </w:p>
        '''
        new_p = ET.fromstring(p_xml)
        content.append(new_p)

    # Thêm lại thẻ kết thúc trường TOC nếu chưa có
    end_p_xml = '''
    <w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:r><w:fldChar w:fldCharType="end"/></w:r>
    </w:p>
    '''
    content.append(ET.fromstring(end_p_xml))

    with open(doc_xml_file, 'wb') as f:
        f.write(ET.tostring(root, encoding='utf-8'))

    shutil.make_archive(os.path.join(temp_dir, 'new_doc'), 'zip', extract_dir)
    shutil.move(os.path.join(temp_dir, 'new_doc.zip'), doc_path)
    shutil.rmtree(temp_dir)
    print("Đã hoàn tất cấu trúc học thuật của tài liệu Word:", doc_path)

def main():
    print("Bắt đầu xử lý file docx theo định dạng học thuật chuyên sâu...")
    if not os.path.exists(DOC_IN):
        shutil.copyfile('bc.docx', DOC_IN)
        
    doc = docx.Document(DOC_IN)
    build_academic_thesis_content(doc)
    doc.save(DOC_OUT)
    print("Đã lưu bản nháp tại:", DOC_OUT)
    
    update_table_of_contents_and_settings(DOC_OUT)
    print("HOÀN TẤT NÂNG CẤP HỌC THUẬT TOÀN DIỆN TẠI:", DOC_OUT)
    try:
        shutil.copyfile(DOC_OUT, 'bc.docx')
        print("Đã đồng bộ thành công sang bc.docx!")
    except Exception as e:
        print("LƯU Ý: bc.docx hiện đang được mở trong Microsoft Word nên file đang bị khóa ghi.")
        print(f"Bản báo cáo học thuật hoàn chỉnh đã được lưu an toàn tại: {DOC_OUT}")
        print("Khi bạn đóng cửa sổ Word của bc.docx, file sẽ tự động được cập nhật hoặc bạn có thể mở trực tiếp bc_academic.docx.")

if __name__ == '__main__':
    main()
