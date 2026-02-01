import streamlit as st
import pandas as pd
import tempfile
import os
import base64
import time
import uuid
from PIL import Image
import textwrap
import config
from core import DREngine
from pdf_engine import create_professional_pdf
import matplotlib.pyplot as plt

# --- SETUP HALAMAN ---
st.set_page_config(
    page_title="RetinaVision AI",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except: pass

local_css("css/style.css")

# --- INIT ENGINE ---
@st.cache_resource
def get_engine(): return DREngine()
try: engine = get_engine()
except Exception as e: st.error(f"System Failure: {e}"); st.stop()

# --- HEADER FUNCTION (DINAMIS & COLOR GRADED) ---
def render_header(placeholder, theme_color="#00FFAA"):
    
    # RACIKAN WARNA "MAHAL" (Analogous Colors)
    if theme_color == "#00FFAA": 
        # HIJAU -> BIRU LAUT (Cyber Calm)
        grad = "linear-gradient(to right, #00FFAA 0%, #0088ff 50%, #00FFAA 100%)"
        
    elif theme_color == "#FFD700": 
        # KUNING -> ORANYE (Solar Flare / Heat)
        # Ini biar efeknya kayak api yang bergerak
        grad = "linear-gradient(to right, #FFD700 0%, #FF8C00 50%, #FFD700 100%)"
        
    else: 
        # MERAH -> MAGENTA/UNGU (Fatal Error / Laser)
        # Kombinasi paling gahar untuk status bahaya
        grad = "linear-gradient(to right, #FF3333 0%, #FF00FF 50%, #FF3333 100%)"
    
    # HTML Header
    html = ""
    html += f'<h1>RetinaVision <span class="shimmer-text" style="background-image: {grad};">AI Diagnostics</span></h1>'
    html += "<p style='color:#888; margin-top:-15px;'>Sistem Deteksi Retinopati Diabetik Berbasis Swin Transformer</p>"
    
    placeholder.markdown(html, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Data Pasien")
    p_name = st.text_input("Nama Lengkap", " ")
    p_id = st.text_input("No. Rekam Medis", "RM-2026-001")
    st.markdown("---")
    st.markdown("### Input Citra")
    uploaded_file = st.file_uploader("Upload Foto Fundus", type=["jpg", "png", "jpeg"])
    st.markdown("---")
    if st.button("Reset System"):
        st.rerun()

# --- HEADER AREA ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    header_ph = st.empty()
    render_header(header_ph) # Default Hijau-Biru

if not uploaded_file:
    st.info("Silakan upload citra fundus melalui sidebar untuk memulai analisis.")
    st.stop()

uploaded_file.seek(0)
image = Image.open(uploaded_file).convert('RGB')

# --- LAYOUT UTAMA ---
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.markdown("### Visualisasi Citra")
    tab_ori, tab_filter = st.tabs(["Original", "Medical Filter (CLAHE)"])
    with tab_ori:
        st.image(image, use_container_width=True, caption="Citra Input Asli")
    with tab_filter:
        with st.spinner("Applying Enhancement..."):
            enhanced = engine.apply_clahe(image)
        st.image(enhanced, use_container_width=True, caption="Green Channel Enhanced")

with col2:
    st.markdown("### Hasil Analisis AI")
    
    # CONTAINER UTAMA
    result_container = st.empty()
    
    with st.spinner("Menganalisis Pola Retina..."):
        # 1. HARD RESET ANIMASI
        result_container.empty()
        time.sleep(0.1) 
        
        run_id = str(uuid.uuid4())
        
        pred_idx, conf, prob_dict = engine.predict(image)
        label = config.CLASS_NAMES[pred_idx]
        
        # --- LOGIKA WARNA BARU ---
        if pred_idx == 0:
            # NORMAL: Hijau Neon
            theme_color = "#00FFAA"
            text_color = "#000000"
            # Hijau <-> Biru
            label_grad = "linear-gradient(to right, #00FFAA 0%, #0088ff 50%, #00FFAA 100%)"
            
        elif pred_idx <= 2:
            # WARNING: Emas
            theme_color = "#FFD700"
            text_color = "#000000"
            # Kuning <-> Oranye (Api)
            label_grad = "linear-gradient(to right, #FFD700 0%, #FF8C00 50%, #FFD700 100%)"
            
        else:
            # CRITICAL: Merah
            theme_color = "#FF3333"
            text_color = "#FFFFFF"
            # Merah <-> Magenta (Laser/Cyber Error)
            label_grad = "linear-gradient(to right, #FF3333 0%, #FF00FF 50%, #FF3333 100%)"

        # Update Header di atas biar sinkron warnanya
        render_header(header_ph, theme_color)

        # Inject CSS (Warna Tombol & Border)
        css_inject = f"<style>"
        css_inject += f".stButton > button {{ background: {theme_color} !important; color: {text_color} !important; border: 1px solid {theme_color} !important; }}"
        css_inject += f".metric-card {{ border-left: 5px solid {theme_color} !important; }}"
        css_inject += f":root {{ --accent: {theme_color}; }}"
        css_inject += f"</style>"
        st.markdown(css_inject, unsafe_allow_html=True)
        
        # --- RENDER KONTEN (Flat String) ---
        with result_container.container():
            # 1. KARTU HASIL
            html_res = ""
            html_res += f'<div class="metric-card">'
            html_res += f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            html_res += f'<span style="color: #888; font-size: 0.85rem; font-weight:600; letter-spacing:1px;">PREDIKSI DIAGNOSA</span>'
            html_res += f'<span style="font-size: 0.8rem; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:4px; color:{theme_color};">SWIN-V2</span>'
            html_res += f'</div>'
            
            # JUDUL HASIL (Dengan Gradasi Baru)
            html_res += f'<h2 class="shimmer-text" style="margin: 15px 0; font-size: 2.2rem !important; line-height:1; font-weight:800; background-image: {label_grad};">{label}</h2>'
            
            html_res += f'<div style="margin-top: 20px;">'
            html_res += f'<div style="display: flex; justify-content: space-between; margin-bottom:8px;">'
            html_res += f'<span style="color: #ccc; font-size:0.9rem;">Confidence Score</span>'
            html_res += f'<span style="font-weight: bold; color: {theme_color}; font-size:1rem;">{conf*100:.2f}%</span>'
            html_res += f'</div>'
            html_res += f'<div style="width:100%; background:#222; height:8px; border-radius:4px; overflow:hidden;">'
            html_res += f'<div class="bar-fill" style="--target-width: {conf*100}%; background:{theme_color}; box-shadow: 0 0 15px {theme_color};"></div>'
            html_res += f'</div></div></div>'
            
            st.markdown(html_res, unsafe_allow_html=True)

            # 2. GRAFIK DISTRIBUSI
            st.markdown("#### Distribusi Probabilitas")
            
            html_chart = f"<div id='chart-{run_id}'>"
            
            for idx, (cls_name, prob) in enumerate(prob_dict.items()):
                percentage = prob * 100
                
                if idx == pred_idx:
                    bar_color = theme_color
                    font_w = "bold"
                    txt_col = "#fff"
                    glow = f"box-shadow: 0 0 10px {theme_color};"
                    op = "1"
                else:
                    bar_color = "#444"
                    font_w = "normal"
                    txt_col = "#888"
                    glow = ""
                    op = "0.3"
                    
                html_chart += f'<div style="display: flex; align-items: center; margin-bottom: 12px; font-size: 0.85rem;">'
                html_chart += f'<div style="width: 120px; color: {txt_col}; text-align: right; padding-right: 15px; font-weight:{font_w};">{cls_name}</div>'
                html_chart += f'<div style="flex-grow: 1; background: #1a1a1a; height: 8px; border-radius: 4px; overflow: hidden;">'
                html_chart += f'<div class="bar-fill" style="--target-width: {percentage}%; background: {bar_color}; opacity: {op}; {glow}"></div>'
                html_chart += f'</div>'
                html_chart += f'<div style="width: 50px; text-align: left; padding-left: 10px; font-weight: bold; color: #fff;">{percentage:.1f}%</div>'
                html_chart += f'</div>'

            html_chart += "</div>"
            st.markdown(html_chart, unsafe_allow_html=True)

# --- TOMBOL AKSI ---
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Explainability")
    if st.button("Generate Heatmap"):
        with st.spinner("Processing..."):
            hm = engine.get_saliency_map(image, pred_idx)
            @st.dialog("Saliency Map Analysis")
            def show_hm():
                st.write("Area merah menunjukkan fokus model.")
                fig_hm, ax = plt.subplots()
                ax.imshow(image); ax.imshow(hm, cmap='jet', alpha=0.5); ax.axis('off')
                st.pyplot(fig_hm)
            show_hm()

with c2:
    st.markdown("#### Laporan Medis")
    if st.button("Download PDF Report"):
        with st.spinner("Generating PDF..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                image.save(tmp.name); tmp_path = tmp.name
            try:
                pdf_bytes = create_professional_pdf({"name": p_name, "id": p_id}, {"label": label, "score": conf*100}, tmp_path)
                b64 = base64.b64encode(pdf_bytes).decode()
                st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="Report.pdf" style="text-decoration:none;"><div style="background:{theme_color}; color:{text_color}; padding:10px; text-align:center; border-radius:6px; font-weight:bold; border: 1px solid #fff;">⬇️ Click to Save PDF</div></a>', unsafe_allow_html=True)
            finally:
                if os.path.exists(tmp_path): os.remove(tmp_path)

st.markdown("<br><br><div style='text-align: center; color: #444; font-size: 0.8rem;'>© 2026 ITB STIKOM BALI</div>", unsafe_allow_html=True)