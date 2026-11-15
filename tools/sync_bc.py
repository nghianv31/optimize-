import shutil
import sys

try:
    shutil.copyfile('bc_academic.docx', 'bc.docx')
    print("SUCCESS: Da dong bo bc_academic.docx sang bc.docx thanh cong!")
except Exception as e:
    print(f"FAILED: bc.docx van dang duoc mo boi Microsoft Word ({e}).")
    print("Vui long dong file bc.docx trong Microsoft Word roi chay lai lenh: python tools/sync_bc.py")
