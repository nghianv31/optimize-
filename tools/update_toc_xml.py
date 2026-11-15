# -*- coding: utf-8 -*-
import zipfile
import xml.etree.ElementTree as ET
import shutil
import tempfile
import os

doc_path = 'bc.docx'

new_toc_items = [
    ("TOC1", "CHƯƠNG 3: THIẾT KẾ VÀ HIỆN THỰC BỘ LẬP LỊCH TÁC VỤ THÍCH ỨNG", "11"),
    ("TOC2", "3.1. Kiến trúc Tổng thể Hệ thống Lập lịch Tầng Ứng dụng", "11"),
    ("TOC3", "3.1.1. Mô hình Phân lớp Kiến trúc", "11"),
    ("TOC3", "3.1.2. Vòng đời và Đường ống Xử lý Tác vụ (Task Lifecycle Pipeline)", "12"),
    ("TOC2", "3.2. Mô hình Tác vụ và Hàng đợi Ưu tiên Đa mức kèm Kỹ thuật Aging (P2)", "13"),
    ("TOC3", "3.2.1. Phân loại Mức độ Ưu tiên Tác vụ", "13"),
    ("TOC3", "3.2.2. Cấu trúc Hàng đợi 3 Làn với Độ phức tạp O(1)", "13"),
    ("TOC3", "3.2.3. Giải thuật Aging Chống Bỏ đói (Zero Starvation)", "14"),
    ("TOC2", "3.3. Cơ chế Đa nhiệm Hợp tác và Kỹ thuật Chunking (P3)", "14"),
    ("TOC3", "3.3.1. Rào cản Bất khả Ngắt của Isolate và Giải pháp Hợp tác", "14"),
    ("TOC3", "3.3.2. Thiết kế Máy Trạng thái Tác vụ và Điểm Nhường Luồng (Yield Point)", "15"),
    ("TOC3", "3.3.3. Hiện thực Chunking trên Tác vụ I/O Đọc Ảnh Thực tế", "15"),
    ("TOC2", "3.4. Kỹ thuật Critical Worker Reserve — Ghế Dự phòng VIP (P3r)", "16"),
    ("TOC2", "3.5. Đồng bộ Nhịp Vsync và Kỹ thuật Frame Yielding (P3)", "16"),
    ("TOC3", "3.5.1. Giám sát Khoảng cách Khung hình Tức thời với FrameSignal", "16"),
    ("TOC3", "3.5.2. Thuật toán Nhường Khung hình có Vùng đệm Trễ (Hysteresis Frame Yielding)", "17"),
    ("TOC2", "3.6. Thuật toán Điều khiển Phản hồi Thích ứng AIMD (P4)", "17"),
    ("TOC3", "3.6.1. Nguyên lý Điều hòa Tắc nghẽn CPU", "17"),
    ("TOC3", "3.6.2. Hiện thực Bộ Điều khiển AimdController", "18"),
    ("TOC3", "3.6.3. Quy tắc Miễn nhiễm cho Tác vụ Khẩn cấp", "18"),
    ("TOC2", "3.7. Cơ chế Áp lực Ngược (Backpressure) và Xả Tải Chủ Động (P4)", "19"),
    ("TOC3", "3.7.1. Cơ sở Toán học từ Định luật Little", "19"),
    ("TOC3", "3.7.2. Chính sách Loại bỏ Tác vụ Hết hạn (Stale Work Elimination)", "19"),
    ("TOC2", "3.8. Máy Trạng thái Suy giảm Thích ứng Môi trường (P4)", "20"),
    ("TOC3", "3.8.1. Thu thập Tín hiệu Nhiệt độ và Pin từ Android Native", "20"),
    ("TOC3", "3.8.2. Ba Chế độ Suy giảm và Cơ chế Trễ Hysteresis", "20"),
    ("TOC2", "3.9. Tổng hợp Đối chiếu Kiến trúc 5 Chính sách Lập lịch (P0 -> P4)", "21"),
    ("TOC1", "CHƯƠNG 4: KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ ĐÓNG GÓP", "22"),
    ("TOC2", "4.1. Thiết lập Môi trường và Phương pháp Đo lường Chuẩn hóa", "22"),
    ("TOC3", "4.1.1. Thiết bị Phần cứng và Môi trường Đo lường", "22"),
    ("TOC3", "4.1.2. Kịch bản Thực nghiệm", "23"),
    ("TOC3", "4.1.3. Phương pháp Đo lường và Kiểm định Thống kê", "23"),
    ("TOC2", "4.2. Kiểm chứng Giả thuyết H1: Nghẽn Main Isolate và Hiệu quả của WorkerPool (P0 vs P1)", "24"),
    ("TOC2", "4.3. Kiểm chứng Giả thuyết H2: Giới hạn của Pool FIFO Cố định Dưới Tải Cao (P1)", "25"),
    ("TOC2", "4.4. Kiểm chứng Giả thuyết H3: Vai trò của Ưu tiên, Chunking, Reserve và Nhường Frame (P1 -> P2 -> P3)", "26"),
    ("TOC3", "4.4.1. Phân rã Đóng góp Kiến trúc (Ablation Study)", "26"),
    ("TOC2", "4.5. Kiểm chứng Giả thuyết H4: Thích ứng Động AIMD và Backpressure Trên Kịch bản S2 (P4 vs P3)", "28"),
    ("TOC2", "4.6. Đo lường Phụ tải (Overhead) của Bộ Lập lịch (Microbenchmark E3)", "30"),
    ("TOC2", "4.7. Đánh giá Khả năng Khái quát hóa Liên Thiết bị (Cross-Device Evaluation)", "31"),
    ("TOC2", "4.8. Thực nghiệm Tác vụ Ảnh Thực tế (s_image) Trên Bộ 80 Ảnh DSLR 24MP", "33"),
    ("TOC2", "4.9. Minh chứng Trực quan Thời Gian Thực qua Stack Monitor HUD", "35"),
    ("TOC1", "CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "37"),
    ("TOC2", "5.1. Các Đóng góp Chính của Đề tài", "37"),
    ("TOC2", "5.2. Những Hạn chế Còn Tồn tại", "38"),
    ("TOC2", "5.3. Hướng Nghiên cứu và Phát triển Tiếp theo", "38"),
    ("TOC1", "TÀI LIỆU THAM KHẢO", "39")
]

temp_dir = tempfile.mkdtemp()
temp_zip = os.path.join(temp_dir, 'temp.docx')
shutil.copyfile(doc_path, temp_zip)

extract_dir = os.path.join(temp_dir, 'extracted')
with zipfile.ZipFile(temp_zip, 'r') as z:
    z.extractall(extract_dir)

doc_xml_file = os.path.join(extract_dir, 'word', 'document.xml')
with open(doc_xml_file, 'r', encoding='utf-8') as f:
    xml_str = f.read()

# Register namespaces
ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')
ET.register_namespace('w14', 'http://schemas.microsoft.com/office/word/2010/wordml')
ET.register_namespace('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships')

root = ET.fromstring(xml_str.encode('utf-8'))
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

sdt = root.find('.//w:sdt', ns)
content = sdt.find('.//w:sdtContent', ns)

# Tìm đoạn văn bản cuối cùng trong sdtContent (chứa fldCharType="end")
all_ps = content.findall('.//w:p', ns)
last_p = all_ps[-1]

# Tạo các đoạn văn bản TOC mới
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
    # Chèn trước đoạn cuối cùng
    idx_last = list(content).index(last_p)
    content.insert(idx_last, new_p)

# Ghi lại document.xml
with open(doc_xml_file, 'wb') as f:
    f.write(ET.tostring(root, encoding='utf-8'))

# Đóng gói lại thành docx
shutil.make_archive(os.path.join(temp_dir, 'new_doc'), 'zip', extract_dir)
shutil.move(os.path.join(temp_dir, 'new_doc.zip'), doc_path)
shutil.rmtree(temp_dir)
print("Đã cập nhật hoàn tất toàn bộ các mục trong Mục lục của bc.docx!")
