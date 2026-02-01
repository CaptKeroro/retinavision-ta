from fpdf import FPDF
from datetime import datetime
import os
import config

class MedicalReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(10, 10, 10) # Margin tipis 1cm biar muat banyak
        self.set_auto_page_break(auto=False) # Kita kontrol halaman manual

    def header(self):
        # --- KOP SURAT PADAT ---
        # Logo
        logo_path = "logo.png"
        header_height = 28
        
        if os.path.exists(logo_path):
            self.image(logo_path, 12, 8, 18)
            text_x = 35
        else:
            text_x = 12

        # Teks Kop
        self.set_xy(text_x, 8)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'RETINAVISION EYE CENTER', 0, 1, 'L')
        
        self.set_x(text_x)
        self.set_font('Arial', 'B', 8)
        self.cell(0, 4, 'DIABETIC RETINOPATHY SCREENING UNIT', 0, 1, 'L')
        
        self.set_x(text_x)
        self.set_font('Arial', '', 7)
        self.set_text_color(80, 80, 80)
        self.cell(0, 4, 'Jl. Raya Puputan No. 86, Renon, Denpasar | Telp: (0361) 244445', 0, 1, 'L')
        
        # Garis batas header
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.line(10, header_height, 200, header_height)
        self.ln(5)

    def draw_section_box(self, title, y_pos, height):
        """Helper bikin kotak section dengan header abu-abu"""
        # Header Box
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(200, 200, 200)
        self.rect(10, y_pos, 190, 6, 'DF')
        
        # Title
        self.set_xy(12, y_pos + 1)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(0, 0, 0)
        self.cell(0, 4, title.upper(), 0, 0, 'L')
        
        # Outer Border untuk konten
        self.set_draw_color(200, 200, 200)
        self.no_fill_color = False
        self.rect(10, y_pos, 190, height) 

def create_professional_pdf(patient_data, prediction_data, img_path):
    pdf = MedicalReport()
    pdf.add_page()
    
    # KUNCI POSISI Y BIAR GAK LARI
    y_curr = 32
    
    # --- 1. PATIENT DEMOGRAPHICS (Format Grid Baris) ---
    pdf.draw_section_box("Patient Information", y_curr, 25)
    pdf.set_xy(12, y_curr + 8)
    
    pdf.set_font('Arial', '', 8)
    
    # Baris 1
    pdf.cell(25, 5, "Patient Name", 0, 0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(70, 5, f": {patient_data['name']}", 0, 0)
    
    pdf.set_font('Arial', '', 8)
    pdf.cell(25, 5, "Record No (MRN)", 0, 0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(50, 5, f": {patient_data['id']}", 0, 1)
    
    # Baris 2
    pdf.set_x(12)
    pdf.set_font('Arial', '', 8)
    pdf.cell(25, 5, "Exam Date", 0, 0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(70, 5, f": {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 0)
    
    pdf.set_font('Arial', '', 8)
    pdf.cell(25, 5, "Referring Dept", 0, 0)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(50, 5, ": Internal Medicine", 0, 1)

    # Baris 3
    pdf.set_x(12)
    pdf.set_font('Arial', '', 8)
    pdf.cell(25, 5, "Technician", 0, 0)
    pdf.cell(70, 5, ": AI Assistant System", 0, 1)

    # --- 2. MAIN CLINICAL FINDINGS (SPLIT LAYOUT) ---
    y_curr += 30 # Turun ke section berikutnya
    content_height = 80 # Tinggi area konten utama
    pdf.draw_section_box("Funduscopy Findings & AI Analysis", y_curr, content_height)
    
    # >> KOLOM KIRI (TEKS) - Lebar 110mm
    left_x = 12
    left_y = y_curr + 8
    pdf.set_xy(left_x, left_y)
    
    label = prediction_data['label']
    score = prediction_data['score']
    
    # A. AI Prediction
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(40, 5, "AI Model Classification:", 0, 0)
    
    # Warna Hasil
    if "Normal" in label:
        pdf.set_text_color(0, 100, 0)
    elif "Severe" in label or "Proliferative" in label:
        pdf.set_text_color(180, 0, 0)
    else:
        pdf.set_text_color(200, 140, 0)
        
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, f"{label.upper()}", 0, 1)
    
    # B. Confidence
    pdf.set_x(left_x)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 5, "Confidence Score:", 0, 0)
    pdf.cell(0, 5, f"{score:.2f}%", 0, 1)
    pdf.ln(3)
    
    # C. Clinical Notes (Medical Text)
    pdf.set_x(left_x)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(0, 5, "Objective Assessment:", 0, 1)
    
    pdf.set_font('Arial', '', 8)
    notes = ""
    if "Normal" in label:
        notes = "Optic disc: Batas tegas, warna normal.\nMacula: Refleks fovea (+), tidak ada edema.\nVessels: A/V ratio 2:3, tidak ada perdarahan.\nRetina: Tidak ditemukan microaneurysms atau eksudat."
    elif "Mild" in label:
        notes = "Optic disc: Normal.\nMacula: Normal.\nVessels: Kaliber normal.\nRetina: Terdeteksi microaneurysms minimal (<5). Tidak ada eksudat keras/lunak."
    elif "Moderate" in label:
        notes = "Optic disc: Normal.\nRetina: Microaneurysms multipel (>5). Terdapat dot/blot hemorrhages. Mungkin terdapat cotton wool spots.\nMacula: Perlu evaluasi ketebalan (OCT)."
    else:
        notes = "CRITICAL FINDING:\nRetina: Pendarahan intraretina luas (4 kuadran). Venous beading (+).\nKemungkinan Neovaskularisasi (NVD/NVE).\nMacula: Risiko tinggi CSME (Clinically Significant Macular Edema)."
    
    pdf.set_x(left_x)
    pdf.multi_cell(100, 4, notes)
    
    # >> KOLOM KANAN (GAMBAR) - Posisi X=130
    right_x = 130
    img_size = 60 # Ukuran 6cm (Compact)
    
    if os.path.exists(img_path):
        # Bingkai Gambar
        pdf.set_draw_color(150, 150, 150)
        pdf.rect(right_x, left_y, img_size, img_size)
        
        # Gambar
        pdf.image(img_path, right_x+1, left_y+1, img_size-2, img_size-2)
        
        # Label Gambar
        pdf.set_xy(right_x, left_y + img_size + 2)
        pdf.set_font('Arial', 'I', 6)
        pdf.cell(img_size, 3, "Fig 1. Digital Fundus Photography (45 deg)", 0, 0, 'C')
    
    # --- 3. PLAN / RECOMMENDATION (Box Bawah) ---
    y_curr += content_height + 5
    plan_height = 35
    pdf.draw_section_box("Plan & Recommendations", y_curr, plan_height)
    
    pdf.set_xy(12, y_curr + 8)
    pdf.set_font('Arial', '', 8)
    
    saran = ""
    if "Normal" in label:
        saran = "1. Observasi rutin 12 bulan sekali.\n2. Edukasi kontrol gula darah (HbA1c < 7%)."
    elif "Severe" in label or "Proliferative" in label:
        saran = "1. RUJUK CITO ke Dokter Spesialis Mata Konsultan Retina.\n2. Rencana Fluorescein Angiography (FFA) dan OCT Macula.\n3. Pertimbangkan Panretinal Photocoagulation (PRP) segera."
    else:
        saran = "1. Observasi ketat tiap 3-6 bulan.\n2. Foto fundus serial untuk monitoring progresivitas.\n3. Konsul Internis untuk regulasi metabolik agresif."
        
    pdf.multi_cell(180, 5, saran)

    # --- 4. SIGNATURE (Fixed Bottom Right) ---
    # Posisi fix di bawah agar rapi
    sig_y = y_curr + plan_height + 10
    
    pdf.set_xy(130, sig_y)
    pdf.set_font('Arial', '', 8)
    pdf.cell(60, 4, f"Denpasar, {datetime.now().strftime('%d %B %Y')}", 0, 1, 'C')
    
    pdf.set_xy(130, sig_y + 5)
    pdf.cell(60, 4, "Ophthalmologist Verification,", 0, 1, 'C')
    
    # Garis Tanda Tangan
    pdf.line(140, sig_y + 25, 180, sig_y + 25)
    
    pdf.set_xy(130, sig_y + 26)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(60, 4, "dr. Eka Surya, Sp.M(K)", 0, 1, 'C')
    
    pdf.set_xy(130, sig_y + 30)
    pdf.set_font('Arial', '', 7)
    pdf.cell(60, 4, "NIP. 19850101 2.026", 0, 1, 'C')

    # --- DISCLAIMER FOOTER ---
    pdf.set_y(-15)
    pdf.set_font('Arial', 'I', 6)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 3, "This document is computer-generated based on AI analysis (Swin-T). Clinical correlation is required.", 0, 1, 'C')
    pdf.cell(0, 3, f"RetinaVision System v3.0 | Print Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')