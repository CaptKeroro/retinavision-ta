import os
import gdown
from pathlib import Path

# --- PATH SETUP ---
BASE_DIR = Path(__file__).parent
# Auto-detect nama file model di folder yang sama
MODEL_PATH = BASE_DIR / "best_model_swin.pth"

if not os.path.exists(MODEL_PATH):
    print("Mengunduh bobot model dari Google Drive...")
    file_id = '1_wkEB-Fs_xt9QlZtsrp1FavEbvDvNxLE'
    url = f'https://drive.google.com/uc?id={file_id}'
    gdown.download(url, str(MODEL_PATH), quiet=False)

# --- MODEL CONFIG ---
MODEL_NAME = 'swin_base_patch4_window7_224'
NUM_CLASSES = 5
IMG_SIZE = 224
# Normalisasi dimatikan di core.py untuk akurasi raw, tapi config tetap disimpan
NORMALIZATION_MEAN = [0.485, 0.456, 0.406]
NORMALIZATION_STD = [0.229, 0.224, 0.225]

# --- UI CONFIG ---
APP_TITLE = "RetinaVision AI"
THEME_COLOR = "#00FFAA" # Warna Cyberpunk Green
COMPANY_NAME = "ITB STIKOM BALI"

# --- LABELS (Sesuai Standar Medis) ---
CLASS_NAMES = {
    0: "Normal (No DR)",
    1: "Mild NPDR",
    2: "Moderate NPDR",
    3: "Severe NPDR",
    4: "Proliferative DR"
}