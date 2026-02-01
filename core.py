import torch
import torch.nn as nn
import torchvision.transforms as transforms
import timm
from PIL import Image
import numpy as np
import config 
import os

# --- 1. DEFINISI ADAPTER (Sesuai Notebook) ---
class SwinFeatureAdapter(nn.Module):
    def forward(self, x):
        # Penyelamat Error 4D: Mengubah (B, H, W, C) -> (B, C)
        if x.dim() == 4:
            x = x.permute(0, 3, 1, 2) # Pindah channel ke depan
            x = x.mean(dim=(2, 3))    # Global Average Pooling
        return x

class DREngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🚀 AI Engine Starting on: {self.device}")
        
        # Load Model dengan Arsitektur Custom
        self.model = self._build_and_load_model()
        self.transform = self._get_transforms()

    def _build_and_load_model(self) -> nn.Module:
        # 1. Cek File Model
        if config.MODEL_PATH.exists():
            weight_path = config.MODEL_PATH
        else:
            # Fallback cari file .pth apa saja
            import pathlib
            files = list(pathlib.Path(__file__).parent.glob("*.pth"))
            if not files:
                raise FileNotFoundError("❌ Tidak ada file model .pth di folder ini!")
            weight_path = files[0]

        print(f"📂 Loading weights from: {weight_path.name}")

        # 2. BANGUN ARSITEKTUR (Sama persis dengan Notebook)
        # Ambil backbone saja (num_classes=0)
        model = timm.create_model(config.MODEL_NAME, pretrained=False, num_classes=0)
        n_inputs = model.num_features # Biasanya 1024 untuk Swin Base

        # Pasang Head Custom (Adapter + MLP)
        model.head = nn.Sequential(
            SwinFeatureAdapter(),
            nn.BatchNorm1d(n_inputs),
            nn.Linear(n_inputs, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 5) # Wajib 5 Kelas (Sesuai Notebook)
        )

        # 3. LOAD BOBOT
        try:
            checkpoint = torch.load(weight_path, map_location=self.device)
            
            # Handle berbagai jenis cara save
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint

            # Load dengan strict=False (Jaga-jaga ada prefix 'module.' dsb)
            model.load_state_dict(state_dict, strict=False)
            
            model.to(self.device)
            model.eval()
            print("✅ Model Structure: Backbone + Custom Head (Loaded Successfully)")
            return model

        except Exception as e:
            raise RuntimeError(f"Gagal memuat model: {e}")

    def _get_transforms(self) -> transforms.Compose:
        # Gunakan Transformasi Validasi dari Notebook (RGB + Normalize)
        return transforms.Compose([
            transforms.Resize((config.IMG_SIZE, config.IMG_SIZE)),
            transforms.ToTensor(),
            # Normalisasi ImageNet (Sesuai Notebook snippet 2.3)
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def predict(self, image: Image.Image) -> tuple:
        # 1. Pastikan RGB (Sesuai Notebook yang pakai PIL)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 2. Preprocess
        img_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # 3. Inference
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            conf, pred = torch.max(probs, 1)
            
        pred_val = pred.item()
        conf_val = conf.item()
        
        # Mapping Probabilitas
        prob_dict = {}
        for i in range(5):
            prob_dict[config.CLASS_NAMES[i]] = float(probs[0, i].item())
        
        return pred_val, conf_val, prob_dict

    def get_saliency_map(self, image: Image.Image, predicted_class: int) -> np.ndarray:
        try:
            if image.mode != 'RGB': image = image.convert('RGB')
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            img_tensor.requires_grad_()
            self.model.zero_grad() # Reset gradien
            
            output = self.model(img_tensor)
            score = output[0][predicted_class]
            score.backward()
            
            saliency, _ = torch.max(img_tensor.grad.data.abs(), dim=1)
            saliency = saliency.reshape(config.IMG_SIZE, config.IMG_SIZE)
            
            # Normalisasi heatmap
            saliency = saliency.cpu().numpy()
            return (saliency - saliency.min()) / (saliency.max() - saliency.min())
        except:
            return np.zeros((config.IMG_SIZE, config.IMG_SIZE))

    @staticmethod
    def apply_clahe(image: Image.Image) -> Image.Image:
        # Konversi ke array numpy
        img_np = np.array(image)
        
        # CLAHE biasanya main di channel Luminance (LAB) atau Green (RGB)
        # Kita ambil Green channel saja untuk visualisasi pembuluh darah
        if len(img_np.shape) == 3:
            g = img_np[:, :, 1] # Green Channel
            import cv2
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(g)
            return Image.fromarray(enhanced)
        return image